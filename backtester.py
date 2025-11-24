from __future__ import annotations

import math
import random
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import systems.strategy as strat
from systems.equity import Equity
from systems.gateway_in import YF_ENDPOINT


@dataclass
class Order:
    order_id: str
    symbol: str
    side: str  # BUY or SELL
    qty: int
    submitted_at: pd.Timestamp
    status: str = "NEW"


@dataclass
class Fill:
    order_id: str
    symbol: str
    side: str
    qty: int
    price: float
    timestamp: pd.Timestamp
    partial: bool
    commission: float = 0.0


@dataclass
class BacktestResult:
    equity_curve: pd.DataFrame
    trades: pd.DataFrame
    metrics: Dict[str, float]
    config: Dict[str, object]
    orders: pd.DataFrame


class MatchingEngine:
    """
    Simulates fills, partial fills, and cancellations against bar data.
    """

    def __init__(
        self,
        fill_rate: float = 0.9,
        cancel_prob: float = 0.05,
        slippage_bps: float = 1.5,
        commission_per_share: float = 0.0,
    ):
        self.fill_rate = fill_rate
        self.cancel_prob = cancel_prob
        self.slippage_bps = slippage_bps
        self.commission_per_share = commission_per_share

    def execute(
        self,
        order: Order,
        bar_price: float,
        bar_volume: float,
        timestamp: pd.Timestamp,
    ) -> Tuple[Order, Optional[Fill]]:
        if random.random() < self.cancel_prob:
            order.status = "CANCELLED"
            return order, None

        potential_qty = int(bar_volume * self.fill_rate)
        filled_qty = min(order.qty, max(potential_qty, 0))
        if filled_qty <= 0:
            order.status = "OPEN"
            return order, None

        slip_mult = 1 + (self.slippage_bps / 10_000) * (
            1 if order.side == "BUY" else -1
        )
        fill_price = bar_price * slip_mult
        partial = filled_qty < order.qty
        order.status = "PARTIALLY_FILLED" if partial else "FILLED"

        commission = self.commission_per_share * filled_qty
        fill = Fill(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            qty=filled_qty,
            price=fill_price,
            timestamp=timestamp,
            partial=partial,
            commission=commission,
        )
        return order, fill


