from pathlib import Path
from typing import Tuple, Union

import pygame as pg
from pygame.sprite import Sprite
from pygame.transform import scale
import json

from support.settings import load_settings
from support.pygame_loaders import ImageLoader
from common_classes import inventory_group, items, Body
from inventory.item_models import ItemParams, ItemType

settings = load_settings()


"""
Здесь объявляются классы для предметов

Item - модель предмета со всеми параметрами
ItemSprite - pygame Sprite предмета с описанием Item
"""


class Item():
    "Моделька для предмета как такового"
    def __init__(self, json_name: str) -> None:
        self.json_name = json_name
        json_path = Path(settings.item_jsons) / self.json_name # Путь до json
        self.properties = ItemParams.model_validate(json.load(open(json_path, "r")))

        texture_path = Path(settings.item_textures) / self.properties.ItemTexture # Путь до картинки
        self.texture = ImageLoader(texture_path).image

        print(f"Initialized item {self.properties.Name}")


class ItemSprite(Body):
    "Спрайт предмета в игре"
    def __init__(self, object: Union[Sprite, None], json_name: str, center: Tuple[int, int]) -> None:
        self.item = Item(json_name)
        self.object_holding = object # Тот, кто держит предмет

        super().__init__(size=self.item.properties.ItemSize)
        self.add(inventory_group, items)

        self.update_image(scale(self.item.texture, self.item.properties.ItemSize))
        self.rect = self.image.get_rect(topleft=center)

        self.apply_physics = False
        

    def use(self) -> str:
        if not self.object_holding:
            raise Exception("Function <use> cannot be called outside of inventory")

        props = self.item.properties

        if props.ItemType == ItemType.Basic:
            print("It`s a dumb object")
            self.kill()
            return "How`d you get this item..."

        if props.ItemType == ItemType.Consumable:
            self.object_holding.hp += self.item.properties.ConsumeProperties.Heal
            self.object_holding.armor += self.item.properties.ConsumeProperties.Armor
            display_text = props.ConsumeProperties.UseText

            self.kill()
            return display_text
        
        if props.ItemType == ItemType.Weapon:
            return ""

        if props.ItemType == ItemType.Look:
            return ""
        
        return "You have used Nothing"


    def update(self):
        if self.apply_physics:
            self.gravitate()

            self.rect.y += self.vector.y
            self.vertical_collisions()