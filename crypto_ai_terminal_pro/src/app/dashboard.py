import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from collectors.coingecko import get_markets
from collectors.binance import get_klines
from collectors.defillama import get_protocols
from collectors.news import get_crypto_news, simple_sentiment
from features.technical import add_indicators, technical_score
from features.patterns import smc_summary, wyckoff_summary, elliott_wave_summary
from scoring.engine import rank_assets
from backtesting.strategies import sma_cross_signals, rsi_mean_reversion_signals
from backtesting.engine import run_backtest
from portfolio.risk import position_size, portfolio_summary
from reports.daily import generate_report
from storage.db import add_journal, list_journal, init_db

st.set_page_config(page_title='AI Crypto Research Terminal Pro', layout='wide')
st.title('AI Crypto Research Terminal Pro')
st.caption('Research and education tool only. It does not guarantee profit and does not place trades.')
init_db()

PAGES = ['Market Ranking','Technical Analysis','SMC / Wyckoff / Elliott','On-chain / DeFi','News + Sentiment','Backtesting','Portfolio Risk','Daily AI Report','Trade Journal','AI Assistant']
with st.sidebar:
    st.header('Settings')
    page = st.radio('Page', PAGES)
    coin_limit = st.slider('Top coins to scan', 10, 250, 100)
    exclude_stables = st.checkbox('Exclude stablecoins', True)
    symbol = st.text_input('Binance symbol', 'BTCUSDT').upper()
    interval = st.selectbox('Interval', ['1d','4h','1h'], index=0)

@st.cache_data(ttl=180)
def cached_markets(limit): return get_markets(per_page=limit)
@st.cache_data(ttl=180)
def cached_klines(symbol, interval, limit): return get_klines(symbol=symbol, interval=interval, limit=limit)
@st.cache_data(ttl=600)
def cached_protocols(): return get_protocols()
@st.cache_data(ttl=600)
def cached_news(): return get_crypto_news(25)

def get_ranked():
    return rank_assets(cached_markets(coin_limit), exclude_stables=exclude_stables)

def get_ta(limit=600):
    return add_indicators(cached_klines(symbol, interval, limit))

try:
    ranked = get_ranked()
except Exception as e:
    st.error(f'Market scanner failed: {e}')
    ranked = pd.DataFrame()

if page == 'Market Ranking':
    st.subheader('Investable Opportunity Ranking')
    st.dataframe(ranked, use_container_width=True)
    st.info('Stablecoins are filtered by default. Score combines liquidity, size, multi-timeframe momentum, volume activity, and ATH recovery.')

elif page == 'Technical Analysis':
    st.subheader(f'Technical Analysis: {symbol}')
    try:
        ta = get_ta()
        score = technical_score(ta)
        c1, c2 = st.columns([3,1])
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=ta['date'], open=ta['open'], high=ta['high'], low=ta['low'], close=ta['close'], name='Price'))
            for col in ['sma_20','sma_50','sma_200','ema_21']:
                fig.add_trace(go.Scatter(x=ta['date'], y=ta[col], name=col.upper()))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.metric('Technical Score', score['technical_score'])
            for note in score['notes']: st.write('•', note)
        st.write('Indicator table includes 50+ computed features.')
        st.dataframe(ta.tail(5).T, use_container_width=True)
    except Exception as e: st.error(f'Could not load technical data: {e}')

elif page == 'SMC / Wyckoff / Elliott':
    st.subheader(f'Pattern Frameworks: {symbol}')
    try:
        ta = get_ta()
        st.write('### Smart Money Concepts')
        st.json(smc_summary(ta))
        st.write('### Wyckoff')
        st.json(wyckoff_summary(ta))
        st.write('### Elliott Wave Heuristic')
        st.json(elliott_wave_summary(ta))
        st.warning('These are rule-based approximations, not certainty. Use them as a structured checklist, not as automatic buy/sell signals.')
    except Exception as e: st.error(f'Pattern analysis failed: {e}')

