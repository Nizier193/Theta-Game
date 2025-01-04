from chunk_engine import ChunkEngine, Chunk, Tile
from classes import active
from common_classes import camera

from classes import (
    NPC,
    Notification,
    foreground,
    background,
    interactive,
)
from classes import (
    Hero,
    Block,
    InvBlock,
    Interactive,
)
from models.interaction_models import InteractiveConfig
from models.tiled_models import ObjectPropertiesParser, Properties
from models.tiled_layers import MapLayers, LayerClass, Layers

import pygame as pg
from pygame.transform import scale
from pytmx.util_pygame import load_pygame
from typing import Tuple, List

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

    def render_chunks(self, dec_positions: List[Tuple[int, int]]):
        "Создание карты по положению игрока в чанке"

        radius = 1 # Количество чанков от игрока
        all_visible_chunks: List[Chunk] = []
        for position in dec_positions:
            visible_chunks_in_area = chunk_engine.get_all_visible_chunks(position, radius=radius)
            for chunk in visible_chunks_in_area:
                if chunk not in all_visible_chunks:
                    all_visible_chunks.append(chunk)

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

        if object_properties.particles_params:
            particles_params = object_properties.particles_params

            config.particles.is_particle_emitter = particles_params.is_particle_emitter
            config.particles.intensity = particles_params.intensity
            config.particles.side = particles_params.side
            config.particles.top = particles_params.top
            config.particles.distance = particles_params.distance
            config.particles.speed = particles_params.speed
            config.particles.spread = particles_params.spread

        game_object.config = config


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
            camera.custom_draw(self.hero, self.screen)

            # Рендер чанков
            all_positions_to_render = [npc.position for npc in active]
            self.map.render_chunks(all_positions_to_render)

            self.display_custom_info([
                "Debug Info:",
                f"FPS: {round(fps)}",
                f"Chunk: {chunk}"
            ])

            pg.display.update()
            self.clock.tick(framerate)


