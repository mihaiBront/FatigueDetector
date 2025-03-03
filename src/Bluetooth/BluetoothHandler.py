import asyncio
from bleak import BleakScanner, BleakClient, BLEDevice
import logging

class BluetoothHandler():
    
    @staticmethod
    async def scanDevices() -> list[BLEDevice]:
        """
        Scan for Bluetooth devices and return a list of discovered devices.
        
        Returns:
            list[BLEDevice]: A list of discovered devices
        """
        logging.info("Scanning for Bluetooth devices...")
        devices = await BleakScanner.discover()
        
        if not devices:
            logging.info("No devices found!")
            return None
        
        if len(devices) == 0:
            logging.info("No devices found!")
            return None
        
        devices = [device for device in devices if device.name]
        
        if len(devices) == 0:
            logging.info("No devices with name found!")
            return None
        
        logging.debug(f"Found {len(devices)} devices")
        
        return devices
                
    @staticmethod
    async def connect(address: BLEDevice | str) -> BleakClient:
        """
        Connect to a Bluetooth device and return the client
        
        Args:
            address (BLEDevice | str): The device to connect to
        Returns:
            BleakClient: The client object if successful, None otherwise
        """
        logging.info(f"Connecting to device {address}...")
        try:
            async with BleakClient(address) as client:
                if client.is_connected:
                    logging.info(f"Connected to device!")                    
                    return client
                else:
                    logging.error("Failed to connect")
                    return None
        except Exception as e:
            logging.error(f"Error connecting to device: {str(e)}")
            return None
    
    @staticmethod
    async def exploreServices(client):
        """
        Explore and interact with device services and characteristics
        
        Args:
            client (BleakClient): The client object to interact with
        
        Returns:

        """
        services = await client.get_services()

        if logging.getLogger().level == logging.DEBUG:
            for service in services:
                logging.debug(f"\nService: {service.uuid}")

                # Explore characteristics within each service
                for char in service.characteristics:
                    logging.debug(f"  Characteristic: {char.uuid}")
                    logging.debug(f"    Properties: {', '.join(char.properties)}")

                    # Try reading the characteristic if it's readable
                    if "read" in char.properties:
                        try:
                            value = await client.read_gatt_char(char.uuid)
                            logging.debug(f"    Value: {value}")
                        except Exception as e:
                            logging.error(f"    Error reading characteristic: {str(e)}")
                        
        return services
