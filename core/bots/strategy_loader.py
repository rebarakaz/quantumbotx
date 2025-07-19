import importlib

def load_strategy(strategy_name):
    """
    Load class strategi berdasarkan nama (string).
    Contoh: "MA_CROSSOVER" => core.bots.ma_crossover.MACrossoverStrategy
    """
    strategy_map = {
        'MA_CROSSOVER': ('ma_crossover', 'MACrossoverStrategy'),
        'RSI_BREAKOUT': ('rsi_breakout', 'RSIBreakoutStrategy'),
        'PULSE_SYNC': ('pulse_sync', 'PulseSyncStrategy')
    }

    if strategy_name not in strategy_map:
        raise ValueError(f"Strategi '{strategy_name}' tidak dikenali.")

    module_name, class_name = strategy_map[strategy_name]
    module = importlib.import_module(f"core.bots.{module_name}")
    strategy_class = getattr(module, class_name)
    return strategy_class
