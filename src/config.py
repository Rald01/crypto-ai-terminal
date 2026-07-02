from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

COINGECKO_BASE_URL = os.getenv("COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3")
BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
DEFILLAMA_BASE_URL = os.getenv("DEFILLAMA_BASE_URL", "https://api.llama.fi")
DATABASE_PATH = ROOT / os.getenv("DATABASE_PATH", "data/crypto_terminal.sqlite")
WATCHLIST = [x.strip().lower() for x in os.getenv("WATCHLIST", "bitcoin,ethereum,solana,chainlink,aave,bittensor,sui,hyperliquid").split(",") if x.strip()]
STABLE_SYMBOLS = set(os.getenv("STABLE_SYMBOLS", "usdt,usdc,dai,usde,usds,usd1,pyusd,usdd,gho,rlusd,usdy,usyc,bfusd,usdf,usd0,usdtb,fdusd,tusd,usdp,frax,lusd").split(","))
