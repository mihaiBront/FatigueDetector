from flask import Flask, render_template, send_from_directory, jsonify
import logging as log
log.basicConfig(level=log.INFO)

from src.Bluetooth.BluetoothMockSimulator import BluetoothMockSimulator
from src.Bluetooth.BluetoothSimulatorESP32 import BluetoothSimulatorESP32

import argparse

client = None

# Parse arguments
parser = argparse.ArgumentParser(description='OBD-II Simulator')
parser.add_argument('--simulation', choices=['mock', 'esp32'], default='mock', help='Select the OBD-II simulation type (mock or esp32)')
parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
parser.add_argument('--debug', action='store_true', help='Enable debug mode')
args = parser.parse_args()

app = Flask(__name__, 
    static_folder='static',  # explicitly set static folder
    template_folder='templates'  # explicitly set template folder
)

client = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/api/obd/data')
async def obd_data():
    global client
    if client == None:
        return jsonify({'error': 'Client not initialized'}), 500
    
    data = await client.request_all_settings()
    return jsonify(data.to_dict())

async def main():
    global client
    if client == None:
        log.info(f"Starting server in {args.simulation} mode on port {args.port}")
        if args.simulation == 'mock':
            client = BluetoothMockSimulator()
        elif args.simulation == 'esp32':
            client = BluetoothSimulatorESP32()
            
        if not client:
            log.error("Failed to create client")
            exit(1)
        
        if not await client.find_device():
            log.error("Failed to find device")
            exit(1)
        
        if not await client.connect():
            log.error("Failed to connect to device")
            exit(1)
        
        if not await client.init_communication():
            log.error("Failed to initialize communication")
            exit(1)
    
    app.run(port=args.port, debug=False)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())