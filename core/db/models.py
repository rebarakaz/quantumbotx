# core/db/models.py
import sqlite3

def log_trade_action(bot_id, action, details):
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO trade_history (bot_id, action, details) VALUES (?, ?, ?)',
                (bot_id, action, details)
            )
            if action.startswith("POSISI") or action.startswith("GAGAL") or action.startswith("AUTO"):
                notif_msg = f"Bot ID {bot_id} - {details}"
                cursor.execute(
                    'INSERT INTO notifications (bot_id, message) VALUES (?, ?)',
                    (bot_id, notif_msg)
                )
            conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Gagal mencatat aksi: {e}")
