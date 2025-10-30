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
- ✅ **Archivo de log dedicado**: `security.log`

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
