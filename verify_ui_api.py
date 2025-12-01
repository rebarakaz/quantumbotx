import os
import sys
import json
from flask import Flask

# Add root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock Flask app
app = Flask(__name__)

def verify_ccxt_api():
    print("--- Verifying UI API for CCXT ---")
    
    # Set Environment
    os.environ['BROKER_TYPE'] = 'CCXT'
    os.environ['EXCHANGE_ID'] = 'binance'
    
    # Import routes after setting env
    from core.routes.api_dashboard import api_dashboard_stats, api_account_info
    from core.routes.api_stocks import get_stocks, get_stock_detail
    
    with app.app_context():
        try:
            print("\n1. Testing api_dashboard_stats()...")
            stats = api_dashboard_stats()
            print("   Result:", stats.get_json())
        except Exception as e:
            print("   FAILED:", e)

        try:
            print("\n2. Testing api_account_info()...")
            info = api_account_info()
            print("   Result:", info.get_json())
        except Exception as e:
            print("   FAILED:", e)

        try:
            print("\n3. Testing get_stocks() (Crypto Tickers)...")
            stocks = get_stocks()
            data = stocks.get_json()
            print(f"   Result: Found {len(data)} symbols")
            if len(data) > 0:
                print("   Sample:", data[0])
        except Exception as e:
            print("   FAILED:", e)

        try:
            print("\n4. Testing get_stock_detail('BTC/USDT')...")
            detail = get_stock_detail('BTC/USDT')
            print("   Result:", detail.get_json())
        except Exception as e:
            print("   FAILED:", e)

if __name__ == "__main__":
    verify_ccxt_api()
