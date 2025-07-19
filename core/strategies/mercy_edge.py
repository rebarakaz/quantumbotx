# core/strategies/mercy_edge.py
import pandas_ta as ta
import MetaTrader5 as mt5
from core.data.fetch import get_rates
from core.utils.ollama import ask_ollama
from core.utils.trade import place_trade

def analyze(bot):
    symbol = bot.market.replace('/', '')
    df_d1 = get_rates(symbol, mt5.TIMEFRAME_D1, 200)
    df_h1 = get_rates(symbol, mt5.TIMEFRAME_H1, 100)

    if df_d1 is None or df_h1 is None or len(df_d1) < 50 or len(df_h1) < 30:
        return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup"}

    macd_d1 = ta.macd(df_d1['close']).rename(columns={'MACDh_12_26_9': 'hist_d1'})
    macd_h1 = ta.macd(df_h1['close']).rename(columns={'MACDh_12_26_9': 'hist_h1'})
    stoch = ta.stoch(df_h1['high'], df_h1['low'], df_h1['close'])

    df_d1 = df_d1.join(macd_d1)
    df_h1 = df_h1.join(macd_h1)
    df_h1['stoch_k'] = stoch.iloc[:, 0]
    df_h1['stoch_d'] = stoch.iloc[:, 1]

    last_d1 = df_d1.iloc[-1]
    last_h1 = df_h1.iloc[-1]
    prev_h1 = df_h1.iloc[-2]

    ta_suggestion = "HOLD"
    if (
        last_d1['hist_d1'] > 0 and last_h1['hist_h1'] > 0 and
        last_h1['stoch_k'] > last_h1['stoch_d'] and
        prev_h1['stoch_k'] <= prev_h1['stoch_d']
    ):
        ta_suggestion = "BUY"
    elif (
        last_d1['hist_d1'] < 0 and last_h1['hist_h1'] < 0 and
        last_h1['stoch_k'] < last_h1['stoch_d'] and
        prev_h1['stoch_k'] >= prev_h1['stoch_d']
    ):
        ta_suggestion = "SELL"

    prompt = f"""
    I'm building a trading bot. Based on my technical indicators:
    - Daily MACD Histogram: {last_d1['hist_d1']:.5f}
    - H1 MACD Histogram: {last_h1['hist_h1']:.5f}
    - Stochastic K: {last_h1['stoch_k']:.2f}, D: {last_h1['stoch_d']:.2f}
    
    My initial suggestion is: {ta_suggestion}

    Do you agree? Respond with BUY, SELL, or HOLD.
    """

    ai_decision = ask_ollama(prompt)
    ai_decision = ai_decision.upper() if ai_decision else "HOLD"

    print(f"[AI Feedback] {symbol}: {ai_decision} (TA suggestion: {ta_suggestion})")

    final_signal = "HOLD"
    if ai_decision == ta_suggestion and ai_decision in ["BUY", "SELL"]:
        final_signal = ai_decision
        place_trade(symbol, mt5.ORDER_TYPE_BUY if ai_decision == "BUY" else mt5.ORDER_TYPE_SELL, bot)

    return {
        "signal": final_signal,
        "price": last_h1["close"],
        "explanation": f"TA: {ta_suggestion}, AI: {ai_decision}"
    }
