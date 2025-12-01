# core/routes/api_bots.py

import json
import logging
from flask import Blueprint, jsonify, request
from core.bots.controller import mulai_bot, hentikan_bot, ambil_semua_bot, shutdown_all_bots
from core.db import queries
from core.utils import market_data
from core.strategies.strategy_map import STRATEGY_MAP

api_bots = Blueprint('api_bots', __name__)
logger = logging.getLogger(__name__)

# --- CRUD Endpoints ---

@api_bots.route('/api/bots', methods=['GET'])
def get_bots():
    """Get all bots"""
    bots = queries.get_all_bots()
    # Parse strategy_params JSON string to dict for frontend
    for bot in bots:
        if isinstance(bot.get('strategy_params'), str):
            try:
                bot['strategy_params'] = json.loads(bot['strategy_params'])
            except:
                bot['strategy_params'] = {}
    return jsonify(bots)

@api_bots.route('/api/bots/<int:bot_id>', methods=['GET'])
def get_bot_detail(bot_id):
    """Get single bot details"""
    bot = queries.get_bot_by_id(bot_id)
    if not bot:
        return jsonify({"error": "Bot not found"}), 404
        
    # Parse strategy_params
    if isinstance(bot.get('strategy_params'), str):
        try:
            bot['strategy_params'] = json.loads(bot['strategy_params'])
        except:
            bot['strategy_params'] = {}
            
    return jsonify(bot)

@api_bots.route('/api/bots', methods=['POST'])
def create_bot():
    """Create a new bot"""
    data = request.json
    try:
        # Extract fields
        name = data.get('name')
        market = data.get('market')
        # Handle risk_percent mapping to lot_size if needed, or just use passed value
        lot_size = data.get('risk_percent', data.get('lot_size', 0.01))
        sl_pips = data.get('sl_atr_multiplier', data.get('sl_pips', 0))
        tp_pips = data.get('tp_atr_multiplier', data.get('tp_pips', 0))
        timeframe = data.get('timeframe', 'H1')
        interval = data.get('check_interval_seconds', 60)
        strategy = data.get('strategy')
        strategy_params = json.dumps(data.get('params', {}))
        enable_strategy_switching = 1 if data.get('enable_strategy_switching') else 0

        bot_id = queries.add_bot(
            name, market, lot_size, sl_pips, tp_pips, timeframe, interval, 
            strategy, strategy_params, enable_strategy_switching
        )
        
        if bot_id:
            return jsonify({"message": "Bot created successfully", "id": bot_id}), 201
        else:
            return jsonify({"error": "Failed to create bot"}), 500
    except Exception as e:
        logger.error(f"Error creating bot: {e}")
        return jsonify({"error": str(e)}), 500

@api_bots.route('/api/bots/<int:bot_id>', methods=['PUT'])
def update_bot_route(bot_id):
    """Update an existing bot"""
    data = request.json
    try:
        # Extract fields
        name = data.get('name')
        market = data.get('market')
        lot_size = data.get('risk_percent', data.get('lot_size'))
        sl_pips = data.get('sl_atr_multiplier', data.get('sl_pips'))
        tp_pips = data.get('tp_atr_multiplier', data.get('tp_pips'))
        timeframe = data.get('timeframe')
        interval = data.get('check_interval_seconds')
        strategy = data.get('strategy')
        strategy_params = json.dumps(data.get('params', {}))
        enable_strategy_switching = 1 if data.get('enable_strategy_switching') else 0

        success = queries.update_bot(
            bot_id, name, market, lot_size, sl_pips, tp_pips, timeframe, interval, 
            strategy, strategy_params, enable_strategy_switching
        )
        
        if success:
            return jsonify({"message": "Bot updated successfully"})
        else:
            return jsonify({"error": "Failed to update bot"}), 500
    except Exception as e:
        logger.error(f"Error updating bot: {e}")
        return jsonify({"error": str(e)}), 500

