from typing import List

class Teleport:
    def __init__(self, object_from, object_to):
        self.object_from = object_from
        self.object_to = object_to


class Dialogue:
    def __init__(self, dialogues: List[str]):
        self.dialogues = dialogues


class NotificationConfig:
    def __init__(self, text: str):
        self.text = text


class InteractiveConfig:
    def __init__(self, object):
        # Объект, к которому привязан конфиг
        self.object = object
        
        # Нотификация, которая привязана к Interactive
        self.notification = None

        # Конфиг для телепорта
        self.teleport = None

        # Конфиг для диалога
        self.dialogue = None