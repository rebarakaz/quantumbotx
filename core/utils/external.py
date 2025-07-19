# core/utils/external.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

CMC_API_KEY = os.getenv("CMC_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def get_crypto_data_from_cmc():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': CMC_API_KEY}
    params = {'start': '1', 'limit': '5', 'convert': 'IDR'}

    try:
        res = requests.get(url, headers=headers, params=params)
        data = res.json().get('data', [])
        crypto_list = []
        for c in data:
            quote = c.get('quote', {}).get('IDR', {})
            crypto_list.append({
                'name': c.get('name'),
                'symbol': c.get('symbol'),
                'price': f"Rp {quote.get('price', 0):,.2f}".replace(',', '.'),
                'change': f"{quote.get('percent_change_24h', 0):.2f}%",
                'market_cap': f"Rp {quote.get('market_cap', 0):,.0f}".replace(',', '.')
            })
        return crypto_list
    except Exception:
        return []

def get_recommendation_trends(symbol):
    try:
        res = requests.get("https://finnhub.io/api/v1/stock/recommendation", params={"symbol": symbol, "token": FINNHUB_API_KEY})
        res.raise_for_status()
        data = res.json()
        return data[0] if data else None
    except:
        return None

def get_company_profile(symbol):
    try:
        res = requests.get("https://finnhub.io/api/v1/stock/profile2", params={"symbol": symbol, "token": FINNHUB_API_KEY})
        res.raise_for_status()
        return res.json()
    except:
        return None
