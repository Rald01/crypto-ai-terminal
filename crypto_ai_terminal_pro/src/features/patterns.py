import pandas as pd


def smc_summary(df: pd.DataFrame) -> dict:
    last = df.iloc[-1]
    return {
        "bias": "Bullish" if last.get("break_of_structure_up", False) else "Bearish" if last.get("break_of_structure_down", False) else "Neutral",
        "fvg_up_count_50": int(df.tail(50).get("fair_value_gap_up", pd.Series(dtype=bool)).sum()),
        "fvg_down_count_50": int(df.tail(50).get("fair_value_gap_down", pd.Series(dtype=bool)).sum()),
        "liquidity_sweep_high_20": int(df.tail(20).get("liquidity_sweep_high", pd.Series(dtype=bool)).sum()),
        "liquidity_sweep_low_20": int(df.tail(20).get("liquidity_sweep_low", pd.Series(dtype=bool)).sum()),
    }


def wyckoff_summary(df: pd.DataFrame) -> dict:
    recent = df.tail(80)
    price_change = recent["close"].iloc[-1] / recent["close"].iloc[0] - 1
    vol_change = recent["volume"].tail(20).mean() / recent["volume"].head(20).mean() - 1
    if price_change > 0.15 and vol_change > 0:
        phase = "Markup / possible expansion"
    elif abs(price_change) < 0.08 and vol_change < 0:
        phase = "Accumulation or quiet range"
    elif price_change < -0.15 and vol_change > 0:
        phase = "Markdown / distribution risk"
    else:
        phase = "Transition / unclear"
    return {"phase": phase, "80_bar_price_change_%": round(price_change*100,2), "volume_change_%": round(vol_change*100,2)}


def elliott_wave_summary(df: pd.DataFrame) -> dict:
    recent = df.tail(120).copy()
    recent["pivot_high"] = (recent["high"] > recent["high"].shift(1)) & (recent["high"] > recent["high"].shift(-1))
    recent["pivot_low"] = (recent["low"] < recent["low"].shift(1)) & (recent["low"] < recent["low"].shift(-1))
    pivots = recent[recent["pivot_high"] | recent["pivot_low"]].tail(8)
    trend = "Bullish impulse possible" if len(pivots) >= 5 and recent["close"].iloc[-1] > recent["close"].iloc[0] else "Corrective/unclear"
    return {"wave_read": trend, "recent_pivots": len(pivots)}
