"""
Schemas Pydantic para Usuario y EstadoAnimo.

¿Qué es un schema?
-------------------
Un schema es un "contrato" que define la forma de los datos que viajan
entre el cliente (app Flet) y el servidor (FastAPI). Pydantic los valida
automáticamente: si el cliente envía datos incorrectos, FastAPI responde
un error 422 ANTES de que el código toque la base de datos.

Separamos los schemas por responsabilidad:
- *Base:   campos comunes (no se usa solo, es para heredar).
- *Create: datos que ENVÍA el cliente al crear un recurso.
- *Out:    datos que DEVUELVE la API (nunca incluye password).
- *Login:  datos específicos para autenticarse.
"""

from datetime import date, datetime
from typing import Literal, Optional

# Pydantic v2: BaseModel para la clase, Field para validaciones,
# ConfigDict reemplaza al viejo "class Config: orm_mode = True" de v1.
from pydantic import BaseModel, ConfigDict, Field

# Tipos de rol permitidos. Usar Literal hace que Pydantic rechace
# automáticamente cualquier valor fuera de esta lista (ej: "admin").
RolUsuario = Literal["estudiante", "profesor", "apoderado"]


# ============================================================
#  SCHEMAS DE USUARIO
# ============================================================

class UsuarioBase(BaseModel):
    """
    Campos comunes a todos los schemas de Usuario.
    No se instancia directamente: sirve de clase padre para no repetir
    los mismos campos en Create, Out, etc. (principio DRY).
    """
    rol: RolUsuario = Field(
        ...,
        description="Rol del usuario: estudiante, profesor o apoderado",
    )
    codigo: str = Field(
        ..., min_length=1, max_length=50,
        description="Código único del colegio (alumno o funcionario)",
    )
    nombres: str = Field(..., min_length=1, max_length=100)
    apellidos: str = Field(..., min_length=1, max_length=100)
    rut: str = Field(
        ..., min_length=1, max_length=12,
        description="RUT chileno, único por usuario",
    )
    cumpleanos: Optional[date] = Field(
        default=None, description="Fecha de nacimiento (opcional)",
    )
    curso: Optional[str] = Field(
        default=None, max_length=50,
        description="Curso del estudiante, ej: '2° Medio A' (opcional)",
    )
    necesidades_medicas: Optional[str] = Field(
        default=None,
        description="Alergias, condiciones médicas, etc. (opcional)",
    )


class UsuarioCreate(UsuarioBase):
    """
    Datos que envía el cliente al REGISTRAR un usuario.
    Hereda todos los campos de UsuarioBase y agrega 'password' en texto
    plano. El servicio se encargará de hashearlo antes de guardarlo.
    """
    password: str = Field(
        ..., min_length=6, max_length=72,
        description=(
            "Contraseña en texto plano. Mínimo 6 caracteres. "
            "Máximo 72 porque bcrypt ignora lo que pase de ahí."
        ),
    )


class UsuarioOut(UsuarioBase):
    """
    Datos que DEVUELVE la API al consultar un usuario.
    - Incluye 'id' que genera la base de datos.
    - NUNCA incluye password ni su hash (seguridad).
    - from_attributes=True permite construirlo desde un modelo SQLAlchemy.
    """
    id: int
    model_config = ConfigDict(from_attributes=True)


class UsuarioLogin(BaseModel):
    """
    Datos mínimos para el LOGIN.
    El usuario se identifica con su 'codigo' (más cómodo que el RUT)
    y su contraseña.
    """
    codigo: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=72)


# ============================================================
#  SCHEMAS DE ESTADO DE ÁNIMO
# ============================================================

class EstadoAnimoBase(BaseModel):
    """
    Campos comunes del estado de ánimo.
    nivel_animo va de 1 (muy mal) a 5 (muy bien). Validamos el rango
    con ge=1 y le=5 (greater/less or equal).
    """
    nivel_animo: int = Field(
        ..., ge=1, le=5,
        description="Nivel de ánimo del 1 (muy mal) al 5 (muy bien)",
    )
    comentario: Optional[str] = Field(
        default=None,
        description="Comentario libre del estudiante (opcional)",
    )


class EstadoAnimoCreate(EstadoAnimoBase):
    """
    Datos que envía el estudiante al REGISTRAR su ánimo.
    El 'estudiante_id' NO lo envía el cliente: lo sacamos del token JWT
    en el endpoint, para que nadie pueda registrar ánimo a nombre de otro.
    Esta es una decisión de SEGURIDAD importante.
    """
    pass  # Hereda todo de EstadoAnimoBase


class EstadoAnimoOut(EstadoAnimoBase):
    """
    Datos que DEVUELVE la API al consultar el historial.
    Incluye id, fecha (la pone la BD) y estudiante_id (lo pone el sistema).
    """
    id: int
    estudiante_id: int
    fecha: datetime
    model_config = ConfigDict(from_attributes=True)