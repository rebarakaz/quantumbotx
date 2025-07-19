import MetaTrader5 as mt5

def get_stock_symbols():
    """
    Mengambil semua simbol saham dari MT5 dan mengembalikannya sebagai list of dicts.
    """
    try:
        if not mt5.terminal_info():
            if not mt5.initialize():
                print("initialize() failed, error code =", mt5.last_error())
                return []

        symbols = mt5.symbols_get()
        stock_list = []
        if symbols:
            for s in symbols:
                if "stocks" in s.path.lower() or "shares" in s.path.lower():
                    stock_list.append({
                        "name": s.name,
                        "description": s.description,
                        "path": s.path,
                        "ask": s.ask,
                        "bid": s.bid,
                        "spread": s.spread,
                        "digits": s.digits
                    })
        return stock_list
    except Exception as e:
        print(f"Error getting stock symbols: {e}")
        return []

def get_forex_symbols():
    """
    Mengambil semua simbol forex dari MT5 dan mengembalikannya sebagai list of dicts.
    """
    try:
        if not mt5.terminal_info():
            if not mt5.initialize():
                print("initialize() failed, error code =", mt5.last_error())
                return []

        symbols = mt5.symbols_get(group="*\\Forex*")
        if not symbols:
            symbols = mt5.symbols_get()

        forex_list = []
        if symbols:
            for s in symbols:
                if "forex" in s.path.lower():
                    forex_list.append({
                        "name": s.name,
                        "description": s.description,
                        "path": s.path,
                        "ask": s.ask,
                        "bid": s.bid,
                        "spread": s.spread,
                        "digits": s.digits,
                        "volume_min": s.volume_min,
                        "volume_max": s.volume_max
                    })
        return forex_list
    except Exception as e:
        print(f"Error getting forex symbols: {e}")
        return []
