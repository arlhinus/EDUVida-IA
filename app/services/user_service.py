"""
Servicios para Usuarios.
Aquí está la lógica para crear usuarios, autenticarlos y buscar información.
Los routers (Paso 3) llamarán a estas funciones.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import Usuario
from app.schemas.user import UsuarioCreate, UsuarioLogin
from app.services.security import obtener_hash_password, verificar_password


def crear_usuario(db: Session, usuario_in: UsuarioCreate) -> Usuario:
    """
    Crea un nuevo usuario en la base de datos.
    Pasos:
    1. Revisa si el RUT o el código ya existen (no queremos duplicados).
    2. Encripta la contraseña.
    3. Guarda al usuario en la BD.
    """
    # 1. Validar que no exista el código o el RUT
    existe_codigo = db.query(Usuario).filter(Usuario.codigo == usuario_in.codigo).first()
    if existe_codigo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El código ya está registrado"
        )
    
    existe_rut = db.query(Usuario).filter(Usuario.rut == usuario_in.rut).first()
    if existe_rut:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El RUT ya está registrado"
        )

    # 2. Encriptar la contraseña
    hash_seguro = obtener_hash_password(usuario_in.password)

    # 3. Crear el objeto modelo SQLAlchemy (usando los datos del schema)
    # Usamos model_dump() para convertir el schema Pydantic a un diccionario,
    # pero excluimos 'password' porque guardaremos el 'hash_seguro'.
    datos_usuario = usuario_in.model_dump(exclude={"password"})
    
    nuevo_usuario = Usuario(
        **datos_usuario,
        password_hash=hash_seguro  # Nota: en el modelo original no vimos 'password_hash', lo agregaremos abajo
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)  # Refresca para obtener el ID generado por la BD
    return nuevo_usuario


def autenticar_usuario(db: Session, login_data: UsuarioLogin) -> Usuario:
    """
    Verifica las credenciales en el Login.
    Devuelve el usuario si todo está bien, o lanza un error 401 si falla.
    """
    usuario = db.query(Usuario).filter(Usuario.codigo == login_data.codigo).first()
    
    # Si el usuario no existe, o la contraseña no coincide...
    if not usuario or not verificar_password(login_data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return usuario


def obtener_usuario_por_codigo(db: Session, codigo: str) -> Usuario | None:
    """Busca un usuario por su código único."""
    return db.query(Usuario).filter(Usuario.codigo == codigo).first()