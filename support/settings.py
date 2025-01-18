from pydantic import BaseModel

class Settings(BaseModel):
    width: int = 1280
    height: int = 720
    framerate: int = 65
    tilesize: int = 48
    initial_tilesize: int = 16
    n_blocks_chunk: int = 10

    # Для инвентаря
    inventory_background_path: str = "None"
    inventory_selector: str = "None"
    inventory_item_bar_path: str = "None"
    inventory_add_text_bar_path: str = "None"

    # Параметры загрузки вещей и их текстур
    item_textures: str = "inventory/items/item_textures"
    item_jsons: str = "inventory/items/item_jsons"
    item_error_path: str = "inventory/items/item_textures/error.png"

    # Для шрифта и всего
    font_path: str = "base/font"
    font_name: str = "Bahnschrift.ttf"

def load_settings() -> Settings:
    json_data = open("support/settings.json").read()
    settings = Settings.model_validate_json(json_data)

    return settings