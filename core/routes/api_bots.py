# core/routes/api_bots.py

from flask import Blueprint, request, jsonify
from core.db.queries import get_db_connection
from core.bots.trading_bot import TradingBot
from core.bots.controller import active_bots
from core.utils.validation import validate_bot_params
import sqlite3

api_bots = Blueprint('api_bots', __name__)

@api_bots.route('/api/bots', methods=['GET'])
def get_bots():
    conn = get_db_connection()
    bots = conn.execute('SELECT * FROM bots').fetchall()
    conn.close()
    return jsonify([dict(bot) for bot in bots])

@api_bots.route('/api/bots/<int:bot_id>', methods=['GET'])
def get_bot(bot_id):
    conn = get_db_connection()
    bot = conn.execute('SELECT * FROM bots WHERE id = ?', (bot_id,)).fetchone()
    conn.close()
    if not bot:
        return jsonify({'error': 'Bot tidak ditemukan'}), 404
    return jsonify(dict(bot))

@api_bots.route('/api/bots', methods=['POST'])
def create_bot():
    data = request.json
    errors = validate_bot_params(data)
    if errors:
        return jsonify({'error': errors}), 400

    bot_name = data['name']
    bot_market = data['market']
    lot_size = data.get('lot_size', 0.01)
    sl_pips = data.get('sl_pips', 100)
    tp_pips = data.get('tp_pips', 200)
    timeframe = data.get('timeframe', 'H1')
    check_interval = data.get('check_interval_seconds', 60)
    strategy = data.get('strategy', 'MA_CROSSOVER')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO bots (name, market, status, lot_size, sl_pips, tp_pips, timeframe, check_interval_seconds, strategy) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (bot_name, bot_market, 'Dijeda', lot_size, sl_pips, tp_pips, timeframe, check_interval, strategy)
        )
        bot_id = cursor.lastrowid
        cursor.execute(
            'INSERT INTO trade_history (bot_id, action, details) VALUES (?, ?, ?)',
            (bot_id, 'Dibuat', f"Bot '{bot_name}' ({strategy}) untuk pasar '{bot_market}' telah dibuat.")
        )
        conn.commit()
        conn.close()

        new_bot = TradingBot(bot_id=bot_id, name=bot_name, market=bot_market,
                             status='Dijeda', lot_size=float(lot_size),
                             sl_pips=int(sl_pips), tp_pips=int(tp_pips),
                             timeframe=timeframe, check_interval_seconds=int(check_interval),
                             strategy=strategy)
        active_bots[bot_id] = new_bot

        return jsonify({'message': 'Bot berhasil dibuat', 'bot_id': bot_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bots.route('/api/bots/<int:bot_id>/start', methods=['POST'])
def start_bot(bot_id):
    bot = active_bots.get(bot_id)
    if bot:
        bot.start()
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO trade_history (bot_id, action, details) VALUES (?, ?, ?)',
            (bot_id, 'Mulai', 'Bot diaktifkan oleh pengguna.')
        )
        conn.execute('UPDATE bots SET status = ? WHERE id = ?', ('Aktif', bot_id))
        conn.commit()
        conn.close()
        return jsonify({'message': f'Bot {bot.name} dimulai.'})
    return jsonify({'error': 'Bot tidak ditemukan'}), 404

@api_bots.route('/api/bots/<int:bot_id>/stop', methods=['POST'])
def stop_bot(bot_id):
    bot = active_bots.get(bot_id)
    if bot:
        bot.stop()
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO trade_history (bot_id, action, details) VALUES (?, ?, ?)',
            (bot_id, 'Berhenti', 'Bot dijeda oleh pengguna.')
        )
        conn.execute('UPDATE bots SET status = ? WHERE id = ?', ('Dijeda', bot_id))
        conn.commit()
        conn.close()
        return jsonify({'message': f'Bot {bot.name} dihentikan.'})
    return jsonify({'error': 'Bot tidak ditemukan'}), 404

@api_bots.route('/api/bots/<int:bot_id>', methods=['PUT'])
def update_bot(bot_id):
    bot = active_bots.get(bot_id)
    if not bot:
        return jsonify({'error': 'Bot tidak ditemukan'}), 404

    data = request.json
    errors = validate_bot_params(data)
    if errors:
        return jsonify({'error': errors}), 400

    try:
        conn = get_db_connection()
        details = f"Pengaturan diubah: Nama='{data['name']}', Strategi='{data['strategy']}', Pasar='{data['market']}', Lot={data['lot_size']}, SL={data['sl_pips']}, TP={data['tp_pips']}, TF='{data['timeframe']}'"
        conn.execute(
            'INSERT INTO trade_history (bot_id, action, details) VALUES (?, ?, ?)',
            (bot_id, 'Edit', details)
        )
        conn.execute(
            '''UPDATE bots SET name = ?, market = ?, lot_size = ?, sl_pips = ?, tp_pips = ?, timeframe = ?, check_interval_seconds = ?, strategy = ?
               WHERE id = ?''',
            (data['name'], data['market'], data['lot_size'], data['sl_pips'], data['tp_pips'],
             data['timeframe'], data['check_interval_seconds'], data['strategy'], bot_id)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        return jsonify({'error': f'Gagal memperbarui bot: {str(e)}'}), 500

    bot.name = data['name']
    bot.market = data['market']
    bot.lot_size = float(data['lot_size'])
    bot.sl_pips = int(data['sl_pips'])
    bot.tp_pips = int(data['tp_pips'])
    bot.timeframe = data['timeframe']
    bot.check_interval = int(data['check_interval_seconds'])
    bot.strategy = data['strategy']

    return jsonify({'message': f'Bot {bot.name} berhasil diperbarui.'})

@api_bots.route('/api/bots/<int:bot_id>', methods=['DELETE'])
def delete_bot(bot_id):
    bot = active_bots.get(bot_id)
    if not bot:
        return jsonify({'error': 'Bot tidak ditemukan'}), 404

    bot.stop()
    del active_bots[bot_id]

    conn = get_db_connection()
    conn.execute('DELETE FROM trade_history WHERE bot_id = ?', (bot_id,))
    conn.execute('DELETE FROM bots WHERE id = ?', (bot_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Bot dan riwayatnya berhasil dihapus.'})
