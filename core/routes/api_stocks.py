# core/routes/api_stocks.py

import logging
import os
from datetime import datetime
from flask import Blueprint, jsonify, request
from core.utils.symbols import get_stock_symbols
from core.utils.external import get_mt5_symbol_profile
from core.utils import market_data
from core.factory.broker_factory import BrokerFactory

try:
    import pandas_ta as ta
except ImportError:
    from core.utils.pandas_ta_compat import ta

logger = logging.getLogger(__name__)

api_stocks = Blueprint('api_stocks', __name__)

@api_stocks.route('/api/stocks/<symbol>/profile')
def get_stock_profile(symbol):
    # Profile fetching is currently external/MT5 specific. 
    # For CCXT we might need a different source or just return empty.
    if os.getenv("BROKER_TYPE") == "CCXT":
        return jsonify({"description": symbol, "sector": "Crypto", "industry": "Digital Assets"})
        
    profile = get_mt5_symbol_profile(symbol)
    if profile:
        return jsonify(profile)
    return jsonify({"error": "Could not fetch symbol profile from MT5"}), 404

@api_stocks.route('/api/stocks')
def get_stocks():
    """
    Mengambil daftar harga saham/crypto terkini.
    """
    broker_type = os.getenv("BROKER_TYPE", "MT5")
    
    if broker_type == "CCXT":
        try:
            broker = BrokerFactory.get_broker()
            if not broker or not hasattr(broker, 'exchange'):
                return jsonify([])
                
            # Fetch top crypto pairs (hardcoded for now or fetch from exchange)
            # Fetching all tickers is heavy, so we fetch a few popular ones
            top_symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT', 'SOL/USDT', 'DOGE/USDT']
            
            result = []
            # Use fetch_tickers if supported for batch fetching
            try:
                tickers = broker.exchange.fetch_tickers(top_symbols)
                for symbol, ticker in tickers.items():
                    result.append({
                        'symbol': symbol,
                        'last_price': ticker['last'],
                        'change': ticker['percentage'] if ticker.get('percentage') else 0.0, # CCXT percentage is usually 24h change
                        'time': datetime.fromtimestamp(ticker['timestamp']/1000).strftime('%H:%M:%S') if ticker.get('timestamp') else datetime.now().strftime('%H:%M:%S')
                    })
            except Exception as e:
                logger.error(f"Error fetching CCXT tickers: {e}")
                
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error in get_stocks (CCXT): {e}")
            return jsonify([])

    # MT5 Logic
    # Ambil 20 saham paling populer (sudah diurutkan berdasarkan volume oleh fungsi)
    stock_symbols = get_stock_symbols(limit=20)
    if not stock_symbols:
        logger.warning("get_stock_symbols() tidak mengembalikan simbol saham.")
        return jsonify([])

    result = []
    symbols_to_process = [stock['name'] for stock in stock_symbols]

    # We need to use MT5 functions directly here because get_stock_symbols returns MT5 objects/paths
    # and the logic is specific to calculating daily change from D1 open.
    # Ideally this should be moved to MT5Adapter, but for now we keep it here if MT5 is available.
    try:
        import MetaTrader5 as mt5
        if not mt5.initialize():
            return jsonify([])
            
        for symbol in symbols_to_process:
            try:
                # 1. Ambil tick terakhir untuk harga saat ini
                tick = mt5.symbol_info_tick(symbol)
                if not tick or tick.ask == 0:
                    continue

                # 2. Ambil data bar harian (D1) untuk harga pembukaan
                rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 0, 1)
                if rates is None or len(rates) == 0:
                    continue

                daily_open = rates[0]['open']
                last_price = tick.ask
                change = last_price - daily_open

                result.append({
                    'symbol': symbol,
                    'last_price': last_price,
                    'change': round(change, 2),
                    'time': datetime.fromtimestamp(tick.time).strftime('%H:%M:%S')
                })
            except Exception as e:
                logger.error(f"Error saat memproses simbol saham {symbol}: {e}")
    except ImportError:
        pass

    return jsonify(result)

@api_stocks.route('/api/stocks/<symbol>')
def get_stock_detail(symbol):
    # Gunakan market_data facade
    df = market_data.get_market_rates(symbol, "D1", 100)

    if df is None or df.empty:
        return jsonify({"error": f"Tidak bisa mengambil data untuk {symbol}"}), 404

    last = df.iloc[-1]
    return jsonify({
        "symbol": symbol,
        "time": last['time'].strftime('%Y-%m-%d %H:%M:%S'),
        "open": last['open'],
        "high": last['high'],
        "low": last['low'],
        "close": last['close'],
        "volume": last['tick_volume']
    })

@api_stocks.route('/api/symbols/all')
def get_all_symbols_with_path():
    """
    Endpoint diagnostik.
    """
    broker_type = os.getenv("BROKER_TYPE", "MT5")
    if broker_type == "CCXT":
        try:
            broker = BrokerFactory.get_broker()
            if broker and hasattr(broker, 'exchange'):
                # Return list of loaded markets
                markets = broker.exchange.markets
                if not markets:
                    broker.exchange.load_markets()
                    markets = broker.exchange.markets
                
                symbols_info = [{"name": s, "path": "Crypto"} for s in markets.keys()]
                return jsonify(symbols_info)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    try:
        import MetaTrader5 as mt5
        all_symbols = mt5.symbols_get()
        if all_symbols:
            symbols_info = [{"name": s.name, "path": s.path} for s in all_symbols]
            return jsonify(symbols_info)
        return jsonify([])
    except Exception as e:
        logger.error(f"Gagal mengambil daftar simbol dari MT5: {e}", exc_info=True)
        return jsonify({"error": "Tidak dapat terhubung atau mengambil data dari MT5."}), 500
