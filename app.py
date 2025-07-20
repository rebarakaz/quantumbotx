# app.py - FIXED VERSION
import os
from flask import Flask, render_template
from flask import send_from_directory
from dotenv import load_dotenv
from core.bots.trading_bot import TradingBot
from core.db.queries import get_db_connection, load_bots_from_db
from core.utils.mt5 import initialize_mt5
from core.bots.controller import load_all_bots
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === INIT APP ===
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

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

# Register blueprints
blueprints = [
    api_dashboard, api_chart, api_bots, api_profile, api_indicators,
    api_bots_analysis, api_bots_fundamentals, api_portfolio, api_history,
    api_notifications, api_stocks, api_forex, api_crypto, api_analysis,
    api_fundamentals
]

for blueprint in blueprints:
    app.register_blueprint(blueprint)

# === ROUTES ===
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

# === ERROR HANDLERS ===
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return render_template('500.html'), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
                               
# === MAIN ===
if __name__ == '__main__':
    # ✅ SECURE: Load from environment variables
    try:
        ACCOUNT = int(os.getenv('MT5_LOGIN'))
        PASSWORD = os.getenv('MT5_PASSWORD')
        SERVER = os.getenv('MT5_SERVER', 'MetaQuotes-Demo')
        
        if not ACCOUNT or not PASSWORD:
            logger.error("MT5 credentials not found in .env file")
            exit(1)
            
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid MT5 credentials in .env: {e}")
        exit(1)

    # Initialize MT5
    if not initialize_mt5(ACCOUNT, PASSWORD, SERVER):
        logger.error("❌ Failed to connect to MT5")
        exit(1)
    else:
        logger.info("✅ MT5 connected successfully")
        
        # Load all bots
        try:
            load_all_bots()
            logger.info("✅ All bots loaded successfully")
        except Exception as e:
            logger.error(f"Error loading bots: {e}")
        
        # Start Flask app
        app.run(
            debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
            host=os.getenv('FLASK_HOST', '127.0.0.1'),
            port=int(os.getenv('FLASK_PORT', 5000)),
            use_reloader=False
        )