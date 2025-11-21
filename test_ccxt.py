import logging
from core.factory.broker_factory import BrokerFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestCCXT")

def test_ccxt():
    logger.info("1. Requesting CCXT adapter from Factory...")
    try:
        broker = BrokerFactory.get_broker('CCXT')
        logger.info("   Success: Got CCXTAdapter instance.")
    except Exception as e:
        logger.error(f"   Failed: {e}")
        return

    logger.info("2. Initializing connection (Binance Public)...")
    # No keys needed for public data
    creds = {
        'EXCHANGE_ID': 'binance',
        'API_KEY': '',
        'API_SECRET': ''
    }
    if broker.initialize(creds):
        logger.info("   Success: Connected to Binance.")
    else:
        logger.error("   Failed: Could not connect.")
        return

    logger.info("3. Fetching Rates for BTC/USDT...")
    try:
        df = broker.get_rates('BTC/USDT', 'H1', 10)
        if not df.empty:
            logger.info(f"   Success: Fetched {len(df)} rows.")
            print(df.head())
        else:
            logger.error("   Failed: DataFrame is empty.")
    except Exception as e:
        logger.error(f"   Failed: {e}")

    logger.info("4. Getting Symbol Info...")
    info = broker.get_symbol_info('BTC/USDT')
    if info:
        logger.info(f"   Success: {info}")
    else:
        logger.error("   Failed: Could not get symbol info.")

if __name__ == "__main__":
    test_ccxt()
