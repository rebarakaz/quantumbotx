import sys
import os
sys.path.append(os.getcwd())

try:
    from core.strategies.strategy_map import STRATEGY_MAP
    print("Successfully imported STRATEGY_MAP")
    
    if 'INDEX_MOMENTUM' in STRATEGY_MAP:
        print("INDEX_MOMENTUM found in STRATEGY_MAP")
        strategy_class = STRATEGY_MAP['INDEX_MOMENTUM']
        print(f"Strategy class: {strategy_class.__name__}")
    else:
        print("INDEX_MOMENTUM NOT found in STRATEGY_MAP")
        exit(1)
        
except Exception as e:
    print(f"Error: {e}")
    exit(1)
