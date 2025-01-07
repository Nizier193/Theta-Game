from pydantic import BaseModel
from typing import Tuple

# Типы предметов
class ItemType:
    Basic: str = "Basic"
    Weapon: str = "Weapon"
    Consumable: str = "Consumable"
    Look: str = "Look"

# Описание типов предметов
class ItemWeapon(BaseModel):
    Damage: int = 0
    Cooldown: int = 0
    Type: str = "Ranged"


class ItemConsumable(BaseModel):
    Heal: int = 0
    Armor: int = 0
    ToggleSomething: str = ""


class ItemLook(BaseModel):
    AdditionalDescription: str = ""
    ToggleSomething: str = ""

# Параметры предмета
class ItemParams(BaseModel):
    ItemTexture: str = "error.png"
    ItemSize: Tuple[int, int] = (16, 16)
    Name: str = "No Name Item"
    Description: str = "Basic Item"
    ItemType: str = ItemType.Basic
    Rarity: str = "Common"

    AttackProperties: ItemWeapon = ItemWeapon()
    ConsumeProperties: ItemConsumable = ItemConsumable()
    LookProperties: ItemLook = ItemLook()
