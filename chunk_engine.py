
from typing import Any, Tuple, List
import math

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

    def calc_chunk(self, dec_position: Tuple) -> Tuple[int, int]:
        x, y = dec_position

        chunk_size = self.tilesize * self.n_blocks

        chunk_x = math.ceil(x / chunk_size)
        chunk_y = math.ceil(y / chunk_size)

        return (chunk_x, chunk_y)
