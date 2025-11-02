#!/usr/bin/env python3
"""
MT5 Bridge Service
Receives trading signals from n8n and executes trades in MetaTrader 5
"""

import os
import logging
import time
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import json
import threading

# Try to import MetaTrader5 - it may not be available in container
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    logging.warning("MetaTrader5 package not available. Make sure MT5 is running on the host system.")
    mt5 = None

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mt5_bridge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class MT5Bridge:
    def __init__(self):
        self.mt5_initialized = False
        self.login = os.getenv('MT5_LOGIN')
        self.password = os.getenv('MT5_PASSWORD')
        self.server = os.getenv('MT5_SERVER')
        self.mt5_path = os.getenv('MT5_PATH', '/opt/mt5')

        # Trading parameters
        self.symbol = os.getenv('TRADING_SYMBOL', 'EURUSD')
        self.lot_size = float(os.getenv('LOT_SIZE', '0.01'))
        self.magic_number = int(os.getenv('MAGIC_NUMBER', '123456'))

        # Initialize MT5 connection
        self.initialize_mt5()

    def initialize_mt5(self):
        """Initialize MT5 connection"""
        if not MT5_AVAILABLE:
            logger.warning("MetaTrader5 package not available in container. "
                          "Make sure MT5 terminal is running on the host system with API access enabled.")
            # For now, we'll assume MT5 is running and available via network
            # In production, you might want to implement a TCP/IP connection to host MT5
            self.mt5_initialized = False
            return False

        try:
            # Initialize MT5
            if not mt5.initialize(path=self.mt5_path):
                logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False

            # Login to account
            if not mt5.login(self.login, self.password, self.server):
                logger.error(f"MT5 login failed: {mt5.last_error()}")
                return False

            logger.info(f"MT5 initialized successfully. Account: {mt5.account_info().login}")
            self.mt5_initialized = True
            return True

        except Exception as e:
            logger.error(f"Error initializing MT5: {str(e)}")
            return False

    def get_account_info(self):
        """Get account information"""
        if not self.mt5_initialized:
            return None

        try:
            account = mt5.account_info()
            if account:
                return {
                    'login': account.login,
                    'balance': account.balance,
                    'equity': account.equity,
                    'margin': account.margin,
                    'margin_free': account.margin_free,
                    'profit': account.profit
                }
            return None
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return None

    def get_symbol_info(self, symbol):
        """Get symbol information"""
        if not self.mt5_initialized:
            return None

        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                return {
                    'symbol': symbol_info.name,
                    'bid': symbol_info.bid,
                    'ask': symbol_info.ask,
                    'spread': symbol_info.spread,
                    'volume_min': symbol_info.volume_min,
                    'volume_max': symbol_info.volume_max,
                    'point': symbol_info.point,
                    'digits': symbol_info.digits
                }
            return None
        except Exception as e:
            logger.error(f"Error getting symbol info: {str(e)}")
            return None

    def open_position(self, direction, symbol, lot_size, sl_price=None, tp_price=None, comment=""):
        """Open a trading position"""
        if not self.mt5_initialized:
            return {'success': False, 'error': 'MT5 not initialized'}

        try:
            # Get current prices
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                return {'success': False, 'error': f'Symbol {symbol} not found'}

            # Select symbol
            if not mt5.symbol_select(symbol, True):
                return {'success': False, 'error': f'Failed to select symbol {symbol}'}

            # Determine order type
            if direction.upper() == 'BUY':
                order_type = mt5.ORDER_TYPE_BUY
                price = symbol_info.ask
            elif direction.upper() == 'SELL':
                order_type = mt5.ORDER_TYPE_SELL
                price = symbol_info.bid
            else:
                return {'success': False, 'error': 'Invalid direction. Use BUY or SELL'}

            # Prepare order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "sl": sl_price,
                "tp": tp_price,
                "deviation": 10,
                "magic": self.magic_number,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            # Send order
            result = mt5.order_send(request)

            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"Position opened successfully: {direction} {symbol} {lot_size} lots")
                return {
                    'success': True,
                    'ticket': result.order,
                    'price': result.price,
                    'volume': result.volume
                }
            else:
                error_msg = f"Order failed: {result.retcode} - {mt5.last_error()}"
                logger.error(error_msg)
                return {'success': False, 'error': error_msg}

        except Exception as e:
            error_msg = f"Error opening position: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}

    def close_position(self, ticket, symbol, lot_size=None):
        """Close a trading position"""
        if not self.mt5_initialized:
            return {'success': False, 'error': 'MT5 not initialized'}

        try:
            # Get position info
            position = mt5.positions_get(ticket=ticket)
            if not position:
                return {'success': False, 'error': f'Position {ticket} not found'}

            position = position[0]

            # Determine close type
            if position.type == mt5.POSITION_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info(symbol).bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info(symbol).ask

            # Use position volume if not specified
            if lot_size is None:
                lot_size = position.volume

            # Prepare close request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "position": ticket,
                "price": price,
                "deviation": 10,
                "magic": self.magic_number,
                "comment": "Close position",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            # Send order
            result = mt5.order_send(request)

            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"Position closed successfully: {ticket}")
                return {'success': True, 'ticket': result.order}
            else:
                error_msg = f"Close order failed: {result.retcode} - {mt5.last_error()}"
                logger.error(error_msg)
                return {'success': False, 'error': error_msg}

        except Exception as e:
            error_msg = f"Error closing position: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}

    def get_positions(self, symbol=None):
        """Get current positions"""
        if not self.mt5_initialized:
            return []

        try:
            if symbol:
                positions = mt5.positions_get(symbol=symbol)
            else:
                positions = mt5.positions_get()

            if positions:
                return [{
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == mt5.POSITION_TYPE_BUY else 'SELL',
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'price_current': pos.price_current,
                    'profit': pos.profit,
                    'sl': pos.sl,
                    'tp': pos.tp
                } for pos in positions]
            return []

        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
            return []

