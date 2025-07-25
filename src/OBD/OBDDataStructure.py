from dataclasses import dataclass

@dataclass
class OBDDataStructure: 
    rpm: int = -1
    speed: int = -1
    runtime: int = -1
    
    def __str__(self):
        return f"RPM: {self.rpm}, Speed: {self.speed}, Runtime: {self.runtime}"
    
    def to_dict(self):
        return {
            "rpm": self.rpm,
            "speed": self.speed,
            "runtime": self.runtime
        }
