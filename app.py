from flask import Flask, render_template, send_from_directory, jsonify
import logging as log
log.basicConfig(level=log.INFO)

from src.Bluetooth.BluetoothMockSimulator import BluetoothMockSimulator
from src.Bluetooth.BluetoothSimulatorESP32 import BluetoothSimulatorESP32

import argparse

obd_client = None

# Parse arguments
parser = argparse.ArgumentParser(description='OBD-II Simulator')
parser.add_argument('--obd', choices=['mock', 'esp32'], default='mock', help='Select the OBD-II type (mock or esp32)')
parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
parser.add_argument('--debug', action='store_true', help='Enable debug mode')
args = parser.parse_args()

app = Flask(__name__, 
    static_folder='static',  # explicitly set static folder
    template_folder='templates'  # explicitly set template folder
)

obd_client = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/api/obd/data')
async def obd_data():
    global obd_client
    if obd_client == None:
        return jsonify({'error': 'Client not initialized'}), 500
    
    data = await obd_client.request_all_settings()
    ret_dict = data.to_dict()
    
    # CAMERA IS_TIRED DATA RETRIEVAL AND ADDITION TO DICT
    ret_dict['is_tired'] = False # TODO: Implement camera client
    
    return jsonify(ret_dict)

async def main():
    global obd_client
    if obd_client == None:
        log.info(f"Starting server in {args.obd} mode on port {args.port}")
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
            
    # CAMERA CLIENT INITIALIZATION
    
    app.run(port=args.port, debug=False)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())