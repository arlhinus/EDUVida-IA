"""
Servicios de seguridad.
Aquí manejamos el hashing de contraseñas. 

¿Por qué hashear? Porque si un hacker roba la base de datos, no debe poder
leer las contraseñas. El hash es una función de un solo sentido: se puede
convertir "123456" en un texto raro, pero del texto raro NO se puede volver
a sacar el "123456".
"""

from passlib.context import CryptContext

# CryptContext configura el algoritmo de encriptación.
# Usamos "bcrypt" porque es el estándar de la industria (lento a propósito
# para evitar ataques de fuerza bruta).
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def obtener_hash_password(password: str) -> str:
    """
    Recibe la contraseña en texto plano (ej: "miClave123") y devuelve
    el hash seguro (ej: "$2b$12$...") para guardarlo en la BD.
    """
    return pwd_context.hash(password)

def verificar_password(password_plano: str, password_hasheado: str) -> bool:
    """
    Compara la contraseña que el usuario escribe en el login (texto plano)
    con el hash que tenemos guardado en la BD.
    Devuelve True si coinciden, False si no.
    """
    return pwd_context.verify(password_plano, password_hasheado)