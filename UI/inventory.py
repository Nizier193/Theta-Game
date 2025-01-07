from pathlib import Path
from typing import Any, Optional, Tuple, Union
from typing import List

import pygame as pg
from pygame.sprite import Sprite, Group, spritecollide
from pygame.transform import scale
import json

from models.settings import load_settings
from common_classes import camera, inventory_group, items, active, Body
from UI.item_models import ItemParams, ItemType

settings = load_settings()
ratio = settings.tilesize / settings.initial_tilesize

# Предмет в инвентаре
class Item():
    def __init__(self, json_name: str, basepath: Path = Path("UI/items")) -> None:
        self.json_name = json_name
        json_path = basepath / Path("item_jsons") / self.json_name
        self.properties = ItemParams.model_validate(json.load(open(json_path, "r")))

        texture_path = basepath / Path("item_textures") / self.properties.ItemTexture
        self.texture = pg.image.load(texture_path)

        print(f"Initialized item {self.properties.Name}")



class ItemSprite(Body):
    def __init__(self, object: Union[Sprite, None], json_name: str, center: Tuple[int, int]) -> None:
        self.item = Item(json_name)
        self.object_holding = object # Тот, кто держит предмет

        super().__init__(size=self.item.properties.ItemSize)
        self.add(inventory_group, items)

        self.update_image(scale(self.item.texture, self.item.properties.ItemSize))
        self.rect = self.image.get_rect(center=center)

        self.apply_physics = False

    def use(self):
        if not self.object_holding:
            raise Exception("Function <use> cannot be called outside of inventory")

        props = self.item.properties

        if props.ItemType == ItemType.Basic:
            print("It`s a dumb object")
            self.kill()
            return -1

        if props.ItemType == ItemType.Consumable:
            self.object_holding.hp += self.item.properties.ConsumeProperties.Heal
            self.object_holding.armor += self.item.properties.ConsumeProperties.Armor
            self.kill()
            return -1 # Объект из инвентаря надо удалить
        
        if props.ItemType == ItemType.Weapon:
            ...

        if props.ItemType == ItemType.Look:
            ...

    def update(self):
        if self.apply_physics:
            self.gravitate()

            self.rect.y += self.vector.y
            self.vertical_collisions()


class Inventory():
    def __init__(self, game_object: Sprite) -> None:
        self.game_object = game_object # Спрайт, к которому привязан инвентарь

        self.item_sprites: Group = Group()

        self.current_index = 0 # На каком предмете селектор
        self.inventory_capacity: int = 16 # TODO: Customize this


    def get_current_item(self) -> Optional[ItemSprite]:
        if self.current_index > len(self.item_sprites) - 1:
            return None

        current_item = list(self.item_sprites)[self.current_index]
        return current_item
    

    def next_item(self, dx: int = 0):
        if dx < 0 and self.current_index != 0:
            self.current_index -= 1
        if dx > 0 and self.current_index != 15:
            self.current_index += 1

        print(self.current_index)


    def drop_item(self):
        item = self.get_current_item()
        if not item:
            return
        
        item_params = item.item

        # Убрать предмет из инвентаря
        item.kill()

        new_x, new_y = (self.game_object.rect.x + 50, self.game_object.rect.centery)
        item_spawned = ItemSprite(None, item_params.json_name, center=(new_x, new_y))
        camera.all_ordered_sprites.add(item_spawned) # Добавление в список на рендер


    # Inventory usage
    def use_item(self):
        "Uses item and does something"
        item = self.get_current_item()
        if not item:
            return

        item.use()


class InventorySprite(Sprite):
    def __init__(self, object: Sprite, inventory: Inventory):
        super().__init__()
        self.add(inventory_group)
        
        self.game_object = object # Чьи параметры будут показываться в инвентаре

        self.ratio = 0.8
        self.inventory_size = (670 * self.ratio, 370 * self.ratio) # Длина и ширина инвентаря
        #       10    650    10    = 670
        #   10   --------------
        #       |             |
        #   350 |             |
        #       |             |
        #   10  --------------
        #
        #  = 370

        self.font_title = pg.font.SysFont("Arial", int(50 * self.ratio))
        self.font_text = pg.font.SysFont("Arial", int(25 * self.ratio))
        self.padding = 25 * self.ratio

        self.inventory = inventory
        self.image = pg.Surface(self.inventory_size)
        self.rect = self.image.get_rect(topleft=(20, 20))

    def close_inventory(self):
        x, _ = self.inventory_size
        x_c, y_c = self.rect.topleft
        self.rect.topleft = (-x, y_c)

        print("Closed inventory")

    def open_inventory(self):
        x, _ = self.inventory_size
        x_c, y_c = self.rect.topleft
        self.rect.topleft = (20, y_c)

        print("Opened inventory")

    def show_parameters(self) -> Tuple[pg.Surface, List[str], Optional[Item]]:
        item = self.inventory.get_current_item()

        if not item:
            return (pg.Surface((20, 20)), ["No item chosen"], None)

        item_properties = item.item

        item_type = item_properties.properties.ItemType
        item_description = item_properties.properties.Description

        name = item_properties.properties.Name

        # Список строк (по вертикали) на рендер
        text: List[str] = [name, item_description, item_type]

        return item.item.texture, text, item_properties
    
    def render_text(self, text: str, topleft: Tuple[int, int], font: pg.font.Font, color: Tuple[int, int, int]):
        text_image = font.render(
            text, True, color
        )
        self.image.blit(text_image, topleft)

    def render_image(self, image: pg.Surface, topleft: Tuple[int, int], size: int):
        image = scale(image, (size, size))
        self.image.blit(image, topleft)

    def render_on_inventory(self):
        self.image.fill((0, 0, 0)) # Заполнение фона
        item_image, item_text, item_properties = self.show_parameters()

        margin_x, margin_y = int(10 * self.ratio), int(10 * self.ratio)
        item_image_size = int(125 * self.ratio)

        self.render_image(item_image, topleft=(margin_x, margin_y), size=item_image_size)

        for idx, text in enumerate(item_text):
            self.render_text(
                text, 
                (int(150 * self.ratio), int(idx * self.padding)), 
                self.font_text,
                color=(255, 255, 255)
            )

    def update(self):
        self.render_on_inventory()

        for item in spritecollide(self.game_object, items, False):
            item: ItemSprite = item
            
            item_params = item.item
            new_item = ItemSprite(self.game_object, item_params.json_name, (0, 0))
            new_item.apply_physics = False

            self.inventory.item_sprites.add(new_item)
            item.kill()
            
