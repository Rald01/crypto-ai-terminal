import numpy as np
import pandas as pd


def _rsi(close, n=14):
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    close, high, low, vol = out['close'], out['high'], out['low'], out['volume']
    for n in [5, 8, 10, 12, 20, 21, 26, 30, 34, 50, 55, 89, 100, 144, 200]:
        out[f'sma_{n}'] = close.rolling(n).mean()
        out[f'ema_{n}'] = close.ewm(span=n, adjust=False).mean()
    for n in [7, 14, 21, 28]:
        out[f'rsi_{n}'] = _rsi(close, n)
    out['macd'] = out['ema_12'] - out['ema_26']
    out['macd_signal'] = out['macd'].ewm(span=9, adjust=False).mean()
    out['macd_hist'] = out['macd'] - out['macd_signal']
    for n in [20, 50]:
        ma = close.rolling(n).mean(); sd = close.rolling(n).std()
        out[f'bb_upper_{n}'] = ma + 2 * sd
        out[f'bb_lower_{n}'] = ma - 2 * sd
        out[f'bb_width_{n}'] = (out[f'bb_upper_{n}'] - out[f'bb_lower_{n}']) / ma
    prev_close = close.shift(1)
    tr = pd.concat([(high-low), (high-prev_close).abs(), (low-prev_close).abs()], axis=1).max(axis=1)
    for n in [7, 14, 21]: out[f'atr_{n}'] = tr.rolling(n).mean()
    low14, high14 = low.rolling(14).min(), high.rolling(14).max()
    out['stoch_k'] = 100 * (close - low14) / (high14 - low14).replace(0, np.nan)
    out['stoch_d'] = out['stoch_k'].rolling(3).mean()
    typical = (high + low + close) / 3
    out['vwap_proxy'] = (typical * vol).cumsum() / vol.replace(0, np.nan).cumsum()
    out['obv'] = (np.sign(close.diff()).fillna(0) * vol).cumsum()
    out['returns'] = close.pct_change()
    for n in [7, 14, 30, 60, 90]:
        out[f'volatility_{n}'] = out['returns'].rolling(n).std() * np.sqrt(365)
        out[f'momentum_{n}'] = close.pct_change(n) * 100
    out['rolling_high'] = close.cummax()
    out['drawdown'] = close / out['rolling_high'] - 1
    out['hl_range_pct'] = (high - low) / close * 100
    out['volume_sma_20'] = vol.rolling(20).mean()
    out['volume_spike'] = vol / out['volume_sma_20']
    out['support_20'] = low.rolling(20).min()
    out['resistance_20'] = high.rolling(20).max()
    out['support_50'] = low.rolling(50).min()
    out['resistance_50'] = high.rolling(50).max()
    # SMC-style approximations
    out['fair_value_gap_up'] = (low > high.shift(2))
    out['fair_value_gap_down'] = (high < low.shift(2))
    out['break_of_structure_up'] = close > high.shift(1).rolling(20).max()
    out['break_of_structure_down'] = close < low.shift(1).rolling(20).min()
    out['liquidity_sweep_high'] = (high > high.shift(1).rolling(20).max()) & (close < high.shift(1).rolling(20).max())
    out['liquidity_sweep_low'] = (low < low.shift(1).rolling(20).min()) & (close > low.shift(1).rolling(20).min())
    return out


def technical_score(df: pd.DataFrame) -> dict:
    clean = df.dropna()
    if clean.empty:
        return {'technical_score': 50, 'notes': ['Not enough data yet'], 'last': {}}
    last = clean.iloc[-1]
    score = 50; notes = []
    checks = [
        (last.close > last.sma_50, 8, 'Price above SMA50', 'Price below SMA50'),
        (last.close > last.sma_200, 8, 'Price above SMA200', 'Price below SMA200'),
        (last.sma_50 > last.sma_200, 8, 'SMA50 above SMA200', 'SMA50 below SMA200'),
        (last.macd > last.macd_signal, 7, 'MACD bullish', 'MACD bearish'),
        (last.close > last.vwap_proxy, 5, 'Price above VWAP proxy', 'Price below VWAP proxy'),
        (last.volume_spike > 1.2, 4, 'Volume expansion', 'No major volume expansion'),
    ]
    for ok, pts, good, bad in checks:
        score += pts if ok else -pts
        notes.append(good if ok else bad)
    rsi = float(last.rsi_14)
    if 45 <= rsi <= 65: score += 8; notes.append('RSI healthy')
    elif rsi > 75: score -= 8; notes.append('RSI overextended')
    elif rsi < 35: score -= 5; notes.append('RSI weak/oversold')
    if bool(last.get('break_of_structure_up', False)): score += 6; notes.append('SMC: bullish break of structure')
    if bool(last.get('break_of_structure_down', False)): score -= 6; notes.append('SMC: bearish break of structure')
    if last.drawdown > -0.30: score += 4; notes.append('Drawdown controlled')
    else: score -= 4; notes.append('Large drawdown')
    return {'technical_score': int(max(0, min(100, score))), 'notes': notes, 'last': last.to_dict()}
