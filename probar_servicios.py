from app.database import SessionLocal, init_db
from app.schemas.user import UsuarioCreate, UsuarioLogin
from app.services.user_service import crear_usuario, autenticar_usuario

# 1. Inicializamos la base de datos (crea las tablas si no existen)
init_db()
db = SessionLocal()

print("--- 1. Creando usuario ---")
datos = UsuarioCreate(
    rol="estudiante", codigo="ALUMNO01", nombres="Juan", apellidos="Pérez",
    rut="11111111-1", password="miClaveSegura123"
)
try:
    u = crear_usuario(db, datos)
    print(f"✅ Usuario creado: {u.nombres} {u.apellidos} (ID: {u.id})")
    print(f"🔒 Contraseña encriptada: {u.password_hash[:20]}...")
except Exception as e:
    print(f"⚠️ Nota: {e}")

print("\n--- 2. Probando Login Correcto ---")
try:
    login = UsuarioLogin(codigo="ALUMNO01", password="miClaveSegura123")
    user_auth = autenticar_usuario(db, login)
    print(f"✅ Login exitoso. Bienvenido {user_auth.nombres}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n--- 3. Probando Login Incorrecto ---")
try:
    login_malo = UsuarioLogin(codigo="ALUMNO01", password="claveEquivocada")
    autenticar_usuario(db, login_malo)
except Exception as e:
    print(f"✅ Bloqueado correctamente: {e.detail}")

db.close()