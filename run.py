# run.py

import os
import sys
import atexit
import logging
from flask import jsonify
from core import create_app
from core.bots.controller import shutdown_all_bots, ambil_semua_bot
from dotenv import load_dotenv

# Conditional MT5 Import
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    # We only import this if MT5 is available to avoid import errors in utils
    # But wait, core.utils.mt5 likely imports mt5 too. 
    # We should handle that gracefully or ensure we don't call it.

load_dotenv()

# Konfigurasi logging bersih dari awal
logging.getLogger('werkzeug').setLevel(logging.WARNING)

def shutdown_app():
    """Fungsi shutdown terpusat."""
    logging.info("Memulai proses shutdown aplikasi...")
    shutdown_all_bots()
    if MT5_AVAILABLE:
        try:
            mt5.shutdown()  # pyright: ignore[reportAttributeAccessIssue]
            logging.info("Koneksi MetaTrader 5 ditutup.")
        except Exception:
            pass
    logging.info("Aplikasi berhenti.")

# Panggil pabrik untuk membuat aplikasi kita
app = create_app()

@app.route('/api/health')
def health_check():
    """Endpoint untuk memastikan server berjalan."""
    mt5_status = "Not Available"
    if MT5_AVAILABLE:
        mt5_status = "MT5 connected" if mt5.terminal_info() is not None else "MT5 not connected"  # pyright: ignore[reportAttributeAccessIssue]
    
    broker_type = os.getenv('BROKER_TYPE', 'MT5')
    return jsonify({
        "status": "ok", 
        "message": "Server is running", 
        "broker_type": broker_type,
        "mt5": mt5_status
    })

if __name__ == '__main__':
    broker_type = os.getenv('BROKER_TYPE', 'MT5')
    logging.info(f"Starting app with BROKER_TYPE={broker_type}")

    # Skip MT5 initialization if SKIP_MT5_INIT is set OR if we are using CCXT
    if os.getenv('SKIP_MT5_INIT') == '1' or broker_type != 'MT5':
        logging.info("Skipping MT5 initialization (CCXT mode or deployment).")
        
        # Still load bots to start them (they will use the configured broker)
        try:
            ambil_semua_bot()
            atexit.register(shutdown_app)
        except Exception as e:
            logging.error(f"Error starting bots: {e}")

        app.run(
            debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
            host=os.getenv('FLASK_HOST', '127.0.0.1'),
            port=int(os.getenv('FLASK_PORT', 5000)),
            use_reloader=False
        )
        sys.exit(0)

    # --- Inisialisasi MT5 Terpusat (Only if BROKER_TYPE is MT5) ---
    if not MT5_AVAILABLE:
        logging.error("CRITICAL: BROKER_TYPE is MT5 but MetaTrader5 module is not installed.")
        sys.exit(1)

    from core.utils.mt5 import initialize_mt5

    try:
        # Ambil kredensial MT5 dari environment variables dengan validasi
        account_str = os.getenv('MT5_LOGIN')
        password = os.getenv('MT5_PASSWORD')
        server = os.getenv('MT5_SERVER', 'MetaQuotes-Demo')
        
        # Validasi kredensial tidak kosong
        if not account_str or not password:
            logging.error("Error: MT5_LOGIN dan MT5_PASSWORD harus diisi di file .env")
            sys.exit(1)
        
        # Convert account to integer dengan error handling
        try:
            account = int(account_str)
        except ValueError:
            logging.error(f"Error: MT5_LOGIN harus berupa angka, ditemukan: {account_str}")
            sys.exit(1)
            
        if initialize_mt5(account, password, server):
            logging.info("Koneksi MT5 berhasil diinisialisasi dari run.py.")
            
            # Load bots
            ambil_semua_bot() 
            atexit.register(shutdown_app) # Daftarkan shutdown HANYA jika koneksi berhasil
        else:
            logging.error("Error: Gagal terhubung ke MT5. Pastikan MT5 terminal berjalan dan kredensial benar.")
            sys.exit(1)
    except Exception as e:
        logging.critical(
            f"GAGAL total saat inisialisasi MT5 di run.py: {e}",
            exc_info=True
        )

    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        host=os.getenv('FLASK_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        use_reloader=False
    )
