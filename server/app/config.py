import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    DB_URL = os.environ.get(
        "DB_URL", "postgresql://postgres:admin@localhost:5432/spraywall"
    )


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "dev": DevelopmentConfig,
    "prod": ProductionConfig,
    "default": DevelopmentConfig,
}