# Global MT5 bridge instance
mt5_bridge = MT5Bridge()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    account_info = mt5_bridge.get_account_info()
    if account_info:
        return jsonify({
            'status': 'healthy',
            'mt5_connected': mt5_bridge.mt5_initialized,
            'account': account_info
        }), 200
    else:
        return jsonify({
            'status': 'unhealthy',
            'mt5_connected': mt5_bridge.mt5_initialized,
            'error': 'MT5 connection failed'
        }), 503

@app.route('/webhook/tradingview', methods=['POST'])
def tradingview_webhook():
    """Receive trading signals from TradingView via n8n"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400

        logger.info(f"Received TradingView signal: {json.dumps(data)}")

        # Extract signal data
        signal = data.get('signal', '').upper()
        symbol = data.get('symbol', mt5_bridge.symbol).upper()
        lot_size = float(data.get('lot_size', mt5_bridge.lot_size))
        sl_percent = float(data.get('sl_percent', 1.0))
        tp_percent = float(data.get('tp_percent', 2.0))

        # Validate signal
        if signal not in ['BUY', 'SELL', 'CLOSE']:
            return jsonify({'success': False, 'error': 'Invalid signal. Use BUY, SELL, or CLOSE'}), 400

        # Execute signal
        if signal in ['BUY', 'SELL']:
            # Calculate SL and TP prices
            symbol_info = mt5_bridge.get_symbol_info(symbol)
            if not symbol_info:
                return jsonify({'success': False, 'error': f'Symbol {symbol} not available'}), 400

            current_price = symbol_info['ask'] if signal == 'BUY' else symbol_info['bid']
            point = symbol_info['point']

            if signal == 'BUY':
                sl_price = current_price * (1 - sl_percent / 100)
                tp_price = current_price * (1 + tp_percent / 100)
            else:
                sl_price = current_price * (1 + sl_percent / 100)
                tp_price = current_price * (1 - tp_percent / 100)

            # Open position
            result = mt5_bridge.open_position(
                direction=signal,
                symbol=symbol,
                lot_size=lot_size,
                sl_price=round(sl_price, symbol_info['digits']),
                tp_price=round(tp_price, symbol_info['digits']),
                comment=f"TV-{signal}"
            )

        elif signal == 'CLOSE':
            # Close all positions for the symbol
            positions = mt5_bridge.get_positions(symbol)
            closed_positions = []

            for pos in positions:
                if pos['type'].upper() == 'BUY':
                    close_signal = 'SELL'
                else:
                    close_signal = 'BUY'

                close_result = mt5_bridge.close_position(
                    ticket=pos['ticket'],
                    symbol=symbol,
                    lot_size=pos['volume']
                )

                if close_result['success']:
                    closed_positions.append(pos['ticket'])

            result = {
                'success': True,
                'message': f'Closed {len(closed_positions)} positions',
                'closed_tickets': closed_positions
            }

        return jsonify(result), 200 if result['success'] else 500

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/positions', methods=['GET'])
def get_positions():
    """Get current positions"""
    symbol = request.args.get('symbol')
    positions = mt5_bridge.get_positions(symbol)
    return jsonify({'positions': positions}), 200

@app.route('/account', methods=['GET'])
def get_account():
    """Get account information"""
    account_info = mt5_bridge.get_account_info()
    if account_info:
        return jsonify(account_info), 200
    else:
        return jsonify({'error': 'Failed to get account info'}), 500

@app.route('/symbol/<symbol>', methods=['GET'])
def get_symbol(symbol):
    """Get symbol information"""
    symbol_info = mt5_bridge.get_symbol_info(symbol.upper())
    if symbol_info:
        return jsonify(symbol_info), 200
    else:
        return jsonify({'error': f'Symbol {symbol} not found'}), 404

if __name__ == '__main__':
    port = int(os.getenv('BRIDGE_PORT', 5000))
    logger.info(f"Starting MT5 Bridge Service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
