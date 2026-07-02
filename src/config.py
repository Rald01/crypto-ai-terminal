from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
COINGECKO_BASE_URL = os.getenv('COINGECKO_BASE_URL', 'https://api.coingecko.com/api/v3')
BINANCE_BASE_URL = os.getenv('BINANCE_BASE_URL', 'https://api.binance.com')
DATABASE_PATH = ROOT / os.getenv('DATABASE_PATH', 'data/crypto_terminal.sqlite')
WATCHLIST = [x.strip() for x in os.getenv('WATCHLIST', 'bitcoin,ethereum,solana,chainlink').split(',') if x.strip()]
