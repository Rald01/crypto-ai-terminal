import pandas as pd
from config import DEFILLAMA_BASE_URL
from collectors.http import get_json

def get_protocols():
    data = get_json(f"{DEFILLAMA_BASE_URL}/protocols")
    df = pd.DataFrame(data)
    cols = ["name", "category", "chains", "tvl", "change_1d", "change_7d", "change_1m"]
    return df[[c for c in cols if c in df.columns]].sort_values("tvl", ascending=False)

def get_stablecoins():
    data = get_json(f"{DEFILLAMA_BASE_URL}/stablecoins")
    return pd.DataFrame(data.get("peggedAssets", []))
