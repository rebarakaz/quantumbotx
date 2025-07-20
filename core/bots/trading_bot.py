# core/bots/trading_bot.py - FIXED VERSION
import time
import threading
import sqlite3
import logging
from datetime import datetime
import MetaTrader5 as mt5
from core.db.models import log_trade_action
from core.mt5.trade import place_trade, close_trade
from core.strategies.ma_crossover import analyze as analyze_ma
from core.strategies.rsi_breakout import analyze as analyze_rsi
from core.strategies.pulse_sync import analyze as analyze_pulse
from core.strategies.mercy_edge import analyze as analyze_mercy
from core.data.fetch import get_rates

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self, bot_id, name, market, status='Dijeda', lot_size=0.01, 
                 sl_pips=100, tp_pips=200, timeframe='H1', strategy='MA_CROSSOVER', 
                 check_interval_seconds=60):
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
        """Get open position for this bot's magic number"""
        try:
            positions = mt5.positions_get(symbol=symbol)
            if positions:
                for p in positions:
                    if p.magic == self.bot_id:
                        return p
            return None
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return None

    def _auto_close(self, pos):
        """Auto close position based on rules"""
        try:
            duration = datetime.now() - datetime.fromtimestamp(pos.time)
            
            # Rule 1: Close after 2 hours
            if duration.total_seconds() > 7200:
                if close_trade(pos):
                    log_trade_action(self.bot_id, "AUTO-CUT", f"Duration > 2h: {duration}")
                    return True
            
            # Rule 2: Take profit at +$100
            elif pos.profit >= 100:
                if close_trade(pos):
                    log_trade_action(self.bot_id, "AUTO-TP", f"Profit: {pos.profit:.2f}")
                    return True
            
            # Rule 3: Stop loss at -$50
            elif pos.profit <= -50:
                if close_trade(pos):
                    log_trade_action(self.bot_id, "AUTO-SL", f"Loss: {pos.profit:.2f}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in auto_close: {e}")
            return False

    def _execute_strategy(self):
        """Execute trading strategy - FIXED VERSION"""
        try:
            symbol = self.market.replace('/', '')
            tf = self.tf_map.get(self.timeframe, mt5.TIMEFRAME_H1)
            pos = self._get_open_position(symbol)

            # Get market data
            df = get_rates(symbol, tf, 100)
            if df is None or df.empty:
                logger.warning(f"No data available for {symbol}")
                return

            # ✅ FIXED: Call correct strategy functions
            signal = 'HOLD'
            
            try:
                if self.strategy == 'MA_CROSSOVER':
                    signal = analyze_ma(df)
                elif self.strategy == 'RSI_BREAKOUT':
                    signal = analyze_rsi(df)
                elif self.strategy == 'PULSE_SYNC':
                    signal = analyze_pulse(df)
                elif self.strategy == 'MERCY_EDGE':
                    signal = analyze_mercy(self)
                else:
                    logger.warning(f"Unknown strategy: {self.strategy}")
                    return
                    
            except Exception as e:
                logger.error(f"Strategy analysis error: {e}")
                return

            # Execute trades based on signal
            self._handle_trade_signal(signal, symbol, pos)
            
            # Auto close check
            if pos:
                self._auto_close(pos)
                
        except Exception as e:
            logger.error(f"Error in execute_strategy: {e}")
            log_trade_action(self.bot_id, "ERROR", str(e))

    def _handle_trade_signal(self, signal, symbol, pos):
        """Handle trade signals"""
        try:
            if signal == 'BUY':
                # Close opposite position first
                if pos and pos.type == mt5.ORDER_TYPE_SELL:
                    if close_trade(pos):
                        log_trade_action(self.bot_id, "CLOSE SELL", "Switch to BUY")
                        pos = None
                
                # Open new BUY if no position
                if not pos:
                    if place_trade(symbol, mt5.ORDER_TYPE_BUY, self.lot_size, 
                                 self.sl_pips, self.tp_pips, self.bot_id):
                        log_trade_action(self.bot_id, "OPEN BUY", f"Strategy: {self.strategy}")
                        
            elif signal == 'SELL':
                # Close opposite position first
                if pos and pos.type == mt5.ORDER_TYPE_BUY:
                    if close_trade(pos):
                        log_trade_action(self.bot_id, "CLOSE BUY", "Switch to SELL")
                        pos = None
                
                # Open new SELL if no position
                if not pos:
                    if place_trade(symbol, mt5.ORDER_TYPE_SELL, self.lot_size, 
                                 self.sl_pips, self.tp_pips, self.bot_id):
                        log_trade_action(self.bot_id, "OPEN SELL", f"Strategy: {self.strategy}")
            else:
                logger.info(f"[{self.name}] No signal. HOLD...")
                
        except Exception as e:
            logger.error(f"Error handling trade signal: {e}")

    def _run_logic(self):
        """Main bot loop"""
        log_trade_action(self.bot_id, "START", f"Bot {self.name} started with {self.strategy}")
        logger.info(f"Bot {self.name} started with strategy {self.strategy}")
        
        try:
            while self.status == 'Aktif' and not self._stop_event.is_set():
                self._execute_strategy()
                time.sleep(self.check_interval)
                
        except Exception as e:
            logger.error(f"Bot {self.name} error: {e}")
            log_trade_action(self.bot_id, "ERROR", str(e))
        finally:
            log_trade_action(self.bot_id, "STOP", "Bot stopped")
            logger.info(f"Bot {self.name} stopped")

    def start(self):
        """Start the trading bot"""
        if self.status != 'Aktif' and (self._thread is None or not self._thread.is_alive()):
            self.status = 'Aktif'
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_logic, daemon=True)
            self._thread.start()
            logger.info(f"Bot {self.name} started successfully")

    def stop(self):
        """Stop the trading bot"""
        if self.status == 'Aktif':
            self.status = 'Dijeda'
            self._stop_event.set()
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=5)  # Increased timeout
            self._thread = None
            logger.info(f"Bot {self.name} stopped successfully")