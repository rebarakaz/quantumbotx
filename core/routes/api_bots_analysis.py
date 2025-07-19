# core/routes/api_bots_analysis.py

from flask import Blueprint, jsonify
from core.bots.manager import active_bots
from core.data.fetch import get_rates as get_rates_from_mt5
import pandas_ta as ta
import MetaTrader5 as mt5

api_bots_analysis = Blueprint('api_bots_analysis', __name__)

@api_bots_analysis.route('/api/bots/<int:bot_id>/analysis')
def get_bot_analysis(bot_id):
    bot_obj = active_bots.get(bot_id)
    if not bot_obj:
        return jsonify({'error': 'Objek bot tidak ditemukan di memori'}), 404

    symbol = bot_obj.market.replace('/', '')
    rates_df = get_rates_from_mt5(symbol, bot_obj.mt5_timeframe, 100)

    if rates_df is None or len(rates_df) < 25:
        return jsonify({'error': 'Data tidak cukup untuk analisis'}), 400

    rates_df['MA7'] = ta.sma(rates_df['close'], length=7)
    rates_df['MA25'] = ta.sma(rates_df['close'], length=25)

    last_row = rates_df.iloc[-1]
    prev_row = rates_df.iloc[-2]

    signal = "TAHAN"
    if last_row['MA7'] > last_row['MA25'] and prev_row['MA7'] <= prev_row['MA25']:
        signal = "SINYAL BELI"
    elif last_row['MA7'] < last_row['MA25'] and prev_row['MA7'] >= prev_row['MA25']:
        signal = "SINYAL JUAL"

    return jsonify({
        "price": last_row['close'],
        "ma7": last_row['MA7'],
        "ma25": last_row['MA25'],
        "signal": signal
    })
