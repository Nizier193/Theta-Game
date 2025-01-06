from typing import List, Any, Optional
from pytmx import load_pygame


class LayerClass:
    def __init__(self, name: str, object_class: Any):
        self.name = name
        self.object_class = object_class

class MapLayers:
    "Класс-обработчик для работы со слоями Tiled"
    def __init__(self):
        self.classes = []

    def add(self, layer_class: LayerClass):
        self.classes.append(layer_class)
    
    def get_layer(self, layer_name: str) -> Optional[LayerClass]:
        layer_class = list(filter(lambda item: item.name == layer_name, self.classes))
        if not layer_class:
            return None

        return layer_class[-1]

# Описание слоёв тайлов
class Layers:
    Background: str = "Background"
    Foreground: str = "Foreground"