# Sistema de Gestión de Flota - Junta de Andalucía

Aplicación web completa para la gestión integral de flotas de vehículos de la Junta de Andalucía, desarrollada con Flask y tecnologías modernas.

## 🚀 Características Principales

### Gestión de Vehículos
- **Catálogo completo** de vehículos con toda la información técnica
- **Clasificación por tipos**: Turismos, furgonetas, vehículos especiales
- **Estados de vehículos**: Disponible, en uso, mantenimiento, averiado
- **Propiedad**: Propios, renting, leasing

### Gestión de Conductores
- **Registro completo** de conductores autorizados
- **Tipos de conductor**: Funcionario, eventual, externo
- **Control de carnets**: Vencimientos y renovaciones automáticas
- **Asignaciones históricas** y actuales

### Sistema de Reservas
- **Reserva avanzada** con calendario integrado
- **Gestión de conflictos** de disponibilidad
- **Aprobaciones automáticas** según permisos
- **Historial completo** de reservas

### Mantenimiento y Cumplimiento
- **Planes de mantenimiento** preventivo y correctivo
- **Control de ITV** y seguros
- **Registro de accidentes** y sanciones
- **Documentación legal** y permisos

### Seguridad y Auditoría
- **Autenticación segura** con rate limiting
- **Registro completo** de actividades
- **Permisos granulares** por roles
- **Auditoría de seguridad** automática

## 🛠️ Tecnologías Utilizadas

### Backend
- **Flask 3.0** - Framework web Python
- **SQLAlchemy 2.0** - ORM para base de datos
- **Flask-Login** - Gestión de sesiones
- **Flask-Limiter** - Protección contra ataques
- **Flask-Talisman** - Headers de seguridad

### Frontend
- **Bootstrap 5.3** - Framework CSS responsive
- **Bootstrap Icons 1.11** - Iconografía completa
- **CSS personalizado** - Identidad corporativa Junta de Andalucía

### Base de Datos
- **SQLite** (desarrollo) / **PostgreSQL** (producción)
- **Alembic** - Migraciones de esquema
- **Relaciones complejas** - Modelo entidad-relación optimizado

### Seguridad
- **Rate limiting** - 5 peticiones/minuto para login
- **CSRF Protection** - Tokens anti-falsificación
- **Content Security Policy** - Protección XSS
- **Auditoría completa** - Log de todas las acciones

## 📋 Instalación y Configuración

### Prerrequisitos
- **Python 3.11+**
- **pip** (gestor de paquetes Python)
- **Git** (opcional, para control de versiones)

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd gestionVehiculos
```

### 2. Crear entorno virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 5. Inicializar base de datos
```bash
python run.py
```
*(La aplicación se iniciará y creará automáticamente las tablas)*

### 6. Crear usuario administrador
La aplicación creará automáticamente un usuario administrador:
- **Usuario**: `admin`
- **Contraseña**: `admin123`

## 🚀 Inicio Rápido

### Desarrollo
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
```bash
# Todos los tests
python run_tests.py

# Tests específicos
python -m pytest tests/ -v

# Tests con cobertura
python -m pytest --cov=app tests/
```

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
**Última actualización**: Octubre 2025
**Estado**: ✅ Producción
