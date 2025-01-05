from common_classes import (
    Body, Tile,
    foreground,
    background,
    active,
    support,
    interactive,
    particles
)

import math
import random
import pygame as pg
from pygame.transform import scale
from typing import Any, Optional, Tuple, cast

from pathlib import Path

from models.tiled_models import Properties

basepath = Path("base/textures")
textures = {
    "square_notify_piece": pg.image.load(basepath / Path("notification/square.png")),
    "left_notify_piece": pg.image.load(basepath / Path("notification/half_1.png")),
    "middle_notify_piece": pg.image.load(basepath / Path("notification/central.png")),
    "right_notify_piece": pg.image.load(basepath / Path("notification/half_2.png"))
}

class Hero(Body):
    '''Класс главного героя со всеми ему надлежащими функциями.'''
                                    # Заглушка
    def __init__(self, bottom_center, properties: Properties, size=(32, 32), texture: pg.Surface=pg.Surface((32, 32))):
        super().__init__(size=size)
        self.add(active)

        self.u_image(texture)
        centerx, bottom = bottom_center
        self.rect = self.image.get_rect(
            centerx=centerx,
            bottom=bottom
        )
        self.position: Tuple[int, int] = (self.rect.x, self.rect.y)

        self.on_surface = False
        self.acceleration_factor = 1
        self.max_speed = 6

        self.properties: Properties = properties

    def get_movement(self):
        keys = pg.key.get_pressed()
        return keys

    def keypress(self, event):
        if event.key == pg.K_SPACE:
            self.jump()

    def jump(self):
        if self.on_surface:
            self.vector.y -= 25
            self.on_surface = False


    def update(self):
        movement = self.get_movement()

        if movement[pg.K_d]:
            if self.vector.x < self.max_speed:
                self.vector.x += self.acceleration_factor
        else:
            if self.vector.x > 0:
                self.vector.x -= self.acceleration_factor
        
        if movement[pg.K_a]:
            if self.vector.x > -self.max_speed:
                self.vector.x -= self.acceleration_factor
        else:
            if self.vector.x < 0:
                self.vector.x += self.acceleration_factor

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
    '''Класс создания персонажа, отличного от героя.'''
    def __init__(self, bottom_center: tuple, size: Tuple[int, int], properties: Properties, texture: pg.Surface):
        super().__init__(size)
        self.add(active)

        self.u_image(texture)
        centerx, bottom = bottom_center
        self.rect = self.image.get_rect(
            centerx=centerx,
            bottom=bottom
        )

        # TODO: // Connect ticks to seconds directly with FPS
        self.properties = properties
        self.tick_counter = 0
        self.position = (self.rect.x, self.rect.y)

    
    def simple_ai(self):
        wait_time = self.properties.movement_params.wait_time
        max_speed = self.properties.movement_params.max_speed

        if self.tick_counter % (wait_time * 60) == 0:
            # Раз в wait_time секунд
            self.vector.x = random.randint(-max_speed, max_speed)

    def __repr__(self) -> str:
        text = f"""

pos: [{self.rect.x} {self.rect.y}]
vector: [{self.vector.x} {self.vector.y}]
"""
        return text
    
    def update(self) -> None:
        self.tick_counter += 1 # Обновление счётчика
        self.gravitate()

        # Простой ИИ для движения персонажа
        self.simple_ai()

        self.rect.y += self.vector.y
        self.vertical_collisions()

        self.rect.x += self.vector.x
        self.horisontal_collisions()

        self.position = (self.rect.x, self.rect.y)


