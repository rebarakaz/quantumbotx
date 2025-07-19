# core/db/queries.py

import sqlite3

def get_db_connection():
    conn = sqlite3.connect('bots.db')
    conn.row_factory = sqlite3.Row
    return conn

def load_bots_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bots")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def tambah_bot(name, market, lot_size, sl_pips, tp_pips, timeframe, interval, strategy):
    conn = sqlite3.connect('bots.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bots (name, market, status, lot_size, sl_pips, tp_pips, timeframe, check_interval_seconds, strategy)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, market, 'Dijeda', lot_size, sl_pips, tp_pips, timeframe, interval, strategy))
    conn.commit()
    conn.close()

def ambil_semua_bot():
    conn = sqlite3.connect('bots.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bots')
    bots = cursor.fetchall()
    conn.close()
    return [dict(bot) for bot in bots]

def get_bot_by_id(bot_id):
    conn = sqlite3.connect('bots.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bots WHERE id = ?", (bot_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_bot(bot_id, name, market, lot_size, sl_pips, tp_pips, timeframe, interval, strategy):
    conn = sqlite3.connect('bots.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE bots SET name=?, market=?, lot_size=?, sl_pips=?, tp_pips=?, timeframe=?, check_interval_seconds=?, strategy=?
        WHERE id=?
    ''', (name, market, lot_size, sl_pips, tp_pips, timeframe, interval, strategy, bot_id))
    conn.commit()
    conn.close()

def hapus_bot(bot_id):
    conn = sqlite3.connect('bots.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM bots WHERE id=?', (bot_id,))
    conn.commit()
    conn.close()

def tambah_history(bot_id, action, details):
    conn = sqlite3.connect('bots.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trade_history (bot_id, action, details)
        VALUES (?, ?, ?)
    ''', (bot_id, action, details))
    conn.commit()
    conn.close()

def tambah_notifikasi(bot_id, message):
    conn = sqlite3.connect('bots.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO notifications (bot_id, message)
        VALUES (?, ?)
    ''', (bot_id, message))
    conn.commit()
    conn.close()
