# core/routes/api_portfolio.py

from flask import Blueprint, jsonify
from core.data.fetch import get_open_positions_from_mt5

api_portfolio = Blueprint('api_portfolio', __name__)

@api_portfolio.route('/api/portfolio/open-positions')
def api_open_positions():
    positions = get_open_positions_from_mt5()
    return jsonify(positions)
