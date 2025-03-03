from src.Commons.Serializable import Serializable
from dataclasses import dataclass, field

@dataclass
class Device(Serializable):
    name: str = ""
    address: str = ""

@dataclass
class Settings(Serializable):
    device: Device = field(default_factory=Device)
    
    
if __name__ == "__main__":
    system = Settings()
    print(system.to_file("config/settings.json"))
    
    system_loaded = Settings.from_file("config/settings.json")
    print(system_loaded.serialize())
    
    

