import pygame as pg
from chunk_engine import ChunkEngine, Chunk, Tile

from classes_l2 import (
    NPC,
    Notification,
    foreground,
    background,
    interactive,
    supGroup
)
from classes_l2 import (
    Hero,
    Block,
    InvBlock,
    Interactive,
)
from tiled_models.interaction_models import InteractiveConfig
from tiled_models.tiled_models import ObjectPropertiesParser, Properties

from pytmx.util_pygame import load_pygame
import math

from pygame.transform import scale

from itertools import product
from typing import Dict, List, Optional, Tuple, Any

from support import MapLayers, LayerClass, Layers

example = supGroup(z_order=-1)

layers = MapLayers()
layers.add(LayerClass(Layers.Foreground, Block, foreground))
layers.add(LayerClass(Layers.Background, InvBlock, background))
layers.add(LayerClass(Layers.Interactive, Interactive, interactive))

tilesize = 32
initial_tilesize = 16
chunk_engine = ChunkEngine(
    n_blocks=5,
    tilesize=tilesize
)

class Map():
    def __init__(self):
        self.tmx_data = load_pygame('base/MAP.tmx')

        self.ratio = tilesize / initial_tilesize

        # Сборка слоёв и их рендер.
        self.render_npc(Layers.Sprites) # NPC
        self.render_tiles(Layers.Background) # BG
        self.render_tiles(Layers.Foreground) # FG
        self.render_object(Layers.Interactive) # Интерактивные штучки
        self.render_object(Layers.Furniture) # Фурнитура

        self.hero = self.render_hero()

    def render_chunks(self, dec_position: Tuple[int, int]):
        "Создание карты по положению игрока в чанке"

        radius = 5 # Количество чанков от игрока
        all_visible_chunks = chunk_engine.get_all_visible_chunks(dec_position, radius=radius)

        for chunk in chunk_engine.memory_chunks:
            if (chunk in all_visible_chunks) and not(chunk in chunk_engine.visible_chunks):
                for tile in chunk.tiles:
                    x, y = tile.position
                    surface = tile.tile
                    tile_class_name = tile.tile_class_name

                    layer = layers.get_layer(tile_class_name)
                    tile_class = layer.object_class

                    tile_object = tile_class(
                        position = (x * tilesize, y * tilesize),
                        surface = scale(surface, (tilesize, tilesize))
                    )
                    tile.object = tile_object
                
                chunk_engine.visible_chunks.append(chunk)
            
            if not(chunk in all_visible_chunks) and (chunk in chunk_engine.visible_chunks):
                for tile in chunk.tiles:
                    tile.object.kill()

                chunk_engine.visible_chunks.remove(chunk)

    def render_hero(self) -> Hero:
        "Функция создания персонажа"
        hero_object = self.tmx_data.get_object_by_name('Player')
        hero_size = (hero_object.width * self.ratio, hero_object.height * self.ratio)
        hero_properties = ObjectPropertiesParser(hero_object).process()
        hero_position = int(hero_object.x * self.ratio), int(hero_object.y * self.ratio)

        hero = Hero(
            bottom_center=hero_position,
            size=hero_size,
            texture=scale(hero_object.image, hero_size)
        )
        self.process_object_params(hero, hero_properties)
        return hero

    def render_tiles(self, name: str):
        "Чанкование тайлов по их положению на карте"

        layer = self.tmx_data.get_layer_by_name(name)
        tiles = layer.tiles()

        for X, Y, SURFACE in tiles:
            position = (X * tilesize, Y * tilesize)
            if not chunk_engine.get_memory_chunk(position):
                chunk_engine.create_memory_chunk(position)
            
            tile = Tile(
                tile = SURFACE,
                position = (X, Y),
                tile_name = name
            )

            chunk_engine.add_memory_chunk(position, tile)

    def render_object(self, name: str):
        layer = self.tmx_data.get_layer_by_name(name)

        for object in layer:
            image = object.image
            sized_width = object.width * self.ratio
            sized_height = object.height * self.ratio

            sized_x = int(object.x * self.ratio)
            sized_y = int(object.y * self.ratio)

            # Параметры Tiled-объекта с карты
            properties = ObjectPropertiesParser(object).process()

            if image: # Если картинка у объекта есть
                # Пусть все прозрачные объекты типа мебели и порталов будут класса Interactive
                image = scale(image, (sized_width, sized_height))
                game_object = Interactive(
                    topleft=(sized_x, sized_y),
                    texture=image
                )          
            else:
                game_object = Interactive(topleft=(sized_x, sized_y))          

            # Присваивание каждому из интерактивных элементов его назначение
            # Создание и заполнение
            self.process_object_params(
                game_object=game_object, 
                object_properties=properties
            )

    def render_npc(self, name: str):
        # Отрендерить NPC-like объекты
        layer = self.tmx_data.get_layer_by_name(name)

        for object in layer:
            image = object.image
            sized_width = object.width * self.ratio
            sized_height = object.height * self.ratio

            sized_x = int(object.x * self.ratio)
            sized_y = int(object.y * self.ratio)

            # Парсинг даты для персонажа
            properties = ObjectPropertiesParser(object).process()
            image = scale(image, (sized_width, sized_height))
            game_object = NPC(
                bottom_center=(sized_x, sized_y),
                size=(sized_width, sized_height),
                texture=image
            )

            # Создание и заполнение
            self.process_object_params(
                game_object=game_object, 
                object_properties=properties
            )

    def process_object_params(self, game_object: NPC, object_properties: Properties):
        "Функция для создания всех необходимых интерактивных плюшек у спрайта"
        "К примеру, нотификация или телепорт штуки"
        # Создание конфига для интерактивного элемента
        config = InteractiveConfig(game_object)

        # Присваивание каждому из интерактивных элементов его назначение

        # Если у объекта есть нотификация
        if object_properties.notification_params:
            notification_params = object_properties.notification_params

            notification_text = notification_params.notification_text
            notification_object = Notification(game_object, notification_text)

            config.notification.connected_to = game_object
            config.notification.text = notification_text
            config.notification.notification = notification_object
        
        # Параметры движения
        if object_properties.movement_params:
            movement_params = object_properties.movement_params
            max_speed = movement_params.max_speed
            wait_time = movement_params.wait_time

            config.movement.wait_time = wait_time
            config.movement.max_speed = max_speed

        game_object.config = config


class Game():
    def __init__(self,
                 width: int = 1280,
                 height: int = 720):

        pg.display.set_caption('Theta - the start of the game.')

        self.borders = (width, height)
        self.screen = pg.display.set_mode(self.borders)

        self.screen = pg.display.get_surface()
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont('Arial', 45)

        self.map = Map()
        self.hero = self.map.hero

    def run(self, framerate: int = 50):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    self.hero.keypress(event)

            self.screen.fill((20, 255, 255))

            # Рендер по z_order
            example.assembly(self.screen, self.hero)

            # Отображение параметров игры
            self.screen.blit(self.font.render(str(round(self.clock.get_fps())), True, (0, 0, 0)), (20, 60))
            self.screen.blit(self.font.render(str(chunk_engine.calc_chunk(self.hero.position)), True, (0, 0, 0)), (20, 20))

            # Рендер чанков
            hero_position = self.hero.position
            self.map.render_chunks(hero_position)

            pg.display.update()
            self.clock.tick(framerate)


