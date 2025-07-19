from core.strategies.logic_ma import run_ma_crossover
from core.strategies.logic_rsi import run_rsi_breakout
from core.strategies.logic_mercy import run_full_mercy

STRATEGY_FUNCTIONS = {
    'MA_CROSSOVER': run_ma_crossover,
    'RSI_BREAKOUT': run_rsi_breakout,
    'FULL_MERCY': run_full_mercy
}
