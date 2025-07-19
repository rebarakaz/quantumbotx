# core/routes/api_notifications.py

from flask import Blueprint, jsonify, request
import sqlite3

api_notifications = Blueprint('api_notifications', __name__)

def get_db():
    conn = sqlite3.connect('bots.db')
    conn.row_factory = sqlite3.Row
    return conn

@api_notifications.route('/api/notifications')
def get_notifications():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT n.id, n.message, n.is_read, n.timestamp, b.name as bot_name
        FROM notifications n
        LEFT JOIN bots b ON n.bot_id = b.id
        ORDER BY n.timestamp DESC
    ''')
    notifications = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(notifications)

@api_notifications.route('/api/notifications/unread-count')
def get_unread_notifications_count():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(id) as unread_count FROM notifications WHERE is_read = 0")
    count = dict(cursor.fetchone())
    conn.close()
    return jsonify(count)

@api_notifications.route('/api/notifications/mark-as-read', methods=['POST'])
def mark_notifications_as_read():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET is_read = 1 WHERE is_read = 0")
    conn.commit()
    conn.close()
    return jsonify({'message': 'Semua notifikasi ditandai sudah dibaca.'})
