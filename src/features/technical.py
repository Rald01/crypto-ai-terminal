import numpy as np
import pandas as pd

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    close = out['close']
    out['sma_20'] = close.rolling(20).mean()
    out['sma_50'] = close.rolling(50).mean()
    out['sma_200'] = close.rolling(200).mean()
    out['ema_12'] = close.ewm(span=12, adjust=False).mean()
    out['ema_26'] = close.ewm(span=26, adjust=False).mean()
    out['macd'] = out['ema_12'] - out['ema_26']
    out['macd_signal'] = out['macd'].ewm(span=9, adjust=False).mean()
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    out['rsi_14'] = 100 - (100 / (1 + rs))
    ma20 = close.rolling(20).mean(); sd20 = close.rolling(20).std()
    out['bb_upper'] = ma20 + 2 * sd20; out['bb_lower'] = ma20 - 2 * sd20
    prev_close = close.shift(1)
    tr = pd.concat([(out['high']-out['low']), (out['high']-prev_close).abs(), (out['low']-prev_close).abs()], axis=1).max(axis=1)
    out['atr_14'] = tr.rolling(14).mean()
    out['returns'] = close.pct_change()
    out['volatility_30d'] = out['returns'].rolling(30).std() * np.sqrt(365)
    out['rolling_high'] = close.cummax()
    out['drawdown'] = (close / out['rolling_high']) - 1
    return out

def technical_score(df: pd.DataFrame) -> dict:
    last = df.dropna().iloc[-1]
    score = 50; notes = []
    if last.close > last.sma_50: score += 10; notes.append('Price above SMA50')
    else: score -= 10; notes.append('Price below SMA50')
    if last.sma_50 > last.sma_200: score += 10; notes.append('SMA50 above SMA200')
    else: score -= 10; notes.append('SMA50 below SMA200')
    if 45 <= last.rsi_14 <= 65: score += 8; notes.append('RSI healthy')
    elif last.rsi_14 > 75: score -= 8; notes.append('RSI overextended')
    elif last.rsi_14 < 35: score -= 5; notes.append('RSI weak/oversold')
    if last.macd > last.macd_signal: score += 8; notes.append('MACD bullish')
    else: score -= 8; notes.append('MACD bearish')
    if last.drawdown > -0.25: score += 5; notes.append('Drawdown controlled')
    else: score -= 5; notes.append('Large drawdown')
    return {'technical_score': int(max(0, min(100, score))), 'notes': notes, 'last': last.to_dict()}
