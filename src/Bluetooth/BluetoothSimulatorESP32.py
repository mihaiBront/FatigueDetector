import bluetooth
import asyncio
from bluetooth import *
import logging as log
from typing import Optional, Dict
import time
from src.OBD.OBDDataStructure import OBDDataStructure
from src.Bluetooth.iBluetoothOBDClient import iBluetoothOBDClient

log.basicConfig(level=log.INFO)

class BluetoothSimulatorESP32(iBluetoothOBDClient):
    def __init__(self):
        super().__init__()
        self.sock = None
        self.target_name = "OBD-II Simulator"
        self.target_address = None
        self.port = 1

    async def find_device(self) -> bool:
        print(f"Searching for {self.target_name}...")
        try:
            # Using asyncio.to_thread to make the blocking bluetooth call non-blocking
            nearby_devices = await asyncio.to_thread(
                discover_devices, lookup_names=True, duration=8
            )
            print(f"Found {len(nearby_devices)} devices")
            
            for addr, name in nearby_devices:
                print(f"Found device: {name} at {addr}")
                if name == self.target_name:
                    self.target_address = addr
                    return True
            return False
        except Exception as e:
            log.error(f"Error searching for devices: {e}")
            return False

    async def connect(self) -> bool:
        if not self.target_address:
            if not await self.find_device():
                log.error(f"Could not find {self.target_name} device")
                return False

        log.info(f"Connecting to {self.target_name} at {self.target_address}...")
        try:
            self.sock = BluetoothSocket(RFCOMM)
            await asyncio.to_thread(
                self.sock.connect, (self.target_address, self.port)
            )
            self.sock.settimeout(1.0)  # Set timeout for operations
            log.info("Connected successfully!")
            return True
        except Exception as e:
            log.error(f"Failed to connect: {e}")
            return False
    
    async def init_communication(self) -> bool:
        log.info("Initializing communication...")
        
        try:
            # Reset device and disable echo
            commands = ["ATZ", "ATE0"]
            for cmd in commands:
                if not await self.send_command(cmd):
                    log.error(f"Failed to execute {cmd}")
                    return False
            return True
        
        except Exception as e:
            log.error(f"Error initializing communication: {e}")
            return False

    async def send_command(self, command: str) -> Optional[str]:
        if not self.sock:
            log.error("Not connected to device")
            return None

        try:
            # Send command with carriage return
            await asyncio.to_thread(
                self.sock.send, (command + "\r").encode()
            )
            await asyncio.sleep(0.1)  # Give device time to respond
            
            # Read response with timeout handling
            response = ""
            start_time = time.time()
            timeout = 2.0  # 2 second timeout
            
            while (time.time() - start_time) < timeout:
                try:
                    data = await asyncio.to_thread(
                        self.sock.recv, 1024
                    )
                    if data:
                        response += data.decode().strip()
                        if "\r" in response or "\n" in response:
                            break
                except bluetooth.btcommon.BluetoothError as e:
                    if "timed out" not in str(e):
                        raise
                    break
            
            return response.strip() if response.strip() else None
            
        except Exception as e:
            log.error(f"Error sending command '{command}': {e}")
            return None
            
    async def request_engine_rpm(self) -> Optional[int]:
        response = await self.send_command("010C")
        if response and response.startswith("41 0C"):
            try:
                data = response.split()
                if len(data) >= 4:
                    rpm = ((int(data[2], 16) * 256) + int(data[3], 16)) // 4
                    log.info(f"Engine RPM: {rpm}")
                    return rpm
            except (ValueError, IndexError) as e:
                log.error(f"Error parsing RPM data: {e}")
        
        log.error("Failed to get RPM data")
        return None
    
    async def request_vehicle_speed(self) -> Optional[int]:
        response = await self.send_command("010D")
        if response and response.startswith("41 0D"):
            try:
                speed = int(response.split()[2], 16)
                log.info(f"Vehicle Speed: {speed} km/h")
                return speed
            except (ValueError, IndexError) as e:
                log.error(f"Error parsing speed data: {e}")
        
        log.error("Failed to get speed data")
        return None
    
    async def request_engine_run_time(self) -> Optional[int]:
        response = await self.send_command("011F")
        if response and response.startswith("41 1F"):
            try:
                data = response.split()
                if len(data) >= 4:
                    run_time = (int(data[2], 16) * 256) + int(data[3], 16)
                    minutes = run_time // 60
                    seconds = run_time % 60
                    log.info(f"Engine Run Time: {minutes} minutes, {seconds} seconds")
                    return run_time
            except (ValueError, IndexError) as e:
                log.error(f"Error parsing run time data: {e}")
            
        log.error("Failed to get engine run time data")
        return None

    async def request_all_settings(self) -> Optional[OBDDataStructure]:
        """Request all vehicle settings at once using the ATALL command."""
        response = await self.send_command("ATALL")
        if not response:
            log.error("Failed to get all settings")
            return None

        try:
            # The response format should match your C++ implementation
            # Assuming it returns a comma-separated string of values
            values = response.split(',')
            if len(values) >= 3:
                rpm = int(values[0].split(":")[1]) if values[0] else None
                speed = int(values[1].split(":")[1]) if values[1] else None
                runtime = int(values[2].split(":")[1]) if values[2] else None

                log.info(f"All settings - RPM: {rpm}, Speed: {speed}(km/h), Runtime: {runtime}(s)")
                
                return OBDDataStructure(rpm, speed, runtime)
                
        except (ValueError, IndexError) as e:
            log.error(f"Error parsing all settings data: {e}")
        
        return None

    async def close(self) -> None:
        if self.sock:
            try:
                await asyncio.to_thread(self.sock.close)
            except Exception as e:
                log.error(f"Error closing connection: {e}")

if __name__ == "__main__":
    # Example usage
    async def main():
        client = BluetoothSimulatorESP32()
        try:
            if await client.connect():
                if await client.init_communication():
                    # Test individual requests
                    # await client.request_engine_rpm()
                    # await client.request_vehicle_speed()
                    # await client.request_engine_run_time()
                    
                    # Test getting all settings at once
                    all_settings = await client.request_all_settings()
                    print("All settings:", all_settings)
        finally:
            await client.close()

    asyncio.run(main()) 