# core/routes/api_history.py

from flask import Blueprint, jsonify
from core.data.fetch import get_trade_history_from_mt5

api_history = Blueprint('api_history', __name__)

@api_history.route('/api/history')
def api_global_history():
    history = get_trade_history_from_mt5()
    return jsonify(history)

@api_history.route('/api/bots/<int:bot_id>/history')
def api_bot_history(bot_id):
    try:
        from core.bots.controller import active_bots
        from datetime import datetime, timedelta
        import MetaTrader5 as mt5

        bot = active_bots.get(bot_id)
        if not bot:
            return jsonify({'error': 'Bot tidak ditemukan'}), 404

        magic = bot.bot_id
        from_date = datetime.now() - timedelta(days=30)
        to_date = datetime.now()
        deals = mt5.history_deals_get(from_date, to_date)

        if deals is None:
            return jsonify([])

        filtered = [
            {
                "ticket": d.ticket,
                "symbol": d.symbol,
                "volume": d.volume,
                "price": d.price,
                "profit": d.profit,
                "type": d.type,
                "time": datetime.fromtimestamp(d.time).isoformat()
            }
            for d in deals if d.magic == magic and d.entry == 1
        ]

        return jsonify(filtered)
    except Exception as e:
        print(f"[ERROR] Bot History {bot_id}: {e}")
        return jsonify({'error': str(e)}), 500
