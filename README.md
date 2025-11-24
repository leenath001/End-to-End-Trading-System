# End-to-End Trading System

Lightweight event-driven trading stack with live Alpaca integration and built-in backtesting.

- **Live loop**: `main.py` wires Alpaca delayed quotes into `Equity`, runs strategy signals (default mean reversion), and routes orders through `OrderManager` (Alpaca paper REST).
- **Data gateways**: `systems/gateway_in.py` provides Alpaca live quotes and yfinance historical bars for backtests.
- **State & strategies**: `systems/equity.py` tracks rolling quotes/trades per symbol; `systems/strategy.py` includes MeanReversion, AutoRegresion (AR(1)), and RandomStrategy examples.
- **Backtester**: `backtester.py` streams historical data, simulates a matching engine (fills/partial/cancel, slippage, commissions), tracks P&L, and emits per-strategy performance reports and equity curves under `reports/`.
- **Reports**: run `python backtester.py` to regenerate `reports/*_performance_report.md`, equity curve PNGs, and a consolidated `reports/comparison_report.md` comparing all strategies.
