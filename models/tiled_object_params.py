# Параметры привязанной нотификации
from typing import Optional
from pydantic import BaseModel

class NotificationParams(BaseModel):
    NotificationText: str = ""
    MovementName: str = "Fixed"
    MarginY: int = 100
    # Other params

# Параметры движения NPC
class MovementParams(BaseModel):
    MaxSpeed: int = 0
    WaitTime: int = 1 # To avoid 0 division error
    WalkTime: int = 0
    # Other params

# Параметры движения NPC
class ParticleParams(BaseModel):
    IsParticleEmitter: bool = False
    Intensity: Optional[int] = None
    Side: Optional[int] = None
    Top: Optional[int] = None
    Distance: Optional[int] = None
    Spread: Optional[int] = None
    Speed: Optional[int] = None
    # Other params


# Параметры движения NPC
class TriggerParams(BaseModel):
    IsTrigger: bool = False
    TriggerType: Optional[str] = None
    OffsetX: Optional[int] = None
    OffsetY: Optional[int] = None
    ToX: Optional[int] = None
    ToY: Optional[int] = None
    CameraMovement: Optional[str] = "Move"


class ItemParams(BaseModel):
    JsonName: str = "error.json"

