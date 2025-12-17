from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "user"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DATABASE: str = "ragdb"
    CHROMA_PATH: str = "./chroma_db"

settings = Settings() 