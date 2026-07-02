# AI Crypto Research Terminal Pro

A Streamlit-based crypto research terminal for market screening, technical analysis, pattern frameworks, DeFi analytics, news sentiment, portfolio risk, backtesting, journaling, and AI-ready reports.

This is an education and research tool. It is **not financial advice**, does not guarantee profit, and does not place trades.

## Current Features

- Live market data from CoinGecko
- Binance OHLCV candlestick data
- Stablecoin filtering
- Investable Opportunity Score
- 50+ technical indicator columns
- Smart Money Concepts approximations
- Wyckoff heuristic
- Elliott Wave heuristic
- DefiLlama TVL/on-chain DeFi data
- Crypto RSS news aggregation
- Simple headline sentiment
- Backtesting
- Position sizing and risk management
- Trade journal
- AI-style daily report
- Offline assistant explanation page

## Deploy on Streamlit Cloud

Main file path:

```text
src/app/dashboard.py
```

## Local Setup

```bash
pip install -r requirements.txt
streamlit run src/app/dashboard.py
```

## Secrets

Do not commit API keys to GitHub. Use Streamlit Community Cloud Secrets for API keys.
