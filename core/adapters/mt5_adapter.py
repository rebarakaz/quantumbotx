from core.interfaces.broker_interface import BrokerInterface
import logging
from datetime import datetime
import pandas as pd
from typing import Dict, Any, List, Optional

try:
    from core.utils.mt5 import (
        initialize_mt5, 
        shutdown_mt5, 
        get_symbol_info, 
        get_rates as get_rates_mt5,
        place_trade,
        close_trade,
        get_open_positions,
        get_account_info_mt5,
        get_open_positions_mt5,
        find_mt5_symbol,
        TIMEFRAME_MAP,
        get_todays_profit_mt5
    )
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    logging.warning("MetaTrader5 module not found. MT5Adapter will not work.")

logger = logging.getLogger(__name__)

class MT5Adapter(BrokerInterface):
    """
    Adapter for MetaTrader 5 using the official python library.
    Wraps the functions from core.utils.mt5.
    """

    def initialize(self, credentials: Dict[str, Any]) -> bool:
        # MT5 usually initialized via run.py, but we can support re-init here
        return True

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        return get_account_info_mt5()

    def get_rates(self, symbol: str, timeframe: str, count: int = 100) -> pd.DataFrame:
        # Convert string timeframe (e.g. "H1") to MT5 constant
        mt5_timeframe = TIMEFRAME_MAP.get(timeframe, mt5.TIMEFRAME_H1)
        
        # Ensure symbol is valid for this broker
        valid_symbol = find_mt5_symbol(symbol)
        if not valid_symbol:
            logger.error(f"Symbol {symbol} not found in MT5")
            return pd.DataFrame()
            
        return get_rates_mt5(valid_symbol, mt5_timeframe, count)

    def get_open_positions(self) -> List[Dict[str, Any]]:
        return get_open_positions_mt5()

    def place_order(self, symbol: str, order_type: str, volume: float, price: float = 0.0, sl: float = 0.0, tp: float = 0.0, comment: str = "") -> bool:
        valid_symbol = find_mt5_symbol(symbol)
        if not valid_symbol:
            return False

        # Basic order logic - simplified for adapter POC
        action = mt5.TRADE_ACTION_DEAL
        type_op = mt5.ORDER_TYPE_BUY if order_type == 'BUY' else mt5.ORDER_TYPE_SELL
        
        request = {
            "action": action,
            "symbol": valid_symbol,
            "volume": volume,
            "type": type_op,
            "price": mt5.symbol_info_tick(valid_symbol).ask if order_type == 'BUY' else mt5.symbol_info_tick(valid_symbol).bid,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 123456,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order failed: {result.comment}")
            return False
            
        logger.info(f"Order placed: {result.order}")
        return True

    def close_position(self, position_id: str, volume: float = 0.0) -> bool:
        try:
            # Logic to close position...
            # For now, returning False as placeholder
            pass
        except:
            pass
        return False

    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        valid_symbol = find_mt5_symbol(symbol)
        if not valid_symbol:
            return None
        info = mt5.symbol_info(valid_symbol)
        if info:
            return info._asdict()
        return None

    def get_todays_profit(self) -> float:
        return get_todays_profit_mt5()
