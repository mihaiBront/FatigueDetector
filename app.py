from flask import Flask, render_template, send_from_directory, jsonify, request
import logging as log
import time
import json
import os
import requests
import asyncio
import websockets
import base64
log.basicConfig(level=log.INFO)

from src.Bluetooth.BluetoothMockSimulator import BluetoothMockSimulator
from src.Bluetooth.BluetoothSimulatorESP32 import BluetoothSimulatorESP32

import argparse

obd_client = None

# Global variables for distance tracking
last_request_time = None
total_distance = 0.0

# Global variable for fatigue detection
fatigue_level = None
fatigue_data = None

# Global variables for fatigue counter system
fatigue_counter = 0
persistent_fatigue_active = False
fatigue_threshold = 3
last_fatigue_detection_time = 0
fatigue_grace_period = 5  # seconds to maintain counter after last detection

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
    ret_dict['fatigue_level'] = fatigue_level  # Use global fatigue level from camera detection
    ret_dict['fatigue_counter'] = fatigue_counter  # Add fatigue counter
    ret_dict['persistent_fatigue_active'] = persistent_fatigue_active  # Add persistent fatigue state
    
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

@app.route('/api/reset_fatigue', methods=['POST'])
def reset_fatigue():
    """Reset the persistent fatigue state"""
    global fatigue_counter, persistent_fatigue_active, fatigue_level
    fatigue_counter = 0
    persistent_fatigue_active = False
    fatigue_level = 0
    log.info("Fatigue state reset by user")
    return jsonify({'status': 'ok', 'fatigue_counter': fatigue_counter, 'persistent_fatigue_active': persistent_fatigue_active})

@app.route('/api/fatigue/data', methods=['POST'])
def update_fatigue_data():
    """Update fatigue data from frontend"""
    global fatigue_level, fatigue_data, fatigue_counter, persistent_fatigue_active, fatigue_threshold, last_fatigue_detection_time, fatigue_grace_period
    try:
        import time
        current_time = time.time()
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        fatigue_data = data
        # Determine fatigue level based on the data
        current_fatigue_level = determine_fatigue_level(data)
        
        # Fatigue counter logic with grace period
        if current_fatigue_level == 1:
            fatigue_counter += 1
            last_fatigue_detection_time = current_time
            log.info(f"Fatigue detected! Counter: {fatigue_counter}/{fatigue_threshold}")
            
            # Check if we've reached the threshold
            if fatigue_counter >= fatigue_threshold and not persistent_fatigue_active:
                persistent_fatigue_active = True
                log.info("PERSISTENT FATIGUE ACTIVATED - 3 detections reached!")
        elif current_fatigue_level == 0:
            # Only reset counter if grace period has passed and we haven't reached persistent state
            if not persistent_fatigue_active and fatigue_counter > 0:
                if last_fatigue_detection_time == 0 or (current_time - last_fatigue_detection_time) > fatigue_grace_period:
                    log.info(f"Fatigue counter reset from {fatigue_counter} to 0 (grace period expired)")
                    fatigue_counter = 0
                else:
                    log.debug(f"Fatigue counter maintained at {fatigue_counter} (within grace period)")
        
        # Set fatigue level - if persistent fatigue is active, always return 2 (heavily tired)
        if persistent_fatigue_active:
            fatigue_level = 2  # Force heavily tired state
        else:
            fatigue_level = current_fatigue_level
        
        return jsonify({
            'status': 'ok', 
            'fatigue_level': fatigue_level,
            'fatigue_counter': fatigue_counter,
            'persistent_fatigue_active': persistent_fatigue_active
        })
    except Exception as e:
        log.error(f"Error updating fatigue data: {e}")
        return jsonify({'error': str(e)}), 500

def determine_fatigue_level(fatigue_data):
    """Determine fatigue level (0=Not tired, 1=Lightly tired, 2=Heavily tired) based on fatigue data"""
    if not fatigue_data:
        return None
    
    # Parse the JSON report if it's a string
    if isinstance(fatigue_data.get('json_report'), str):
        try:
            report = json.loads(fatigue_data['json_report'])
        except:
            report = {}
    else:
        report = fatigue_data.get('json_report', {})
    
    # Count positive reports
    positive_reports = 0
    
    # Check various fatigue indicators
    if report.get('yawn', {}).get('report', False):
        positive_reports += 1
    if report.get('eye_rub_first_hand', {}).get('report', False):
        positive_reports += 1
    if report.get('eye_rub_second_hand', {}).get('report', False):
        positive_reports += 1
    if report.get('flicker', {}).get('report', False):
        positive_reports += 1
    if report.get('micro_sleep', {}).get('report', False):
        positive_reports += 1
    if report.get('pitch', {}).get('report', False):
        positive_reports += 1
    
    # Determine level based on number of positive reports
    if positive_reports == 0:
        return 0  # Not tired
    elif positive_reports <= 2:
        return 1  # Lightly tired
    else:
        return 2  # Heavily tired

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
    asyncio.run(main())