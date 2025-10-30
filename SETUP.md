# Guía de Instalación y Configuración

## Sistema de Gestión de Flota de Vehículos (Backend Flask)

### Requisitos Previos

- Python 3.11+
- PostgreSQL (para producción) o SQLite (desarrollo)

### Instalación del Backend

1. **Crear entorno virtual**
```bash
python -m venv venv
# Windows
venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

Para herramientas de desarrollo (linters, formateadores, tests, documentación):
```bash
pip install -r requirements-dev.txt
```

3. **Configurar variables de entorno**
Copiar `.env.example` a `.env` y ajustar según tu entorno:
```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password
POSTGRES_DB=gestion_vehiculos
SECRET_KEY=tu_clave_secreta_aqui
USE_SQLITE=True
SQLITE_DB_PATH=gestion_vehiculos.db
```

4. **Crear base de datos** (si usas PostgreSQL)
```sql
CREATE DATABASE gestion_vehiculos;
```

5. **Ejecutar migraciones (Alembic)**
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

6. **Crear usuario administrador**
No existe una cuenta por defecto en producción. Puedes crear un administrador desde la interfaz web o usando el script de administración si está disponible en `archive_root_files/create_admin_user.py`.

7. **Iniciar servidor (desarrollo)**
```bash
python run.py
```

El backend estará disponible por defecto en `http://127.0.0.1:5000` (o el puerto configurado).

### Notas sobre archivos en el repositorio raíz

- Para limpieza del repositorio muchos scripts de inicialización fueron movidos a `archive_root_files/` en lugar de eliminarse.
- No subas ni compartas ficheros sensibles como `gestion_vehiculos.db` o `security.log` en el control de versiones.

Si al intentar mover o borrar `gestion_vehiculos.db` u otros archivos observas que están bloqueados, lo más probable es que un proceso local (editor, servidor, LSP) los esté manteniendo abiertos. En Windows PowerShell puedes identificar procesos que usan la ruta del repositorio con:

```powershell
$repo = 'C:\Users\ramon\OneDrive\Documentos\windsurf\gestionVehiculos'
Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -and ($_.CommandLine -match [regex]::Escape($repo)) } | Select ProcessId,Name,CommandLine
```

Para detener procesos por PID (hazlo solo si sabes que cerrarás la tarea que los inició):

```powershell
# Reemplaza <PID> por el identificador listado
Stop-Process -Id <PID> -Force
```

Después de liberar los ficheros, puedes moverlos a `archive_root_files\` si procede.

### Estructura del Proyecto

```
gestionVehiculos/
├── app/                    # Código principal de la aplicación (Flask)
│   ├── controllers/        # Rutas y controladores
│   ├── models/             # Modelos SQLAlchemy
│   ├── services/           # Lógica de negocio
│   └── templates/          # Plantillas Jinja2
├── alembic/                # Migraciones de base de datos
├── requirements.txt        # Dependencias de runtime
├── requirements-dev.txt    # Dependencias de desarrollo (tests, lint)
└── run.py                  # Punto de entrada de la aplicación
```
