import numpy as np
import pandas as pd
from config import STABLE_SYMBOLS


def normalize_rank(series, ascending=False):
    return pd.to_numeric(series, errors="coerce").rank(pct=True, ascending=ascending).fillna(0.5) * 100


def add_asset_flags(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["symbol"] = out["symbol"].astype(str).str.lower()
    out["name"] = out["name"].astype(str)
    out["is_stablecoin"] = out["symbol"].isin(STABLE_SYMBOLS) | out["name"].str.lower().str.contains("usd|dollar|tether|stable", regex=True)
    out["is_low_volume"] = pd.to_numeric(out.get("total_volume", 0), errors="coerce").fillna(0) < 1_000_000
    return out


def rank_assets(markets: pd.DataFrame, exclude_stables: bool = True) -> pd.DataFrame:
    df = add_asset_flags(markets)
    if exclude_stables:
        df = df[~df["is_stablecoin"]].copy()
    if df.empty:
        return df

    df["liquidity_score"] = normalize_rank(df["total_volume"], ascending=True)
    df["size_score"] = normalize_rank(df["market_cap"], ascending=True)
    m24 = pd.to_numeric(df.get("price_change_percentage_24h", 0), errors="coerce").fillna(0)
    m7 = pd.to_numeric(df.get("price_change_percentage_7d_in_currency", 0), errors="coerce").fillna(0)
    m30 = pd.to_numeric(df.get("price_change_percentage_30d_in_currency", 0), errors="coerce").fillna(0)
    df["momentum_24h"] = (m24.clip(-15, 15) + 15) / 30 * 100
    df["momentum_7d"] = (m7.clip(-35, 35) + 35) / 70 * 100
    df["momentum_30d"] = (m30.clip(-60, 60) + 60) / 120 * 100
    df["ath_recovery_score"] = (100 + pd.to_numeric(df.get("ath_change_percentage", -50), errors="coerce").fillna(-50)).clip(0, 100)
    df["volume_to_mcap"] = (pd.to_numeric(df["total_volume"], errors="coerce") / pd.to_numeric(df["market_cap"], errors="coerce")).replace([np.inf, -np.inf], np.nan).fillna(0)
    df["activity_score"] = normalize_rank(df["volume_to_mcap"], ascending=True)

    df["opportunity_score"] = (
        0.18 * df["liquidity_score"] +
        0.12 * df["size_score"] +
        0.18 * df["momentum_24h"] +
        0.22 * df["momentum_7d"] +
        0.12 * df["momentum_30d"] +
        0.10 * df["activity_score"] +
        0.08 * df["ath_recovery_score"]
    ).round(1)
    df["risk_label"] = np.where(df["market_cap_rank"] <= 10, "Lower", np.where(df["market_cap_rank"] <= 50, "Medium", "High"))
    cols = ["market_cap_rank","symbol","name","current_price","market_cap","total_volume","price_change_percentage_24h","price_change_percentage_7d_in_currency","price_change_percentage_30d_in_currency","opportunity_score","risk_label","is_stablecoin"]
    return df[[c for c in cols if c in df.columns]].sort_values("opportunity_score", ascending=False).reset_index(drop=True)
