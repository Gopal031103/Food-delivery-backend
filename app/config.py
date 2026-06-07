from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "mysql+mysqlconnector://root:Gokul%402003@localhost:3306/food_delivery"
    SQLALCHEMY_DATABASE_URL: str = "mysql+mysqlconnector://root:Gokul%402003@localhost:3306/food_delivery"
    
    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production-min-32-chars-long-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Application
    APP_NAME: str = "Food Delivery Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
