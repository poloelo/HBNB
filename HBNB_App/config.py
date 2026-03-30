import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JSON_SORT_KEYS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    # SQLite en développement : fichier local dans le répertoire de l'app
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///hbnb_dev.db'
    )

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # En production, DATABASE_URL doit être définie explicitement (ex: MySQL).
    # L'absence de la variable lève une KeyError au démarrage, ce qui est voulu.
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
