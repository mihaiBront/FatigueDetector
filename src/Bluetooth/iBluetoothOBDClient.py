from abc import ABC, abstractmethod
from bluetooth import *

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
    def send_command(self, command: str) -> str | None:
        """Send a command to the device and return the response."""
        pass

    @abstractmethod
    def request_engine_rpm(self) -> int | None:
        """Request current engine RPM."""
        pass
    
    @abstractmethod
    def request_vehicle_speed(self) -> int | None:
        """Request current vehicle speed."""
        pass
    
    @abstractmethod
    def request_engine_run_time(self) -> int | None:
        """Request engine run time."""
        pass

    def close(self) -> None:
        """Close the Bluetooth connection."""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass