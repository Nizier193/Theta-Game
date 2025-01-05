from typing import Optional
from models.tiled_object_params import NotificationParams, TriggerParams, MovementParams, ParticleParams

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

    # Trigger Params
    IsTrigger: str = "IsTrigger"
    TriggerType: str = "TriggerType"
    OffsetX: str = "OffsetX"
    OffsetY: str = "OffsetY"
    ToX: str = "ToX"
    ToY: str = "ToY"

    # Параметры движения камеры
    CameraMovement: str = "CameraMovement"


# Класс, описывающий атрибуты объектов в Tiled
class Properties:
    def __init__(self) -> None:
        self.notification_params: Optional[NotificationParams] = None
        self.movement_params: MovementParams = MovementParams()
        self.particles_params: ParticleParams = ParticleParams()
        self.trigger_params: TriggerParams = TriggerParams()

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

    def parse_movement(self, props) -> MovementParams:
        params = MovementParams()
        params.max_speed = props.get(ObjectPropertiesName.MaxSpeed, 0)
        params.wait_time = props.get(ObjectPropertiesName.WaitTime, 0)

        return params
    
    def parse_trigger(self, props) -> TriggerParams:
        params = TriggerParams()
        params.is_trigger = props.get(ObjectPropertiesName.IsTrigger, False)
        params.offset_x = props.get(ObjectPropertiesName.OffsetX)
        params.offset_y = props.get(ObjectPropertiesName.OffsetY)
        params.to_x = props.get(ObjectPropertiesName.ToX)
        params.to_y = props.get(ObjectPropertiesName.ToY)
        params.trigger_type = props.get(ObjectPropertiesName.TriggerType)
        params.camera_movement = props.get(ObjectPropertiesName.CameraMovement)

        return params
    
    def process(self) -> Properties:
        "Парсер Tiled-объекта"
        properties = Properties()

        object_properties = self.object.properties
        properties.notification_params = self.parse_notification(object_properties)
        properties.movement_params = self.parse_movement(object_properties)
        properties.particles_params = self.parse_particles(object_properties)
        properties.trigger_params = self.parse_trigger(object_properties)

        return properties