class BACKTESTING_ENGINE:
    """
    Event-driven backtester that reuses the strategy and Equity classes.
    """

    def __init__(
        self,
        symbols: List[str],
        strategy: strat.Strategy,
        data_endpoint,
        initial_cash: float = 100_000,
        order_size: int = 100,
        fill_rate: float = 0.9,
        cancel_prob: float = 0.05,
        slippage_bps: float = 1.5,
        commission_per_share: float = 0.0,
        data_period: str = "365d",
        data_interval: str = "60m",
    ):
        self.symbols = symbols
        self.strategy = strategy
        self.data_endpoint_cls = data_endpoint
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.order_size = order_size
        self.positions = {sym: 0 for sym in self.symbols}
        self.avg_price = {sym: 0.0 for sym in self.symbols}
        self.eq = {sym: Equity(sym) for sym in self.symbols}
        self.equity_curve: List[Dict[str, object]] = []
        self.trades: List[Dict[str, object]] = []
        self.orders: List[Dict[str, object]] = []
        self.realized_pnl = 0.0
        self.total_commissions = 0.0
        self.matching_engine = MatchingEngine(
            fill_rate=fill_rate,
            cancel_prob=cancel_prob,
            slippage_bps=slippage_bps,
            commission_per_share=commission_per_share,
        )
        self.period = data_period
        self.interval = data_interval

        self.endpoint = self.data_endpoint_cls(
            self.symbols, self.period, self.interval
        )
        self.endpoint.data_grabber()
        self._stream_iter = self.endpoint.stream()

    def _scalar(self, value) -> float:
        try:
            if hasattr(value, "iloc"):
                return float(value.iloc[0])
            if hasattr(value, "item"):
                return float(value.item())
            return float(value)
        except Exception:
            arr = np.asarray(value).flatten()
            return float(arr[0])

    def _mark_price(self, symbol: str, price: float, size: float, ts):
        self.eq[symbol].update_trade(price=price, size=size, timestamp=ts)

    def load_next_tick(self):
        try:
            ts, bars = next(self._stream_iter)
        except StopIteration:
            return None

        for sym in self.symbols:
            bar = bars[sym]
            close_px = self._scalar(bar["close"])
            vol = self._scalar(bar["volume"])
            self._mark_price(sym, close_px, vol, ts)

        return ts, bars

    def _update_positions_from_fill(self, fill: Fill) -> float:
        sym = fill.symbol
        side = fill.side
        qty = fill.qty
        price = fill.price
        pos = self.positions.get(sym, 0)
        avg_price = self.avg_price.get(sym, 0.0)
        realized = 0.0

        if side == "BUY":
            if pos < 0:
                closing = min(qty, -pos)
                realized += (avg_price - price) * closing
                self.cash -= price * closing
                pos += closing
                qty -= closing
                if pos == 0:
                    avg_price = 0.0
            if qty > 0:
                self.cash -= price * qty
                if pos >= 0:
                    new_qty = pos + qty
                    avg_price = (
                        (avg_price * pos + price * qty) / new_qty if new_qty else 0.0
                    )
                    pos = new_qty
                else:
                    pos += qty
                    avg_price = price
        elif side == "SELL":
            if pos > 0:
                closing = min(qty, pos)
                realized += (price - avg_price) * closing
                self.cash += price * closing
                pos -= closing
                qty -= closing
                if pos == 0:
                    avg_price = 0.0
            if qty > 0:
                self.cash += price * qty
                if pos <= 0:
                    new_qty = pos - qty
                    avg_price = (
                        (avg_price * abs(pos) + price * qty) / abs(new_qty)
                        if new_qty
                        else 0.0
                    )
                    pos = new_qty
                else:
                    pos -= qty
                    avg_price = price

        self.positions[sym] = pos
        self.avg_price[sym] = avg_price
        self.realized_pnl += realized
        self.total_commissions += fill.commission
        return realized

    def _record_equity(self, ts, bars):
        equity_val = self.cash
        for sym in self.symbols:
            price = self._scalar(bars[sym]["close"])
            equity_val += self.positions.get(sym, 0) * price
        self.equity_curve.append({"timestamp": ts, "equity": equity_val})

    def _orders_per_year(self) -> float:
        interval = self.interval
        if interval.endswith("m"):
            minutes = int(interval[:-1])
            bars_per_day = max(1, 390 // minutes)
        elif interval.endswith("h"):
            hours = int(interval[:-1])
            bars_per_day = max(1, int(6.5 // hours))
        else:
            bars_per_day = 1
        return bars_per_day * 252

    def compute_metrics(self) -> Dict[str, float]:
        eq_df = pd.DataFrame(self.equity_curve)
        metrics: Dict[str, float] = {}
        if eq_df.empty:
            return metrics

        eq_df["returns"] = eq_df["equity"].pct_change()
        returns = eq_df["returns"].dropna()
        periods_per_year = self._orders_per_year()

        if not returns.empty and returns.std() != 0:
            sharpe = math.sqrt(periods_per_year) * returns.mean() / returns.std()
            metrics["sharpe"] = sharpe
        else:
            metrics["sharpe"] = float("nan")

        running_max = eq_df["equity"].cummax()
        drawdown = (eq_df["equity"] - running_max) / running_max
        metrics["max_drawdown_pct"] = drawdown.min() * 100
        metrics["final_equity"] = eq_df["equity"].iloc[-1]
        metrics["total_return_pct"] = (
            (eq_df["equity"].iloc[-1] - eq_df["equity"].iloc[0])
            / eq_df["equity"].iloc[0]
            * 100
        )

        trades_df = pd.DataFrame(self.trades)
        if not trades_df.empty:
            wins = trades_df.loc[trades_df["realized_pnl"] > 0, "realized_pnl"]
            losses = trades_df.loc[trades_df["realized_pnl"] < 0, "realized_pnl"]
            metrics["win_rate"] = len(wins) / len(trades_df)
            metrics["avg_win"] = wins.mean() if not wins.empty else 0.0
            metrics["avg_loss"] = losses.mean() if not losses.empty else 0.0
            if not wins.empty and not losses.empty:
                metrics["win_loss_ratio"] = abs(wins.mean() / losses.mean())
            else:
                metrics["win_loss_ratio"] = float("nan")
        metrics["realized_pnl"] = self.realized_pnl
        metrics["commissions"] = self.total_commissions
        return metrics

    def run(self) -> BacktestResult:
        target = self.strategy.symbol.upper()
        while True:
            tick = self.load_next_tick()
            if tick is None:
                break

            ts, bars = tick
            signal = self.strategy.compute_signal()
            price = self._scalar(bars[target]["close"])
            volume = self._scalar(bars[target]["volume"])

            if signal in ("BUY", "SELL"):
                order = Order(
                    order_id=str(uuid.uuid4()),
                    symbol=target,
                    side=signal,
                    qty=self.order_size,
                    submitted_at=ts,
                    status="NEW",
                )
                order, fill = self.matching_engine.execute(order, price, volume, ts)
                self.orders.append(
                    {
                        "timestamp": ts,
                        "symbol": target,
                        "side": signal,
                        "qty": self.order_size,
                        "status": order.status,
                    }
                )
                if fill:
                    realized = self._update_positions_from_fill(fill)
                    self.trades.append(
                        {
                            "timestamp": ts,
                            "symbol": target,
                            "side": signal,
                            "qty": fill.qty,
                            "price": fill.price,
                            "partial": fill.partial,
                            "realized_pnl": realized,
                            "commission": fill.commission,
                            "position_after": self.positions[target],
                        }
                    )

            self._record_equity(ts, bars)

        eq_df = pd.DataFrame(self.equity_curve)
        trades_df = pd.DataFrame(self.trades)
        orders_df = pd.DataFrame(self.orders)
        metrics = self.compute_metrics()
        config = {
            "symbols": self.symbols,
            "strategy": type(self.strategy).__name__,
            "order_size": self.order_size,
            "initial_cash": self.initial_cash,
            "data_period": self.period,
            "data_interval": self.interval,
            "fill_rate": self.matching_engine.fill_rate,
            "cancel_prob": self.matching_engine.cancel_prob,
            "slippage_bps": self.matching_engine.slippage_bps,
        }
        return BacktestResult(
            equity_curve=eq_df,
            trades=trades_df,
            metrics=metrics,
            config=config,
            orders=orders_df,
        )


def plot_equity_curve(dates, equity_values, path: Path, strategy_name="Strategy"):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dates, equity_values, label=strategy_name, color="mediumblue", linewidth=2)
    ax.set_title("Equity Curve", fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity ($)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="best")
    fig.autofmt_xdate(rotation=45)
    plt.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def render_report(result: BacktestResult, report_path: Path, equity_path: Path):
    report_path.parent.mkdir(parents=True, exist_ok=True)
    equity_path.parent.mkdir(parents=True, exist_ok=True)

    if not result.equity_curve.empty:
        plot_equity_curve(
            result.equity_curve["timestamp"],
            result.equity_curve["equity"],
            equity_path,
            strategy_name=result.config["strategy"],
        )

    md: List[str] = []
    md.append("# Backtest Performance Report\n")
    md.append("## Configuration")
    for k, v in result.config.items():
        md.append(f"- **{k}**: {v}")

    md.append("\n## Performance Metrics")
    if result.metrics:
        for k, v in result.metrics.items():
            md.append(f"- **{k}**: {v:.4f}" if isinstance(v, float) else f"- **{k}**: {v}")
    else:
        md.append("- No metrics computed (no equity curve).")

    md.append("\n## Trade Summary")
    if not result.trades.empty:
        md.append(f"- Trades: {len(result.trades)}")
        md.append(
            f"- Partial fills: {int(result.trades['partial'].sum())}"
        )
        try:
            trade_table = result.trades.head(5).to_markdown(index=False)
        except Exception:
            trade_table = result.trades.head(5).to_string(index=False)
        md.append(f"- First 5 trades:\n\n{trade_table}")
    else:
        md.append("- No trades executed.")

    if equity_path.exists():
        md.append(f"\n## Equity Curve\n![Equity Curve]({equity_path})")

    report_path.write_text("\n".join(md))


def render_comparison(entries: List[Dict[str, object]], report_path: Path):
    """
    Build a side-by-side comparison markdown for multiple strategy results.
    """
    report_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    links = []
    for entry in entries:
        name = entry["name"]
        result: BacktestResult = entry["result"]
        metrics = result.metrics
        trades_count = len(result.trades)
        rows.append(
            {
                "strategy": name,
                "sharpe": metrics.get("sharpe"),
                "total_return_pct": metrics.get("total_return_pct"),
                "max_drawdown_pct": metrics.get("max_drawdown_pct"),
                "final_equity": metrics.get("final_equity"),
                "win_rate": metrics.get("win_rate"),
                "trades": trades_count,
                "realized_pnl": metrics.get("realized_pnl"),
            }
        )
        links.append(
            f"- **{name}**: [performance report]({entry['report']}), "
            f"[equity curve]({entry['equity']})"
        )

    df = pd.DataFrame(rows)
    md: List[str] = []
    md.append("# Strategy Comparison")
    md.append("\n## Summary Table")
    try:
        table = df.to_markdown(index=False, floatfmt=".4f")
    except Exception:
        table = df.to_string(index=False)
    md.append(f"\n{table}\n")
    md.append("## Links")
    md.extend(links)

    report_path.write_text("\n".join(md))


if __name__ == "__main__":
    SYMBOLS = ["AAPL", "NVDA"]
    DATA_ENDPOINT = YF_ENDPOINT
    INITIAL_CASH = 80_000
    ORDER_SIZE = 75
    FILL_RATE = 0.85
    CANCEL_PROB = 0.05
    SLIPPAGE_BPS = 2.0
    COMMISSION_PER_SHARE = 0.0
    DATA_PERIOD = "365d"
    DATA_INTERVAL = "60m"

    strategies = [
        ("MeanReversion", strat.MeanReversion(symbol="AAPL", window=10, z_thresh=1.3)),
        ("AutoRegresion", strat.AutoRegresion(symbol="AAPL")),
        ("RandomStrategy", strat.RandomStrategy(symbol="AAPL")),
    ]

    report_dir = Path("reports")
    comparison_entries = []
    for name, strategy in strategies:
        print(f"Starting backtest for {name}...")
        engine = BACKTESTING_ENGINE(
            symbols=SYMBOLS,
            strategy=strategy,
            data_endpoint=DATA_ENDPOINT,
            initial_cash=INITIAL_CASH,
            order_size=ORDER_SIZE,
            fill_rate=FILL_RATE,
            cancel_prob=CANCEL_PROB,
            slippage_bps=SLIPPAGE_BPS,
            commission_per_share=COMMISSION_PER_SHARE,
            data_period=DATA_PERIOD,
            data_interval=DATA_INTERVAL,
        )

        result = engine.run()
        print(f"Backtest complete for {name}.")

        report_path = report_dir / f"{name.lower()}_performance_report.md"
        equity_path = report_dir / f"{name.lower()}_equity_curve.png"
        render_report(result, report_path=report_path, equity_path=equity_path)

        comparison_entries.append(
            {"name": name, "result": result, "report": report_path, "equity": equity_path}
        )

        print(f"Report written to {report_path}")

    render_comparison(comparison_entries, report_dir / "comparison_report.md")
    print(f"Comparison report written to {report_dir / 'comparison_report.md'}")
