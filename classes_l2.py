from turtle import position
from typing import Any
import pygame as pg
from pygame.transform import scale
from classes import *
import math
import random

from interactions import InteractiveConfig


FONTSIZE = 20
BASE = 'base/textures/'
textures = {
    'hero': pg.image.load(f'{BASE}hero/char_50.png'),
    'Nizier': pg.image.load(f'{BASE}NPC/Nizier.png'),
    'red6orion': pg.image.load(f'{BASE}NPC/red6orion.png'),

    'Notify_0': pg.image.load(f'{BASE}notification/square.png'),
    'Notify_1': pg.image.load(f'{BASE}notification/half_1.png'),
    'Notify_2': pg.image.load(f'{BASE}notification/central.png'),
    'Notify_3': pg.image.load(f'{BASE}notification/half_2.png'),
}

particles = {
    'Music': [pg.image.load(f'{BASE}particles/note1.png'), pg.image.load(f'{BASE}particles/note2.png')],
    'Bytes': [pg.image.load(f'{BASE}particles/byte0.png'), pg.image.load(f'{BASE}particles/byte1.png')],
    'Water': [pg.image.load(f'{BASE}particles/water1.png'), pg.image.load(f'{BASE}particles/water2.png')],
}


class Hero(Body):
    '''
    Класс главного героя со всеми ему надлежащими функциями.
    '''

                                    # Заглушка
    def __init__(self, topleft, size=(32, 32)):
        super().__init__(size=size)
        self.add(active)

        image = textures['hero']
        image = pg.transform.scale(image, (60, 60))

        self.u_image(image)
        self.rect = self.image.get_rect(topleft=topleft)
        self.position: Tuple[int, int] = (self.rect.x, self.rect.y)

        self.vector = pg.Vector2()

        self.on_surface = False

    def get_movement(self):
        keys = pg.key.get_pressed()

        return keys

    def horisontal_collisions(self):
        for sprites in foreground.sprites():
            if sprites.rect.colliderect(self.rect):
                if self.vector.x > 0:
                    self.rect.right = sprites.rect.left
                if self.vector.x < 0:
                    self.rect.left = sprites.rect.right

    def vertical_collisions(self):
        for sprites in foreground.sprites():
            if sprites.rect.colliderect(self.rect):
                if self.vector.y < 0:
                    self.rect.top = sprites.rect.bottom

                if self.vector.y > 0:
                    self.rect.bottom = sprites.rect.top

                    self.on_surface = True

    def keypress(self, event):
        if event.key == pg.K_SPACE:
            self.jump()


    def jump(self):
        if self.on_surface:
            self.vector.y -= 25

            self.on_surface = False

    def gravitate(self):
        self.vector.y += 1 if self.vector.y < 9 else 0

    def update(self):
        movement = self.get_movement()

        self.vector.x = 0

        self.vector.x += 4 if movement[pg.K_d] else 0
        self.vector.x -= 4 if movement[pg.K_a] else 0

        self.gravitate()

        # mark: Каждая коллизия должна обрабатываться отдельно после обновления координат.
        # vertical
        self.rect.y += self.vector.y
        self.vertical_collisions()

        # horisontal
        self.rect.x += self.vector.x
        self.horisontal_collisions()

        self.position = (self.rect.x, self.rect.y)


class NPC(Body):
    '''
    Класс создания персонажа, отличного от героя.
    '''

    def __init__(self,
                 topleft: tuple,
                 texture: pg.Surface):
        super().__init__()
        self.add(active)

        self.u_image(texture)
        self.rect = self.image.get_rect(topleft=topleft)


class Interactive(Tile):
    def __init__(self, topleft: tuple, texture: pg.Surface = pg.Surface((0, 0))):
        super().__init__()
        self.add(interactive)

        # Обновление текстурки на Tiled-текстуру
        self.u_image(texture)
        self.rect = self.image.get_rect(topleft=topleft)

        # Конфиг действий интерактивной штуки
        self.config: InteractiveConfig = None


class Block(Tile):
    '''Это то, по чему мы ходим.'''
    def __init__(self, position: tuple, surface: pg.Surface):
        super().__init__()
        self.add(foreground)

        # Обновление картинки
        self.u_image(surface)
        self.rect = self.image.get_rect(topleft=position)


