# core/routes/api_bots_analysis.py

from flask import Blueprint, jsonify
from core.bots.manager import active_bots
from core.data.fetch import get_rates as get_rates_from_mt5
import pandas_ta as ta
import MetaTrader5 as mt5
import pandas as pd

api_bots_analysis = Blueprint('api_bots_analysis', __name__)

@api_bots_analysis.route('/api/bots/<int:bot_id>/analysis')
def get_bot_analysis(bot_id):
    bot_obj = active_bots.get(bot_id)
    if not bot_obj:
        return jsonify({'error': 'Objek bot tidak ditemukan di memori'}), 404

    strategy = bot_obj.strategy
    symbol = bot_obj.market.replace('/', '')
    response_data = {}

    try:
        # --- LOGIKA DINAMIS BERDASARKAN STRATEGI ---

        if strategy == 'MA_CROSSOVER':
            df = get_rates_from_mt5(symbol, bot_obj.mt5_timeframe, 52)
            if df is None or len(df) < 51: return jsonify({'error': 'Data tidak cukup'}), 400

            df["ma_fast"] = ta.sma(df["close"], length=20)
            df["ma_slow"] = ta.sma(df["close"], length=50)
            df.dropna(inplace=True)
            if df.empty: return jsonify({'error': 'Indikator belum matang'}), 400
            
            last = df.iloc[-1]
            signal = "BULLISH (Beli)" if last['ma_fast'] > last['ma_slow'] else "BEARISH (Jual)"
            
            response_data = {
                "price": last['close'],
                "ma_fast": last['ma_fast'],
                "ma_slow": last['ma_slow'],
                "signal": signal
            }

        elif strategy == 'RSI_BREAKOUT':
            df = get_rates_from_mt5(symbol, bot_obj.mt5_timeframe, 15)
            if df is None or len(df) < 15: return jsonify({'error': 'Data tidak cukup'}), 400
            
            df["rsi"] = ta.rsi(df["close"], length=14)
            df.dropna(inplace=True)
            if df.empty: return jsonify({'error': 'Indikator belum matang'}), 400

            last = df.iloc[-1]
            signal = "NETRAL"
            if last['rsi'] > 70: signal = "OVERBOUGHT (Jual)"
            elif last['rsi'] < 30: signal = "OVERSOLD (Beli)"

            response_data = {
                "price": last['close'],
                "rsi": last['rsi'],
                "signal": signal
            }

        elif strategy in ['MERCY_EDGE', 'FULL_MERCY']:
            df_d1 = get_rates_from_mt5(symbol, mt5.TIMEFRAME_D1, 200)
            df_h1 = get_rates_from_mt5(symbol, bot_obj.mt5_timeframe, 100)
            if df_d1 is None or df_h1 is None or len(df_d1) < 50 or len(df_h1) < 30:
                return jsonify({'error': 'Data tidak cukup'}), 400

            df_d1.ta.macd(append=True)
            df_h1.ta.macd(append=True)
            df_h1.ta.stoch(append=True)
            df_d1.dropna(inplace=True)
            df_h1.dropna(inplace=True)
            if df_d1.empty or df_h1.empty: return jsonify({'error': 'Indikator belum matang'}), 400

            last_d1 = df_d1.iloc[-1]
            last_h1 = df_h1.iloc[-1]
            
            signal = "TAHAN"
            if last_d1['MACDh_12_26_9'] > 0 and last_h1['MACDh_12_26_9'] > 0: signal = "BULLISH (Beli)"
            elif last_d1['MACDh_12_26_9'] < 0 and last_h1['MACDh_12_26_9'] < 0: signal = "BEARISH (Jual)"

            # ** PERBAIKAN KUNCI DI SINI: Samakan nama kunci dengan yang diharapkan JavaScript **
            response_data = {
                "price": last_h1['close'],
                "D1_MACDh": last_d1['MACDh_12_26_9'],
                "H1_MACDh": last_h1['MACDh_12_26_9'],
                "H1_STOCHk": last_h1['STOCHk_14_3_3'],
                "H1_STOCHd": last_h1['STOCHd_14_3_3'],
                "signal": signal
            }
        
        else:
            last_price_df = get_rates_from_mt5(symbol, bot_obj.mt5_timeframe, 1)
            if last_price_df is not None and not last_price_df.empty:
                response_data = {
                    "price": last_price_df.iloc[-1]['close'],
                    "signal": "TAHAN",
                    "info": f"UI Analisis untuk strategi '{strategy}' belum diimplementasikan."
                }
            else:
                return jsonify({'error': 'Gagal mengambil harga terakhir'}), 400

        return jsonify(response_data)

    except Exception as e:
        print(f"CRITICAL ERROR in get_bot_analysis for bot {bot_id} ({strategy}): {e}")
        # Kirim error 500 yang jelas jika terjadi crash
        return jsonify({'error': 'Terjadi kesalahan internal di server saat melakukan analisis.'}), 500