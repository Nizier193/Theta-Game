from pathlib import Path
from typing import Any, Optional, Tuple, Union
from typing import List

import pygame as pg
from pygame.sprite import Sprite, Group, spritecollide
from pygame.transform import scale

from support.pygame_loaders import ImageLoader
from support.settings import load_settings
from common_classes import camera, inventory_group, items, active, Body

from inventory.item_models import ItemType
from inventory.item_classes import Item, ItemSprite
from inventory.item_bar import ItemBarSprite
from inventory.inventory_models import TextBarSprite

settings = load_settings()
font_path = Path(settings.font_path) / Path(settings.font_name)

ratio = 0.8
text_bar = TextBarSprite(
    (670 * ratio, 150 * ratio),
    (20 * ratio, (370 + 40) * ratio)
)


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


    def hold_item(self):
        # I`m lazy to implement this
        # TODO: Implement this ok? =)
        pass

    # Inventory usage
    def use_item(self):
        "Uses item and does something"
        item = self.get_current_item()
        if not item:
            return

        text = item.use()
        text_bar.set_new_text(text)


class InventorySprite(Sprite):
    def __init__(self, object: Sprite, inventory: Inventory):
        super().__init__()
        self.add(inventory_group)

        self.ratio = ratio

        # Дополнительная штука, отображение всех айтемов
        self.bar = ItemBarSprite(inventory)
        self.text_bar = text_bar
        
        self.game_object = object # Чьи параметры будут показываться в инвентаре

        self.inventory_size = (670 * self.ratio, 370 * self.ratio) # Длина и ширина инвентаря

        self.font_title = pg.font.Font(font_path, int(50 * self.ratio))
        self.font_text = pg.font.Font(font_path, int(25 * self.ratio))
        self.padding = 25 * self.ratio

        self.inventory = inventory

        self.texture = ImageLoader(settings.inventory_background_path, self.inventory_size).sized_image
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
            self.text_bar.close_bar()
            self.opened = False


        else:
            x, _ = self.inventory_size
            x_c, y_c = self.rect.topleft
            self.rect.topleft = (20, y_c)
            self.bar.open_bar()
            self.text_bar.open_bar()
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
        self.image.blit(self.texture, (0, 0)) # Заполнение фона
        item_image, item_text, item_properties = self.show_parameters()

        margin_x, margin_y = int(10 * self.ratio), int(10 * self.ratio)
        item_image_size = int(125 * self.ratio)

        self.render_image(item_image, topleft=(margin_x, margin_y), size=item_image_size)

        texts: List[str] = [txt for sentence in item_text for txt in self.split_sentence(sentence, 45)]

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
            if len(list(self.inventory.item_sprites)) < 16:
                item: ItemSprite = item
                
                item_params = item.item
                new_item = ItemSprite(self.game_object, item_params.json_name, (0, 0))
                new_item.apply_physics = False

                self.inventory.item_sprites.add(new_item)
                item.kill()
            
