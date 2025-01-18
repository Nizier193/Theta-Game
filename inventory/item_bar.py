from pathlib import Path
from typing import Tuple

import pygame as pg
from pygame.sprite import Sprite
from pygame.transform import scale

from support.pygame_loaders import ImageLoader
from support.settings import load_settings
from common_classes import inventory_group

from support.settings import load_settings


settings = load_settings()


"""
Здесь описывается, как создавать экран с предметами
"""


class ItemBarSprite(Sprite):
    def __init__(self, inventory):
        super().__init__()
        self.add(inventory_group)

        self.inventory = inventory

        self.ratio =  1
        self.item_size = 64
        self.padding = 5
        self.n_row = 8
        self.n_col = 2

        self.selector = ImageLoader(settings.inventory_selector).image
        self.selector = scale(self.selector, (self.item_size * self.ratio, self.item_size * self.ratio))

        self.bar_size = (
            (self.item_size * self.n_row + (self.padding * (self.n_row + 1))) * self.ratio, # n_row айтемов в ряду + (n_row + 1) отступов
            (self.item_size * self.n_col + (self.padding * (self.n_col + 1))) * self.ratio  # n_col айтема в строке + (n_col + 1) отступов
        )
        _, height = self.bar_size

        self.texture = ImageLoader(settings.inventory_item_bar_path, self.bar_size).image
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
        self.image.blit(self.texture, (0, 0))
        
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
