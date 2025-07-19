import pandas as pd
import pandas_ta as ta
import MetaTrader5 as mt5
from core.data.fetch import get_rates as get_rates_from_mt5
from core.bots.trade import place_trade


def run_rsi_breakout(bot):
    print(f"[{bot.name}] Analisis RSI_BREAKOUT aktif...")

    symbol = bot.market.replace('/', '')
    df = get_rates_from_mt5(symbol, bot.mt5_timeframe, 100)

    if df is None or len(df) < 20:
        print(f"[{bot.name}] Data tidak cukup untuk analisis RSI.")
        return

    df['RSI'] = ta.rsi(df['close'], length=14)
    last, prev = df.iloc[-1], df.iloc[-2]

    if pd.isna(last['RSI']) or pd.isna(prev['RSI']):
        return

    pos = bot._get_open_position(symbol)
    if not pos:
        if prev['RSI'] < 30 and last['RSI'] > 30:
            bot._log_action("SINYAL BELI (RSI)", f"Breakout RSI naik: {last['RSI']:.2f}")
            place_trade(symbol, mt5.ORDER_TYPE_BUY, bot.lot_size, bot.sl_pips, bot.tp_pips, bot.bot_id)
        elif prev['RSI'] > 70 and last['RSI'] < 70:
            bot._log_action("SINYAL JUAL (RSI)", f"Breakout RSI turun: {last['RSI']:.2f}")
            place_trade(symbol, mt5.ORDER_TYPE_SELL, bot.lot_size, bot.sl_pips, bot.tp_pips, bot.bot_id)