class InvBlock(Tile):
    '''Это то, по чему мы ходим.'''
    def __init__(self, position: tuple, surface: pg.Surface):
        super().__init__()
        self.add(background)

        # Обновление картинки
        self.u_image(surface)
        self.rect = self.image.get_rect(topleft=position)


class Notification(Tile):
    '''
    Класс нотификаций, привязывается к объекту или
    координатам, после чего плавает над ней до ручного
    удаления или бесконечно.
    '''

    def __init__(
            self,
            object: Any,
            text: str,
    ):
        super().__init__()
        self.add(active)
        font = pg.font.SysFont('Arial', FONTSIZE)
        surf = font.render(text, True, (0, 0, 0))

        self.image = self.compile(surf.get_width())
        w, h = self.image.get_rect().w, self.image.get_rect().h

        x, y = (object.rect.centerx, object.rect.centery)
        self.rect = self.image.get_rect(
            bottom=y-30,
            centerx=x
        )
        self.pos = (x, y)
        self.connected_to = object

        self.image.blit(surf, ((w - surf.get_width()) / 2, (h - surf.get_height()) / 2))
        self.counter = 0

    def compile(self, pixtext):
        if pixtext < 50:
            surf = pg.Surface((50, 50))
            surf.blit(textures['Notify_0'], (0, 0))
            return surf

        if pixtext > 50 and pixtext < 100:
            surf = pg.Surface((100, 50))
            surf.blit(textures['Notify_1'], (0, 0))
            surf.blit(textures['Notify_3'], (50, 0))

            return surf

        if pixtext > 100:
            n = pixtext // 50 + 1
            surf = pg.Surface((n * 50, 50))

            surf.blit(textures['Notify_1'], (0, 0))
            surf.blit(textures['Notify_3'], ((n - 1) * 50, 0))

            for i in range(int(n - 2)):
                surf.blit(textures['Notify_2'], (i * 50 + 50, 0))

            return surf

    def sine(self):
        return math.sin(self.counter * 0.05) * 10

    def update(self):
        margin_y = 100 # Смещение по Y для красоты

        self.counter += 1
        self.counter = 0 if self.counter > 120 else self.counter

        self.rect.centerx = self.connected_to.rect.centerx
        self.rect.bottom = self.sine() + self.connected_to.rect.centery - margin_y


class Animation(Tile):
    '''
    Класс красивых анимаций, вызывается единоразово,
    создавая объект класса, а после удаляя его.
    '''

    def __init__(self, center: tuple,
                 name:str,
                 distance:int,
                 intensity:int,
                 mode:str,
                 ):
        super().__init__()

        self.add(active)

        self.rect = self.image.get_rect(center=center)

        self.center = center
        self.name = name
        self.distance = distance
        self.intensity = intensity
        self.mode = mode

    def launch(self):
        for i in range(self.intensity):
            Particle(
                center=self.center,
                texture=random.choice(particles.get(self.name)),
                distance=self.distance,
                mode=self.mode,
            )


class Particle(Tile):
    def __init__(self,
                 center: tuple,
                 texture: pg.Surface,
                 distance:int,
                 mode:str,
                ):
        super().__init__()
        self.add(active)

        self.u_image(texture)
        self.rect = self.image.get_rect(center=center)

        self.mode = mode
        self.distance = distance
        self.center = center
        self.vector = pg.Vector2(self.calc_rand(animations.get(mode)))

    def calc_rand(self, available):
        return (random.randint(available[0][0], available[0][1]), random.randint(available[1][0], available[1][1]))

    def calc_distance(self):
        return abs(self.rect.x - self.center[0]), abs(self.rect.y - self.center[1])

    def animate(self):
        dst = self.calc_distance()

        if dst[0] > self.distance or dst[1] > self.distance:
            self.rect.center = self.center
            self.vector.x, self.vector.y = self.calc_rand(animations.get(self.mode))

    def update(self):
        self.animate()

        self.rect.x += self.vector.x
        self.rect.y += self.vector.y


animations = {
    'fly': ((-3, 3), (-5, -2)),
    'fall': ((-3, 3), (2, 5)),
    'slowfly': ((-1, 1), (-3, -1)),
    'slowfall': ((-1, 1), (1, 3)),
}