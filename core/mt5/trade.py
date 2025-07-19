import MetaTrader5 as mt5

def place_trade(symbol, trade_type, lot, sl_pips, tp_pips, magic_number):
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Gagal mendapatkan info untuk simbol {symbol}")
        return None

    allowed_filling_modes = symbol_info.filling_modes
    if mt5.ORDER_FILLING_FOK in allowed_filling_modes:
        filling_type = mt5.ORDER_FILLING_FOK
    elif mt5.ORDER_FILLING_IOC in allowed_filling_modes:
        filling_type = mt5.ORDER_FILLING_IOC
    else:
        filling_type = allowed_filling_modes[0]

    point = symbol_info.point
    price = mt5.symbol_info_tick(symbol).ask if trade_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": trade_type,
        "price": price,
        "sl": price - sl_pips * point if trade_type == mt5.ORDER_TYPE_BUY else price + sl_pips * point,
        "tp": price + tp_pips * point if trade_type == mt5.ORDER_TYPE_BUY else price - tp_pips * point,
        "magic": magic_number,
        "comment": "Trade dari Python Bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_type,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order gagal: {result.comment}")
        return None
    print(f"Order terkirim. Ticket: {result.order}")
    return result

def close_trade(position):
    trade_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
    price = mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": trade_type,
        "position": position.ticket,
        "price": price,
        "magic": position.magic,
        "comment": "Auto close dari Python Bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Gagal menutup posisi #{position.ticket}: {result.comment}")
        return False
    print(f"Posisi #{position.ticket} berhasil ditutup.")
    return True
