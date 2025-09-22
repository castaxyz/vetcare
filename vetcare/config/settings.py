import os
from datetime import timedelta

# Directorio base del proyecto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(os.path.dirname(BASE_DIR), "instance")

class Config:
    """Configuración base para toda la aplicación"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-for-university'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuraciones de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Configuraciones de paginación
    ITEMS_PER_PAGE = 10

class DevelopmentConfig(Config):
    """Configuración para desarrollo local"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        f"sqlite:///{os.path.join(INSTANCE_DIR, 'vetcare_dev.db')}"

class ProductionConfig(Config):
    """Configuración para producción (Azure/Render)"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.join(INSTANCE_DIR, 'vetcare_prod.db')}"

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Diccionario para seleccionar configuración fácilmente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
