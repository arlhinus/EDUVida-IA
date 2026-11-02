"""
Configuración de la base de datos SQLite con SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Ruta local del archivo SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./edu_vida.db"

# check_same_thread=False es necesario para SQLite + FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  # Cambia a True si quieres ver el SQL generado
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependencia de FastAPI para obtener una sesión de BD por request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Crea todas las tablas registradas en los modelos.
    """
    # Importamos los modelos AQUÍ ADENTRO para evitar importaciones circulares.
    # Al importarlos, SQLAlchemy se entera de que las tablas existen y las crea.
    from app.models.user import Usuario, EstadoAnimo
    
    Base.metadata.create_all(bind=engine)

