import pandas as pd

def normalize_rank(series, ascending=False):
    return series.rank(pct=True, ascending=ascending).fillna(0.5) * 100

def rank_assets(markets: pd.DataFrame) -> pd.DataFrame:
    df = markets.copy()
    df['liquidity_score'] = normalize_rank(df['total_volume'], ascending=True)
    df['size_score'] = normalize_rank(df['market_cap'], ascending=True)
    df['momentum_24h'] = df.get('price_change_percentage_24h', 0).fillna(0).clip(-20,20) + 50
    df['momentum_7d'] = df.get('price_change_percentage_7d_in_currency', 0).fillna(0).clip(-40,40) + 50
    df['ath_risk'] = (100 + df.get('ath_change_percentage', -50).fillna(-50)).clip(0,100)
    df['score'] = (0.25*df['liquidity_score'] + 0.20*df['size_score'] + 0.20*df['momentum_24h'] + 0.25*df['momentum_7d'] + 0.10*df['ath_risk']).round(1)
    cols = ['market_cap_rank','symbol','name','current_price','market_cap','total_volume','price_change_percentage_24h','price_change_percentage_7d_in_currency','score']
    return df[[c for c in cols if c in df.columns]].sort_values('score', ascending=False).reset_index(drop=True)
