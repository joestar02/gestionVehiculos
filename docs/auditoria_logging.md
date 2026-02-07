# Sistema de Auditoría y Logging

## Resumen Ejecutivo

Este documento detalla el sistema completo de auditoría implementado en el Sistema de Gestión de Flota de Vehículos, incluyendo logging de base de datos, seguridad y análisis de logs.

**Archivos principales**:
- `app/services/security_audit_service.py`: Servicio de auditoría de seguridad
- `app/services/database_audit_service.py`: Servicio de auditoría de base de datos
- `app/extensions.py`: Inicialización automática de listeners
- `scripts/test_database_logging.py`: Script de prueba del sistema
- `scripts/analyze_security_logs.py`: Herramientas de análisis

**Archivos de log**:
- `security.log`: Eventos de seguridad y autenticación
- `database.log`: Operaciones de base de datos

**Última actualización**: Enero 2026
**Versión**: 1.0

## Arquitectura del Sistema

### Componentes Principales

#### 1. Database Audit Service
- **Ubicación**: `app/services/database_audit_service.py`
- **Función**: Captura automática de todas las operaciones CRUD mediante SQLAlchemy event listeners
- **Características**:
  - Logging automático de INSERT, UPDATE, DELETE, SELECT
  - Captura de transacciones (commits/rollbacks)
  - Información detallada de cambios (before/after values)
  - Contexto completo de usuario y operación

#### 2. Security Audit Service
- **Ubicación**: `app/services/security_audit_service.py`
- **Función**: Logging de eventos de seguridad y operaciones de negocio
- **Características**:
  - Autenticación (login/logout, intentos fallidos)
  - Verificaciones de permisos
  - Cambios de modelo con contexto de negocio
  - Eventos de seguridad con niveles de severidad

#### 3. API REST (FastAPI)
- **Ubicación**: `api_app.py`, `app/api/endpoints/`
- **Función**: Endpoints REST para integración con sistemas externos
- **Características**:
  - Documentación automática (Swagger/OpenAPI)
  - Autenticación JWT
  - Endpoints para todas las entidades del sistema
  - Logging integrado de operaciones API

#### 4. Inicialización Automática
- **Ubicación**: `app/extensions.py`
- **Función**: Configuración automática de listeners al iniciar la aplicación
- **Características**:
  - Setup automático de SQLAlchemy listeners
  - Configuración de handlers de logging
  - Integración transparente con la aplicación

## Tipos de Operaciones Auditadas

### Operaciones de Base de Datos
- **CREATE**: Inserción de nuevos registros
- **UPDATE**: Modificación de registros existentes
- **DELETE**: Eliminación de registros (soft delete)
- **SELECT**: Consultas de lectura (opcional, configurable)

### Eventos de Seguridad
- **Autenticación**: Login/logout, creación de usuarios, cambios de contraseña
- **Permisos**: Verificaciones de acceso, denegaciones
- **Sesiones**: Inicio/fin de sesiones, timeouts
- **Actividad Sospechosa**: Intentos de acceso no autorizado, rate limiting

### Operaciones de Negocio
- **Vehículos**: CRUD completo con trazabilidad
- **Reservas**: Ciclo de vida completo (crear, confirmar, iniciar, completar, cancelar)
- **Usuarios**: Gestión de usuarios y roles
- **Asignaciones**: Vinculación conductor-vehículo

## Formato de Logs

### Database Log (database.log)
```json
{
  "timestamp": "2026-01-26T22:39:33.422384",
  "level": "INFO",
  "user": "[system]",
  "operation": "CREATE",
  "table": "vehicle",
  "record_id": "5",
  "action": "vehicle_created",
  "new_values": {
    "license_plate": "AUDIT-001",
    "make": "TestMake",
    "model": "TestModel",
    "year": 2023,
    "vehicle_type": "coche",
    "ownership_type": "propiedad"
  },
  "created_by_service": "VehicleService.create_vehicle"
}
```

### Security Log (security.log)
```json
{
  "timestamp": "2026-01-26T22:39:33.422384",
  "level": "INFO",
  "user": "[user_123]",
  "event": "authentication_success",
  "severity": "info",
  "details": {
    "username": "admin",
    "ip": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "session_id": "abc123",
    "endpoint": "/login",
    "method": "POST",
    "duration_ms": 150
  }
}
```

## Información Registrada

### Campos Comunes
- **timestamp**: Fecha y hora exacta de la operación
- **level**: Nivel de log (INFO, WARNING, ERROR)
- **user**: Identificación del usuario (ID, nombre, rol)
- **ip**: Dirección IP del cliente
- **user_agent**: Información del navegador/cliente
- **session_id**: ID de sesión único

### Campos Específicos por Tipo

#### Operaciones CRUD
- **operation**: CREATE, UPDATE, DELETE
- **table**: Nombre de la tabla afectada
- **record_id**: ID del registro modificado
- **old_values**: Valores anteriores (solo UPDATE/DELETE)
- **new_values**: Valores nuevos (solo CREATE/UPDATE)
- **changed_fields**: Lista de campos modificados
- **change_count**: Número de campos modificados

#### Eventos de Seguridad
- **event**: Tipo de evento (authentication_success, permission_denied, etc.)
- **severity**: Criticidad (info, warning, error, critical)
- **details**: Información contextual específica del evento

