# core/utils/mt5.py
import MetaTrader5 as mt5
import sqlite3
from datetime import datetime
from core.utils.trade import close_trade
import pandas as pd

def initialize_mt5(account, password, server):
    """Login ke MetaTrader 5."""
    if not mt5.initialize():
        print("Gagal inisialisasi MT5:", mt5.last_error())
        return False
    authorized = mt5.login(account, password=password, server=server)
    if not authorized:
        print("Login gagal:", mt5.last_error())
        mt5.shutdown()
        return False
    print(f"Berhasil login ke MT5 ({account}) di server {server}")
    return True

def get_mt5_account_info():
    """Mengambil info akun dari MetaTrader 5."""
    try:
        info = mt5.account_info()
        if info is not None:
            return info._asdict()
        else:
            print("Gagal mengambil account_info():", mt5.last_error())
            return None
    except Exception as e:
        print(f"Error saat mengambil info akun MT5: {e}")
        return None

def get_todays_profit():
    """Menghitung total profit dari histori trading hari ini."""
    try:
        # Tentukan rentang waktu dari jam 00:00 hari ini sampai sekarang
        from_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        to_date = datetime.now()
        
        # Ambil histori order yang sudah selesai
        history_deals = mt5.history_deals_get(from_date, to_date)
        
        if history_deals is None:
            return 0.0

        total_profit = 0.0
        for deal in history_deals:
            # Hanya hitung deal yang merupakan 'penutupan' posisi
            if deal.entry == 1: # 0 = in, 1 = out, 2 = in/out
                total_profit += deal.profit
        return total_profit
    except Exception as e:
        print(f"Gagal menghitung profit hari ini: {e}")
        return 0.0
        
def get_open_position(symbol, bot_id):
    """Ambil posisi terbuka berdasarkan magic number bot."""
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        return None
    for p in positions:
        if p.magic == bot_id:
            return p
    return None

def log_bot_action(bot_id, action, details, bot_name=None):
    """Catat aktivitas bot ke DB + notifikasi."""
    print(f"[LOG] Bot #{bot_id} - {action} - {details}")
    try:
        with sqlite3.connect("bots.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO trade_history (bot_id, action, details) VALUES (?, ?, ?)',
                (bot_id, action, details)
            )
            if action.startswith("POSISI") or action.startswith("GAGAL") or action.startswith("AUTO"):
                notif = f"Bot '{bot_name}' - {details}" if bot_name else details
                cursor.execute(
                    'INSERT INTO notifications (bot_id, message) VALUES (?, ?)',
                    (bot_id, notif)
                )
            conn.commit()
    except Exception as e:
        print("Gagal mencatat aksi ke DB:", e)

def auto_close_position(bot, symbol):
    """Cek apakah posisi perlu ditutup otomatis berdasarkan durasi/profit/loss."""
    pos = get_open_position(symbol, bot.bot_id)
    if not pos:
        return

    duration = datetime.now() - datetime.fromtimestamp(pos.time)
    if duration.total_seconds() > 7200:
        if close_trade(pos):
            log_bot_action(bot.bot_id, "AUTO-CUT BY TIME", f"Ditutup setelah {duration}", bot.name)
    elif pos.profit >= 100:
        if close_trade(pos):
            log_bot_action(bot.bot_id, "AUTO-CLOSE PROFIT", f"Profit = {pos.profit:.2f}", bot.name)
    elif pos.profit <= -50:
        if close_trade(pos):
            log_bot_action(bot.bot_id, "AUTO-CLOSE LOSS", f"Loss = {pos.profit:.2f}", bot.name)

def get_rates_from_mt5(symbol, timeframe, count):
    """Fungsi utama untuk mengambil data harga historis langsung dari MT5."""
    try:
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        if rates is None or len(rates) == 0:
            print(f"Gagal mengambil data dari MT5 untuk {symbol}")
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    except Exception as e:
        print(f"Error saat mengambil data dari MT5: {e}")
        return None

# 🔁 Alias supaya bisa di-import sebagai get_rates_df
get_rates_df = get_rates_from_mt5
