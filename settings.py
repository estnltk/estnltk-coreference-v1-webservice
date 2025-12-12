from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    max_content_length: int = 200000
    coreference_dir: str = "coreference/model_2021-01-04"
    stanza_models_dir: str = "stanza_resources"

settings = Settings()