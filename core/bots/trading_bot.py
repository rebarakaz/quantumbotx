# core/bots/trading_bot.py
import time
import threading
import sqlite3
from datetime import datetime
import MetaTrader5 as mt5
from core.db.models import log_trade_action
from core.mt5.trade import place_trade, close_trade
from core.strategies.ma_crossover import analyze as analyze_ma
from core.strategies.rsi_breakout import analyze as analyze_rsi
from core.strategies.pulse_sync import analyze as analyze_pulse
from core.strategies.mercy_edge import analyze as analyze_mercy
from core.data.fetch import get_rates

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
        self._thread = None
        self._stop_event = threading.Event()
        self.tf_map = {
            "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15, "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4, "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1, "MN1": mt5.TIMEFRAME_MN1
        }

    def _get_open_position(self, symbol):
        positions = mt5.positions_get(symbol=symbol)
        if positions:
            for p in positions:
                if p.magic == self.bot_id:
                    return p
        return None

    def _auto_close(self, pos):
        duration = datetime.now() - datetime.fromtimestamp(pos.time)
        if duration.total_seconds() > 7200:
            if close_trade(pos):
                log_trade_action(self.bot_id, "AUTO-CUT", f"Durasi lebih dari 2 jam: {duration}")
        elif pos.profit >= 100:
            if close_trade(pos):
                log_trade_action(self.bot_id, "AUTO-TP", f"Profit: {pos.profit:.2f}")
        elif pos.profit <= -50:
            if close_trade(pos):
                log_trade_action(self.bot_id, "AUTO-SL", f"Loss: {pos.profit:.2f}")

    def _execute_strategy(self):
        symbol = self.market.replace('/', '')
        tf = self.tf_map.get(self.timeframe, mt5.TIMEFRAME_H1)
        pos = self._get_open_position(symbol)

        # --- Modular strategy handler ---
        signal = 'HOLD'

        if self.strategy == 'MA_CROSSOVER':
            df = get_rates(symbol, tf, 100)
            signal = analyze(df)
        elif self.strategy == 'RSI_BREAKOUT':
            df = get_rates(symbol, tf, 100)
            signal = analyze(df)
        elif self.strategy == 'PULSE_SYNC':
            df = get_rates(symbol, tf, 100)
            signal = analyze(df)
        elif self.strategy == 'MERCY_EDGE':
            signal = analyze(self)

        if signal == 'BUY':
            if pos and pos.type == mt5.ORDER_TYPE_SELL:
                close_trade(pos)
                log_trade_action(self.bot_id, "CLOSE SELL", "Switch ke BUY")
            if not pos or pos.type == mt5.ORDER_TYPE_SELL:
                place_trade(symbol, mt5.ORDER_TYPE_BUY, self.lot_size, self.sl_pips, self.tp_pips, self.bot_id)
                log_trade_action(self.bot_id, "OPEN BUY", f"{self.strategy}")
        elif signal == 'SELL':
            if pos and pos.type == mt5.ORDER_TYPE_BUY:
                close_trade(pos)
                log_trade_action(self.bot_id, "CLOSE BUY", "Switch ke SELL")
            if not pos or pos.type == mt5.ORDER_TYPE_BUY:
                place_trade(symbol, mt5.ORDER_TYPE_SELL, self.lot_size, self.sl_pips, self.tp_pips, self.bot_id)
                log_trade_action(self.bot_id, "OPEN SELL", f"{self.strategy}")
        else:
            print(f"[{self.name}] Tidak ada sinyal. HOLD...")

        # --- Auto Close Check ---
        if pos:
            self._auto_close(pos)

    def _run_logic(self):
        log_trade_action(self.bot_id, "START", f"Bot {self.name} aktif dengan strategi {self.strategy}")
        try:
            while self.status == 'Aktif' and not self._stop_event.is_set():
                self._execute_strategy()
                time.sleep(self.check_interval)
        except Exception as e:
            log_trade_action(self.bot_id, "ERROR", str(e))
        finally:
            log_trade_action(self.bot_id, "STOP", "Bot dihentikan.")

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
