import sys
import os

# Tambahkan direktori root ke sys.path agar bisa import modul core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.db.queries import add_bot

def create_crypto_bot():
    print("Creating Crypto Bot for CCXT...")
    
    # Parameter Bot
    name = "BTC-Scalper-CCXT"
    market = "BTC/USDT"  # Simbol standar CCXT (Binance)
    lot_size = 0.001     # Sesuaikan dengan min order exchange
    sl_pips = 50         # Dalam poin/pips (tergantung strategi)
    tp_pips = 100
    timeframe = "M15"    # String timeframe standar
    interval = 60        # Check interval seconds
    strategy = "RSI Crossover" # Strategi yang sudah ada
    
    # Tambahkan ke Database
    bot_id = add_bot(
        name=name,
        market=market,
        lot_size=lot_size,
        sl_pips=sl_pips,
        tp_pips=tp_pips,
        timeframe=timeframe,
        interval=interval,
        strategy=strategy
    )
    
    if bot_id:
        print(f"✅ Bot '{name}' berhasil dibuat dengan ID: {bot_id}")
        print(f"ℹ️  Pastikan container berjalan dengan BROKER_TYPE=CCXT")
    else:
        print("❌ Gagal membuat bot.")

if __name__ == "__main__":
    create_crypto_bot()