class Interactive(Tile):
    def __init__(self, topleft: tuple, properties: Properties, texture: pg.Surface = pg.Surface((0, 0))):
        super().__init__()
        self.add(interactive)

        self.texture = texture

        # Обновление текстурки на Tiled-текстуру
        self.u_image(texture)
        self.rect = self.image.get_rect(topleft=topleft)

        # Конфиг действий интерактивной штуки, обязательно есть
        self.properties: Properties = properties

        # Если является эмиттером - удалить текстурку
        if self.properties.particles_params.is_particle_emitter:
            # Группа для партиклов эмиттера
            # Обновление спрайта эмиттера на ничего
            self.particle_group = pg.sprite.Group()

    
    def emit_particles(self):
        # Чтобы партиклы разлетались от этого объекта
        intensity: int = self.properties.particles_params.intensity
        
        if len(self.particle_group) <= intensity:
            p = Particle(
                position=(self.rect.centerx, self.rect.centery),
                surface=self.texture,
                emitter_properties=self.properties
            )
            self.particle_group.add(p)


    def update(self, *args: Any, **kwargs: Any) -> None:
        if self.properties.particles_params.is_particle_emitter:
            self.emit_particles()
        
        return super().update(*args, **kwargs)


class Block(Tile):
    '''Это то, по чему мы ходим.'''
    def __init__(self, position: tuple, surface: pg.Surface):
        super().__init__()
        self.add(foreground)

        # Обновление картинки
        self.u_image(surface)
        self.rect = self.image.get_rect(topleft=position)


class InvBlock(Tile):
    '''Это то, что прозрачное.'''
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
    def __init__(self, object: Any, text: str):
        super().__init__()
        self.add(support)             # TODO : // Customize fontsize
        font = pg.font.SysFont('Arial', 20)
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
        self.counter = random.randint(0, 120)

    def compile(self, pixtext):
        if pixtext < 50:
            surf = pg.Surface((50, 50))
            surf.blit(textures['square_notify_piece'], (0, 0))
            return surf

        if pixtext > 50 and pixtext < 100:
            surf = pg.Surface((100, 50))
            surf.blit(textures['left_notify_piece'], (0, 0))
            surf.blit(textures['right_notify_piece'], (50, 0))

            return surf

        if pixtext > 100:
            n = pixtext // 50 + 1
            surf = pg.Surface((n * 50, 50))

            surf.blit(textures['left_notify_piece'], (0, 0))
            surf.blit(textures['right_notify_piece'], ((n - 1) * 50, 0))

            for i in range(int(n - 2)):
                surf.blit(textures['middle_notify_piece'], (i * 50 + 50, 0))

            return surf

    def sine(self):
        return math.sin(self.counter * 0.05) * 10

    def update(self):
        margin_y = 100 # Смещение по Y для красоты

        self.counter += 1
        self.counter = 0 if self.counter > 120 else self.counter

        self.rect.centerx = self.connected_to.rect.centerx
        self.rect.bottom = self.sine() + self.connected_to.rect.centery - margin_y


class Particle(Tile):
    """Партикл, прозрачный двигающийся объект"""
    def __init__(self, position: Tuple[int, int], surface: pg.Surface, emitter_properties: Properties):
        super().__init__()
        self.add(background)
        
        # Спавн
        self.spawn_pos = position

        # Обновление спрайта
        self.u_image(surface)
        self.rect = self.image.get_rect(center=position)

        # Конфиг с описанием эмиттера партиклов
        self.emitter_props: Properties = emitter_properties

        # Скорость партиклов в обе стороны
        self.distance: int = self.emitter_props.particles_params.distance
        spread: int = self.emitter_props.particles_params.spread
        side: int = self.emitter_props.particles_params.side
        top: int = self.emitter_props.particles_params.top
        speed: int = self.emitter_props.particles_params.speed

        self.speed_const_x = speed * side + random.randint(-spread, spread)
        self.speed_const_y = speed * top + random.randint(-spread, spread)

    def calc_dist(self, spawn_pos, current_pos) -> int:
        spx, spy = spawn_pos # Изначальное положение
        cpx, cpy = current_pos # Конечное положение

        dx = abs(cpx - spx)
        dy = abs(cpy - spy)
        
        return int(math.sqrt(dx ** 2 + dy ** 2))
    
    def update(self) -> None:
        if self.calc_dist(self.spawn_pos, (self.rect.centerx, self.rect.centery)) > self.distance:
            self.kill()

        self.rect.x += self.speed_const_x
        self.rect.y += self.speed_const_y
