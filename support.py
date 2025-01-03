from typing import List, Any


class LayerClass:
    def __init__(self, name: str, object_class: Any, support_group: Any):
        self.name = name
        self.object_class = object_class
        self.support_group = support_group

class MapLayers:
    def __init__(self):
        self.classes = []

    def add(self, layer_class: LayerClass):
        self.classes.append(layer_class)
    
    def get_layer(self, layer_name: str) -> LayerClass:
        layer_class = list(filter(lambda item: item.name == layer_name, self.classes))
        if not layer_class:
            return None

        return layer_class[-1]
    
class Layers:
    Foreground: str = "Foreground"
    Interactive: str = "Interactive"
    Ladders: str = "Ladders"
