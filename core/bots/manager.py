# core/bots/manager.py

from core.bots.trading_bot import TradingBot
from core.db.queries import load_bots_from_db

active_bots = {}

def start_bot(bot_id):
    bot = active_bots.get(bot_id)
    if bot and bot.status != "Aktif":
        bot.start()
        print(f"[MANAGER] Bot #{bot_id} dimulai.")

def stop_bot(bot_id):
    bot = active_bots.get(bot_id)
    if bot and bot.status == "Aktif":
        bot.stop()
        print(f"[MANAGER] Bot #{bot_id} dihentikan.")

def get_bot_status(bot_id):
    bot = active_bots.get(bot_id)
    return bot.status if bot else "Tidak Ditemukan"

def get_active_bot(bot_id):
    return active_bots.get(bot_id)

def load_all_bots():
    bots_data = load_bots_from_db()
    for bot_data in bots_data:
        bot = TradingBot(**bot_data)
        active_bots[bot.bot_id] = bot
        if bot.status == "Aktif":
            bot.start()
    print(f"[MANAGER] Total bot dimuat: {len(active_bots)}")
