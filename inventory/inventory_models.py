from typing import Tuple

from common_classes import inventory_group
from support.pygame_loaders import ImageLoader
from support.settings import load_settings

import pygame as pg
from pygame.sprite import Sprite
from pygame.transform import scale

from pathlib import Path

settings = load_settings()
font_path = Path(settings.font_path) / Path(settings.font_name)

pg.init()

# Для отображения дополнительного текста по желанию
class TextBarSprite(Sprite):
    "Для вывода дополнительной информации"
    def __init__(self, size: Tuple[int, int], topleft: Tuple[int, int]):
        super().__init__()
        self.add(inventory_group)

        self.texture = ImageLoader(settings.inventory_item_bar_path, size).image
        self.image = pg.Surface(size)

        w, h = self.image.get_size()
        x, y = topleft
        self.rect = self.image.get_rect(topleft=(-w, y))

        self.fontsize = 24
        self.font = pg.font.Font(font_path, self.fontsize)

        self.set_new_text("uwu")


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


    def set_new_text(self, text: str):
        self.image.blit(self.texture, (0, 0))
        self.text = self.split_sentence(text, 50)


    def close_bar(self):
        x, _ = self.rect.size
        _, y_c = self.rect.topleft

        self.rect.topleft = (-x, y_c)
        print("Closed bar")


    def open_bar(self):
        x, _ = self.rect.size
        _, y_c = self.rect.topleft

        self.rect.topleft  = (20, y_c)
        print("Opened bar")
   

    def update(self):
        for idx, txt in enumerate(self.text):
            text = self.font.render(txt, False, (255, 255, 255))
            self.image.blit(text, (20, 25 * idx))


# Для вывода параметров персонажа
class ParamBarSprite(Sprite):
    "Для вывода параметров персонажа"
    def __init__(self, object: Sprite, inventory):
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