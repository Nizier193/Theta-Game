from engine import Game, chunk_engine

'''
Это мой локальный проект, посвященный созданию игры, которая будет мне по душе)

Ламповая атмосфера, 2D, красивые текстуры, знакомые места, люди.
В будущем будут мини-игры, песочница, другие режимы!

Но пока что это бегалка по площадке.

Фичи:
  - Хп, без брони. Несколько аксессуаров.

  - Инвентарь на 5 слотов.
  - Рабочая система сундуков и дропа вещей.

  - Диалоги и НПС.
  - Освещение по блокам, не RayTracing.

  - Полная рабочая система камеры с классом.
  - Маленькие квесты, система их настройки.
  
  - Мною впервые примененная система чанков! Для того, чтобы
    игра не лагала.

'''
import pygame as pg


pg.init()
game = Game()
game.run()

