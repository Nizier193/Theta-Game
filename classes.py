from typing import Tuple
import pygame as pg

class Camera(pg.sprite.Group):
    def __init__(self):
        super().__init__()

        self.half_width, self.half_height = 1280 / 2, 720 / 2
        self.offset = pg.Vector2(0, 0)

        self.offset_add = pg.Vector2(0, -100)

    def target_camera(self, target):
        self.offset.x = (target.rect.centerx - self.half_width) + self.offset_add.x
        self.offset.y = (target.rect.centery - self.half_height) + self.offset_add.y

    def draw_group(self, group, display, coefficient: float = 1):
        for sprites in group.sprites():
            offset_pos_x = (sprites.rect.topleft[0] - self.offset.x * coefficient)
            offset_pos_y = sprites.rect.topleft[1] - self.offset.y
            display.blit(sprites.image, (offset_pos_x, offset_pos_y))

    def custom_draw(self, target, display):
        self.target_camera(target)

        self.draw_group(backbackground, display, coefficient=0.8)
        self.draw_group(background, display)
        self.draw_group(foreground, display)
        self.draw_group(interactive, display)
        self.draw_group(active, display)
        self.draw_group(firstground, display, coefficient=0.9)
        self.draw_group(slowfirstground, display, coefficient=0.9)


camera = Camera()

class supGroup(pg.sprite.Group):
    '''Вспомогательный класс, который регулирует отрисовку объектов на экране по z_order.'''

    all__ = []
    def __init__(self, z_order: int = 1):
        super().__init__()

        self.all__.append(self)
        self.z_order = z_order

    def assembly(self, display: pg.Surface, hero):
        camera.update()
        camera.custom_draw(hero, display)

foreground = supGroup(z_order=1)
background = supGroup(z_order=2)

backbackground = supGroup(z_order=2)
interactive = supGroup(z_order=3)
active = supGroup(z_order=4)
firstground = supGroup(z_order=5)
slowfirstground = supGroup(z_order=6)

class Tile(pg.sprite.Sprite):
    '''
    Базовый класс создания клетки на поле.
    '''

    def __init__(self, size: tuple = (0, 0), addgroup_: pg.sprite.Group = None):
        super().__init__()
        self.add(camera)

        if addgroup_:
            self.add(addgroup_)

        self.image = pg.Surface(size)
        self.rect = self.image.get_rect()

    def u_image(self, newimage: pg.Surface):
        self.image = newimage
        self.rect = self.image.get_rect()

    def any_(self, f_):
        f_()


class Body(pg.sprite.Sprite):
    '''
    Класс, создающий спрайт объекта: НПС или Главного героя.
    '''

    def __init__(self, size: Tuple):
        super().__init__()
        self.add(camera)

        self.image = pg.Surface(size)
        self.rect = self.image.get_rect()

    def u_image(self, newimage: pg.Surface):
        self.image = newimage
        self.rect = self.image.get_rect()

    def any_(self, f_):
        f_()
