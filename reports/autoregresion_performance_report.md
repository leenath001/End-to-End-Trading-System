# Backtest Performance Report

## Configuration
- **symbols**: ['AAPL', 'NVDA']
- **strategy**: AutoRegresion
- **order_size**: 75
- **initial_cash**: 80000
- **data_period**: 365d
- **data_interval**: 60m
- **fill_rate**: 0.85
- **cancel_prob**: 0.05
- **slippage_bps**: 2.0

## Performance Metrics
- **sharpe**: -0.7560
- **max_drawdown_pct**: -389.8475
- **final_equity**: -5987686.2192
- **total_return_pct**: -7584.7858
- **win_rate**: 0.0108
- **avg_win**: 568.5266
- **avg_loss**: -3577.4957
- **win_loss_ratio**: 0.1589
- **realized_pnl**: -2857947.3908
- **commissions**: 0.0000

## Trade Summary
- Trades: 2416
- Partial fills: 0
- First 5 trades:

| timestamp                 | symbol   | side   |   qty |   price | partial   |   realized_pnl |   commission |   position_after |
|:--------------------------|:---------|:-------|------:|--------:|:----------|---------------:|-------------:|-----------------:|
| 2024-06-12 13:30:00+00:00 | AAPL     | SELL   |    75 | 126.815 | False     |              0 |            0 |              -75 |
| 2024-06-12 14:30:00+00:00 | AAPL     | SELL   |    75 | 125.515 | False     |              0 |            0 |             -150 |
| 2024-06-12 15:30:00+00:00 | AAPL     | SELL   |    75 | 125.555 | False     |              0 |            0 |             -225 |
| 2024-06-12 16:30:00+00:00 | AAPL     | SELL   |    75 | 125.854 | False     |              0 |            0 |             -300 |
| 2024-06-12 17:30:00+00:00 | AAPL     | SELL   |    75 | 125.625 | False     |              0 |            0 |             -375 |

## Equity Curve
![Equity Curve](reports/autoregresion_equity_curve.png)