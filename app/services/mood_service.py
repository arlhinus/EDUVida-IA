"""
Servicio de alertas para el estado de ánimo.
Aquí vive la inteligencia de Edu-vida: detectar patrones de riesgo.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import EstadoAnimo, Usuario

def verificar_alerta_emocional(db: Session, estudiante_id: int) -> dict | None:
    """
    Revisa si el estudiante tiene 3 o más registros de ánimo bajo (1 o 2)
    en los últimos 3 días.
    
    Devuelve un diccionario con la alerta si se cumple la condición,
    o None si el estudiante está bien.
    """
    # Calculamos la fecha de hace 3 días
    fecha_limite = datetime.utcnow() - timedelta(days=3)
    
    # Buscamos los registros bajos en ese rango de tiempo
    registros_bajos = db.query(EstadoAnimo).filter(
        EstadoAnimo.estudiante_id == estudiante_id,
        EstadoAnimo.nivel_animo <= 2,       # Nivel 1 o 2 (bajo)
        EstadoAnimo.fecha >= fecha_limite   # En los últimos 3 días
    ).all()
    
    # Si hay 3 o más, disparamos la alerta
    if len(registros_bajos) >= 3:
        return {
            "alerta": True,
            "mensaje": "⚠️ ALERTA: El estudiante ha reportado un ánimo bajo por 3 días seguidos.",
            "nivel_riesgo": "alto",
            "registros_detectados": len(registros_bajos)
        }
    
    # Si no cumple la condición, no hay alerta
    return None