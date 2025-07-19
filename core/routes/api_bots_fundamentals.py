# core/routes/api_bots_fundamentals.py

from flask import Blueprint, jsonify
from core.db.queries import get_bot_by_id
from core.data.fetch import get_recommendation_trends, get_company_profile

api_bots_fundamentals = Blueprint('api_bots_fundamentals', __name__)

@api_bots_fundamentals.route('/api/bots/<int:bot_id>/fundamentals')
def get_bot_fundamentals(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot:
        return jsonify({'error': 'Bot tidak ditemukan'}), 404

    # Hanya untuk saham
    if '/' in bot['market']:
        return jsonify({})  # Kosong untuk forex/crypto

    symbol = bot['market']
    recommendations = get_recommendation_trends(symbol)
    profile = get_company_profile(symbol)

    return jsonify({
        'recommendations': recommendations,
        'profile': profile
    })
