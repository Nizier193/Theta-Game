from pathlib import Path
from typing import Any, Optional, Tuple, Union
from typing import List

import pygame as pg
from pygame.sprite import Sprite, Group, spritecollide
from pygame.transform import scale
import json

from models.settings import load_settings
from common_classes import camera, inventory_group, items, active, Body
from inventory.item_models import ItemParams, ItemType

settings = load_settings()
ratio = settings.tilesize / settings.initial_tilesize

# Предмет в инвентаре
class Item():
    def __init__(self, json_name: str, basepath: Path = Path(settings.item_basepath)) -> None:
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
        self.rect = self.image.get_rect(topleft=center)

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
        


class ParamBarSprite(Sprite):
    def __init__(self, object: Sprite, inventory: Inventory):
        super().__init__()
        self.add(inventory_group)

        self.font = pg.font.SysFont("Arial", 24)

        self.object = object
        self.inventory = inventory

        self.ratio = 1
        self.row_size = 128
        self.col_size = 64
        self.n_col = 4

        self.padding = 5

        self.bar_size = (
            self.row_size + (self.padding * 2), 
            (self.col_size + self.padding) * self.n_col
        )
        self.image = pg.Surface(self.bar_size)

        width, height = self.bar_size
        self.rect = self.image.get_rect(
            topleft = (settings.width - width - 20, settings.height - height - 20)
        )

    def render_image(self, image: pg.Surface, topleft: Tuple[int, int]):
        image = scale(image, (self.col_size, self.col_size))
        self.image.blit(image, topleft)

    def render_text(self, text: str, topleft: Tuple[int, int], font: pg.font.Font, color: Tuple[int, int, int]):
        text_image = font.render(
            text, True, color
        )
        self.image.blit(text_image, topleft)    
    
    def update(self):
        self.image.fill((0, 0, 0))

        # for idx, metric in enumerate(self.metrics):
        #     posx = self.padding
        #     posy = self.padding + self.col_size * idx
        #     self.render_image(metric.image, topleft=(posx, posy))
        #     metric.get_metric()
        #     self.render_text(metric.metric, (posx + 64, posy), self.font, (255, 255, 255))
    


class ItemBarSprite(Sprite):
    def __init__(self, inventory: Inventory):
        super().__init__()
        self.add(inventory_group)

        self.inventory = inventory

        self.ratio =  1
        self.item_size = 64
        self.padding = 5
        self.n_row = 8
        self.n_col = 2

        self.selector = pg.image.load(settings.item_basepath / Path("selector.png"))
        self.selector = scale(self.selector, (self.item_size * self.ratio, self.item_size * self.ratio))

        self.bar_size = (
            (self.item_size * self.n_row + (self.padding * (self.n_row + 1))) * self.ratio, # n_row айтемов в ряду + (n_row + 1) отступов
            (self.item_size * self.n_col + (self.padding * (self.n_col + 1))) * self.ratio  # n_col айтема в строке + (n_col + 1) отступов
        )
        _, height = self.bar_size

        self.image = pg.Surface(self.bar_size)
        x, _ = self.bar_size
        self.rect = self.image.get_rect(topleft = (-x, settings.height - height - 20))

    def close_bar(self):
        x, _ = self.bar_size
        _, y_c = self.rect.topleft

        self.rect.topleft = (-x, y_c)
        print("Closed bar")
   
    def open_bar(self):
        x, _ = self.bar_size
        _, y_c = self.rect.topleft

        self.rect.topleft  = (20, y_c)
        print("Opened bar")
   
    def render_image(self, image: pg.Surface, topleft: Tuple[int, int]):
        image = scale(image, (self.item_size, self.item_size))
        self.image.blit(image, topleft)
 
    def point_on_selected(self):
        selected_item = self.inventory.current_index

        n_row = selected_item // 8
        n_col = selected_item % 8

        x = n_col * (self.item_size + self.padding) + self.padding
        y = n_row * (self.item_size + self.padding) + self.padding

        self.image.blit(self.selector, (x, y))

    def update(self):
        self.image.fill((0, 0, 0)) # Заглушка на фон
        
        for idx, item in enumerate(self.inventory.item_sprites):
            n_row = idx // 8
            n_col = idx % 8

            image: pg.Surface = item.item.texture
            self.render_image(
                image, 
                (n_col * (self.item_size + self.padding) + self.padding, 
                 n_row * (self.item_size + self.padding) + self.padding)
            )

        self.point_on_selected()

            

class InventorySprite(Sprite):
    def __init__(self, object: Sprite, inventory: Inventory):
        super().__init__()
        self.add(inventory_group)

        # Дополнительная штука, отображение всех айтемов
        self.bar = ItemBarSprite(inventory)
        
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

        x, _ = self.inventory_size
        self.rect = self.image.get_rect(topleft=(-x, 20))
        self.opened = False

    def open_close_inventory(self):
        if self.opened:
            x, _ = self.inventory_size
            x_c, y_c = self.rect.topleft
            self.rect.topleft = (-x, y_c)
            self.bar.close_bar()
            self.opened = False
        else:
            x, _ = self.inventory_size
            x_c, y_c = self.rect.topleft
            self.rect.topleft = (20, y_c)
            self.bar.open_bar()
            self.opened = True

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

    def split_sentence(self, sentence, num_of_char):
        split_sentence = []
        sentence_word = sentence.split(' ')
        current_line = ""
        for word in sentence_word:
            if len(current_line) + len(word) <= num_of_char:
                current_line += word + " "
            else:
                split_sentence.append(current_line)
                current_line = word + " "
        split_sentence.append(current_line)
        return split_sentence

    def render_on_inventory(self):
        self.image.fill((0, 0, 0)) # Заполнение фона
        item_image, item_text, item_properties = self.show_parameters()

        margin_x, margin_y = int(10 * self.ratio), int(10 * self.ratio)
        item_image_size = int(125 * self.ratio)

        self.render_image(item_image, topleft=(margin_x, margin_y), size=item_image_size)

        texts: List[str] = [txt for sentence in item_text for txt in self.split_sentence(sentence, 50)]

        # Отображение основного текста
        for idx, text in enumerate(texts):
            addictional_padding = 0
            if idx == len(texts) - 1:
                addictional_padding = 10

            self.render_text(
                text, 
                (int(150 * self.ratio), int(idx * self.padding + addictional_padding)), 
                self.font_text,
                color=(255, 255, 255)
            )

        # Отображение сбоку
        if item_properties:
            props = item_properties.properties
            item_type: str = item_properties.properties.ItemType
            if item_type == ItemType.Consumable:
                texts: List[str] = [
                    f"Heal: {props.ConsumeProperties.Heal}",
                    f"Armor: {props.ConsumeProperties.Armor}"
                ]
            
            for idx, text in enumerate(texts):
                self.render_text(
                    text, 
                    (int(10 * self.ratio), int(idx * self.padding + 150 * self.ratio)), 
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
            
