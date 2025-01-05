from typing import Any, List, Optional


class NotificationConfig:
    def __init__(self):
        self.text: Optional[str] = None
        self.connected_to: Any = None
        self.notification: Any = None


class MovementConfig:
    def __init__(self):
        self.max_speed: int = 0
        self.wait_time: int = 0


class ParticleConfig:
    def __init__(self) -> None:
        self.is_particle_emitter: bool = False
        self.intensity: Optional[int] = None
        self.side: Optional[int] = None
        self.top: Optional[int] = None
        self.distance: Optional[int] = None
        self.spread: Optional[int] = None
        self.speed: Optional[int] = None


class InteractiveConfig:
    def __init__(self):
        # Объект, к которому привязан конфиг
        self.object: Optional[Any] = None
        
        # Нотификация, которая привязана к Interactive
        self.notification: NotificationConfig = NotificationConfig()

        # Параметры движения
        self.movement: MovementConfig = MovementConfig()

        # Параметры партиклов
        self.particles: ParticleConfig = ParticleConfig()


    def __repr__(self) -> str:
        text = f"""

cfg: {self.object} 
<Нотификация: Text: [{self.notification.text}]; Conn_to: [{self.notification.connected_to}]; Notification: [{self.notification.notification}]>
<Перемещение: max_speed: [{self.movement.max_speed}]; wait_time: [{self.movement.wait_time}]>
<Партиклы: is_emitter [{self.particles.is_particle_emitter}]>"""
        
        return text