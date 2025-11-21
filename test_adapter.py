import os
import logging
from dotenv import load_dotenv
from core.factory.broker_factory import BrokerFactory

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestAdapter")

def main():
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    mt5_login = os.getenv('MT5_LOGIN')
    mt5_password = os.getenv('MT5_PASSWORD')
    mt5_server = os.getenv('MT5_SERVER')
    
    if not all([mt5_login, mt5_password, mt5_server]):
        logger.error("Missing MT5 credentials in .env file")
        return

    credentials = {
        'MT5_LOGIN': mt5_login,
        'MT5_PASSWORD': mt5_password,
        'MT5_SERVER': mt5_server
    }

    # 1. Use Factory to get Adapter
    logger.info("1. Requesting MT5 adapter from Factory...")
    broker = BrokerFactory.get_broker('MT5')
    
    if not broker:
        logger.error("Failed to get broker adapter!")
        return
        
    logger.info("   Success: Got MT5Adapter instance.")

    # 2. Initialize Connection
    logger.info("2. Initializing connection...")
    if broker.initialize(credentials):
        logger.info("   Success: Connected to MT5.")
    else:
        logger.error("   Failed: Could not connect to MT5.")
        return

    # 3. Get Account Info
    logger.info("3. Fetching account info...")
    info = broker.get_account_info()
    if info:
        logger.info(f"   Success: Balance = {info.get('balance')}, Equity = {info.get('equity')}")
    else:
        logger.error("   Failed: Could not fetch account info.")

    # 4. Get Rates (Test Data Fetching)
    symbol = "XAUUSD" # Or any symbol you know exists
    logger.info(f"4. Fetching rates for {symbol}...")
    rates = broker.get_rates(symbol, "H1", count=5)
    if not rates.empty:
        logger.info(f"   Success: Fetched {len(rates)} rows.")
        print(rates.head())
    else:
        logger.warning(f"   Warning: Could not fetch rates for {symbol} (Market might be closed or symbol wrong).")

    logger.info("Test Complete.")

if __name__ == "__main__":
    main()
