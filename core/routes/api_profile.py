# core/routes/api_profile.py

from flask import Blueprint, jsonify, request
import sqlite3
from werkzeug.security import generate_password_hash

api_profile = Blueprint('api_profile', __name__)

def get_db():
    conn = sqlite3.connect('bots.db')
    conn.row_factory = sqlite3.Row
    return conn

@api_profile.route('/api/profile', methods=['GET'])
def get_profile():
    conn = get_db()
    user = conn.execute('SELECT id, name, email, strftime("%d %b %Y", join_date) as join_date FROM users WHERE id = ?', (1,)).fetchone()
    conn.close()
    if user is None:
        return jsonify({'error': 'Pengguna tidak ditemukan'}), 404
    return jsonify(dict(user))

@api_profile.route('/api/profile', methods=['PUT'])
def update_profile():
    data = request.json
    name = data.get('name')
    password = data.get('password')

    if not name:
        return jsonify({'error': 'Nama tidak boleh kosong'}), 400

    conn = get_db()
    if password:
        conn.execute('UPDATE users SET name = ?, password_hash = ? WHERE id = ?', (name, generate_password_hash(password), 1))
    else:
        conn.execute('UPDATE users SET name = ? WHERE id = ?', (name, 1))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Profil berhasil diperbarui.'})
