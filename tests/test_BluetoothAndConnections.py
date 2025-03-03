from unittest import TestCase, IsolatedAsyncioTestCase
from src.Commons.LoggingHelper import LoggingHelper
from src.Settings import Settings
from bleak import BleakScanner, BleakClient, BLEDevice
from src.Bluetooth.BluetoothHandler import BluetoothHandler
import logging as log

LoggingHelper.init_logger("DEBUG")

class connectivityTests(IsolatedAsyncioTestCase, TestCase):
    listDevices : list[BLEDevice] = None
    config: Settings = None
    
    async def test_connectivity(self):
        self.listDevices = await BluetoothHandler.scanDevices()
        self.assertGreater(len(self.listDevices), 0, "No devices found")
        [log.info(device) for device in self.listDevices]
        
    async def test_test(self):
        # arrange
        if self.listDevices is None:
            self.listDevices = await BluetoothHandler.scanDevices()
        self.assertIsNotNone(self.listDevices, "ListDevices is None")
        [log.debug(f"\t{device.name}") for device in self.listDevices]
        log.debug(f"Found {len(self.listDevices)} devices:")
        self.assertGreater(len(self.listDevices), 0, "No devices found")
        
        self.settings = Settings.from_file("config\settings.json")
        device = list(filter(lambda x: x.name == self.settings.device.name, self.listDevices))
        self.assertGreater(len(device), 0, f"Device {self.settings.device.name} not found")
        device = device[0]
        
        # act
        device_connection = await BluetoothHandler.connect(device)
        log.info(device_connection.services)