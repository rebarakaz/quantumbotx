# core/strategies/rsi_breakout.py
import pandas_ta as ta
from core.data.fetch import get_rates
import MetaTrader5 as mt5

def analyze(bot):
    symbol = bot.market.replace('/', '')
    tf = bot.tf_map.get(bot.timeframe, mt5.TIMEFRAME_H1)
    df = get_rates(symbol, tf, 100)

    if df is None or df.empty or len(df) < 20:
        return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup"}

    df["RSI"] = ta.rsi(df["close"], length=14)
    df = df.dropna()
    last = df.iloc[-1]
    price = last["close"]
    rsi = last["RSI"]

    signal = "HOLD"
    explanation = f"RSI saat ini {rsi:.2f}, dalam zona netral"

    if rsi > 70:
        signal = "SELL"
        explanation = f"RSI {rsi:.2f} > 70 (overbought)"
    elif rsi < 30:
        signal = "BUY"
        explanation = f"RSI {rsi:.2f} < 30 (oversold)"

    return {
        "signal": signal,
        "price": price,
        "explanation": explanation
    }
