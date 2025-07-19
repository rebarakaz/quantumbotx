import locale
import MetaTrader5 as mt5

locale.setlocale(locale.LC_NUMERIC, 'C')

def parse_decimal(val):
    try:
        return float(str(val).replace(',', '.'))
    except Exception:
        return 0.0

def initialize_mt5(account, password, server):
    if not mt5.initialize():
        print("Gagal inisialisasi MT5!", mt5.last_error())
        return False

    if not mt5.login(account, password=password, server=server):
        print(f"Gagal login MT5 ke {server}, kode: {mt5.last_error()}")
        mt5.shutdown()
        return False

    print(f"Login sukses ke akun MT5: {account} @ {server}")
    return True
