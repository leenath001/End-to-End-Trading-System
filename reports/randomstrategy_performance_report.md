# Backtest Performance Report

## Configuration
- **symbols**: ['AAPL', 'NVDA']
- **strategy**: RandomStrategy
- **order_size**: 75
- **initial_cash**: 80000
- **data_period**: 365d
- **data_interval**: 60m
- **fill_rate**: 0.85
- **cancel_prob**: 0.05
- **slippage_bps**: 2.0

## Performance Metrics
- **sharpe**: -1.4055
- **max_drawdown_pct**: -42.6521
- **final_equity**: 49392.0512
- **total_return_pct**: -38.2574
- **win_rate**: 0.2233
- **avg_win**: 121.0262
- **avg_loss**: -162.7216
- **win_loss_ratio**: 0.7438
- **realized_pnl**: -28270.1226
- **commissions**: 0.0000

## Trade Summary
- Trades: 1603
- Partial fills: 0
- First 5 trades:

| timestamp                 | symbol   | side   |   qty |   price | partial   |   realized_pnl |   commission |   position_after |
|:--------------------------|:---------|:-------|------:|--------:|:----------|---------------:|-------------:|-----------------:|
| 2024-06-12 13:30:00+00:00 | AAPL     | BUY    |    75 | 215.278 | False     |          0     |            0 |               75 |
| 2024-06-12 14:30:00+00:00 | AAPL     | SELL   |    75 | 217.537 | False     |        169.39  |            0 |                0 |
| 2024-06-12 16:30:00+00:00 | AAPL     | BUY    |    75 | 216.973 | False     |          0     |            0 |               75 |
| 2024-06-12 17:30:00+00:00 | AAPL     | SELL   |    75 | 218.916 | False     |        145.728 |            0 |                0 |
| 2024-06-12 19:30:00+00:00 | AAPL     | BUY    |    75 | 213.154 | False     |          0     |            0 |               75 |

## Equity Curve
![Equity Curve](reports/randomstrategy_equity_curve.png)