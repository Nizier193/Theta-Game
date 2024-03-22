import pygame as pg
from classes import TILESIZE, CHUNKSIZE
from classes_l2 import *
from pytmx.util_pygame import load_pygame
import math

example = supGroup(z_order=-1)

'''
Здесь расположен основной код всей системы.
'''

classes_ = {
    'Foreground':      (Block, obstacles),
    'Background':      (BG, passive),
    'BackBackground':  (FG, backbackground),
    'Ladders':         (Interactive, interactive),
    'FirstGround':     (FG, firstground),
    'SlowFirstGround': (FG, slowfirstground),
}
CHUNKMAP = dict()
CHUNKHASH = dict()
class Map():
    def __init__(self):
        const = TILESIZE / 16
        self.tmx_data = load_pygame('base/MAP.tmx')

        # Сборка слоёв и их рендер.
        self.render_tiles('BackBackground')
        self.render_tiles('Background')
        self.render_tiles('Foreground')
        self.render_ladders('Ladders')
        self.render_tiles('FirstGround')
        self.render_tiles('SlowFirstGround')

        hero_position = self.tmx_data.get_object_by_name('Player')
        self.hero_position = hero_position.x * const, hero_position.y * const

        self.render_chunks(self.hero_position)

        for OBJECT in self.tmx_data.get_layer_by_name('Interactive'):
            Interactive((OBJECT.x * const, OBJECT.y * const),
               pg.transform.scale(OBJECT.image, (OBJECT.width * const, OBJECT.height * const)),
                        {
                            'name':OBJECT.name[2:],
                            'index':int(OBJECT.name[0]),
                         })

        for OBJECT in self.tmx_data.get_layer_by_name('Furniture'):
            NPC((OBJECT.x * const, OBJECT.y * const),
               pg.transform.scale(OBJECT.image, (OBJECT.width * const, OBJECT.height * const)))

        for OBJECT in self.tmx_data.get_layer_by_name('Sprites'):
            if OBJECT.name == 'Player':
                self.hero = Hero((OBJECT.x * const, OBJECT.y * const))

            else:
                NPC((OBJECT.x * const, OBJECT.y * const),
                    pg.transform.scale(
                        pg.transform.flip(textures[OBJECT.name], True, False),
                        (TILESIZE, TILESIZE)))

        for OBJECT in self.tmx_data.get_layer_by_name('NOTIFICATIONS'):
            Notification(
                (OBJECT.x * const, OBJECT.y * const),
                {
                    'text': OBJECT.name
                }
            )

        for OBJECT in self.tmx_data.get_layer_by_name('PARTICLES'):
            Animation(
                center=(OBJECT.x * const, OBJECT.y * const),
                name=OBJECT.name,
                distance=OBJECT.properties.get('distance'),
                intensity=OBJECT.properties.get('intensity'),
                mode=OBJECT.properties.get('mode'),
            ).launch()


    def render_chunks(self, hero_position):
        player_chunk = self.calc_chunk(hero_position)

        dy = [num for num in range(-2, 3) for i in range(5)]
        dx = [num for i in range(5) for num in range(-2, 3)]

        self.clear_chunks(hero_position)
        # 8 times
        for (dx_, dy_) in zip(dx, dy):
            key = (player_chunk[0] + dx_, player_chunk[1] + dy_)
            if CHUNKMAP.get(key):
                if CHUNKHASH.get(key) == None:
                    CHUNKHASH[key] = []
                    for X, Y, SURFACE, name in CHUNKMAP.get(key):
                        property_ = classes_.get(name)
                        if name in ['Ladders']:
                            tile_ = property_[0]((X * TILESIZE, Y * TILESIZE),
                                                pg.transform.scale(SURFACE, (TILESIZE, TILESIZE)),
                                                 {'name': name})
                        elif name in ['BackBackground', 'SlowFirstGround', 'FirstGround']:
                            tile_ = property_[0]((X * TILESIZE, Y * TILESIZE),
                                       pg.transform.scale(SURFACE, (TILESIZE, TILESIZE)),
                                                 property_[1])
                        else:
                            tile_ = property_[0]((X * TILESIZE, Y * TILESIZE),
                                          pg.transform.scale(SURFACE, (TILESIZE, TILESIZE)))

                        CHUNKHASH[key].append(tile_)


    def clear_chunks(self, hero_position):
        player_chunk = self.calc_chunk(hero_position)

        keys = CHUNKHASH.keys()
        dokill_ = []
        for HASH in keys:
            if abs(player_chunk[0] - HASH[0]) > 1 or abs(player_chunk[1] - HASH[1]) > 1:
                for group in CHUNKHASH[HASH]:
                    group.kill()

                dokill_.append(HASH)


        for kill in dokill_:
            CHUNKHASH.pop(kill)


    def render_ladders(self, name):
        layer = self.tmx_data.get_layer_by_name(name)

        for X, Y, SURFACE in layer.tiles():
            chunkmap_pos = self.calc_chunk((X * TILESIZE, Y * TILESIZE))
            if not CHUNKMAP.get(chunkmap_pos):
                CHUNKMAP[self.calc_chunk((X * TILESIZE, Y * TILESIZE))] = []

            CHUNKMAP[chunkmap_pos].append((X, Y, SURFACE, name))

    def render_tiles(self, name):
        layer = self.tmx_data.get_layer_by_name(name)

        for X, Y, SURFACE in layer.tiles():
            chunkmap_pos = self.calc_chunk((X * TILESIZE, Y * TILESIZE))
            if not CHUNKMAP.get(chunkmap_pos):
                CHUNKMAP[self.calc_chunk((X * TILESIZE, Y * TILESIZE))] = []

            CHUNKMAP[chunkmap_pos].append((X, Y, SURFACE, name))


    def calc_chunk(self, object):
        if type(object) is not tuple:
            chunk_x = math.ceil(object.rect.x / 640)
            chunk_y = math.ceil(object.rect.y / 640)
        else:
            chunk_x = math.ceil(object[0] / 640)
            chunk_y = math.ceil(object[1] / 640)
        return (chunk_x, chunk_y)

class Game():
    def __init__(self,
                 width: int = 1280,
                 height: int = 720):

        pg.display.set_caption('Theta - the start of the game.')

        self.borders = (width, height)
        self.screen = pg.display.set_mode(self.borders)

        self.screen = pg.display.get_surface()
        self.clock = pg.time.Clock()

        self.map = Map()

        self.hero = self.map.hero
        self.hero_chunk = self.map.calc_chunk(self.hero)

        self.font = pg.font.SysFont('Arial', 45)

    def run(self,
            framerate: int = 50
            ):

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    self.hero.keypress(event)

            self.screen.fill((20, 255, 255))
            example.assembly(self.screen, self.hero)
            self.screen.blit(self.font.render(str(round(self.clock.get_fps())), True, (0, 0, 0)), (20, 60))
            self.screen.blit(self.font.render(str(self.map.calc_chunk(self.hero)), True, (0, 0, 0)), (20, 20))

            if self.map.calc_chunk(self.hero) != self.hero_chunk:
                self.hero_chunk = self.map.calc_chunk(self.hero)
                self.map.render_chunks(self.hero.rect.center)

            pg.display.update()
            self.clock.tick(framerate)


