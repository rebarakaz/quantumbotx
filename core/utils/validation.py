# core/utils/validation.py

def validate_bot_params(data):
    required_fields = ['name', 'market', 'lot_size', 'sl_pips', 'tp_pips', 'timeframe', 'check_interval_seconds', 'strategy']
    errors = []

    for field in required_fields:
        if field not in data:
            errors.append(f"Field '{field}' is required.")

    if not isinstance(data.get('lot_size'), (int, float)) or data['lot_size'] <= 0:
        errors.append("Lot size must be a positive number.")

    if not isinstance(data.get('sl_pips'), int) or data['sl_pips'] <= 0:
        errors.append("SL (Stop Loss) must be a positive integer.")

    if not isinstance(data.get('tp_pips'), int) or data['tp_pips'] <= 0:
        errors.append("TP (Take Profit) must be a positive integer.")

    return errors
