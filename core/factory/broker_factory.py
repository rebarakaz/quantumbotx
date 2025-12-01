from typing import Dict, Any, Optional
from core.interfaces.broker_interface import BrokerInterface
from core.adapters.ccxt_adapter import CCXTAdapter
import os

class BrokerFactory:
    """
    Factory class to create and return the appropriate broker adapter
    based on configuration.
    """
    _instances = {}
    
    @staticmethod
    def get_broker(broker_type=None, exchange_id=None):
        """
        Returns an instance of a broker adapter.
        
        Args:
            broker_type (str): The type of broker (e.g., 'MT5', 'BINANCE', 'OANDA').
            
        Returns:
            Optional[BrokerInterface]: An instance of the requested broker adapter, or None if not supported.
        """
        if not broker_type:
            broker_type = os.getenv("BROKER_TYPE", "MT5")

        # Create a unique key for caching
        cache_key = f"{broker_type}_{exchange_id}"
        
        if cache_key in BrokerFactory._instances:
            return BrokerFactory._instances[cache_key]

        if broker_type == "CCXT":
            exchange_id = exchange_id or os.getenv("EXCHANGE_ID")
            adapter = CCXTAdapter()
            # Initialize immediately with env credentials for convenience
            from dotenv import load_dotenv
            load_dotenv()
            creds = {
                'EXCHANGE_ID': exchange_id,
                'API_KEY': os.getenv('CCXT_API_KEY'),
                'API_SECRET': os.getenv('CCXT_API_SECRET'),
                'PASSWORD': os.getenv('CCXT_API_PASSWORD'),
                'TESTNET': os.getenv('CCXT_TESTNET', 'false').lower() == 'true'
            }
            adapter.initialize(creds)
            BrokerFactory._instances[cache_key] = adapter
            return adapter
            
        elif broker_type == "MT5":
            # Import MT5Adapter only when needed to avoid ImportError on Linux
            from core.adapters.mt5_adapter import MT5Adapter
            adapter = MT5Adapter()
            # MT5Adapter usually initializes itself or via run.py, but we can cache it
            BrokerFactory._instances[cache_key] = adapter
            return adapter
        else:
            raise ValueError(f"Unsupported broker type: {broker_type}")
