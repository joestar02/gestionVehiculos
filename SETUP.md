# Guía de Instalación y Configuración

## Sistema de Gestión de Flota de Vehículos

### Requisitos Previos

- Python 3.9+
- PostgreSQL 13+
- Node.js 16+
- npm o yarn

### Instalación del Backend

1. **Crear entorno virtual**
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
Copiar `.env.example` a `.env` y configurar:
```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password
POSTGRES_DB=gestion_vehiculos
SECRET_KEY=tu_clave_secreta_aqui
```

4. **Crear base de datos**
```sql
CREATE DATABASE gestion_vehiculos;
```

5. **Ejecutar migraciones**
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

6. **Crear usuario administrador**
```bash
python -c "from app.db.session import SessionLocal; from app.models import User; from app.core.security import get_password_hash; db = SessionLocal(); user = User(username='admin', email='admin@example.com', hashed_password=get_password_hash('admin123'), is_superuser=True, role='admin'); db.add(user); db.commit()"
```

7. **Iniciar servidor**
```bash
python run.py
```

El backend estará disponible en `http://localhost:8000`

### Instalación del Frontend

1. **Instalar dependencias**
```bash
cd frontend
npm install
```

2. **Iniciar servidor de desarrollo**
```bash
npm run dev
```

El frontend estará disponible en `http://localhost:3000`

### Credenciales por Defecto

- **Usuario:** admin
- **Contraseña:** admin123

### Documentación API

Una vez iniciado el backend, la documentación interactiva está disponible en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Estructura del Proyecto

```
gestionVehiculos/
├── app/                    # Backend FastAPI
│   ├── api/               # Endpoints
│   ├── core/              # Configuración
│   ├── db/                # Base de datos
│   ├── models/            # Modelos SQLAlchemy
│   └── schemas/           # Esquemas Pydantic
├── frontend/              # Frontend React
│   └── src/
│       ├── components/    # Componentes
│       ├── pages/         # Páginas
│       ├── stores/        # Estado global
│       └── lib/           # Utilidades
└── alembic/               # Migraciones
```
