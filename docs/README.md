# 📚 Documentación del Sistema de Gestión de Flota

Bienvenido a la documentación completa del Sistema de Gestión de Flota de Vehículos. Esta carpeta contiene toda la documentación técnica, de usuario y de seguridad del proyecto.

## 📋 Índice de Documentación

### 📖 Documentación Principal
- **[README.md](../README.md)** - Archivo principal del proyecto con instalación, características y uso básico
- **[SECURITY.md](SECURITY.md)** - Guía completa de seguridad y mejores prácticas
- **[auditoria_logging.md](auditoria_logging.md)** - Sistema de auditoría y logging avanzado

### 👥 Usuarios y Permisos
- **[user_profiles.md](user_profiles.md)** - Perfiles de usuario, roles y permisos detallados
- **[historias_de_usuario.md](historias_de_usuario.md)** - Historias de usuario y requisitos funcionales

### 🗄️ Base de Datos
- **[db_erd.md](db_erd.md)** - Diagrama de entidad-relación de la base de datos
- **[db_erd.puml](db_erd.puml)** - Diagrama ER en formato PlantUML
- **[db_erd_sources.txt](db_erd_sources.txt)** - Fuentes y referencias del diagrama ER

### 🎨 Diseño e Interfaz
- **[JUNTA_ANDALUCIA_DESIGN.md](JUNTA_ANDALUCIA_DESIGN.md)** - Guía de diseño y estándares visuales

## 🚀 Inicio Rápido

Para comenzar con el sistema:

1. **Instalación**: Consulta [README.md](../README.md#instalación-y-uso)
2. **Configuración de seguridad**: Lee [SECURITY.md](SECURITY.md)
3. **Perfiles de usuario**: Revisa [user_profiles.md](user_profiles.md)
4. **Sistema de auditoría**: Consulta [auditoria_logging.md](auditoria_logging.md)

## 🏗️ Arquitectura del Sistema

### Componentes Principales
- **Backend**: Flask + SQLAlchemy + PostgreSQL/SQLite
- **Frontend**: Bootstrap + HTML/CSS/JavaScript
- **Seguridad**: Sistema de permisos granular + auditoría completa
- **API**: RESTful API con documentación automática

### Servicios Core
- **Gestión de Vehículos**: CRUD completo con trazabilidad
- **Sistema de Reservas**: Ciclo de vida completo de reservas
- **Gestión de Usuarios**: Autenticación y autorización
- **API REST**: Endpoints FastAPI para integración externa
- **Auditoría**: Logging automático de todas las operaciones

## 🔌 API REST

### Documentación de Endpoints
- **[API Endpoints](../api_app.py)**: Aplicación FastAPI principal
- **[Esquemas Pydantic](../app/schemas/)**: Modelos de datos API
- **[Dependencias API](../app/api/deps.py)**: Autenticación y dependencias

### Endpoints Disponibles
- `POST /api/v1/auth/login` - Autenticación JWT
- `GET /api/v1/vehicles/` - Listar vehículos
- `POST /api/v1/vehicles/` - Crear vehículo
- `GET /api/v1/reservations/` - Listar reservas
- `POST /api/v1/reservations/` - Crear reserva
- Y más endpoints para todas las entidades...

### 🚀 Ejecutar API
```bash
python api_app.py
# Acceder en: http://localhost:8000/docs
```

### 🧪 Probar API
```bash
# Ejecutar pruebas de la API REST
python scripts/test_api_rest.py
```

## 🔐 Seguridad

El sistema implementa múltiples capas de seguridad:

- **Autenticación**: Flask-Login con bcrypt
- **Autorización**: Sistema de roles y permisos granular
- **Auditoría**: Logging completo de base de datos y operaciones
- **Protecciones**: CSRF, rate limiting, headers de seguridad

## 📊 Monitoreo y Logs

- **Database Logs**: `database.log` - Operaciones CRUD con before/after values
- **Security Logs**: `security.log` - Eventos de autenticación y permisos
- **Herramientas de análisis**: Scripts en `scripts/` para análisis de logs

## 🧪 Testing

```bash
# Ejecutar todos los tests
python -m pytest

# Tests específicos
python -m pytest tests/test_security.py
python -m pytest tests/test_reservations_flow.py

# Verificar logging
python scripts/test_database_logging.py
```

## 📞 Soporte

Para soporte técnico o preguntas sobre la documentación:

- **Issues**: Crea un issue en el repositorio
- **Documentación**: Esta carpeta contiene toda la información técnica
- **Scripts**: Revisa `scripts/` para utilidades de mantenimiento

---

**Última actualización**: Enero 2026
**Versión del sistema**: 1.1.0
**Versión de documentación**: 1.0</content>
<parameter name="filePath">c:\Users\ramon\OneDrive\Documentos\windsurf\gestionVehiculos\docs\README.md