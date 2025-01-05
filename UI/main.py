from typing import Any, Optional
from game_control import Windows

class Dialogue():
    def __init__(self) -> None:
        pass

    # Dialogue usage
    def set_dialogue(self, text: str):
        "Sets text for dialogue"
        pass

    def open_dialogue(self):
        "Opens dialogue for user"
        pass

    def close_dialogue(self):
        "Closes dialogue for user"
        pass


class Inventory():
    def __init__(self) -> None:
        pass

    # Inventory usage
    def use_item(self):
        "Uses item and does something"
        pass



class UserInterface():
    def __init__(self) -> None:
        self.inventory: Inventory = Inventory()
        self.dialogue: Dialogue = Dialogue()
        self.windows: Optional[Windows] = None # // TODO: Это ещё нескоро

    

