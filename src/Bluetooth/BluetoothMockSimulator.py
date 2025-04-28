import asyncio
import logging as log
from typing import Optional
import random
import time
from src.OBD.OBDDataStructure import OBDDataStructure
from src.Bluetooth.iBluetoothOBDClient import iBluetoothOBDClient

log.basicConfig(level=log.INFO)

class BluetoothMockSimulator(iBluetoothOBDClient):
    """A mock implementation of iBluetoothOBDClient for testing purposes."""
    
    def __init__(self):
        super().__init__()
        self.connected = False
        self.initialized = False
        self.start_time = time.time()
        # Base values for simulation
        self.base_rpm = 1000
        self.base_speed = 0

    def _get_mock_values(self):
        """Generate dynamic mock values based on time and randomization."""
        # Time-based runtime
        runtime = int(time.time() - self.start_time)
        
        # RPM varies between 800 and 6000
        rpm = max(800, min(6000, 
            self.base_rpm + random.randint(-500, 500)))
        self.base_rpm = rpm  # Save for next time
        
        # Speed varies between 0 and 120 km/h
        speed = max(0, min(120, 
            self.base_speed + random.randint(-10, 10)))
        self.base_speed = speed  # Save for next time
        
        return rpm, speed, runtime

    async def find_device(self) -> bool:
        """Simulate device discovery."""
        log.info("Mock: Searching for device...")
        await asyncio.sleep(0.5)  # Reduced delay
        log.info("Mock: Device found")
        return True

    async def connect(self) -> bool:
        """Simulate connection establishment."""
        log.info("Mock: Connecting to device...")
        await asyncio.sleep(0.2)  # Reduced delay
        self.connected = True
        log.info("Mock: Connected successfully")
        return True

    async def init_communication(self) -> bool:
        """Simulate communication initialization."""
        if not self.connected:
            log.error("Mock: Not connected")
            return False
        
        log.info("Mock: Initializing communication...")
        await asyncio.sleep(0.2)  # Reduced delay
        self.initialized = True
        self.start_time = time.time()  # Reset start time
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
            rpm, _, _ = self._get_mock_values()
            return f"41 0C {rpm // 4:04X}"
        elif command == "010D":  # Speed
            _, speed, _ = self._get_mock_values()
            return f"41 0D {speed:02X}"
        elif command == "011F":  # Runtime
            _, _, runtime = self._get_mock_values()
            return f"41 1F {runtime:04X}"
        elif command == "ATALL":  # All settings
            rpm, speed, runtime = self._get_mock_values()
            return f"RPM:{rpm},SPEED:{speed},RUNTIME:{runtime}"
        
        return None

    async def request_engine_rpm(self) -> Optional[int]:
        """Get simulated RPM."""
        if not self.connected or not self.initialized:
            return None
        rpm, _, _ = self._get_mock_values()
        log.info(f"Mock: RPM = {rpm}")
        return rpm

    async def request_vehicle_speed(self) -> Optional[int]:
        """Get simulated speed."""
        if not self.connected or not self.initialized:
            return None
        _, speed, _ = self._get_mock_values()
        log.info(f"Mock: Speed = {speed} km/h")
        return speed

    async def request_engine_run_time(self) -> Optional[int]:
        """Get simulated runtime."""
        if not self.connected or not self.initialized:
            return None
        _, _, runtime = self._get_mock_values()
        log.info(f"Mock: Runtime = {runtime} seconds")
        return runtime

    async def request_all_settings(self) -> Optional[OBDDataStructure]:
        """Get all simulated settings at once."""
        if not self.connected or not self.initialized:
            return None
            
        rpm, speed, runtime = self._get_mock_values()
        log.info(f"Mock: All settings - RPM: {rpm}, "
                f"Speed: {speed}(km/h), Runtime: {runtime}(s)")
        return OBDDataStructure(rpm, speed, runtime)

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