@api_bots.route('/api/bots/<int:bot_id>', methods=['DELETE'])
def delete_bot_route(bot_id):
    """Delete a bot"""
    try:
        # Stop bot first if running
        hentikan_bot(bot_id)
        
        success = queries.delete_bot(bot_id)
        if success:
            return jsonify({"message": "Bot deleted successfully"})
        else:
            return jsonify({"error": "Failed to delete bot"}), 500
    except Exception as e:
        logger.error(f"Error deleting bot: {e}")
        return jsonify({"error": str(e)}), 500

# --- Control Endpoints ---

@api_bots.route('/api/bots/<int:bot_id>/start', methods=['POST'])
@api_bots.route('/api/bots/start', methods=['POST']) # Legacy support
def start_bot(bot_id=None):
    if not bot_id:
        data = request.json
        bot_id = data.get('id')
    
    bot_data = queries.get_bot_by_id(bot_id)
    if not bot_data:
        return jsonify({"status": "error", "message": "Bot tidak ditemukan"}), 404

    success, message = mulai_bot(bot_id)
    if success:
        return jsonify({"status": "success", "message": message})
    else:
        return jsonify({"status": "error", "message": message}), 500

@api_bots.route('/api/bots/<int:bot_id>/stop', methods=['POST'])
@api_bots.route('/api/bots/stop', methods=['POST']) # Legacy support
def stop_bot_route(bot_id=None):
    if not bot_id:
        data = request.json
        bot_id = data.get('id')
    
    success, message = hentikan_bot(bot_id)
    if success:
        return jsonify({"status": "success", "message": message})
    else:
        return jsonify({"status": "error", "message": message}), 500

@api_bots.route('/api/bots/start_all', methods=['POST'])
def start_all_bots_route():
    # Logic to start all paused bots
    # This requires a controller function or loop here
    # For now, placeholder
    return jsonify({"message": "Not implemented yet"}), 501

@api_bots.route('/api/bots/stop_all', methods=['POST'])
def stop_all_bots_route():
    shutdown_all_bots()
    return jsonify({"message": "All bots stopped"})

# --- Detail & Analysis Endpoints ---

@api_bots.route('/api/bots/<int:bot_id>/history', methods=['GET'])
def get_bot_history(bot_id):
    """Get trade history for a bot"""
    history = queries.get_history_by_bot_id(bot_id)
    return jsonify(history)

@api_bots.route('/api/bots/<int:bot_id>/analysis', methods=['GET'])
def get_bot_analysis(bot_id):
    """Run strategy analysis for a bot and return result"""
    try:
        bot = queries.get_bot_by_id(bot_id)
        if not bot:
            return jsonify({"error": "Bot not found"}), 404
            
        symbol = bot['market']
        timeframe = bot['timeframe']
        strategy_name = bot['strategy']
        
        # Load Strategy
        strategy_class = STRATEGY_MAP.get(strategy_name)
        if not strategy_class:
            return jsonify({"error": "Strategy not found", "signal": "ERROR"}), 400
            
        # Fetch Data using Market Data Facade
        df = market_data.get_market_rates(symbol, timeframe, 100)
        if df is None or df.empty:
            return jsonify({"error": "No market data", "signal": "NO DATA"}), 404
            
        # Instantiate and Analyze
        strategy_params = {}
        if isinstance(bot.get('strategy_params'), str):
            try:
                strategy_params = json.loads(bot['strategy_params'])
            except:
                pass
        elif isinstance(bot.get('strategy_params'), dict):
            strategy_params = bot['strategy_params']
            
        strategy = strategy_class(symbol, timeframe, strategy_params)
        signal, explanation = strategy.analyze(df)
        
        # Return analysis result
        return jsonify({
            "signal": signal,
            "explanation": explanation,
            "price": df['close'].iloc[-1] if not df.empty else 0,
            "rsi": df['RSI'].iloc[-1] if 'RSI' in df.columns else None
        })
        
    except Exception as e:
        logger.error(f"Error in bot analysis: {e}")
        return jsonify({"error": str(e), "signal": "ERROR"}), 500