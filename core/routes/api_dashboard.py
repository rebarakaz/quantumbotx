# core/routes/api_dashboard.py

from flask import Blueprint, jsonify
from core.utils.mt5 import get_mt5_account_info, get_todays_profit
from core.db.queries import get_db_connection

api_dashboard = Blueprint('api_dashboard', __name__)

@api_dashboard.route('/api/dashboard/stats')
def api_dashboard_stats():
    account_info = get_mt5_account_info()
    todays_profit = get_todays_profit()

    conn = get_db_connection()
    active_bots_count = conn.execute("SELECT COUNT(id) FROM bots WHERE status = 'Aktif'").fetchone()[0]
    active_bots_data = conn.execute("SELECT name, market FROM bots WHERE status = 'Aktif'").fetchall()
    conn.close()

    active_bots_list = [{'name': bot['name'], 'market': bot['market']} for bot in active_bots_data]

    stats = {
        "balance": account_info.get('balance', 0) if account_info else 0,
        "equity": account_info.get('equity', 0) if account_info else 0,
        "profit": account_info.get('profit', 0) if account_info else 0,
        "active_bots_count": active_bots_count,
        "todays_profit": todays_profit,
        "active_bots": active_bots_list
    }
    return jsonify(stats)
