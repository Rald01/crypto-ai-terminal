import pandas as pd
from config import COINGECKO_BASE_URL
from collectors.http import get_json

def get_markets(vs_currency='usd', per_page=100, page=1):
    url = f'{COINGECKO_BASE_URL}/coins/markets'
    params = {'vs_currency': vs_currency, 'order': 'market_cap_desc', 'per_page': per_page, 'page': page, 'sparkline': 'false', 'price_change_percentage': '1h,24h,7d,30d'}
    data = get_json(url, params=params)
    df = pd.DataFrame(data)
    keep = ['id','symbol','name','current_price','market_cap','market_cap_rank','total_volume','price_change_percentage_24h','price_change_percentage_7d_in_currency','price_change_percentage_30d_in_currency','ath_change_percentage']
    return df[[c for c in keep if c in df.columns]]

def get_coin_details(coin_id: str):
    url = f'{COINGECKO_BASE_URL}/coins/{coin_id}'
    params = {'localization':'false','tickers':'false','market_data':'true','community_data':'true','developer_data':'true','sparkline':'false'}
    return get_json(url, params=params)
