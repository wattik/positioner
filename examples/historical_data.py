import requests
from datetime import datetime, timedelta, timezone

ts = datetime(
    year=2021, month=5, day=31, hour=14, minute=39, second=9,
    tzinfo=timezone.utc
)

def timestamp(dt):
    return int(dt.timestamp() * 1000)

payload = {
    "symbol": "BTCUSDT",
    "interval": "1m",
    "startTime": timestamp(ts),
    "endTime": timestamp(ts + timedelta(minutes=100)),
    "limit": 1
}
r = requests.get('https://api.binance.com/api/v3/klines', params=payload)

print(
    r.json()
)