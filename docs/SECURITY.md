# Guía de Seguridad - Sistema de Gestión de Flota

## Medidas de Seguridad Implementadas

### 1. Configuración Segura
- ✅ **Secret Key segura**: Generada automáticamente con `secrets.token_hex(32)`
- ✅ **Configuración de producción**: Variables de entorno obligatorias para producción
- ✅ **Timeouts de sesión**: 1 día en lugar de 8 días
- ✅ **Host seguro**: Por defecto `127.0.0.1` (localhost) en lugar de `0.0.0.0`

### 2. Protección contra Ataques de Fuerza Bruta
- ✅ **Rate Limiting**: 5 intentos por minuto para login, 3 registros por hora
- ✅ **Seguimiento de intentos fallidos**: Sistema interno de rastreo por IP
- ✅ **Mensajes de error genéricos**: Evita enumeración de usuarios

### 3. Protección CSRF
- ✅ **Tokens CSRF**: Implementados en formularios de login y registro
- ✅ **Protección automática**: Flask-WTF CSRF protection habilitado

### 4. Validación y Sanitización de Datos
- ✅ **Validación estricta de entrada**:
  - Emails con formato correcto usando `email-validator`
  - Usuarios con caracteres permitidos y longitud adecuada
  - Contraseñas con requisitos de complejidad
  - Números de teléfono y placas de vehículos validados
- ✅ **Sanitización**: Uso de `bleach` para limpiar datos HTML
- ✅ **Longitud máxima**: Límites establecidos para todos los campos

### 5. Auditoría y Logging de Seguridad
- ✅ **Registro de eventos de seguridad**:
  - Intentos de autenticación (exitosos y fallidos)
  - Registros de usuarios
  - Actividades sospechosas
  - Errores de registro
- ✅ **Sistema de auditoría de base de datos**:
  - Logging automático de todas las operaciones CRUD
  - Captura de cambios con valores antes/después
  - Trazabilidad completa de transacciones
  - Información detallada de usuario y contexto
- ✅ **Archivos de log dedicados**:
  - `security.log`: Eventos de seguridad y autenticación
  - `database.log`: Operaciones de base de datos y cambios de modelo

### 6. Headers de Seguridad HTTP
- ✅ **Content Security Policy (CSP)**: Restringe fuentes de contenido
- ✅ **X-Frame-Options**: Previene clickjacking (`DENY`)
- ✅ **X-XSS-Protection**: Protección XSS del navegador
- ✅ **Referrer Policy**: Control de información de referrer
- ✅ **Feature Policy**: Restringe acceso a características sensibles

### 7. Autenticación Segura
- ✅ **Hash de contraseñas**: Usando bcrypt con salt automático
- ✅ **Validación de redirecciones**: URLs de redirección validadas
- ✅ **Gestión de sesiones**: Flask-Login configurado correctamente

## Sistema de Auditoría de Base de Datos

### Arquitectura del Sistema de Logging

El sistema implementa **auditoría completa de todas las operaciones de base de datos** mediante múltiples capas de logging:

#### 🏗️ **Componentes del Sistema**

1. **Database Audit Service** (`app/services/database_audit_service.py`)
   - SQLAlchemy event listeners automáticos
   - Captura de operaciones CRUD en tiempo real
   - Logging estructurado JSON con metadatos completos

2. **Security Audit Service** (`app/services/security_audit_service.py`)
   - Logging de eventos de seguridad y autenticación
   - Métodos para logging de cambios de modelo
   - Integración con operaciones de negocio

3. **Inicialización Automática** (`app/extensions.py`)
   - Configuración automática de listeners al iniciar la aplicación
   - Logging de transacciones y commits

#### 📊 **Tipos de Operaciones Auditadas**

- **Operaciones CRUD**: CREATE, UPDATE, DELETE en todas las tablas
- **Transacciones**: Commits, rollbacks y operaciones SQL ejecutadas
- **Autenticación**: Login/logout, intentos fallidos, creación de usuarios
- **Permisos**: Verificaciones de acceso, denegaciones
- **Cambios de Modelo**: Valores antes/después en modificaciones

#### 📋 **Información Registrada por Operación**

Cada operación registra automáticamente:
- **Identificación**: Usuario, IP, User-Agent, Session ID, timestamp
- **Operación**: Tipo (CREATE/UPDATE/DELETE), tabla afectada, ID del registro
- **Cambios**: Campos modificados, valores anteriores/nuevos
- **Contexto**: Servicio que ejecutó la operación, acción de negocio
- **Metadatos**: Duración, código de respuesta, endpoint

#### 📁 **Archivos de Log y Formatos**

