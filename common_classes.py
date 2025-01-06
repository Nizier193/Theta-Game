from typing import Tuple
import pygame as pg
from models.settings import load_settings

settings = load_settings()

class Camera(pg.sprite.Group):
    "Класс для перемещения спрайтов в зависимости от положения игрока."
    def __init__(self):
        super().__init__()

        self.half_width, self.half_height = settings.width / 2, settings.height / 2 # TODO: // Make this customizable

        self.offset = pg.Vector2(0, 0)
        self.offset_add = pg.Vector2(0, -100)

        self.target: pg.sprite.Sprite = None
        self.ratio: int = 1

        # Упорядоченные в порядке отрисовки спрайты
        self.all_ordered_sprites = pg.sprite.Group()

    def target_camera(self, target):
        self.offset.x = (target.rect.centerx - self.half_width) + self.offset_add.x
        self.offset.y = (target.rect.centery - self.half_height) + self.offset_add.y

    def draw_group(self, group, display, coefficient: float = 1):
        for sprites in group.sprites():
            offset_pos_x = (sprites.rect.topleft[0] - self.offset.x * coefficient)
            offset_pos_y = sprites.rect.topleft[1] - self.offset.y
            display.blit(sprites.image, (offset_pos_x, offset_pos_y))

    def custom_draw(self, display):
        self.target_camera(self.target)

        self.draw_group(background, display)
        self.draw_group(foreground, display)
        self.draw_group(self.all_ordered_sprites, display)

    # Customize
    def set_new_target(self, target: pg.sprite.Sprite):
        "Установить камере новую цель для отслеживания"
        self.target = target

    def set_new_camera_pos(self, position: Tuple[int, int]):
        "Поставить камеру в определенную position точку"
        x, y = position
        dummy_sprite = pg.sprite.Sprite()
        dummy_sprite.image = pg.Surface((0, 0))
        dummy_sprite.rect = dummy_sprite.image.get_rect(centerx=x, centery=y)
        self.set_new_target(dummy_sprite)

camera = Camera()

# Вспомогательные группы для столкновений etc
foreground = pg.sprite.Group() # Стены, пол, etc
background = pg.sprite.Group() # Фон

interactive = pg.sprite.Group() # Мебель, картины, прозрачные объекты
particles = pg.sprite.Group() # Партиклы: пули, стрелы, сердечки
active = pg.sprite.Group() # Группа для NPC / Hero
support = pg.sprite.Group() # Группа для саппорта: Диалоги, Инвентарь, Нотификации


class Tile(pg.sprite.Sprite):
    '''Базовый класс создания клетки на поле.'''
    def __init__(self, size: tuple = (0, 0)):
        super().__init__()
        self.add(camera)

        self.image = pg.Surface(size)
        self.rect = self.image.get_rect()

    def update_image(self, newimage: pg.Surface):
        self.image = newimage
        self.rect = self.image.get_rect()

    def any_(self, f_):
        f_()


class Body(pg.sprite.Sprite):
    '''Класс, создающий спрайт объекта: НПС или Главного героя.'''
    def __init__(self, size: Tuple[int, int]):
        super().__init__()
        self.add(camera)

        self.image = pg.Surface(size)
        self.rect = self.image.get_rect()
        self.vector = pg.Vector2()


    def update_image(self, newimage: pg.Surface):
        self.image = newimage
        self.rect = self.image.get_rect()


    def horisontal_collisions(self):
        for sprites in foreground.sprites():
            if sprites.rect.colliderect(self.rect):
                if self.vector.x > 0:
                    self.rect.right = sprites.rect.left
                    self.vector.x = 0
                    
                if self.vector.x < 0:
                    self.rect.left = sprites.rect.right
                    self.vector.x = 0


    def vertical_collisions(self):
        for sprites in foreground.sprites():
            if sprites.rect.colliderect(self.rect):
                if self.vector.y < 0:
                    self.rect.top = sprites.rect.bottom

                if self.vector.y > 0:
                    self.rect.bottom = sprites.rect.top

                    self.on_surface = True


    def gravitate(self):
        if self.vector.y < 10:
            self.vector.y += 1

