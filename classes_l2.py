import pygame as pg
from classes import *
import math
import random


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

    def __init__(self, topleft):
        super().__init__()
        self.add(active)

        image = textures['hero']
        image = pg.transform.scale(image, (60, 60))

        self.u_image(image)
        self.rect = self.image.get_rect(topleft=topleft)

        self.vector = pg.Vector2()

        self.on_surface = False

    def get_movement(self):
        keys = pg.key.get_pressed()

        return keys

    def horisontal_collisions(self):
        for sprites in obstacles.sprites():
            if sprites.rect.colliderect(self.rect):
                if self.vector.x > 0:
                    self.rect.right = sprites.rect.left
                if self.vector.x < 0:
                    self.rect.left = sprites.rect.right

    def vertical_collisions(self):
        for sprites in obstacles.sprites():
            if sprites.rect.colliderect(self.rect):
                if self.vector.y < 0:
                    self.rect.top = sprites.rect.bottom

                if self.vector.y > 0:
                    self.rect.bottom = sprites.rect.top

                    self.on_surface = True

    def keypress(self, event):
        if event.key == pg.K_SPACE:
            self.jump()

        if event.key == pg.K_f:
            self.interactive()

    def interactive(self):
        for sprites in pg.sprite.spritecollide(self, interactive, False):
            desc = sprites.description

            if desc.get('name') == 'closet':
                index = desc['index']
                for obj in interactive:
                    desc_obj = obj.description

                    if desc_obj['name'] == 'closet' and \
                            obj != sprites and desc_obj['index'] == index:
                        self.rect.bottom = obj.rect.bottom
                        self.rect.centerx = obj.rect.centerx

            if desc.get('name') == 'door':
                index = desc['index']
                for obj in interactive:
                    desc_obj = obj.description

                    if desc_obj['name'] == 'door' and \
                            obj != sprites and desc_obj['index'] == index:
                        self.rect.bottom = obj.rect.bottom
                        self.rect.centerx = obj.rect.centerx

    def push_interactive(self, movement):
        for sprites in pg.sprite.spritecollide(self, interactive, False):
            desc = sprites.description
            if movement[pg.K_SPACE]:
                if desc.get('name') == 'Ladders':
                    self.vector.y = -5
                    self.on_surface = False

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

        self.push_interactive(movement)
        self.gravitate()

        # mark: Каждая коллизия должна обрабатываться отдельно после обновления координат.
        # vertical
        self.rect.y += self.vector.y
        self.vertical_collisions()

        # horisontal
        self.rect.x += self.vector.x
        self.horisontal_collisions()


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
    '''
    Класс создания интерактивных вещей, объектов.
    К ним можно прикрепить нотификацию для упрощения
    понимания интерактивчика.
    '''

    def __init__(self,
                 topleft: tuple,
                 texture: pg.Surface,
                 description: dict
                 ):
        super().__init__()
        self.add(interactive)

        self.description = description

        self.u_image(texture)
        self.rect = self.image.get_rect(topleft=topleft)

        if self.description.get('notification'):
            notificate = self.description.get('notification')

            Notification(
                self,
                {'text': notificate['text']}
            )

class FG(Tile):
    '''
    Класс создания прозрачных по хитбоксам
    клеток. Используется в основном для декораций.
    '''

    def __init__(self,
                 topleft: tuple,
                 texture: pg.Surface,
                 group: pg.sprite.Group,
                 ):
        super().__init__()
        self.add(group)

        self.u_image(texture)
        self.rect = self.image.get_rect(topleft=topleft)


class BG(Tile):
    '''
    Класс создания прозрачных по хитбоксам
    клеток. Используется в основном для декораций.
    '''

    def __init__(self,
                 topleft: tuple,
                 texture: pg.Surface):
        super().__init__()
        self.add(passive)

        self.u_image(texture)
        self.rect = self.image.get_rect(topleft=topleft)


class Block(Tile):
    '''
    Класс непрозрачных по хитбоксам объектов.
    Используется для создания препятствий герою.
    '''

    def __init__(self,
                 topleft: tuple,
                 texture: pg.Surface):
        super().__init__()
        self.add(obstacles)

        self.u_image(texture)
        self.rect = self.image.get_rect(topleft=topleft)


class Notification(Tile):
    '''
    Класс нотификаций, привязывается к объекту или
    координатам, после чего плавает над ней до ручного
    удаления или бесконечно.
    '''

    def __init__(
            self,
            notificated,
            description: dict,
    ):
        super().__init__()

        font = pg.font.SysFont('Arial', FONTSIZE)

        self.add(active)

        text = description['text']
        surf = font.render(text, True, (0, 0, 0))

        self.pos = notificated

        self.image = self.compile(surf.get_width())
        w, h = self.image.get_rect().w, self.image.get_rect().h

        if type(self.pos) is not tuple:
            self.rect = self.image.get_rect(
                bottom=notificated.rect.top - 30,
                centerx=notificated.rect.centerx
            )
            self.pos = notificated.rect.center

        else:
            self.rect = self.image.get_rect(
                bottom=notificated[1] - 30,
                centerx=notificated[0]
            )
            self.pos = notificated[0], notificated[1]

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
        self.counter += 1

        self.counter = 0 if self.counter > 120 else self.counter

        self.rect.y = self.sine() + self.pos[1] - 120


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