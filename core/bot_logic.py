#bot_logic.py

import time
import threading
import sqlite3
from datetime import datetime
import pandas as pd
import pandas_ta as ta
import MetaTrader5 as mt5
from api import data_fetcher

from .helpers import parse_decimal, initialize_mt5, place_trade, close_trade


class TradingBot:
    def __init__(self, bot_id, name, market, status='Dijeda', lot_size=0.01, sl_pips=100, tp_pips=200, timeframe='H1', strategy='MA_CROSSOVER', check_interval_seconds=60):
        self.bot_id = bot_id
        self.name = name
        self.market = market
        self.status = status
        self.lot_size = lot_size
        self.sl_pips = sl_pips
        self.tp_pips = tp_pips
        self.timeframe = timeframe
        self.strategy = strategy
        self.check_interval = check_interval_seconds
        self.mt5_timeframe_map = {
            "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15, "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1, "W1": mt5.TIMEFRAME_W1,
            "MN1": mt5.TIMEFRAME_MN1
        }
        self.mt5_timeframe = self.mt5_timeframe_map.get(self.timeframe, mt5.TIMEFRAME_H1)
        self._thread = None
        self._stop_event = threading.Event()

    def _log_action(self, action, details):
        print(f"LOGGING: Bot {self.bot_id} - {action} - {details}")
        try:
            with sqlite3.connect('bots.db') as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO trade_history (bot_id, action, details) VALUES (?, ?, ?)', (self.bot_id, action, details))
                if action.startswith("POSISI") or action.startswith("GAGAL") or action.startswith("AUTO"):
                    notif_message = f"Bot '{self.name}' - {details}"
                    cursor.execute('INSERT INTO notifications (bot_id, message) VALUES (?, ?)', (self.bot_id, notif_message))
                conn.commit()
        except Exception as e:
            print(f"Gagal mencatat aksi ke DB: {e}")

    def _get_open_position(self, symbol: str):
        positions = mt5.positions_get(symbol=symbol)
        if positions:
            for p in positions:
                if p.magic == self.bot_id:
                    return p
        return None

    def _check_position_auto_close(self, symbol):
        pos = self._get_open_position(symbol)
        if not pos:
            return
        duration = datetime.now() - datetime.fromtimestamp(pos.time)
        if duration.total_seconds() > 7200:
            if close_trade(pos):
                self._log_action("AUTO-CUT BY TIME", f"Posisi ditutup setelah {duration}")
        elif pos.profit >= 100:
            if close_trade(pos):
                self._log_action("AUTO-CLOSE PROFIT", f"Profit = {pos.profit:.2f}")
        elif pos.profit <= -50:
            if close_trade(pos):
                self._log_action("AUTO-CLOSE LOSS", f"Loss = {pos.profit:.2f}")

    def _analyze(self):
        print("Menjalankan MA Crossover...")
        symbol = self.market.replace('/', '')
        df = data_fetcher.get_rates_from_mt5(symbol, self.mt5_timeframe, 100)
        if df is None or len(df) < 50:
            return

        df['SMA_fast'] = ta.sma(df['close'], length=20)
        df['SMA_slow'] = ta.sma(df['close'], length=50)
        last, prev = df.iloc[-1], df.iloc[-2]

        if pd.isna(last['SMA_fast']) or pd.isna(last['SMA_slow']):
            return

        pos = self._get_open_position(symbol)
        if prev['SMA_fast'] <= prev['SMA_slow'] and last['SMA_fast'] > last['SMA_slow']:
            if pos and pos.type == mt5.ORDER_TYPE_SELL:
                close_trade(pos)
                self._log_action("CLOSE SELL", "Tutup posisi jual karena sinyal BELI (MA)")
            if not pos or pos.type == mt5.ORDER_TYPE_SELL:
                self._log_action("SINYAL BELI (MA)", "Cross up terdeteksi")
                place_trade(symbol, mt5.ORDER_TYPE_BUY, self.lot_size, self.sl_pips, self.tp_pips, self.bot_id)
        elif prev['SMA_fast'] >= prev['SMA_slow'] and last['SMA_fast'] < last['SMA_slow']:
            if pos and pos.type == mt5.ORDER_TYPE_BUY:
                close_trade(pos)
                self._log_action("CLOSE BUY", "Tutup posisi beli karena sinyal JUAL (MA)")
            if not pos or pos.type == mt5.ORDER_TYPE_BUY:
                self._log_action("SINYAL JUAL (MA)", "Cross down terdeteksi")
                place_trade(symbol, mt5.ORDER_TYPE_SELL, self.lot_size, self.sl_pips, self.tp_pips, self.bot_id)

    def _analyze(self):
        print("Menjalankan RSI Breakout...")
        symbol = self.market.replace('/', '')
        df = data_fetcher.get_rates_from_mt5(symbol, self.mt5_timeframe, 100)
        if df is None or len(df) < 20:
            return
        df['RSI'] = ta.rsi(df['close'], length=14)
        last, prev = df.iloc[-1], df.iloc[-2]

        if pd.isna(last['RSI']) or pd.isna(prev['RSI']):
            return

        pos = self._get_open_position(symbol)
        if not pos:
            if prev['RSI'] < 30 and last['RSI'] > 30:
                self._log_action("SINYAL BELI (RSI)", f"Breakout RSI naik: {last['RSI']:.2f}")
                place_trade(symbol, mt5.ORDER_TYPE_BUY, self.lot_size, self.sl_pips, self.tp_pips, self.bot_id)
            elif prev['RSI'] > 70 and last['RSI'] < 70:
                self._log_action("SINYAL JUAL (RSI)", f"Breakout RSI turun: {last['RSI']:.2f}")
                place_trade(symbol, mt5.ORDER_TYPE_SELL, self.lot_size, self.sl_pips, self.tp_pips, self.bot_id)

    def _run_logic(self):
        symbol = self.market.replace('/', '')
        self._log_action("INFO", f"Bot memulai untuk {self.market} dengan strategi {self.strategy}")
        try:
            while self.status == 'Aktif' and not self._stop_event.is_set():
                if self.strategy == 'MA_CROSSOVER':
                    self._analyze()
                elif self.strategy == 'RSI_BREAKOUT':
                    self._analyze()
                self._check_position_auto_close(symbol)
                time.sleep(self.check_interval)
        except Exception as e:
            self._log_action("ERROR", str(e))
        finally:
            self._log_action("INFO", "Bot dihentikan.")

    def start(self):
        if self.status != 'Aktif' and (self._thread is None or not self._thread.is_alive()):
            self.status = 'Aktif'
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_logic, daemon=True)
            self._thread.start()

    def stop(self):
        if self.status == 'Aktif':
            self.status = 'Dijeda'
            self._stop_event.set()
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=2)
            self._thread = None
