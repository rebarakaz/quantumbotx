# core/db/connection.py

import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "bots.db")

def get_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # biar hasilnya bisa dipanggil pakai nama kolom
        return conn
    except sqlite3.Error as e:
        print(f"[DB] Gagal koneksi ke database: {e}")
        return None

def fetch_all(query, params=()):
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        results = cur.fetchall()
        return [dict(row) for row in results]
    except sqlite3.Error as e:
        print(f"[DB] Error saat fetch_all: {e}")
        return []
    finally:
        conn.close()

def execute_query(query, params=()):
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB] Error saat execute_query: {e}")
        return False
    finally:
        conn.close()
