# Backtest Performance Report

## Configuration
- **symbols**: ['AAPL', 'NVDA']
- **strategy**: MeanReversion
- **order_size**: 75
- **initial_cash**: 80000
- **data_period**: 365d
- **data_interval**: 60m
- **fill_rate**: 0.85
- **cancel_prob**: 0.05
- **slippage_bps**: 2.0

## Performance Metrics
- **sharpe**: 1.7351
- **max_drawdown_pct**: -80.1852
- **final_equity**: 1036545.0045
- **total_return_pct**: 1195.6813
- **win_rate**: 0.3252
- **avg_win**: 2754.1455
- **avg_loss**: 0.0000
- **win_loss_ratio**: nan
- **realized_pnl**: 958442.6292
- **commissions**: 0.0000

## Trade Summary
- Trades: 1070
- Partial fills: 0
- First 5 trades:

| timestamp                 | symbol   | side   |   qty |   price | partial   |   realized_pnl |   commission |   position_after |
|:--------------------------|:---------|:-------|------:|--------:|:----------|---------------:|-------------:|-----------------:|
| 2024-06-13 16:30:00+00:00 | AAPL     | SELL   |    75 | 128.383 | False     |              0 |            0 |              -75 |
| 2024-06-13 17:30:00+00:00 | AAPL     | SELL   |    75 | 128.814 | False     |              0 |            0 |             -150 |
| 2024-06-13 18:30:00+00:00 | AAPL     | SELL   |    75 | 129.064 | False     |              0 |            0 |             -225 |
| 2024-06-13 19:30:00+00:00 | AAPL     | SELL   |    75 | 129.344 | False     |              0 |            0 |             -300 |
| 2024-06-14 13:30:00+00:00 | AAPL     | SELL   |    75 | 132.613 | False     |              0 |            0 |             -375 |

## Equity Curve
![Equity Curve](reports/meanreversion_equity_curve.png)