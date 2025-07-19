# core/routes/api_forex.py

from flask import Blueprint, jsonify
from core.utils.symbols import get_forex_symbols

api_forex = Blueprint('api_forex', __name__)

@api_forex.route('/api/forex-data')
def get_forex_data():
    forex_symbols = get_forex_symbols()
    if forex_symbols:
        return jsonify({s['name']: s for s in forex_symbols})
    return jsonify({})
