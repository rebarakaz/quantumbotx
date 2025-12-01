import os
import sys
import json
from flask import Flask

# Add root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock Flask app
app = Flask(__name__)

def verify_bot_api():
    print("--- Verifying Bot Management API ---")
    
    # Set Environment
    os.environ['BROKER_TYPE'] = 'CCXT' # Test in CCXT mode
    
    # Import routes
    from core.routes.api_bots import create_bot, get_bot_detail, update_bot_route, delete_bot_route, get_bot_analysis
    
    with app.app_context():
        # 1. Create Bot
        print("\n1. Testing create_bot()...")
        # Mock request
        class MockRequest:
            json = {
                "name": "TestBot_API",
                "market": "BTC/USDT",
                "risk_percent": 1.0,
                "sl_atr_multiplier": 2.0,
                "tp_atr_multiplier": 3.0,
                "timeframe": "H1",
                "check_interval_seconds": 60,
                "strategy": "RSI_CROSSOVER",
                "params": {"rsi_period": 14, "rsi_overbought": 70, "rsi_oversold": 30},
                "enable_strategy_switching": True
            }
        
        # We need to monkeypatch request
        import flask
        flask.request = MockRequest()
        
        try:
            response = create_bot()
            data = response[0].get_json() if isinstance(response, tuple) else response.get_json()
            print("   Result:", data)
            bot_id = data.get('id')
        except Exception as e:
            print("   FAILED:", e)
            return

        if not bot_id:
            print("   No Bot ID returned, stopping.")
            return

        # 2. Get Bot Detail
        print(f"\n2. Testing get_bot_detail({bot_id})...")
        try:
            response = get_bot_detail(bot_id)
            data = response.get_json()
            print("   Result Name:", data.get('name'))
            print("   Result Params:", data.get('strategy_params'))
        except Exception as e:
            print("   FAILED:", e)

        # 3. Update Bot
        print(f"\n3. Testing update_bot_route({bot_id})...")
        MockRequest.json['name'] = "TestBot_API_Updated"
        MockRequest.json['params']['rsi_period'] = 21
        try:
            response = update_bot_route(bot_id)
            data = response.get_json()
            print("   Result:", data)
        except Exception as e:
            print("   FAILED:", e)

        # 4. Verify Update
        print(f"\n4. Verifying Update...")
        try:
            response = get_bot_detail(bot_id)
            data = response.get_json()
            print("   Result Name:", data.get('name'))
            print("   Result Params:", data.get('strategy_params'))
        except Exception as e:
            print("   FAILED:", e)

        # 5. Test Analysis
        print(f"\n5. Testing get_bot_analysis({bot_id})...")
        try:
            response = get_bot_analysis(bot_id)
            data = response.get_json()
            print("   Result Signal:", data.get('signal'))
            print("   Result Price:", data.get('price'))
        except Exception as e:
            print("   FAILED:", e)

        # 6. Delete Bot
        print(f"\n6. Testing delete_bot_route({bot_id})...")
        try:
            response = delete_bot_route(bot_id)
            data = response.get_json()
            print("   Result:", data)
        except Exception as e:
            print("   FAILED:", e)

if __name__ == "__main__":
    verify_bot_api()
