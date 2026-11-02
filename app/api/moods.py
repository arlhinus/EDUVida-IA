"""
Routers para el Estado de Ánimo.
Aquí un estudiante podrá registrar cómo se siente, y un profesor podrá
ver el historial de un alumno.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import Usuario, EstadoAnimo
from app.schemas.user import EstadoAnimoCreate, EstadoAnimoOut
from app.services.auth import obtener_usuario_actual
from app.services.mood_service import verificar_alerta_emocional

router = APIRouter(prefix="/animo", tags=["Estado de Ánimo"])


@router.post("/registrar", status_code=status.HTTP_201_CREATED)
def registrar_animo(
    animo_in: EstadoAnimoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Registra el estado de ánimo del estudiante logueado.
    El 'estudiante_id' se obtiene del Token, NO del cliente.
    """
    # Seguridad: Solo los estudiantes pueden registrar su ánimo.
    if usuario_actual.rol != "estudiante":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los estudiantes pueden registrar su estado de ánimo"
        )

    # Creamos el registro usando el ID del usuario que viene en el token
    nuevo_animo = EstadoAnimo(
        estudiante_id=usuario_actual.id,
        nivel_animo=animo_in.nivel_animo,
        comentario=animo_in.comentario
    )

    db.add(nuevo_animo)
    db.commit()
    db.refresh(nuevo_animo)

    # Llamamos al servicio de alertas para ver si se debe avisar al profesor
    alerta = verificar_alerta_emocional(db, usuario_actual.id)

    # Devolvemos el registro guardado (convertido a formato JSON) y la alerta (si es que hay)
    return {
        "registro": EstadoAnimoOut.model_validate(nuevo_animo),
        "alerta": alerta
    }


@router.get("/historial/{estudiante_codigo}", response_model=List[EstadoAnimoOut])
def ver_historial(
    estudiante_codigo: str,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Permite a un profesor o apoderado ver el historial de un estudiante.
    El estudiante también puede ver su propio historial.
    """
    # Buscamos al estudiante por su código
    estudiante = db.query(Usuario).filter(Usuario.codigo == estudiante_codigo).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    # Validación de permisos: el profesor/apoderado puede ver a cualquiera.
    # El estudiante solo se puede ver a sí mismo.
    if usuario_actual.rol == "estudiante" and usuario_actual.id != estudiante.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver el historial de otro estudiante"
        )

    # Devolvemos la lista ordenada por fecha (la más reciente primero)
    historial = db.query(EstadoAnimo).filter(
        EstadoAnimo.estudiante_id == estudiante.id
    ).order_by(EstadoAnimo.fecha.desc()).all()

    return historial