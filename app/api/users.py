"""
Routers para los endpoints de Usuarios.
Aquí definimos las URLs que el frontend podrá llamar.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import Usuario
from app.schemas.user import UsuarioCreate, UsuarioOut, UsuarioLogin
from app.services.user_service import crear_usuario, autenticar_usuario
from app.services.auth import crear_token_acceso, obtener_usuario_actual

# APIRouter es como un "mini-FastAPI". Nos permite agrupar rutas
router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("/registro", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario_in: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Endpoint para registrar un nuevo usuario.
    Recibe los datos (validados por UsuarioCreate), llama al servicio
    y devuelve los datos públicos del usuario (UsuarioOut, sin password).
    """
    nuevo_usuario = crear_usuario(db, usuario_in)
    return nuevo_usuario


@router.post("/login")
def login(login_data: UsuarioLogin, db: Session = Depends(get_db)):
    """
    Endpoint para iniciar sesión.
    Devuelve un Token JWT para acceder a rutas protegidas.
    """
    usuario = autenticar_usuario(db, login_data)
    
    # Creamos el "payload" (la información que viaja dentro del token)
    token_data = {"sub": usuario.codigo, "rol": usuario.rol}
    token = crear_token_acceso(token_data)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": UsuarioOut.model_validate(usuario)
    }


@router.get("/estudiantes", response_model=List[UsuarioOut])
def listar_estudiantes(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Devuelve la lista de todos los estudiantes.
    Solo accesible para profesores o apoderados.
    """
    # Validación de seguridad: solo los profesores pueden ver a todos los alumnos
    if usuario_actual.rol not in ["profesor", "apoderado"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo profesores o apoderados pueden ver esta lista"
        )
    
    # Buscamos en la base de datos solo los que tengan rol "estudiante"
    estudiantes = db.query(Usuario).filter(Usuario.rol == "estudiante").all()
    return estudiantes