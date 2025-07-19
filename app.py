# app.py
from flask import Flask, render_template, jsonify, request
from core.bots.trading_bot import TradingBot
from core.db.queries import get_db_connection, load_bots_from_db
from core.utils.mt5 import initialize_mt5
import MetaTrader5 as mt5
from core.bots.controller import load_all_bots

# === INIT APP ===
app = Flask(__name__)

# === REGISTER BLUEPRINTS ===
from core.routes.api_dashboard import api_dashboard
from core.routes.api_chart import api_chart
from core.routes.api_bots import api_bots
from core.routes.api_profile import api_profile
from core.routes.api_indicators import api_indicators
from core.routes.api_bots_analysis import api_bots_analysis
from core.routes.api_bots_fundamentals import api_bots_fundamentals
from core.routes.api_portfolio import api_portfolio
from core.routes.api_history import api_history
from core.routes.api_notifications import api_notifications
from core.routes.api_stocks import api_stocks
from core.routes.api_forex import api_forex
from core.routes.api_crypto import api_crypto
from core.routes.api_analysis import api_analysis
from core.routes.api_fundamentals import api_fundamentals

# === DAFTARKAN BLUEPRINTS ===
app.register_blueprint(api_dashboard)
app.register_blueprint(api_chart)
app.register_blueprint(api_bots)
app.register_blueprint(api_profile)
app.register_blueprint(api_indicators)
app.register_blueprint(api_bots_analysis)
app.register_blueprint(api_bots_fundamentals)
app.register_blueprint(api_portfolio)
app.register_blueprint(api_history)
app.register_blueprint(api_notifications)
app.register_blueprint(api_stocks)
app.register_blueprint(api_forex)
app.register_blueprint(api_crypto)
app.register_blueprint(api_analysis)
app.register_blueprint(api_fundamentals)

# Load semua bot dari database
load_all_bots()

# Halaman Utama
@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/trading_bots')
def bots_page():
    return render_template('trading_bots.html')

@app.route('/bots/<int:bot_id>')
def bot_detail_page(bot_id):
    return render_template('bot_detail.html')

@app.route('/portfolio')
def portfolio_page():
    return render_template('portfolio.html')

@app.route('/history')
def history_page():
    return render_template('history.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/profile')
def profile_page():
    return render_template('profile.html')

@app.route('/notifications')
def notifications_page():
    return render_template('notifications.html')

# ✨ ENDPOINT API (akan kita pisahkan nanti jadi routes modular)
# Tapi untuk sementara, biarkan tetap di sini agar tidak error.

# --- JALANKAN APP ---
if __name__ == '__main__':
    ACCOUNT = 94464091
    PASSWORD = "3rX@GcMm"
    SERVER = "MetaQuotes-Demo"

    if not initialize_mt5(ACCOUNT, PASSWORD, SERVER):
        print("❌ Gagal terhubung ke MT5")
    else:
        load_all_bots()
        app.run(debug=True, use_reloader=False)
