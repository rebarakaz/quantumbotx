# core/routes/api_history.py

from flask import Blueprint, jsonify
from core.data.fetch import get_trade_history_from_mt5

api_history = Blueprint('api_history', __name__)

@api_history.route('/api/history')
def api_global_history():
    history = get_trade_history_from_mt5()
    return jsonify(history)
