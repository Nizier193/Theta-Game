from chunk_engine import ChunkEngine, Tile
from classes import active
from common_classes import camera, settings, inventory_group
from models.support import TiledClassNames
from inventory.inventory import InventorySprite, Inventory, ItemSprite

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
from models.tiled_models import ObjectPropertiesParser, Properties, ObjectTypeNames
from models.tiled_layers import MapLayers, LayerClass, Layers

import pygame as pg
from pygame.transform import scale, rotate
from pytmx.util_pygame import load_pygame
from typing import Optional, Tuple, List, Union, Any

# Для описания тайлов карты: Background и Foreground
# остальное описывается в функции render_object
layers: MapLayers = MapLayers()
layers.add(LayerClass(Layers.Foreground, Block))
layers.add(LayerClass(Layers.Background, InvBlock))

tilesize = settings.tilesize
initial_tilesize = settings.initial_tilesize
n_blocks_chunk = settings.n_blocks_chunk

chunk_engine = ChunkEngine(
    n_blocks=n_blocks_chunk, # Количество блоков в чанке
    tilesize=tilesize, # Тайлсайз
    layers=layers
)

class Map():
    def __init__(self):
        self.tmx_data = load_pygame('base/MAP.tmx')

        self.ratio = tilesize / initial_tilesize

        # Background и Foreground всегда остаются теми же
        # К слою привязан класс Block или InvTile
        ordered_sprites_group = pg.sprite.Group()

        # Отрисовка BG и FG
        self.render_tiles(Layers.Background)
        self.render_tiles(Layers.Foreground)

        # Отрисовка Слоёв
        for group in self.tmx_data.objectgroups:
            name: str = group.name
            for sprite in self.render_object(name):
                ordered_sprites_group.add(sprite) # Интерактивные штучки

        self.hero = self.render_hero() # Создание игрока
        ordered_sprites_group.add(self.hero)

        camera.all_ordered_sprites = ordered_sprites_group
        camera.set_new_target(self.hero)

    def render_hero(self) -> Hero:
        "Функция создания персонажа"
        hero_object: Any = None
        for object in self.tmx_data.objects:
            if object.properties.get("ObjectType") == "Hero":
                hero_object = object

        hero_size = (hero_object.width * self.ratio, hero_object.height * self.ratio)
        hero_properties = ObjectPropertiesParser(hero_object).process()
        hero_position = int(hero_object.x * self.ratio), int(hero_object.y * self.ratio)

        hero = Hero(
            bottom_center=hero_position,
            size=hero_size,
            texture=scale(hero_object.image, hero_size),
            properties=hero_properties,
        )

        item = ItemSprite(hero, "reimu_fumo.json", (550 * self.ratio, 1300 * self.ratio))
        item.apply_physics = True

        self.process_object_properties(hero, hero_properties)
        return hero

    def render_tiles(self, name: str) -> List[Tile]:
        "Чанкование тайлов по их положению на карте"

        layer: Any = self.tmx_data.get_layer_by_name(name)
        objects: List[Any] = []
        tiles = layer.tiles()

        for X, Y, SURFACE in tiles:
            position = (X * tilesize, Y * tilesize)
            if not chunk_engine.get_memory_chunk(position):
                chunk_engine.create_memory_chunk(position)
            
            # Cannot assign this to render without layers
            tile = Tile(
                tile = SURFACE,
                position = (X, Y),
                tile_name = name
            )

            objects.append(tile)
            chunk_engine.add_memory_chunk(position, tile)
        
        return objects

    def render_object(self, name: str) -> List[pg.sprite.Sprite]:
        layer: Any = self.tmx_data.get_layer_by_name(name)
        objects: List[pg.sprite.Sprite] = [] # Упорядоченный список рендера

        for object in layer:
            image = object.image
            sized_width = object.width * self.ratio
            sized_height = object.height * self.ratio
            rotation = object.rotation

            sized_x = int(object.x * self.ratio)
            sized_y = int(object.y * self.ratio)

            # Параметры Tiled-объекта с карты
            properties = ObjectPropertiesParser(object).process()
            image = scale(image, (sized_width, sized_height))
            image = rotate(image, rotation).convert_alpha()
    
            # Пусть все прозрачные объекты типа мебели и порталов будут класса Interactive
            if properties.object_type in [ObjectTypeNames.Interactive, ObjectTypeNames.Particle]:
                game_object = Interactive(
                    topleft=(sized_x, sized_y),
                    texture=image,
                    properties=properties
                )
            elif properties.object_type == ObjectTypeNames.NPC:
                game_object = NPC(
                    bottom_center=(sized_x, sized_y),
                    size=(sized_width, sized_height),
                    texture=image,
                    properties=properties
                )
            elif properties.object_type == ObjectTypeNames.Trigger:
                game_object = Trigger(
                    trigger_sprite=self.hero,
                    center=(sized_x, sized_y),
                    properties=properties,
                    surface=image
                )
            
            elif properties.object_type == ObjectTypeNames.Hero or properties.object_type == "Particle":
                # Создание игрока, можно сюда чё-то запихать, но в целом не нужно
                # Из-за этой штуки не создаётся нотификация
                # TODO: // Fix this
                continue

            else:
                raise Exception(f"Такого объекта нет в нотациях: {properties.object_type}")

            objects.append(game_object)
            property_objects = self.process_object_properties(game_object, properties)

            objects.extend(property_objects)
        
        return objects

    def process_object_properties(self, object: Union[Interactive, Hero, NPC, Trigger], properties: Properties) -> List[pg.sprite.Sprite]:
        "Обработка параметров объектов: Создание диалогов, партиклов, эмиттеров, etc."
        objects: List[pg.sprite.Sprite] = []

        if properties.notification_params.NotificationText:
            text = properties.notification_params.NotificationText
            # У объекта есть нотификация
            notification = Notification(
                object=object,
                text=text,
                properties=properties
            )
            objects.append(notification)

        return objects
        

class Game():
    def __init__(self):
        pg.display.set_caption('Theta - the start of the game.')

        self.borders = (settings.width, settings.height)
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

    def run(self):
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

            # Отрисовка инвентаря поверх всего
            inventory_group.update()
            inventory_group.draw(self.screen)

            # Рендер чанков
            all_positions_to_render = [npc.position for npc in active]
            chunk_engine.render_chunks(all_positions_to_render)

            self.display_custom_info([
                "Debug Info:",
                f"FPS: {round(fps)}",
                f"Chunk: {chunk}"
            ])
            pg.display.update()
            self.clock.tick(settings.framerate)
