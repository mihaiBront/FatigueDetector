from abc import ABC, abstractmethod
from bluetooth import *
from typing import Optional
from src.OBD.OBDDataStructure import OBDDataStructure


class iBluetoothOBDClient(ABC):
    def __init__(self):
        self.sock = None
        self.target_name = None
        self.target_address = None
        self.port = None
        
    @abstractmethod
    def find_device(self) -> bool:
        """Search for the target Bluetooth device."""
        pass

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection with the device."""
        pass
    
    @abstractmethod
    def init_communication(self) -> bool:
        """Initialize communication protocol with the device."""
        pass

    @abstractmethod
    def send_command(self, command: str) -> Optional[str]:
        """Send a command to the device and return the response."""
        pass

    @abstractmethod
    def request_engine_rpm(self) -> Optional[int]:
        """Request current engine RPM."""
        pass
    
    @abstractmethod
    def request_vehicle_speed(self) -> Optional[int]:
        """Request current vehicle speed."""
        pass
    
    @abstractmethod
    def request_engine_run_time(self) -> Optional[int]:
        """Request engine run time."""
        pass

    @abstractmethod
    def request_all_settings(self) -> Optional[OBDDataStructure]:
        """Request all vehicle settings at once."""
        pass

    def close(self) -> None:
        """Close the Bluetooth connection."""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass