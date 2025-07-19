# core/strategies/pulse_sync.py
import pandas_ta as ta
import MetaTrader5 as mt5
from core.data.fetch import get_rates
from core.utils.ollama import ask_ollama

def analyze(bot):
    symbol = bot.market.replace('/', '')
    tf = bot.tf_map.get(bot.timeframe, mt5.TIMEFRAME_H1)
    df = get_rates(symbol, tf, 100)

    if df is None or df.empty or len(df) < 30:
        return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup"}

    df['SMA21'] = ta.sma(df['close'], length=21)
    last = df.iloc[-1]

    prompt = f"""
    I'm building an AI trading bot. The current price of {symbol} is {last['close']:.5f}.
    The 21-period moving average is {last['SMA21']:.5f}.
    Based on this info, what would you recommend: BUY or SELL? 
    Respond only with 'BUY' or 'SELL'.
    """

    ai_decision = ask_ollama(prompt)
    ai_decision = ai_decision.upper() if ai_decision else "HOLD"

    signal = "HOLD"
    if "BUY" in ai_decision:
        signal = "BUY"
    elif "SELL" in ai_decision:
        signal = "SELL"

    return {
        "signal": signal,
        "price": last["close"],
        "explanation": f"Ollama AI recommends: {ai_decision}"
    }
