"""
Modelos de base de datos para Edu-vida.
"""
from datetime import date, datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rol = Column(String(20), nullable=False)              # ej: 'estudiante', 'profesor', 'apoderado'
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    rut = Column(String(12), unique=True, nullable=False, index=True)
    cumpleanos = Column(Date, nullable=True)
    curso = Column(String(50), nullable=True)             # ej: '4°B'
    necesidades_medicas = Column(Text, nullable=True)

    # Relaciones
    estados_animo = relationship(
        "EstadoAnimo",
        back_populates="estudiante",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} codigo={self.codigo} rol={self.rol}>"


class EstadoAnimo(Base):
    __tablename__ = "estados_animo"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    estudiante_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    nivel_animo = Column(Integer, nullable=False)  # ej: 1 (muy bajo) ... 5 (muy alto)
    comentario = Column(Text, nullable=True)

    # Relación inversa
    estudiante = relationship("Usuario", back_populates="estados_animo")

    def __repr__(self) -> str:
        return f"<EstadoAnimo id={self.id} estudiante_id={self.estudiante_id} nivel={self.nivel_animo}>"