## Herramientas de Análisis

### Script de Análisis de Logs
```bash
# Resumen general
python scripts/analyze_security_logs.py --summary

# Actividad de usuario específico
python scripts/analyze_security_logs.py --user-activity admin

# Intentos de login fallidos
python scripts/analyze_security_logs.py --failed-logins

# Eventos sospechosos
python scripts/analyze_security_logs.py --suspicious

# Rendimiento de API
python scripts/analyze_security_logs.py --api-performance
```

### Script de Prueba
```bash
# Ejecuta pruebas completas del sistema de logging
python scripts/test_database_logging.py
```

## Configuración y Mantenimiento

### Variables de Entorno
```bash
# Logging
LOG_LEVEL=INFO
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5
LOG_FORMAT=json

# Auditoría
AUDIT_ENABLED=true
AUDIT_DATABASE_OPERATIONS=true
AUDIT_SECURITY_EVENTS=true
```

### Rotación de Logs
- **Rotación por tamaño**: 10MB por archivo
- **Retención**: 5 archivos de backup
- **Compresión**: Archivos antiguos comprimidos automáticamente
- **Ubicación**: Directorio raíz del proyecto

### Monitoreo
- **Alertas**: Eventos de alta severidad generan alertas
- **Dashboards**: Métricas disponibles para monitoreo
- **Reportes**: Generación automática de reportes de auditoría

## Casos de Uso

### Cumplimiento Normativo
- **GDPR**: Trazabilidad de operaciones con datos personales
- **SOX**: Auditoría financiera y operativa
- **ISO 27001**: Control de acceso y logging de seguridad

### Seguridad
- **Detección de intrusiones**: Identificación de patrones sospechosos
- **Análisis forense**: Reconstrucción de incidentes de seguridad
- **Monitoreo continuo**: Alertas en tiempo real

### Operaciones
- **Solución de problemas**: Debugging con contexto completo
- **Optimización**: Análisis de rendimiento de operaciones
- **Auditoría interna**: Verificación de cumplimiento de procesos

## Implementación en Servicios

### Patrón de Logging en Servicios
```python
from app.services.security_audit_service import SecurityAudit

class ExampleService:
    @staticmethod
    def create_example(data):
        # Capturar valores antes de cambios
        old_data = {...}  # Si existe registro previo
        
        # Realizar operación
        example = ExampleModel(**data)
        db.session.add(example)
        db.session.commit()
        
        # Log de creación
        SecurityAudit.log_model_change(
            model_class='Example',
            operation='CREATE',
            instance_id=str(example.id),
            new_data=data,
            details={
                'action': 'example_created',
                'created_by_service': 'ExampleService.create_example'
            }
        )
        
        return example
```

### Logging de Eventos de Seguridad
```python
# Evento de seguridad
SecurityAudit.log_security_event(
    event_type='permission_denied',
    severity='warning',
    details={
        'action': 'access_attempt',
        'resource': 'vehicle',
        'permission': 'vehicle:delete',
        'reason': 'insufficient_permissions'
    }
)
```

## Métricas y KPIs

### Métricas de Seguridad
- **Intentos de login fallidos**: Por usuario/IP
- **Denegaciones de permisos**: Por rol/recurso
- **Sesiones activas**: Número y duración
- **Eventos de alta severidad**: Conteo por tipo

### Métricas de Rendimiento
- **Tiempo de respuesta**: Por endpoint/operación
- **Volumen de operaciones**: Por tipo/usuario
- **Tasa de error**: Por servicio/operación
- **Uso de recursos**: CPU/memoria durante operaciones

### Métricas de Cumplimiento
- **Cobertura de auditoría**: Porcentaje de operaciones auditadas
- **Tiempo de retención**: Cumplimiento de políticas
- **Accesos no autorizados**: Detección y respuesta
- **Reportes generados**: Frecuencia y completitud

## Troubleshooting

### Problemas Comunes

#### Logs no aparecen
- Verificar configuración de logging en `app/extensions.py`
- Comprobar permisos de escritura en directorio de logs
- Revisar nivel de log configurado

#### Eventos faltantes
- Verificar que servicios llamen a métodos de logging
- Comprobar configuración de listeners de SQLAlchemy
- Revisar filtros de logging

#### Rendimiento degradado
- Considerar logging asíncrono para alta carga
- Implementar muestreo para operaciones de alto volumen
- Optimizar formato de logs (JSON vs texto)

### Diagnóstico
```bash
# Verificar estado del sistema de logging
python scripts/test_database_logging.py

# Analizar logs existentes
python scripts/analyze_security_logs.py --summary

# Verificar configuración
python -c "from app.extensions import app; print('Logging configured:', hasattr(app, 'logger'))"
```

## Conclusión

El sistema de auditoría implementado proporciona **trazabilidad completa** de todas las operaciones del sistema, garantizando:

- **Seguridad**: Detección y respuesta a amenazas
- **Cumplimiento**: Requisitos regulatorios y normativos
- **Transparencia**: Visibilidad completa de operaciones
- **Confianza**: Base sólida para auditorías y revisiones

La arquitectura modular y extensible permite adaptarse a futuros requisitos de auditoría y seguridad.</content>
<parameter name="filePath">c:\Users\ramon\OneDrive\Documentos\windsurf\gestionVehiculos\docs\auditoria_logging.md