elif page == 'On-chain / DeFi':
    st.subheader('On-chain / DeFi Analytics')
    try:
        protocols = cached_protocols()
        st.dataframe(protocols.head(50), use_container_width=True)
        st.info('This uses DefiLlama protocol TVL data. Wallet-level whale tracking normally needs specialist APIs or exchange/wallet data access.')
    except Exception as e: st.error(f'DeFi data failed: {e}')

elif page == 'News + Sentiment':
    st.subheader('News Aggregation + Simple Sentiment')
    try:
        news = cached_news()
        news['sentiment_score'] = news['title'].apply(simple_sentiment)
        st.dataframe(news, use_container_width=True)
        st.metric('Headline sentiment total', int(news['sentiment_score'].sum()))
        st.info('X/Reddit sentiment can be added with official APIs or manual text paste. Avoid scraping accounts without permission.')
    except Exception as e: st.error(f'News failed: {e}')

elif page == 'Backtesting':
    st.subheader(f'Backtesting: {symbol}')
    strategy = st.selectbox('Strategy', ['SMA Cross','RSI Mean Reversion'])
    try:
        ta = get_ta(1000)
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
    st.subheader('Risk Management')
    c1, c2, c3, c4 = st.columns(4)
    account = c1.number_input('Account size $', value=1000.0, min_value=0.0)
    risk_pct = c2.number_input('Risk % per trade', value=1.0, min_value=0.1, max_value=10.0)
    entry = c3.number_input('Entry price', value=100.0, min_value=0.0)
    stop = c4.number_input('Stop price', value=95.0, min_value=0.0)
    try: st.json(position_size(account, risk_pct, entry, stop))
    except Exception as e: st.error(str(e))

elif page == 'Daily AI Report':
    st.subheader('Daily AI-Style Research Report')
    try:
        ta = get_ta()
        report = generate_report(ranked, symbol, technical_score(ta), smc=smc_summary(ta), wyckoff=wyckoff_summary(ta), elliott=elliott_wave_summary(ta))
        st.markdown(report)
        st.download_button('Download report', report, file_name='daily_crypto_report.md')
    except Exception as e: st.error(f'Report failed: {e}')

elif page == 'Trade Journal':
    st.subheader('Trade Journal')
    with st.form('journal'):
        asset = st.text_input('Asset', symbol)
        thesis = st.text_area('Thesis')
        setup = st.text_area('Setup')
        risk = st.text_area('Risk / invalidation')
        outcome = st.text_area('Outcome / lesson')
        if st.form_submit_button('Save'): add_journal(asset, thesis, setup, risk, outcome); st.success('Saved')
    rows = list_journal()
    st.dataframe(pd.DataFrame(rows, columns=['created_at','asset','thesis','setup','risk','outcome']), use_container_width=True)

elif page == 'AI Assistant':
    st.subheader('AI Assistant Explanation')
    st.write('This offline assistant explains the dashboard scores using available data. Full LLM chat can be connected later with API keys stored in Streamlit Secrets.')
    if not ranked.empty:
        coin = st.selectbox('Choose asset', ranked['symbol'].head(30).str.upper())
        row = ranked[ranked['symbol'].str.upper()==coin].iloc[0]
        st.markdown(f"""
### Why {coin} is ranked this way
- Opportunity score: **{row.get('opportunity_score', 'N/A')}/100**
- Risk label: **{row.get('risk_label','N/A')}**
- 24h change: **{row.get('price_change_percentage_24h','N/A')}%**
- 7d change: **{row.get('price_change_percentage_7d_in_currency','N/A')}%**
- Interpretation: the score is high when the asset has strong liquidity, strong recent momentum, meaningful volume activity, and acceptable market-cap quality.

This is not a buy instruction. Confirm fundamentals, chart structure, invalidation level, and position size before acting.
""")
