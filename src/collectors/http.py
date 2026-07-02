import time
import requests

class HTTPError(RuntimeError):
    pass

def get_json(url: str, params: dict | None = None, timeout: int = 20, retries: int = 3):
    last_error = None
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=timeout, headers={'User-Agent': 'crypto-ai-terminal/1.0'})
            if r.status_code == 429:
                time.sleep(2 + attempt * 2)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            last_error = exc
            time.sleep(1 + attempt)
    raise HTTPError(f'GET failed: {url} params={params} error={last_error}')
