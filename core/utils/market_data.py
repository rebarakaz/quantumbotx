# core/utils/market_data.py

import logging
from core.factory.broker_factory import BrokerFactory
import pandas as pd

logger = logging.getLogger(__name__)

def get_market_rates(symbol: str, timeframe: str, count: int = 100) -> pd.DataFrame:
    """
    Fetch market rates (OHLCV) from the active broker.
    Broker-agnostic wrapper.
    """
    try:
        broker = BrokerFactory.get_broker()
        if not broker:
            logger.error("No active broker found.")
            return pd.DataFrame()
            
        return broker.get_rates(symbol, timeframe, count)
    except Exception as e:
        logger.error(f"Error fetching market rates for {symbol}: {e}")
        return pd.DataFrame()

def get_symbol_info(symbol: str):
    """
    Fetch symbol information from the active broker.
    """
    try:
        broker = BrokerFactory.get_broker()
        if not broker:
            return None
        return broker.get_symbol_info(symbol)
    except Exception as e:
        logger.error(f"Error fetching symbol info for {symbol}: {e}")
        return None

def get_account_info():
    """
    Fetch account info (balance, equity, etc.) from the active broker.
    """
    try:
        broker = BrokerFactory.get_broker()
        if not broker:
            return None
        return broker.get_account_info()
    except Exception as e:
        logger.error(f"Error fetching account info: {e}")
        return None

def get_open_positions():
    """
    Fetch open positions from the active broker.
    """
    try:
        broker = BrokerFactory.get_broker()
        if not broker:
            return []
        return broker.get_open_positions()
    except Exception as e:
        logger.error(f"Error fetching open positions: {e}")
        return []

def get_todays_profit() -> float:
    """
    Fetch today's profit from the active broker.
    """
    try:
        broker = BrokerFactory.get_broker()
        if not broker:
            return 0.0
        return broker.get_todays_profit()
    except Exception as e:
        logger.error(f"Error fetching today's profit: {e}")
        return 0.0
