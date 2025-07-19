# core/routes/api_stocks.py

from flask import Blueprint, jsonify, request
from core.utils.symbols import get_stock_symbols
import MetaTrader5 as mt5
import pandas as pd

api_stocks = Blueprint('api_stocks', __name__)

@api_stocks.route('/api/stocks')
def get_stocks():
    if not mt5.terminal_info():
        if not mt5.initialize():
            return jsonify({"error": "MT5 connection failed"}), 500

    stock_symbols = get_stock_symbols()
    result = []

    for stock in stock_symbols[:20]:  # Max 20 untuk UI
        symbol = stock['name']
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 1)

        if rates is not None and len(rates) > 0:
            last = rates[0]
            try:
                result.append({
                    'symbol': symbol,
                    'last_price': last['close'],
                    'change': round(last['close'] - last['open'], 2),
                    'time': pd.to_datetime(last['time'], unit='s').strftime('%H:%M')
                })
            except Exception:
                pass

    return jsonify(result)

@api_stocks.route('/api/stocks/<symbol>')
def get_stock_detail(symbol):
    if not mt5.terminal_info():
        if not mt5.initialize():
            return jsonify({"error": "MT5 connection failed"}), 500

    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 1)
    if not rates:
        return jsonify({"error": f"Tidak bisa mengambil data untuk {symbol}"}), 404

    last = rates[0]
    try:
        return jsonify({
            "symbol": symbol,
            "time": pd.to_datetime(last['time'], unit='s').strftime('%Y-%m-%d %H:%M:%S'),
            "open": last['open'],
            "high": last['high'],
            "low": last['low'],
            "close": last['close'],
            "volume": last['tick_volume']
        })
    except Exception:
        return jsonify({"error": "Format data tidak valid"}), 500
