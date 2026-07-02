import pandas as pd

def sma_cross_signals(df: pd.DataFrame, fast=20, slow=50) -> pd.DataFrame:
    out = df.copy()
    out['fast'] = out['close'].rolling(fast).mean()
    out['slow'] = out['close'].rolling(slow).mean()
    out['signal'] = (out['fast'] > out['slow']).astype(int)
    out['position'] = out['signal'].shift(1).fillna(0)
    return out

def rsi_mean_reversion_signals(df: pd.DataFrame, buy_below=35, sell_above=60) -> pd.DataFrame:
    out = df.copy(); pos = []; current = 0
    for rsi in out['rsi_14'].fillna(50):
        if rsi < buy_below: current = 1
        elif rsi > sell_above: current = 0
        pos.append(current)
    out['position'] = pd.Series(pos, index=out.index).shift(1).fillna(0)
    return out
