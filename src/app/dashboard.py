import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from collectors.coingecko import get_markets
from collectors.binance import get_klines
from features.technical import add_indicators, technical_score
from scoring.engine import rank_assets
from backtesting.strategies import sma_cross_signals, rsi_mean_reversion_signals
from backtesting.engine import run_backtest
from portfolio.risk import position_size, portfolio_summary
from reports.daily import generate_report
from storage.db import add_journal, list_journal, init_db

st.set_page_config(page_title='AI Crypto Research Terminal Pro', layout='wide')
st.title('AI Crypto Research Terminal Pro')
st.caption('Research tool only. Not financial advice. No profit is guaranteed.')
init_db()

with st.sidebar:
    st.header('Settings')
    page = st.radio('Page', ['Market Ranking','Technical Analysis','Backtesting','Portfolio Risk','Daily AI Report','Trade Journal'])
    coin_limit = st.slider('Top coins to scan', 10, 250, 100)
    symbol = st.text_input('Binance symbol', 'BTCUSDT').upper()
    interval = st.selectbox('Interval', ['1d','4h','1h'], index=0)

@st.cache_data(ttl=180)
def cached_markets(limit): return get_markets(per_page=limit)
@st.cache_data(ttl=180)
def cached_klines(symbol, interval, limit): return get_klines(symbol=symbol, interval=interval, limit=limit)

try:
    markets = cached_markets(coin_limit)
    ranked = rank_assets(markets)
except Exception as e:
    st.error(f'Market scanner failed: {e}')
    ranked = pd.DataFrame()

if page == 'Market Ranking':
    st.subheader('Market Ranking')
    st.dataframe(ranked, use_container_width=True)
    st.info('Score combines liquidity, market size, 24h/7d momentum, and distance from all-time high.')

elif page == 'Technical Analysis':
    st.subheader(f'Technical Analysis: {symbol}')
    try:
        ta = add_indicators(cached_klines(symbol, interval, 500))
        score = technical_score(ta)
        c1, c2 = st.columns([3,1])
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=ta['date'], open=ta['open'], high=ta['high'], low=ta['low'], close=ta['close'], name='Price'))
            fig.add_trace(go.Scatter(x=ta['date'], y=ta['sma_50'], name='SMA 50'))
            fig.add_trace(go.Scatter(x=ta['date'], y=ta['sma_200'], name='SMA 200'))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.metric('Technical Score', score['technical_score'])
            for note in score['notes']: st.write('•', note)
        st.line_chart(ta.set_index('date')[['rsi_14','macd','macd_signal']])
    except Exception as e: st.error(f'Could not load technical data: {e}')

elif page == 'Backtesting':
    st.subheader(f'Backtesting: {symbol}')
    strategy = st.selectbox('Strategy', ['SMA Cross','RSI Mean Reversion'])
    try:
        ta = add_indicators(cached_klines(symbol, interval, 1000))
        if strategy == 'SMA Cross':
            fast = st.slider('Fast SMA', 5, 100, 20); slow = st.slider('Slow SMA', 20, 250, 50)
            sig = sma_cross_signals(ta, fast, slow)
        else:
            buy = st.slider('Buy RSI below', 10, 50, 35); sell = st.slider('Sell RSI above', 50, 90, 60)
            sig = rsi_mean_reversion_signals(ta, buy, sell)
        res = run_backtest(sig)
        st.write(res['metrics'])
        st.line_chart(res['df'].set_index('date')[['equity','buy_hold']])
    except Exception as e: st.error(f'Backtest failed: {e}')

elif page == 'Portfolio Risk':
    st.subheader('Position Size Calculator')
    account = st.number_input('Account size', min_value=0.0, value=10000.0)
    risk_pct = st.number_input('Risk per trade (%)', min_value=0.1, max_value=10.0, value=1.0)
    entry = st.number_input('Entry price', min_value=0.0, value=100.0)
    stop = st.number_input('Stop price', min_value=0.0, value=95.0)
    if st.button('Calculate position size'): st.json(position_size(account, risk_pct, entry, stop))
    st.subheader('Sample Portfolio Snapshot')
    sample = [{'asset':'BTC','quantity':0.1,'price':60000},{'asset':'ETH','quantity':2,'price':3000},{'asset':'Cash','quantity':1,'price':5000}]
    rows, total = portfolio_summary(sample)
    st.metric('Sample portfolio value', f'${total:,.2f}')
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

elif page == 'Daily AI Report':
    st.subheader('Daily AI-Style Research Report')
    try:
        tech = technical_score(add_indicators(cached_klines(symbol, interval, 500)))
        report = generate_report(ranked, symbol, tech)
        st.markdown(report)
        st.download_button('Download report as Markdown', report, file_name='daily_crypto_report.md')
    except Exception as e: st.error(f'Report failed: {e}')

elif page == 'Trade Journal':
    st.subheader('Trade Journal')
    with st.form('journal'):
        asset = st.text_input('Asset', symbol); thesis = st.text_area('Thesis'); setup = st.text_area('Setup')
        risk = st.text_area('Risk / invalidation'); outcome = st.text_area('Outcome / lessons')
        if st.form_submit_button('Save journal entry'):
            add_journal(asset, thesis, setup, risk, outcome); st.success('Saved.')
    entries = list_journal()
    if entries: st.dataframe(pd.DataFrame(entries, columns=['created_at','asset','thesis','setup','risk','outcome']), use_container_width=True)
