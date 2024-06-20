from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB: str
    MAX_QUEUE_SIZE: int
    WEBSOCKET_URI: str
