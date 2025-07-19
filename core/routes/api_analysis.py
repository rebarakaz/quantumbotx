# core/routes/api_analysis.py
from flask import Blueprint, jsonify, request
from core.bots.controller import get_active_bot
from core.strategies.ma_crossover import analyze
from core.strategies.rsi_breakout import analyze
from core.strategies.pulse_sync import analyze
from core.strategies.mercy_edge import analyze

api_analysis = Blueprint("api_analysis", __name__)

@api_analysis.route("/api/bots/<int:bot_id>/analysis")
def get_bot_analysis(bot_id):
    bot = get_active_bot(bot_id)
    if not bot:
        return jsonify({'error': 'Bot tidak ditemukan di memori'}), 404


    tf = bot.tf_map.get(bot.timeframe)

    result = {
        "price": None,
        "signal": "-",
        "strategy": bot.strategy,
        "explanation": "",
        "extra": {}
    }

    try:
        # Ambil analisis berdasarkan strategi
        if bot.strategy == "MA_CROSSOVER":
            df = bot.fetch_data(tf, 100)
            analysis = analyze(df)
        elif bot.strategy == "RSI_BREAKOUT":
            df = bot.fetch_data(tf, 100)
            analysis = analyze(df)
        elif bot.strategy == "PULSE_SYNC":
            df = bot.fetch_data(tf, 100)
            analysis = analyze(df)
        elif bot.strategy == "MERCY_EDGE":
            analysis = analyze(bot)
        else:
            analysis = None

        if analysis:
            result["price"] = float(analysis.get("price", 0))
            result["signal"] = analysis.get("signal", "-")
            result["explanation"] = analysis.get("explanation", "")
            result["extra"] = {k: v for k, v in analysis.items() if k not in ["price", "signal", "explanation"]}

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})
