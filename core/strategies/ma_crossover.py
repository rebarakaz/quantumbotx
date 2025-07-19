# core/strategies/ma_crossover.py
import pandas_ta as ta
from core.data.fetch import get_rates
import MetaTrader5 as mt5

def analyze(bot):
    symbol = bot.market.replace('/', '')
    tf = bot.tf_map.get(bot.timeframe, mt5.TIMEFRAME_H1)
    df = get_rates(symbol, tf, 100)

    if df is None or df.empty or len(df) < 30:
        return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup"}

    df["ma7"] = ta.sma(df["close"], length=7)
    df["ma25"] = ta.sma(df["close"], length=25)
    df = df.dropna()
    last = df.iloc[-1]
    prev = df.iloc[-2]

    price = last["close"]

    signal = "HOLD"
    explanation = "Tidak ada crossover yang jelas"

    if prev["ma7"] < prev["ma25"] and last["ma7"] > last["ma25"]:
        signal = "BUY"
        explanation = "MA7 cross up MA25"
    elif prev["ma7"] > prev["ma25"] and last["ma7"] < last["ma25"]:
        signal = "SELL"
        explanation = "MA7 cross down MA25"

    return {
        "signal": signal,
        "price": price,
        "explanation": explanation
    }
