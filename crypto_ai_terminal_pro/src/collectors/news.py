import feedparser
import pandas as pd

FEEDS = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss",
}

def get_crypto_news(limit=20):
    rows = []
    for source, url in FEEDS.items():
        feed = feedparser.parse(url)
        for e in feed.entries[:limit]:
            rows.append({"source": source, "title": e.get("title", ""), "link": e.get("link", ""), "published": e.get("published", "")})
    return pd.DataFrame(rows).head(limit)

def simple_sentiment(text: str) -> int:
    bullish = ["surge", "rally", "gain", "approval", "record", "breakout", "accumulate", "inflow", "bull"]
    bearish = ["hack", "lawsuit", "ban", "crash", "fall", "outflow", "liquidation", "bear", "fraud", "exploit"]
    t = text.lower()
    return sum(w in t for w in bullish) - sum(w in t for w in bearish)
