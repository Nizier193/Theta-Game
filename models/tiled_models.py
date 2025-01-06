from typing import Optional
from models.tiled_object_params import NotificationParams, TriggerParams, MovementParams, ParticleParams

class ObjectTypeNames:
    NPC: str = "NPC"
    Particle: str = "Particle"
    Trigger: str = "Trigger"
    Interactive: str = "Interactive"
    Particle: str = "Particle"
    Hero: str = "Hero"


# Класс, описывающий атрибуты объектов в Tiled
class Properties:
    def __init__(self) -> None:
        self.object_type: str = "Invisible"
        self.notification_params: NotificationParams = NotificationParams()
        self.movement_params: MovementParams = MovementParams()
        self.particles_params: ParticleParams = ParticleParams()
        self.trigger_params: TriggerParams = TriggerParams()

    def __repr__(self) -> str:
        text = f"""
Object Type [{self.object_type}]
Notification [{self.notification_params.NotificationText}]
Movement [{self.movement_params.MaxSpeed} {self.movement_params.WaitTime} {self.movement_params.WalkTime}]
Particles [{self.particles_params.IsParticleEmitter} {self.particles_params.Intensity} others..]
Trigger [{self.trigger_params.IsTrigger} {self.trigger_params.TriggerType}]
"""
        return text


class ObjectPropertiesParser:
    "Парсер Tiled-аргументов объектов"
    def __init__(self, object):
        self.object = object
    
    def process(self) -> Properties:
        "Парсер Tiled-объекта"
        properties = Properties()

        object_properties = self.object.properties
        properties.object_type = object_properties.get("ObjectType")

        properties.notification_params = NotificationParams.model_validate(object_properties)
        properties.movement_params = MovementParams.model_validate(object_properties)
        properties.particles_params = ParticleParams.model_validate(object_properties)
        properties.trigger_params = TriggerParams.model_validate(object_properties)

        return properties