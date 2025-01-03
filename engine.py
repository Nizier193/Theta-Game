import pygame as pg

from classes_l2 import (
    obstacles,
    interactive,
    supGroup
)
from classes_l2 import (
    Hero,
    Block,
    Interactive,
)

from pytmx.util_pygame import load_pygame
import math

from pygame.transform import scale

from itertools import product
from typing import Dict, List, Tuple, Any

from support import MapLayers, LayerClass, Layers

example = supGroup(z_order=-1)

'''
Здесь расположен основной код всей системы.
'''

layers = MapLayers()
layers.add(LayerClass(Layers.Foreground, Block, obstacles))
layers.add(LayerClass(Layers.Interactive, Interactive, interactive))

class Tile:
    def __init__(self, tile: Any, position: Tuple[int, int], tile_name: str):
        self.tile = tile
        self.position = position
        self.tile_class_name = tile_name

        self.object = None

    def __repr__(self) -> str:
        return f"Pos: {self.position}, tile_class_name: {self.tile_class_name}"

class Chunk:
    def __init__(self, chu_position: Tuple[int, int]):
        self.chu_position = chu_position
        self.tiles: List[Tile] = []

    def add(self, tile: Tile):
        self.tiles.append(tile)

    def __repr__(self) -> str:
        return f"""
Chunk: {self.chu_position}
Tiles: {self.tiles[:5]}
N_tiles: {len(self.tiles)}
"""

# dec_position - в декартовой системе
# chu_position - в системе чанков

class ChunkEngine:
    def __init__(self, n_blocks: int = 5, tilesize: int = 16):
        self.n_blocks = n_blocks
        self.tilesize = tilesize

        self.memory_chunks: List[Chunk] = [] # Все чанки хранятся в памяти
        self.visible_chunks: List[Chunk] = [] # Отображаемые чанки

    def get_visible_chunk(self, dec_position: Tuple[int, int]) -> Chunk:
        chu_position = self.calc_chunk(dec_position)

        "Получение видимого чанка на карте"
        chunk = list(filter(lambda x: x.chu_position == chu_position, self.visible_chunks))
        return chunk[-1] if chunk else None
    
    def get_memory_chunk(self, dec_position: Tuple[int, int]) -> Chunk:
        "Получение сохраненного чанка на карте"
        chu_position = self.calc_chunk(dec_position)

        chunk = list(filter(lambda x: x.chu_position == chu_position, self.memory_chunks))
        return chunk[-1] if chunk else None
    
    def create_memory_chunk(self, dec_position: Tuple[int, int]) -> Chunk:
        "Добавление чанка в memory карту чанков"
        chu_position = self.calc_chunk(dec_position)

        chunk = Chunk(chu_position)
        self.memory_chunks.append(chunk)

        return chunk

    def add_memory_chunk(self, dec_position: Tuple[int, int], tile: Tile):
        "Добавление тайла в memory карту чанков"
        chu_position = self.calc_chunk(dec_position)

        if not self.get_memory_chunk(dec_position):
            raise Exception(f"There`s no that memory chunk -> {chu_position}")

        chunk = self.get_memory_chunk(dec_position)
        chunk.add(tile)

    def create_visible_chunk(self, dec_position: Tuple[int, int]) -> Chunk:
        chu_position = self.calc_chunk(dec_position)

        "Добавление чанка в memory карту чанков"
        chunk = Chunk(chu_position)
        self.visible_chunks.append(chunk)

        return chunk

    def add_visible_chunk(self, dec_position: Tuple[int, int], tile: Tile):
        chu_position = self.calc_chunk(dec_position)

        "Добавление тайла в memory карту чанков"
        if not self.get_visible_chunk(chu_position):
            raise Exception(f"There`s no that memory chunk -> {chu_position}")

        chunk = self.get_visible_chunk(chu_position)
        chunk.add(tile)

    def get_all_visible_chunks(self, dec_position: Tuple[int, int], radius: int = 2):
        "Получение всех чанков, которые видны с position радиусом radius"
        pos_x, pos_y = self.calc_chunk(dec_position)

        def fc(c: Chunk, r: int):
            x, y = c.chu_position
            return (x - r <= pos_x <= x + r) and (y - r <= pos_y <= y + r)
        
        return list(filter(lambda c: fc(c, radius), self.memory_chunks))

    def clear_chunks(self, dec_position: Tuple[int, int], radius: int = 2):
        "Удаление невидимых чанков radius в чанках"
        visible_chunks: List[Chunk] = self.get_all_visible_chunks(dec_position, radius)
        invisible_chunks: List[Chunk] = []

        pos_x, pos_y = self.calc_chunk(dec_position)
        def fc(c: Chunk, r: int):
            x, y = c.chu_position
            return (x - r <= pos_x <= x + r) and (y - r <= pos_y <= y + r)

        # Список невидимых чанков
        for chunk in self.visible_chunks:
            if not fc(chunk, radius):
                invisible_chunks.append(chunk)

        # Удаление тайлов, которые не видно
        for chunk in invisible_chunks:
            for tile in chunk.tiles:
                tile.object.kill()

            self.visible_chunks.remove(chunk)

    def calc_chunk(self, dec_position: Tuple) -> Tuple[int, int]:
        x, y = dec_position

        chunk_size = self.tilesize * self.n_blocks

        chunk_x = math.ceil(x / chunk_size)
        chunk_y = math.ceil(y / chunk_size)

        return (chunk_x, chunk_y)

tilesize = 64
initial_tilesize = 16
chunk_engine = ChunkEngine(
    n_blocks=5,
    tilesize=tilesize
)

class Map():
    def __init__(self):
        self.tmx_data = load_pygame('base/MAP.tmx')

        ratio = tilesize / initial_tilesize

        hero_position = self.tmx_data.get_object_by_name('Player')
        self.hero_position = int(hero_position.x * ratio), int(hero_position.y * ratio)
        self.hero = Hero(topleft=self.hero_position)

        # Сборка слоёв и их рендер.
        self.render_tiles(Layers.Foreground)

    def render_chunks(self, dec_position: Tuple[int, int]):
        "Создание карты по положению игрока в чанке"


        radius = 2 # Количество чанков от игрока

        # Добавление в список видимых чанков те, что стало видно
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

            # Проверка на то, что имя тайла есть в списке тайлов
            assert name in list(Layers.__annotations__.keys())
            chunk_engine.add_memory_chunk(position, tile)


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


