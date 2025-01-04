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


class InteractiveConfig:
    def __init__(self, object):
        # Объект, к которому привязан конфиг
        self.object = object
        
        # Нотификация, которая привязана к Interactive
        self.notification: NotificationConfig = NotificationConfig()

        # Параметры движения
        self.movement: MovementConfig = MovementConfig()


    def __repr__(self) -> str:
        text = f"""

cfg: {self.object} 
<Нотификация: Text: [{self.notification.text}]; Conn_to: [{self.notification.connected_to}]; Notification: [{self.notification.notification}]>
<Перемещение: max_speed: [{self.movement.max_speed}]; wait_time: [{self.movement.wait_time}]>"""
        
        return text