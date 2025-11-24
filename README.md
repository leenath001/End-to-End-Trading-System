# End-to-End Trading System

Lightweight event-driven trading stack with live Alpaca integration and built-in backtesting.

## Overview

- **Live loop**: `main.py` wires Alpaca delayed quotes into `Equity`, runs strategy signals (default mean reversion), and routes orders through `OrderManager` (Alpaca paper REST).
- **Data gateways**: `systems/gateway_in.py` provides Alpaca live quotes and yfinance historical bars for backtests.
- **State & strategies**: `systems/equity.py` tracks rolling quotes/trades per symbol; `systems/strategy.py` includes MeanReversion, AutoRegresion (AR(1)), and RandomStrategy examples.
- **Backtester**: `backtester.py` streams historical data, simulates a matching engine (fills/partial/cancel, slippage, commissions), tracks P&L, and emits per-strategy performance reports and equity curves under `reports/`.
- **Reports**: run `python backtester.py` to regenerate `reports/*_performance_report.md`, equity curve PNGs, and a consolidated `reports/comparison_report.md` comparing all strategies.

## Prerequisites

- Python 3.8 or higher
- An Alpaca trading account ([alpaca.markets](https://alpaca.markets))
- Alpaca API credentials (API Key and Secret)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd End-to-End-Trading-System
```

### 2. Install Dependencies

Install all required Python packages using pip:

```bash
pip install -r requirements.txt
```

This will install:
- `alpaca_trade_api` - Alpaca trading API client
- `python-dotenv` - Environment variable management
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `yfinance` - Yahoo Finance data
- `matplotlib` - Data visualization
- `statsmodels` - Statistical modeling

### 3. Create Environment File

Create a `.env` file in the root directory of the project with your Alpaca API credentials:

```bash
touch .env
```

Then open the `.env` file and add your credentials:

```
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET=your_secret_key_here
```

**How to get your Alpaca credentials:**

1. Go to [Alpaca Markets](https://alpaca.markets) and sign up for an account
2. Log in to your account dashboard
3. Navigate to the API Keys section
4. Generate a new API key and secret
5. Copy the API key and secret and paste them into your `.env` file

⚠️ **Important Security Notice:** Never commit the `.env` file to version control. The file is listed in `.gitignore` to prevent accidental exposure of your credentials.

## Running the Trading System

### Start the Live Trading Bot

```bash
python main.py
```

The system will:
1. Connect to the Alpaca live market feed for the configured symbols
2. Subscribe to real-time quote updates (BID/ASK prices)
3. Update equity data for each symbol
4. Compute trading signals based on the mean reversion strategy
5. Automatically place buy/sell orders when signals are generated
6. Run continuously until interrupted

### Stopping the System

Press `Ctrl+C` to gracefully stop the trading system.

### Run Backtester

To backtest strategies against historical data:

```bash
python backtester.py
```

This generates performance reports and equity curves in the `reports/` directory.

## Configuration

The main trading parameters can be adjusted in `main.py`:

- **SYMBOLS**: List of stock tickers to trade (default: `["AAPL", "NVDA", "MSFT"]`)
- **LOOP_DELAY**: Time (in seconds) between each trading cycle (default: `25`)
- **TRADE_QTY**: Number of shares to trade per order (default: `75`)
- **Strategy Parameters** (in MeanReversion initialization):
  - `window`: Rolling window size for mean reversion calculation (default: `10`)
  - `z_thresh`: Z-score threshold for generating trading signals (default: `1.3`)

## Running Tests

To run the test suite:

```bash
python -m pytest tests/
```

## Troubleshooting

- **"ModuleNotFoundError"**: Ensure all dependencies are installed with `pip install -r requirements.txt`
- **"API Key Error"**: Verify your `.env` file is in the root directory and contains valid credentials
- **"Connection Failed"**: Check your internet connection and Alpaca account status
- **"Insufficient Buying Power"**: Ensure your Alpaca account has sufficient funds for trading

## Disclaimer

This trading system is provided for educational purposes. Paper trading is recommended before running with live capital. Past performance does not guarantee future results. Always trade responsibly and within your risk tolerance.
