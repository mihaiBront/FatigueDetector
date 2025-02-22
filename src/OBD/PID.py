from src.Commons.Serializable import Serializable
from dataclasses import dataclass, field
from typing import Any

@dataclass
class PID(Serializable):
    PID: str = field(default_factory=str),
    DataLen:int = field(default_factory=int)
    Desc: str = field(default_factory=str)
    
    @classmethod
    def from_dict(cls, self: Any):
        pass