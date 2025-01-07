from pydantic import BaseModel

class Settings(BaseModel):
    width: int = 1280
    height: int = 720
    framerate: int = 65
    tilesize: int = 48
    initial_tilesize: int = 16
    n_blocks_chunk: int = 10
    item_basepath: str = "inventory/items"

def load_settings() -> Settings:
    json_data = open("settings.json").read()
    settings = Settings.model_validate_json(json_data)

    return settings