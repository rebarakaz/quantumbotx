import pandas as pd
import pandas_ta as ta
import MetaTrader5 as mt5
from core.data.fetch import get_rates as get_rates_from_mt5
from core.bots.trade import place_trade, close_trade


def run_ma_crossover(bot):
    print(f"[{bot.name}] Analisis MA_CROSSOVER aktif...")

    symbol = bot.market.replace('/', '')
    df = get_rates_from_mt5(symbol, bot.mt5_timeframe, 100)

    if df is None or len(df) < 50:
        print(f"[{bot.name}] Data tidak cukup.")
        return

    df['SMA_fast'] = ta.sma(df['close'], length=20)
    df['SMA_slow'] = ta.sma(df['close'], length=50)
    last, prev = df.iloc[-1], df.iloc[-2]

    if pd.isna(last['SMA_fast']) or pd.isna(last['SMA_slow']):
        return

    pos = bot._get_open_position(symbol)

    # --- SINYAL BELI ---
    if prev['SMA_fast'] <= prev['SMA_slow'] and last['SMA_fast'] > last['SMA_slow']:
        if pos and pos.type == mt5.ORDER_TYPE_SELL:
            close_trade(pos)
            bot._log_action("CLOSE SELL", "Tutup posisi jual karena sinyal BELI (MA)")
        if not pos or pos.type == mt5.ORDER_TYPE_SELL:
            bot._log_action("SINYAL BELI (MA)", "Cross up terdeteksi")
            place_trade(symbol, mt5.ORDER_TYPE_BUY, bot.lot_size, bot.sl_pips, bot.tp_pips, bot.bot_id)

    # --- SINYAL JUAL ---
    elif prev['SMA_fast'] >= prev['SMA_slow'] and last['SMA_fast'] < last['SMA_slow']:
        if pos and pos.type == mt5.ORDER_TYPE_BUY:
            close_trade(pos)
            bot._log_action("CLOSE BUY", "Tutup posisi beli karena sinyal JUAL (MA)")
        if not pos or pos.type == mt5.ORDER_TYPE_BUY:
            bot._log_action("SINYAL JUAL (MA)", "Cross down terdeteksi")
            place_trade(symbol, mt5.ORDER_TYPE_SELL, bot.lot_size, bot.sl_pips, bot.tp_pips, bot.bot_id)
