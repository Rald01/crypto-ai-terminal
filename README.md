# AI Crypto Research Terminal Pro

A local crypto research terminal for market screening, technical analysis, portfolio risk, backtesting, scoring, journaling, and AI-ready reporting.

This is a research and education tool, not financial advice and not an automatic trading bot.

## Features

- CoinGecko market scanner
- Binance OHLCV collector
- SQLite storage
- Technical indicators: SMA, EMA, RSI, MACD, Bollinger Bands, ATR, volatility, drawdown
- Multi-factor scoring engine
- Simple backtesting engine
- Portfolio risk calculator
- Trade journal
- AI-style daily report generator
- Streamlit dashboard

## Setup

```bash
cd crypto_ai_terminal_pro
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
streamlit run src/app/dashboard.py
```

## Dashboard Pages

1. Market Ranking
2. Technical Analysis
3. Backtesting
4. Portfolio Risk
5. Daily AI Report
6. Trade Journal

## Important Warning

No system can guarantee profit in crypto. Use small position sizes, avoid leverage until advanced, and always define your invalidation point before entering a trade.
