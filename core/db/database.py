# core/db/database.py

import sqlite3
from werkzeug.security import generate_password_hash

def get_connection():
    return sqlite3.connect('bots.db')

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            market TEXT NOT NULL,
            status TEXT NOT NULL,
            lot_size REAL DEFAULT 0.01,
            sl_pips INTEGER DEFAULT 100,
            tp_pips INTEGER DEFAULT 200,
            timeframe TEXT DEFAULT 'H1',
            check_interval_seconds INTEGER DEFAULT 60,
            strategy TEXT DEFAULT 'MA_CROSSOVER'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_id INTEGER, action TEXT, details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bot_id) REFERENCES bots (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_id INTEGER, message TEXT, is_read INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bot_id) REFERENCES bots (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL, join_date DATE DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Add default user
    cursor.execute("SELECT id FROM users WHERE id = 1")
    if cursor.fetchone() is None:
        cursor.execute(
            'INSERT INTO users (id, name, email, password_hash) VALUES (?, ?, ?, ?)',
            (1, 'Reynov Christian', 'contact@chrisnov.com', generate_password_hash('password123'))
        )

    conn.commit()
    conn.close()

# Untuk bisa dijalankan langsung
if __name__ == '__main__':
    init_db()
    print("Database berhasil dibuat / diperbarui!")
