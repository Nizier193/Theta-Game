from typing import Optional

# Нотация переменных из Tiled
class ObjectPropertiesName:
    # Notification Text Params
    NotificationText: str = "NotificationText"

    # Teleport Params
    FirstTeleportPair: str = "FirstTeleportPair"
    SecondTeleportPair: str = "SecondTeleportPair"

    # NPC Params
    MaxSpeed: str = "MaxSpeed"
    WaitTime: str = "WaitTime"

    # Particles Params
    IsParticleEmitter: str = "IsParticleEmitter" # // Является ли испускателем частиц
    Intensity: str = "Intensity" # // Интенсивность
    Side: str = "Side" # // Влево или вправо 1 / -1
    Top: str = "Top" # // Вверх или вниз 1 / -1
    Distance: str = "Distance" # // Расстояние которое частицы пролетят
    Spread: str = "Spread" # // Разброс партиклов
    Speed: str = "Speed" # // Скорость партиклов

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


# Класс, описывающий атрибуты объектов в Tiled
class Properties:
    def __init__(self) -> None:
        self.notification_params: Optional[NotificationParams] = None
        self.teleport_params: Optional[TeleportParams] = None
        self.movement_params: MovementParams = MovementParams()
        self.particles_params: ParticleParams = ParticleParams()

    def __repr__(self) -> str:
        return f"<Properties Particles Param [{self.particles_params.is_particle_emitter}]>"


class ObjectPropertiesParser:
    "Парсер Tiled-аргументов объектов"
    def __init__(self, object):
        self.object = object

    def parse_particles(self, props) -> ParticleParams:
        params = ParticleParams()
        params.is_particle_emitter = props.get(ObjectPropertiesName.IsParticleEmitter, False)
        params.intensity = props.get(ObjectPropertiesName.Intensity, 0)
        params.side = props.get(ObjectPropertiesName.Side, 1)
        params.top = props.get(ObjectPropertiesName.Top, 1)
        params.distance = props.get(ObjectPropertiesName.Distance, 0)
        params.speed = props.get(ObjectPropertiesName.Speed, 0)
        params.spread = props.get(ObjectPropertiesName.Spread, 0)

        return params
    
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
        properties.particles_params = self.parse_particles(object_properties)

        print(properties)

        return properties