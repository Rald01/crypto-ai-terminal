import numpy as np
import pandas as pd

def run_backtest(signals: pd.DataFrame, fee_bps=10) -> dict:
    df = signals.copy().dropna(subset=['close'])
    df['returns'] = df['close'].pct_change().fillna(0)
    df['trade'] = df['position'].diff().abs().fillna(0)
    fee = fee_bps / 10000
    df['strategy_returns'] = df['position'] * df['returns'] - df['trade'] * fee
    df['equity'] = (1 + df['strategy_returns']).cumprod()
    df['buy_hold'] = (1 + df['returns']).cumprod()
    total_return = df['equity'].iloc[-1] - 1
    bh_return = df['buy_hold'].iloc[-1] - 1
    max_dd = (df['equity'] / df['equity'].cummax() - 1).min()
    vol = df['strategy_returns'].std() * np.sqrt(365)
    sharpe = (df['strategy_returns'].mean() * 365 / vol) if vol and vol > 0 else 0
    return {'df': df, 'metrics': {'Total return %': round(total_return*100,2), 'Buy-hold return %': round(bh_return*100,2), 'Max drawdown %': round(max_dd*100,2), 'Sharpe approx': round(sharpe,2), 'Trades': int(df['trade'].sum())}}
