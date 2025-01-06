
from typing import Any, Tuple, List
from pygame.transform import scale
import math

from models.tiled_layers import MapLayers

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

class ChunkEngine:
    def __init__(self, layers: MapLayers, n_blocks: int = 5, tilesize: int = 16):
        self.n_blocks = n_blocks
        self.tilesize = tilesize
        self.layers = layers

        self.memory_chunks: List[Chunk] = [] # Все чанки хранятся в памяти
        self.visible_chunks: List[Chunk] = [] # Отображаемые чанки

    def get_visible_chunk(self, dec_position: Tuple[int, int]) -> Chunk:
        "Получение видимого чанка на карте"
        chu_position = self.calc_chunk(dec_position)

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
        "Добавление чанка в memory карту чанков"

        chu_position = self.calc_chunk(dec_position)
        chunk = Chunk(chu_position)
        self.visible_chunks.append(chunk)

        return chunk

    def add_visible_chunk(self, dec_position: Tuple[int, int], tile: Tile):
        "Добавление тайла в memory карту чанков"
        chu_position = self.calc_chunk(dec_position)

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

    def calc_chunk(self, dec_position: Tuple) -> Tuple[int, int]:
        x, y = dec_position

        chunk_size = self.tilesize * self.n_blocks

        chunk_x = math.ceil(x / chunk_size)
        chunk_y = math.ceil(y / chunk_size)

        return (chunk_x, chunk_y)
    
    def render_chunks(self, dec_positions: List[Tuple[int, int]]):
        "Создание карты по положению игрока в чанке"

        radius = 5 # Количество чанков от игрока
        all_visible_chunks: List[Chunk] = []
        for position in dec_positions:
            visible_chunks_in_area = self.get_all_visible_chunks(position, radius=radius)
            for chunk in visible_chunks_in_area:
                if chunk not in all_visible_chunks:
                    all_visible_chunks.append(chunk)

        for chunk in self.memory_chunks:
            if (chunk in all_visible_chunks) and not(chunk in self.visible_chunks):
                for tile in chunk.tiles:
                    x, y = tile.position
                    surface = tile.tile
                    tile_class_name = tile.tile_class_name

                    layer = self.layers.get_layer(tile_class_name)
                    tile_class = layer.object_class

                    tile_object = tile_class(
                        position = (x * self.tilesize, y * self.tilesize),
                        surface = scale(surface, (self.tilesize, self.tilesize))
                    )
                    tile.object = tile_object
                
                self.visible_chunks.append(chunk)
            
            if not(chunk in all_visible_chunks) and (chunk in self.visible_chunks):
                for tile in chunk.tiles:
                    tile.object.kill()

                self.visible_chunks.remove(chunk)
