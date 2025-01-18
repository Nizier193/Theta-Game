from pathlib import Path
from typing import Tuple, Union
from pygame.image import load
import pygame as pg

from support.settings import load_settings

settings = load_settings()

class ImageLoader():
    "Класс для загрузки текстурок"
    def __init__(self, path_to_image: Union[Path, str], size: Tuple[int, int] = (0, 0)) -> None:
        self.image = self.load_image(path_to_image)
        self.sized_image = self.size_image(self.image, size)

    def load_image(self, image_path: Path) -> pg.Surface:
        try:
            image = load(image_path)
        
        except Exception:
            error_image = load(settings.item_error_path)
            image = error_image
            print(f"Error while trying to fetch image -> {image_path}")

        return image
    
    def size_image(self, image: pg.Surface, size: Tuple[int, int]):
        return pg.transform.scale(image, size)