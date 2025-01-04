from typing import Optional

# Названия переменных из Tiled
class ObjectPropertiesName:
    # Notification Text Params
    NotificationText: str = "NotificationText"

    # Teleport Params
    FirstTeleportPair: str = "FirstTeleportPair"
    SecondTeleportPair: str = "SecondTeleportPair"

    # NPC Params
    MaxSpeed: str = "MaxSpeed"
    WaitTime: str = "WaitTime"

# Параметры привязанной нотификации
class NotificationParams:
    def __init__(self) -> None:
        self.notification_text: str
        # Other params

# Параметры телепортов
class TeleportParams:
    def __init__(self) -> None:
        self.first_teleport: Optional[str] = None
        self.second_teleport: Optional[str] = None
        # Other params

# Параметры движения NPC
class MovementParams:
    def __init__(self) -> None:
        self.max_speed: int = 0
        self.wait_time: int = 0
        # Other params

# Класс, описывающий атрибуты объектов в Tiled
class Properties:
    def __init__(self) -> None:
        self.notification_params: Optional[NotificationParams] = None
        self.teleport_params: Optional[TeleportParams] = None
        self.movement_params: MovementParams = MovementParams()

    def __repr__(self) -> str:
        return f"<Properties Movement Params [{self.movement_params.max_speed}, {self.movement_params.wait_time}]>"


class ObjectPropertiesParser:
    "Парсер Tiled-аргументов объектов"
    def __init__(self, object):
        self.object = object

    
    def parse_notification(self, props) -> Optional[NotificationParams]:
        params = NotificationParams()
        params.notification_text = props.get(ObjectPropertiesName.NotificationText)

        if params.notification_text == None or len(params.notification_text) == 0:
            return None

        return params
    
    
    def parse_teleport(self, props) -> Optional[TeleportParams]:
        params = TeleportParams()
        params.first_teleport = props.get(ObjectPropertiesName.FirstTeleportPair)
        params.second_teleport = props.get(ObjectPropertiesName.SecondTeleportPair)

        if params.first_teleport == None or params.second_teleport == None:
            return None

        return params
    

    def parse_movement(self, props) -> MovementParams:
        params = MovementParams()
        params.max_speed = props.get(ObjectPropertiesName.MaxSpeed, 0)
        params.wait_time = props.get(ObjectPropertiesName.WaitTime, 0)

        return params

    
    def process(self) -> Properties:
        "Парсер Tiled-объекта"
        properties = Properties()

        object_properties = self.object.properties
        properties.notification_params = self.parse_notification(object_properties)
        properties.teleport_params = self.parse_teleport(object_properties)
        properties.movement_params = self.parse_movement(object_properties)

        return properties