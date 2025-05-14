from flask import Flask, render_template, send_from_directory, jsonify, request
import logging as log
import time
import json
import os
log.basicConfig(level=log.INFO)

from src.Bluetooth.BluetoothMockSimulator import BluetoothMockSimulator
from src.Bluetooth.BluetoothSimulatorESP32 import BluetoothSimulatorESP32

import argparse

obd_client = None

# Global variables for distance tracking
last_request_time = None
total_distance = 0.0

# Configuration management
CONFIG_PATH = 'config/fatigue_triggers.json'

def load_config():
    """Load configuration from file"""
    try:
        if not os.path.exists(CONFIG_PATH):
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            # Create default config
            default_config = {
                "speed_threshold": 120,
                "distance_threshold": 200,
                "time_threshold": 7200,
                "fatigue_threshold": 2
            }
            with open(CONFIG_PATH, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config
        
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            # Ensure all required fields exist
            required_fields = ['speed_threshold', 'distance_threshold', 'time_threshold', 'fatigue_threshold']
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Missing required field: {field}")
            return config
    except Exception as e:
        log.error(f"Error loading config: {e}")
        return None

def save_config(config):
    """Save configuration to file"""
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        log.error(f"Error saving config: {e}")
        return False

# Load initial configuration
current_config = load_config()

def calculate_distance_increment(speed_kmh, elapsed_seconds):
    """Calculate distance increment based on speed and elapsed time"""
    # Distance = speed (km/h) * time (h)
    # Convert seconds to hours: seconds / 3600
    return (speed_kmh * elapsed_seconds) / 3600

# Parse arguments
parser = argparse.ArgumentParser(description='OBD-II Simulator')
parser.add_argument('--obd', choices=['mock', 'esp32'], default='mock', help='Select the OBD-II type (mock or esp32)')
parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
parser.add_argument('--debug', action='store_true', help='Enable debug mode')
parser.add_argument('--host', default='127.0.0.1', help='Host to run the server on')
args = parser.parse_args()

app = Flask(__name__, 
    static_folder='static',  # explicitly set static folder
    template_folder='templates'  # explicitly set template folder
)

# Enable CORS for debugging
@app.after_request
def after_request(response):
    # Allow access from any origin when debugging
    if args.debug:
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Enable source maps
@app.route('/static/js/<path:filename>.map')
def serve_source_map(filename):
    return send_from_directory('static/js', f'{filename}.map')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/config')
def config():
    return render_template('config.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    global current_config
    if current_config is None:
        current_config = load_config()
    return jsonify(current_config)

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    global current_config
    try:
        new_config = request.get_json()
        if not new_config:
            return jsonify({'error': 'No data provided'}), 400

        # Load current config to preserve non-updated values
        if current_config is None:
            current_config = load_config()
        if current_config is None:
            return jsonify({'error': 'Failed to load current configuration'}), 500

        # Create updated config starting with current values
        updated_config = current_config.copy()

        # Validate and update only provided fields
        valid_fields = {
            'speed_threshold': {'type': int, 'min': 0, 'max': None},
            'distance_threshold': {'type': int, 'min': 0, 'max': None},
            'time_threshold': {'type': int, 'min': 0, 'max': None},
            'fatigue_threshold': {'type': int, 'min': 0, 'max': 2}
        }

        for field, value in new_config.items():
            # Skip unknown fields
            if field not in valid_fields:
                continue

            # Validate field type
            field_type = valid_fields[field]['type']
            if not isinstance(value, field_type):
                return jsonify({'error': f"Invalid type for {field}. Expected {field_type.__name__}"}), 400

            # Validate field value
            if valid_fields[field]['min'] is not None and value < valid_fields[field]['min']:
                return jsonify({'error': f"{field} must be greater than or equal to {valid_fields[field]['min']}"}), 400
            if valid_fields[field]['max'] is not None and value > valid_fields[field]['max']:
                return jsonify({'error': f"{field} must be less than or equal to {valid_fields[field]['max']}"}), 400

            # Update the field
            updated_config[field] = value

        # Save configuration
        if save_config(updated_config):
            current_config = updated_config
            return jsonify({'status': 'ok', 'config': current_config})
        else:
            return jsonify({'error': 'Failed to save configuration'}), 500

    except Exception as e:
        log.error(f"Error updating config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/obd/data')
async def obd_data():
    global obd_client, last_request_time, total_distance, current_config
    
    if obd_client == None:
        return jsonify({'error': 'Client not initialized'}), 500
    
    current_time = time.time()
    data = await obd_client.request_all_settings()
    ret_dict = data.to_dict()
    
    # Calculate distance increment if we have a previous request
    if last_request_time is not None:
        elapsed_seconds = current_time - last_request_time
        distance_increment = calculate_distance_increment(ret_dict['speed'], elapsed_seconds)
        total_distance += distance_increment
        log.debug(f"Added distance: {distance_increment:.2f} km (speed: {ret_dict['speed']} km/h, time: {elapsed_seconds:.2f}s)")
    
    last_request_time = current_time
    
    # Add accumulated distance and fatigue data to response
    ret_dict['accumulated_distance'] = round(total_distance, 1)
    ret_dict['fatigue_level'] = None  # TODO: Implement camera client (0=Not tired, 1=Lightly tired, 2=Heavily tired)
    
    # Add worried triggers status
    if current_config:
        ret_dict['worried_triggers'] = {
            'speed_exceeded': ret_dict['speed'] > current_config['speed_threshold'],
            'distance_exceeded': total_distance > current_config['distance_threshold'],
            'time_exceeded': ret_dict['runtime'] > current_config['time_threshold'],
            'fatigue_exceeded': ret_dict['fatigue_level'] is not None and ret_dict['fatigue_level'] >= current_config['fatigue_threshold']
        }
    
    return jsonify(ret_dict)

@app.route('/api/reset_distance', methods=['POST'])
def reset_distance():
    """Reset the accumulated distance"""
    global last_request_time, total_distance
    last_request_time = None
    total_distance = 0.0
    return jsonify({'status': 'ok', 'distance': total_distance})

async def main():
    global obd_client, last_request_time, total_distance
    if obd_client == None:
        log.info(f"Starting server in {args.obd} mode on {args.host}:{args.port}")
        if args.obd == 'mock':
            obd_client = BluetoothMockSimulator()
        elif args.obd == 'esp32':
            obd_client = BluetoothSimulatorESP32()
            
        if not obd_client:
            log.error("Failed to create client")
            exit(1)
        
        if not await obd_client.find_device():
            log.error("Failed to find device")
            exit(1)
        
        if not await obd_client.connect():
            log.error("Failed to connect to device")
            exit(1)
        
        if not await obd_client.init_communication():
            log.error("Failed to initialize communication")
            exit(1)
            
    # Reset distance tracking
    last_request_time = None
    total_distance = 0.0
            
    # CAMERA CLIENT INITIALIZATION
    
    app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=args.debug)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())