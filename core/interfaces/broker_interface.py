from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime

class BrokerInterface(ABC):
    """
    Abstract Base Class for all broker adapters.
    This defines the universal contract that the bot uses to interact with any broker.
    """

    @abstractmethod
    def initialize(self, credentials: Dict[str, Any]) -> bool:
        """
        Initialize connection to the broker.
        """
        pass

    @abstractmethod
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Get account balance, equity, and other info.
        """
        pass

    @abstractmethod
    def get_rates(self, symbol: str, timeframe: str, count: int = 100) -> pd.DataFrame:
        """
        Get historical price data as a DataFrame.
        DataFrame must have index 'time' and columns: open, high, low, close, tick_volume.
        """
        pass

    @abstractmethod
    def get_open_positions(self) -> List[Dict[str, Any]]:
        """
        Get list of currently open positions.
        """
        pass

    @abstractmethod
    def place_order(self, symbol: str, order_type: str, volume: float, price: float = 0.0, sl: float = 0.0, tp: float = 0.0, comment: str = "") -> bool:
        """
        Place a trade order.
        order_type: 'BUY' or 'SELL' (or 'BUY_LIMIT', etc.)
        """
        pass

    @abstractmethod
    def close_position(self, position_id: str, volume: float = 0.0) -> bool:
        """
        Close an existing position.
        """
        pass

    @abstractmethod
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get specifications for a symbol (min lot, max lot, tick size, etc.)
        """
        pass

    @abstractmethod
    def get_todays_profit(self) -> float:
        """
        Calculate total profit for trades closed today.
        """
        pass
