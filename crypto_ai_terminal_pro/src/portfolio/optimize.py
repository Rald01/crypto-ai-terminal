import numpy as np
import pandas as pd

def inverse_vol_weights(returns: pd.DataFrame) -> pd.Series:
    vol = returns.std().replace(0, np.nan)
    inv = 1 / vol
    w = inv / inv.sum()
    return w.fillna(0)

def max_sharpe_random(returns: pd.DataFrame, n=2000, seed=42):
    rng = np.random.default_rng(seed)
    mu = returns.mean() * 365
    cov = returns.cov() * 365
    best = None
    cols = list(returns.columns)
    for _ in range(n):
        w = rng.random(len(cols)); w = w / w.sum()
        ret = float(w @ mu)
        vol = float(np.sqrt(w @ cov.values @ w))
        sharpe = ret / vol if vol > 0 else 0
        if best is None or sharpe > best["sharpe"]:
            best = {"weights": dict(zip(cols, w.round(4))), "return": round(ret,4), "volatility": round(vol,4), "sharpe": round(sharpe,3)}
    return best