**Database Log** (`database.log`):
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
    "year": 2023
  }
}
```

**Security Log** (`security.log`):
```json
{
  "timestamp": "2026-01-26T22:39:33.422384",
  "level": "INFO",
  "user": "[user_123]",
  "event": "authentication_success",
  "details": {
    "username": "admin",
    "ip": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
  }
}
```

#### 🔍 **Herramientas de Análisis y Monitoreo**

```bash
# Análisis de logs de seguridad
python scripts/analyze_security_logs.py --summary
python scripts/analyze_security_logs.py --user-activity admin
python scripts/analyze_security_logs.py --failed-logins
python scripts/analyze_security_logs.py --suspicious
python scripts/analyze_security_logs.py --api-performance

# Prueba del sistema de logging
python scripts/test_database_logging.py
```

#### 🛡️ **Beneficios de Seguridad**

- **Trazabilidad Completa**: Todas las operaciones quedan registradas con contexto completo
- **Detección de Anomalías**: Identificación automática de actividades sospechosas
- **Cumplimiento Normativo**: Requisitos de auditoría y retención de logs
- **Análisis Forense**: Capacidad de reconstruir eventos y cambios
- **Monitoreo Continuo**: Alertas automáticas para eventos críticos

#### ⚙️ **Configuración y Mantenimiento**

- **Rotación de Logs**: Los logs se rotan automáticamente por tamaño y fecha
- **Compresión**: Logs antiguos se comprimen para ahorrar espacio
- **Retención**: Configurable según políticas de la organización
- **Monitoreo**: Alertas para eventos de alta severidad

## Configuración de Producción

### Variables de Entorno Requeridas

```bash
# Configuración básica
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False

# Base de datos (PostgreSQL recomendado)
USE_SQLITE=False
POSTGRES_SERVER=your-db-server
POSTGRES_USER=your-db-user
POSTGRES_PASSWORD=your-secure-db-password
POSTGRES_DB=your-db-name

# Seguridad adicional
ACCESS_TOKEN_EXPIRE_MINUTES=60
HOST=127.0.0.1
PORT=5000
```

## Recomendaciones Adicionales de Seguridad

### 1. Configuración del Servidor Web
- Usar HTTPS en producción (certificado SSL)
- Configurar servidor web (nginx/apache) como proxy reverso
- Implementar firewall (ufw/iptables)

### 2. Base de Datos
- Usar PostgreSQL en producción
- Configurar usuario de base de datos con permisos mínimos
- Realizar backups cifrados regularmente
- Usar prepared statements (ya implementado con SQLAlchemy)

### 3. Monitoreo
- Configurar alertas para eventos de seguridad
- Monitorear logs de seguridad regularmente
- Implementar SIEM si es posible

### 4. Mantenimiento
- Actualizar dependencias regularmente
- Realizar auditorías de seguridad periódicas
- Revisar y rotar logs de seguridad
- Monitorear vulnerabilidades conocidas (CVE)

## Instalación de Dependencias

```bash
pip install -r requirements.txt
```

## Ejecutar en Producción

```bash
# Con variables de entorno
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
# ... otras variables

python run.py

# O usando gunicorn (recomendado)
gunicorn --bind 127.0.0.1:5000 --workers 4 run:app
```

## Checklist de Seguridad para Producción

- [ ] Variables de entorno configuradas correctamente
- [ ] Base de datos PostgreSQL configurada
- [ ] Certificado SSL instalado
- [ ] Servidor web configurado como proxy reverso
- [ ] Firewall configurado
- [ ] Logs de seguridad monitoreados
- [ ] Backups automatizados configurados
- [ ] Dependencias actualizadas

## Contacto de Seguridad

Para reportar vulnerabilidades de seguridad, por favor contactar al equipo de desarrollo inmediatamente.

---

### Notas operativas y de desarrollo

- Evita incluir en commits archivos sensibles como la base de datos de desarrollo (`gestion_vehiculos.db`) o `security.log`.
- Muchos scripts y utilidades han sido archivados en `archive_root_files/`; antes de ejecutar scripts antiguos, revísalos y actualiza según tu entorno.
- Si necesitas mover o eliminar archivos que aparecen como "en uso" en Windows, identifica procesos que usan la ruta del repo y ciérralos (editores, servidores, LSP). Por ejemplo, en PowerShell:

```powershell
$repo = 'C:\Users\ramon\OneDrive\Documentos\windsurf\gestionVehiculos'
Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -and ($_.CommandLine -match [regex]::Escape($repo)) } | Select-Object ProcessId,Name,CommandLine
```

Usa `Stop-Process -Id <PID> -Force` con precaución para detener procesos que bloqueen archivos.

**Nota**: Esta guía debe actualizarse regularmente conforme se implementen nuevas medidas de seguridad.
