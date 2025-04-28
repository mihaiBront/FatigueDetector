import asyncio
import logging as log
from typing import Optional
import random
from src.OBD.OBDDataStructure import OBDDataStructure
from src.Bluetooth.iBluetoothOBDClient import iBluetoothOBDClient

log.basicConfig(level=log.INFO)

class BluetoothMockSimulator(iBluetoothOBDClient):
    """A mock implementation of iBluetoothOBDClient for testing purposes."""
    
    def __init__(self):
        super().__init__()
        self.connected = False
        self.initialized = False
        # Simulated values that will change over time
        self.mock_rpm = 1000
        self.mock_speed = 0
        self.mock_runtime = 0
        # Start the background task to update mock values
        asyncio.create_task(self._update_mock_values())

    async def _update_mock_values(self):
        """Background task to simulate changing vehicle values."""
        while True:
            if self.connected and self.initialized:
                # Simulate RPM changes (idle ~ 1000, max ~ 6000)
                self.mock_rpm = max(800, min(6000, 
                    self.mock_rpm + random.randint(-200, 200)))
                
                # Simulate speed changes (0-120 km/h)
                self.mock_speed = max(0, min(120, 
                    self.mock_speed + random.randint(-5, 5)))
                
                # Increment runtime
                self.mock_runtime += 1
            
            await asyncio.sleep(1)  # Update every second

    async def find_device(self) -> bool:
        """Simulate device discovery."""
        log.info("Mock: Searching for device...")
        await asyncio.sleep(2)  # Simulate search delay
        log.info("Mock: Device found")
        return True

    async def connect(self) -> bool:
        """Simulate connection establishment."""
        log.info("Mock: Connecting to device...")
        await asyncio.sleep(1)  # Simulate connection delay
        self.connected = True
        log.info("Mock: Connected successfully")
        return True

    async def init_communication(self) -> bool:
        """Simulate communication initialization."""
        if not self.connected:
            log.error("Mock: Not connected")
            return False
        
        log.info("Mock: Initializing communication...")
        await asyncio.sleep(0.5)  # Simulate initialization delay
        self.initialized = True
        log.info("Mock: Communication initialized")
        return True

    async def send_command(self, command: str) -> Optional[str]:
        """Simulate sending commands."""
        if not self.connected or not self.initialized:
            log.error("Mock: Not connected or not initialized")
            return None

        await asyncio.sleep(0.1)  # Simulate command delay
        
        # Simulate responses based on command
        if command == "010C":  # RPM
            return f"41 0C {self.mock_rpm // 4:04X}"
        elif command == "010D":  # Speed
            return f"41 0D {self.mock_speed:02X}"
        elif command == "011F":  # Runtime
            return f"41 1F {self.mock_runtime:04X}"
        elif command == "ATALL":  # All settings
            return f"RPM:{self.mock_rpm},SPEED:{self.mock_speed},RUNTIME:{self.mock_runtime}"
        
        return None

    async def request_engine_rpm(self) -> Optional[int]:
        """Get simulated RPM."""
        if not self.connected or not self.initialized:
            return None
        log.info(f"Mock: RPM = {self.mock_rpm}")
        return self.mock_rpm

    async def request_vehicle_speed(self) -> Optional[int]:
        """Get simulated speed."""
        if not self.connected or not self.initialized:
            return None
        log.info(f"Mock: Speed = {self.mock_speed} km/h")
        return self.mock_speed

    async def request_engine_run_time(self) -> Optional[int]:
        """Get simulated runtime."""
        if not self.connected or not self.initialized:
            return None
        log.info(f"Mock: Runtime = {self.mock_runtime} seconds")
        return self.mock_runtime

    async def request_all_settings(self) -> Optional[OBDDataStructure]:
        """Get all simulated settings at once."""
        if not self.connected or not self.initialized:
            return None
            
        log.info(f"Mock: All settings - RPM: {self.mock_rpm}, "
                f"Speed: {self.mock_speed}(km/h), Runtime: {self.mock_runtime}(s)")
        return OBDDataStructure(self.mock_rpm, self.mock_speed, self.mock_runtime)

    async def close(self) -> None:
        """Simulate closing the connection."""
        if self.connected:
            log.info("Mock: Closing connection...")
            await asyncio.sleep(0.5)  # Simulate closing delay
            self.connected = False
            self.initialized = False
            log.info("Mock: Connection closed")

if __name__ == "__main__":
    # Example usage
    async def main():
        client = BluetoothMockSimulator()
        try:
            if await client.connect():
                if await client.init_communication():
                    # Wait a bit to let the mock values change
                    for _ in range(5):
                        all_settings = await client.request_all_settings()
                        print(f"Settings: {all_settings}")
                        await asyncio.sleep(2)
        finally:
            await client.close()

    asyncio.run(main()) 