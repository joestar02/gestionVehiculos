# Sistema de Gestión de Flota de Vehículos

Aplicación web empresarial completa para la gestión integral de flotas de vehículos, desarrollada con Flask y FastAPI.

## 📚 Documentación

**Toda la documentación se encuentra en la carpeta `docs/`**

### Inicio Rápido
- **[5-Minute Quickstart](docs/QUICKSTART.md)** - Comienza en 5 minutos
- **[Documentation Index](docs/DOCUMENTACION_INDEX.md)** - Índice completo de documentación

### API REST
- **[API Complete Guide](docs/API_GUIA_COMPLETA.md)** - Guía exhaustiva (20 minutos)
- **[API Implementation](docs/API_IMPLEMENTATION.md)** - Detalles técnicos
- **Swagger UI**: http://localhost:8000/docs (cuando API está ejecutándose)

### Seguridad y Auditoría
- **[Security Guide](docs/SECURITY.md)** - Políticas de seguridad
- **[Audit & Logging](docs/auditoria_logging.md)** - Sistema de auditoría completo

### Diseño y Arquitectura
- **[Design Guide](docs/DESIGN_GUIDE.md)** - Especificaciones de diseño
- **[Database Schema](docs/db_erd.md)** - Diagrama de relaciones

### Gestión del Proyecto
- **[Project Status](docs/PROJECT_STATUS.md)** - Estado final y checklist
- **[Implementation Summary](docs/IMPLEMENTACION_COMPLETA.md)** - Resumen de implementación
- **[User Profiles](docs/user_profiles.md)** - Perfiles y casos de uso
- **[User Stories](docs/historias_de_usuario.md)** - Requisitos y historias

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database
```bash
python archive_root_files/init_db.py
python scripts/init_permissions.py
python scripts/create_sample_users.py
```

### 3. Run Application
```bash
python run.py
```
Access: http://localhost:5000

### 4. Test Users
| User | Password | Role |
|------|----------|------|
| `admin` | `admin123` | ADMIN |
| `fleet_manager` | `fleet123` | FLEET_MANAGER |
| `ops_manager` | `ops123` | OPERATIONS_MANAGER |
| `conductor1` | `driver123` | DRIVER |
| `visor` | `view123` | VIEWER |

### 5. API REST
```bash
python api_simple.py
# or
from api_simple import app
app.run(host='0.0.0.0', port=8000)
```
API Docs: http://localhost:8000/docs

---

## ✨ Key Features

- ✅ **Vehicle Management** - Complete CRUD with documentation (ITV, insurance, taxes)
- ✅ **Driver Management** - Profiles with accident and fine history
- ✅ **Reservation System** - Complete with conflict detection
- ✅ **Maintenance Tracking** - Preventive and corrective maintenance
- ✅ **Driver Assignments** - Manage driver-vehicle associations
- ✅ **Provider Management** - Service provider management
- ✅ **Granular Permissions** - 26 specific permissions across 9 modules
- ✅ **Complete Audit System** - Database and security logging with full traceability
- ✅ **REST API** - Modern FastAPI with automatic Swagger documentation
- ✅ **Security** - Authentication, CSRF protection, rate limiting, security headers

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_security.py -v
pytest tests/test_reservations_flow.py -v

# Verify logging
python scripts/test_database_logging.py
```

---

## 📊 Technology Stack

**Backend**: Flask 3.0+, FastAPI 0.10+, SQLAlchemy 2.0+, Pydantic v2
**Frontend**: Bootstrap 5, Jinja2, HTML5/CSS3
**Database**: SQLite (dev), PostgreSQL (production)
**Tools**: Alembic (migrations), pytest (testing), Werkzeug (security)

---

## 📁 Project Structure

```
├── app/                          # Flask application
│   ├── controllers/             # Flask blueprints
│   ├── api/                     # FastAPI routers
│   ├── models/                  # SQLAlchemy models
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Business logic
│   ├── templates/               # Jinja2 templates
│   └── static/                  # CSS, JS, images
├── docs/                         # Complete documentation
├── tests/                        # Test suite
├── scripts/                      # Utility scripts
└── api_simple.py               # Standalone FastAPI app
```

---

## 📞 Support

For detailed information, see [Complete Documentation Index](docs/DOCUMENTACION_INDEX.md)

---

**Project Status**: ✅ Complete and Production-Ready
