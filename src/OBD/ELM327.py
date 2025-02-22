from dataclasses import dataclass, field
from bleak import BleakClient

from src.Commons.Serializable import Serializable

INSTRUCTIONS_SET = {
    "reset": "ATZ",
}

@dataclass
class ELM327(Serializable):
    name: str = field(default_factory=str)
    address: str = field(default_factory=str)
    
    