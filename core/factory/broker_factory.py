from typing import Dict, Any, Optional
from core.interfaces.broker_interface import BrokerInterface
from core.adapters.mt5_adapter import MT5Adapter
from core.adapters.ccxt_adapter import CCXTAdapter

class BrokerFactory:
    """
    Factory class to create and return the appropriate broker adapter
    based on configuration.
    """
    
    @staticmethod
    def get_broker(broker_type: str) -> Optional[BrokerInterface]:
        """
        Returns an instance of a broker adapter.
        
        Args:
            broker_type (str): The type of broker (e.g., 'MT5', 'BINANCE', 'OANDA').
            
        Returns:
            Optional[BrokerInterface]: An instance of the requested broker adapter, or None if not supported.
        """
        broker_type = broker_type.upper()
        
        if broker_type == 'MT5':
            return MT5Adapter()
        elif broker_type == 'CCXT' or broker_type in ['BINANCE', 'BYBIT', 'KUCOIN']:
            return CCXTAdapter()
        else:
            raise ValueError(f"Unknown broker type: {broker_type}")
