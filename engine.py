from chunk_engine import ChunkEngine, Tile
from classes import active
from common_classes import camera

from classes import (
    NPC,
    Notification,
    foreground,
    background,
    interactive,
    camera
)
from classes import (
    Hero,
    Block,
    InvBlock,
    Interactive,
    Trigger
)
from models.tiled_models import ObjectPropertiesParser, Properties
from models.tiled_layers import MapLayers, LayerClass, Layers

import pygame as pg
from pygame.transform import scale
from pytmx.util_pygame import load_pygame
from typing import Tuple, List, Union

layers: MapLayers = MapLayers()
layers.add(LayerClass(Layers.Foreground, Block, foreground))
layers.add(LayerClass(Layers.Background, InvBlock, background))
layers.add(LayerClass(Layers.Interactive, Interactive, interactive))

tilesize = 48
initial_tilesize = 16
chunk_engine = ChunkEngine(
    n_blocks=5, # Количество блоков в чанке
    tilesize=tilesize, # Тайлсайз
    layers=layers
)

class Map():
    def __init__(self):
        self.tmx_data = load_pygame('base/MAP.tmx')

        self.ratio = tilesize / initial_tilesize

        # Сборка слоёв и их рендер.
        self.render_npc(Layers.Sprites) # NPC
        self.render_tiles(Layers.Background) # BG
        self.render_tiles(Layers.Foreground) # FG

        # Создание игрока
        self.hero = self.render_hero()
        camera.set_new_target(self.hero)

        self.render_object(Layers.Interactive) # Интерактивные штучки



    def render_hero(self) -> Hero:
        "Функция создания персонажа"
        hero_object = self.tmx_data.get_object_by_name('Player')
        hero_size = (hero_object.width * self.ratio, hero_object.height * self.ratio)
        hero_properties = ObjectPropertiesParser(hero_object).process()
        hero_position = int(hero_object.x * self.ratio), int(hero_object.y * self.ratio)

        hero = Hero(
            bottom_center=hero_position,
            size=hero_size,
            texture=scale(hero_object.image, hero_size),
            properties=hero_properties
        )
        self.process_object_properties(hero, hero_properties)
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

            # Пусть все прозрачные объекты типа мебели и порталов будут класса Interactive
            if not properties.trigger_params.is_trigger:
                image = scale(image, (sized_width, sized_height))

                game_object = Interactive(
                    topleft=(sized_x, sized_y),
                    texture=image,
                    properties=properties
                )
            else:
                image = scale(pg.Surface((1, 1)), (sized_width, sized_height))

                game_object = Trigger(
                    trigger_sprite=self.hero,
                    center=(sized_x, sized_y),
                    properties=properties,
                    surface=image
                )

            self.process_object_properties(game_object, properties)

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
                texture=image,
                properties=properties
            )
            self.process_object_properties(game_object, properties)

    def process_object_properties(self, object: Union[Interactive, Hero, NPC, Trigger], properties: Properties):
        "Обработка параметров объектов: Создание диалогов, партиклов, эмиттеров, etc."

        if properties.notification_params:
            text = properties.notification_params.notification_text
            # У объекта есть нотификация
            Notification(
                object=object,
                text=text
            )
        


class Game():
    def __init__(self, width: int = 1280, height: int = 720):
        pg.display.set_caption('Theta - the start of the game.')

        self.borders = (width, height)
        self.screen = pg.display.set_mode(self.borders)

        self.screen = pg.display.get_surface()
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont('Arial', 30)

        self.map = Map()
        self.hero = self.map.hero

    def display_custom_info(self, text: List[str]):
        for idx, string in enumerate(text):
            rendered_text = self.font.render(string, True, (0, 0, 0))
            self.screen.blit(rendered_text, (20, 30 * idx))

    def run(self, framerate: int = 60):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    self.hero.keypress(event)

            self.screen.fill((20, 255, 255))

            # Вывод нужной информации   
            fps = self.clock.get_fps()
            chunk = chunk_engine.calc_chunk(self.hero.position)

            # Кастомная отрисовка
            camera.update()
            camera.custom_draw(self.screen)

            # Рендер чанков
            all_positions_to_render = [npc.position for npc in active]
            chunk_engine.render_chunks(all_positions_to_render)

            self.display_custom_info([
                "Debug Info:",
                f"FPS: {round(fps)}",
                f"Chunk: {chunk}"
            ])
            pg.display.update()
            self.clock.tick(framerate)


