from pydantic import BaseModel

class Settings(BaseModel):
    width: int = 1280
    height: int = 720
    framerate: int = 65

def load_settings() -> Settings:
    json_data = open("settings.json").read()

    settings = Settings.model_validate_json(json_data)

    return settings