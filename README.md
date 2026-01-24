# Sistema de Gestión de Flota de Vehículos

Aplicación web para la gestión integral de flotas de vehículos, desarrollada con Flask.

## 🚀 Características

- Gestión de vehículos, conductores y reservas
- Sistema de mantenimiento y cumplimiento normativo
- Autenticación segura con roles
- Interfaz responsive con Bootstrap

## 🛠️ Tecnologías

- **Backend**: Flask, SQLAlchemy, PostgreSQL/SQLite
- **Frontend**: Bootstrap, HTML/CSS
- **Seguridad**: Flask-Login, Flask-Limiter, CSRF

## 🚀 Instalación y Uso

1. Clona el repositorio
2. Instala dependencias: `pip install -r requirements.txt`
3. Configura variables de entorno (ver `app/core/config.py`)
4. Ejecuta: `python run.py`

## 🧪 Tests

Ejecuta tests con: `python -m pytest`

## 📄 Licencia

Propiedad de la Junta de Andalucía.

**Versión**: 1.0.0
```bash
python run.py
```
- 🌐 **URL**: http://127.0.0.1:5000
- 🔧 **Modo desarrollo**: Activado automáticamente
- 🔄 **Recarga automática**: Cambios en código se reflejan inmediatamente

### Producción
```bash
# Configurar variables de entorno para producción
export FLASK_ENV=production
export SECRET_KEY=<tu-clave-secreta>
export DATABASE_URL=<url-de-tu-base-de-datos>

python run.py
```

## 📖 Uso de la Aplicación

### Acceso al Sistema
1. Abrir navegador en `http://127.0.0.1:5000`
2. Iniciar sesión con credenciales de administrador
3. Acceder al **dashboard principal**

### Funcionalidades Principales

#### Dashboard
- **Vista calendario** mensual de reservas
- **Estadísticas rápidas** de flota
- **Accesos directos** a funciones principales

#### Gestión de Vehículos
- **Lista completa** con filtros avanzados
- **Ficha detallada** de cada vehículo
- **Registro de mantenimiento** y revisiones
- **Documentación asociada**

#### Gestión de Conductores
- **Base de datos** de conductores autorizados
- **Control de permisos** y carnets
- **Historial de asignaciones**
- **Alertas de vencimientos**

#### Sistema de Reservas
- **Interfaz calendario** intuitiva
- **Gestión de conflictos** automática
- **Aprobaciones workflow**
- **Notificaciones** por email

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Flask
FLASK_ENV=development|production
SECRET_KEY=<clave-secreta-obligatoria>

# Base de datos
USE_SQLITE=True|False
SQLITE_DB_PATH=gestion_vehiculos.db
# Para PostgreSQL:
POSTGRES_SERVER=localhost
POSTGRES_USER=usuario
POSTGRES_PASSWORD=contraseña
POSTGRES_DB=gestion_vehiculos

# Seguridad
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Usuario administrador inicial
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_USERNAME=admin
FIRST_SUPERUSER_PASSWORD=<contraseña-segura>
```

### Configuración de Seguridad

#### Rate Limiting
- **Login**: 5 intentos por minuto
- **Registro**: 3 intentos por hora
- **General**: 200 peticiones por día, 50 por hora

#### Content Security Policy
- ✅ Recursos de `cdn.jsdelivr.net` permitidos
- ✅ Bootstrap e íconos cargan correctamente
- ✅ Estilos inline seguros permitidos

## 🧪 Testing

### Ejecutar tests
Se recomienda usar `pytest` directamente. Ejemplos:
```bash
# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar un test concreto
pytest tests/test_example.py -q

# Ejecutar con cobertura
pytest --cov=app tests/
```

Nota: el antiguo script `run_tests.py` fue movido a `archive_root_files/` para limpieza del repositorio raíz.

### Página de Test Bootstrap
Para verificar que Bootstrap funciona correctamente:
```
http://127.0.0.1:5000/test-bootstrap
```
*(Requiere autenticación)*

## 📁 Estructura del Proyecto

```
gestionVehiculos/
├── app/                          # Código principal de la aplicación
│   ├── controllers/             # Controladores Flask (lógica de rutas)
│   ├── models/                  # Modelos de datos SQLAlchemy
│   ├── services/                # Lógica de negocio
│   ├── templates/               # Plantillas HTML
│   ├── static/                  # Archivos estáticos (CSS, JS, imágenes)
│   ├── core/                    # Configuración y utilidades
│   └── extensions.py            # Extensiones Flask
├── requirements.txt              # Dependencias Python
├── requirements-dev.txt         # Dependencias de desarrollo
├── run.py                       # Punto de entrada de la aplicación
├── pytest.ini                  # Configuración de tests
└── .env.example                 # Ejemplo de variables de entorno
```

## 🔒 Seguridad

### Medidas Implementadas
- **Autenticación robusta** con hash seguro de contraseñas
- **Rate limiting** contra ataques de fuerza bruta
- **CSRF protection** en formularios
- **Content Security Policy** contra XSS
- **Validación estricta** de entradas
- **Auditoría completa** de acciones

### Mejores Prácticas
- ✅ **Nunca** almacenar contraseñas en texto plano
- ✅ **Validación** en cliente y servidor
- ✅ **Principio de menor privilegio** en permisos
- ✅ **Logs de seguridad** para auditoría
- ✅ **Actualizaciones regulares** de dependencias

## 🚨 Solución de Problemas

### Bootstrap no carga correctamente
**Síntoma**: Íconos no visibles, estilos rotos

**Solución**:
1. Recargar completamente (`Ctrl+F5`)
2. Verificar conexión a internet (CDN externos)
3. Comprobar consola del navegador (F12)
4. Acceder a `/test-bootstrap` para diagnóstico

### Error de permisos de base de datos
**Solución**:
```bash
# Linux/Mac
chmod 666 gestion_vehiculos.db

# Windows (en PowerShell como administrador)
icacls gestion_vehiculos.db /grant Everyone:F
```

### Error de puerto ocupado
```bash
# Encontrar proceso usando el puerto
netstat -ano | findstr :5000

# Terminar proceso (reemplazar <PID>)
taskkill /PID <PID> /F
```

## 📞 Soporte

Para soporte técnico o reporte de bugs:
1. Revisar los logs de la aplicación
2. Verificar la configuración de variables de entorno
3. Comprobar conectividad de red
4. Consultar la documentación de Flask

## 📄 Licencia

Este proyecto es propiedad de la **Junta de Andalucía** y está desarrollado para uso exclusivo en la administración pública.

---

**Versión**: 1.0.0
**Última actualización**: 30 de octubre de 2025
**Estado**: ✅ Producción

## Notas sobre archivos en el root y archivado

- Para mantener el repositorio raíz limpio, muchos scripts de setup y utilidades fueron movidos a `archive_root_files/` en vez de eliminarse. Revisa ese directorio antes de ejecutar scripts antiguos.
- No incluyas en el control de versiones archivos sensibles como `gestion_vehiculos.db` o `security.log`.
- Si al intentar mover o eliminar archivos observas que están "en uso" en Windows, cierra editores/servicios que los puedan tener abiertos (por ejemplo servidores de desarrollo o extensiones LSP). En PowerShell puedes listar procesos que referencian la ruta del repo:

```powershell
$repo = 'C:\Users\ramon\OneDrive\Documentos\windsurf\gestionVehiculos'
Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -and ($_.CommandLine -match [regex]::Escape($repo)) } | Select-Object ProcessId,Name,CommandLine
```

Detén procesos por PID únicamente si estás seguro de su origen:

```powershell
Stop-Process -Id <PID> -Force
```
