# 🚀 Inicio Rápido - Gestión de Flota

## ✅ Instalación en 3 pasos

### 1. Preparar entorno
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar aplicación
```bash
# Copiar configuración ejemplo
cp .env.example .env

# La aplicación está lista - no requiere configuración adicional
```

### 3. Iniciar aplicación
```bash
python run.py
```

🌐 **Acceder en**: http://127.0.0.1:5000

## 🔑 Credenciales iniciales

**Usuario administrador:**
- **Usuario**: `admin`
- **Contraseña**: `admin123`

## 🎯 Funcionalidades principales

### Gestión de Vehículos
- ✅ Ver catálogo completo de vehículos
- ✅ Registrar nuevos vehículos
- ✅ Gestionar mantenimiento y revisiones
- ✅ Controlar documentación (ITV, seguros)

### Gestión de Conductores
- ✅ Base de datos de conductores autorizados
- ✅ Control de carnets y permisos
- ✅ Asignación de vehículos
- ✅ Alertas de vencimientos

### Sistema de Reservas
- ✅ Reserva de vehículos con calendario
- ✅ Gestión de conflictos de disponibilidad
- ✅ Aprobaciones automáticas
- ✅ Historial completo

### Seguridad y Cumplimiento
- ✅ Autenticación segura
- ✅ Auditoría de acciones
- ✅ Control de permisos
- ✅ Logs de seguridad

## 🔧 Comandos útiles

```bash
# Iniciar aplicación
python run.py

# Ejecutar tests
python run_tests.py

# Página de diagnóstico Bootstrap
# http://127.0.0.1:5000/test-bootstrap

# Ver logs de seguridad
tail -f security.log
```

## 🆘 Solución de problemas comunes

### Íconos no se muestran
1. **Recargar completamente** (`Ctrl+F5`)
2. **Verificar conexión** a internet
3. **Acceder a página de test**: `/test-bootstrap`

### Error de base de datos
```bash
# Recrear base de datos limpia
rm gestion_vehiculos.db
python run.py  # Se creará automáticamente
```

### Puerto ocupado
```bash
# Encontrar y terminar proceso
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

## 📱 Acceso móvil

La aplicación es **completamente responsive** y funciona perfectamente en:
- 📱 **Teléfonos móviles**
- 📱 **Tablets**
- 💻 **Ordenadores de escritorio**

## 🎨 Diseño corporativo

Aplicación desarrollada con la **identidad visual corporativa** de la Junta de Andalucía:
- 🟢 **Verde corporativo** (#009640)
- ⚫ **Gris corporativo** (#58595B)
- 🔒 **Seguridad integrada**
- 📱 **Responsive design**

---

**¿Problemas?** Consulta el [README completo](./README.md) para documentación detallada.
