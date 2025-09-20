"""
Configuración central de la base de datos.
Maneja la conexión, sesiones y inicialización de SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from config.settings import config
import os

# Variable global para el engine
_engine = None
_session_factory = None

def initialize_database(config_name: str = 'development'):
    """
    Inicializa la configuración de base de datos.
    Debe ser llamado al inicio de la aplicación.
    """
    global _engine, _session_factory
    
    app_config = config[config_name]
    database_url = app_config.SQLALCHEMY_DATABASE_URI
    
    # Configuración específica para SQLite
    if database_url.startswith('sqlite'):
        _engine = create_engine(
            database_url,
            poolclass=StaticPool,
            pool_pre_ping=True,
            echo=app_config.DEBUG,  # Log SQL queries en desarrollo
            connect_args={"check_same_thread": False}  # Para SQLite
        )
    else:
        # Configuración para PostgreSQL/MySQL
        _engine = create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=app_config.DEBUG
        )
    
    _session_factory = sessionmaker(bind=_engine)

def get_db_session() -> Session:
    """
    Retorna una nueva sesión de base de datos.
    Debe ser cerrada después de usar.
    """
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    
    return _session_factory()

def create_tables():
    """
    Crea todas las tablas definidas en los modelos.
    Útil para development y testing.
    """
    if _engine is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    
    from infra.database.models import Base
    Base.metadata.create_all(_engine)

def drop_tables():
    """
    Elimina todas las tablas. Solo para testing.
    """
    if _engine is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    
    from infra.database.models import Base
    Base.metadata.drop_all(_engine)

def get_engine():
    """Retorna el engine actual"""
    return _engine