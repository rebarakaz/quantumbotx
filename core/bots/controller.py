# core/bots/controller.py
from core.bots.trading_bot import TradingBot
from core.db.queries import ambil_semua_bot
import threading

# Dictionary untuk menyimpan semua bot aktif
active_bots = {}

def load_all_bots():
    bots = ambil_semua_bot()
    for bot_data in bots:
        bot_data['bot_id'] = bot_data.pop('id')  # GANTI id → bot_id
        bot = TradingBot(**bot_data)
        active_bots[bot.bot_id] = bot
        if bot.status == 'Aktif':
            bot.start()

def get_active_bot(bot_id):
    return active_bots.get(int(bot_id))
    
def start_bot(bot_id):
    bot = active_bots.get(bot_id)
    if bot and bot.status != 'Aktif':
        bot.start()

def stop_bot(bot_id):
    bot = active_bots.get(bot_id)
    if bot and bot.status == 'Aktif':
        bot.stop()

def get_bot_status(bot_id):
    bot = active_bots.get(bot_id)
    if bot:
        return bot.status
    return "Tidak ditemukan"

def restart_all_bots():
    for bot in active_bots.values():
        if bot.status == 'Aktif':
            bot.stop()
            bot.start()

def reload_all_bots():
    """
    Hentikan semua bot, hapus dictionary,
    lalu load ulang dari database.
    """
    for bot in active_bots.values():
        bot.stop()
    active_bots.clear()
    load_all_bots()
