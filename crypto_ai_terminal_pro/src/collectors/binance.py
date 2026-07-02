import pandas as pd
from config import BINANCE_BASE_URL
from collectors.http import get_json

def get_klines(symbol='BTCUSDT', interval='1d', limit=365):
    url = f'{BINANCE_BASE_URL}/api/v3/klines'
    data = get_json(url, params={'symbol': symbol.upper(), 'interval': interval, 'limit': limit})
    cols = ['open_time','open','high','low','close','volume','close_time','quote_volume','trades','taker_buy_base','taker_buy_quote','ignore']
    df = pd.DataFrame(data, columns=cols)
    for c in ['open','high','low','close','volume','quote_volume','taker_buy_base','taker_buy_quote']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['date'] = pd.to_datetime(df['open_time'], unit='ms')
    return df[['date','open','high','low','close','volume','quote_volume','trades']]
