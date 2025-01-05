# Параметры привязанной нотификации
from typing import Optional

class NotificationParams:
    def __init__(self) -> None:
        self.notification_text: str
        # Other params

# Параметры движения NPC
class MovementParams:
    def __init__(self) -> None:
        self.max_speed: int = 0
        self.wait_time: int = 0
        # Other params

# Параметры движения NPC
class ParticleParams:
    def __init__(self) -> None:
        self.is_particle_emitter: bool = False
        self.intensity: Optional[int] = None
        self.side: Optional[int] = None
        self.top: Optional[int] = None
        self.distance: Optional[int] = None
        self.spread: Optional[int] = None
        self.speed: Optional[int] = None
        # Other params


# Параметры движения NPC
class TriggerParams:
    def __init__(self) -> None:
        self.is_trigger: bool = False
        self.trigger_type: Optional[str] = None
        self.offset_x: Optional[int] = None
        self.offset_y: Optional[int] = None
        self.to_x: Optional[int] = None
        self.to_y: Optional[int] = None
        # Other params

        self.camera_movement: Optional[str] = "Move"