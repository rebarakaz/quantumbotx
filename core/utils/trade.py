import MetaTrader5 as mt5

def place_trade(symbol, trade_type, lot, sl_pips, tp_pips, magic_number):
    """Buka order trading (BUY/SELL)."""
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"[ERROR] Info simbol {symbol} tidak ditemukan")
        return None

    allowed_filling_modes = symbol_info.filling_modes
    filling_type = (
        mt5.ORDER_FILLING_FOK if mt5.ORDER_FILLING_FOK in allowed_filling_modes
        else mt5.ORDER_FILLING_IOC if mt5.ORDER_FILLING_IOC in allowed_filling_modes
        else allowed_filling_modes[0]
    )

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
        "comment": "Trade by QuantumBotX",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_type,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"[ERROR] Gagal buka order: {result.comment}")
        return None

    print(f"[TRADE] Order berhasil - Ticket #{result.order}")
    return result


def close_trade(position):
    """Menutup posisi terbuka (BUY/SELL) berdasarkan tiket."""
    trade_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
    price = mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask

    close_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": trade_type,
        "position": position.ticket,
        "price": price,
        "magic": position.magic,
        "comment": "Closed by QuantumBotX",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    result = mt5.order_send(close_request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"[ERROR] Gagal tutup posisi #{position.ticket}: {result.comment}")
        return False

    print(f"[TRADE] Posisi #{position.ticket} berhasil ditutup.")
    return True
