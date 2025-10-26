# 🚀 Guía de Inicio Rápido

## Sistema de Gestión de Flota de Vehículos

### ⚡ Inicio Rápido (SQLite)

**1. Instalar dependencias del backend:**
```bash
pip install -r requirements.txt
```

**2. Inicializar la base de datos con datos de prueba:**
```bash
python init_db.py
```

**3. Iniciar el servidor backend:**
```bash
python run.py
```

El backend estará disponible en: **http://localhost:8000**
- Documentación API: **http://localhost:8000/docs**

**4. Instalar dependencias del frontend:**
```bash
cd frontend
npm install
```

**5. Iniciar el servidor frontend:**
```bash
npm run dev
```

El frontend estará disponible en: **http://localhost:3000**

---

### 🔑 Credenciales de Acceso

```
Usuario: admin
Contraseña: admin123
```

---

### 📊 Datos de Prueba Incluidos

El script `init_db.py` crea automáticamente:

- ✅ **3 Unidades Organizativas**
  - Dirección General
  - Departamento de Operaciones
  - Departamento de Logística

- ✅ **4 Vehículos**
  - Toyota Corolla (1234ABC) - Disponible
  - Ford Transit (5678DEF) - Disponible
  - Renault Clio (9012GHI) - En uso
  - Mercedes Sprinter (3456JKL) - Mantenimiento

- ✅ **3 Conductores**
  - Pedro Martínez (Oficial)
  - Ana López (Oficial)
  - Luis Fernández (Autorizado)

- ✅ **2 Reservas**
  - Próximas reservas confirmadas

- ✅ **Registros de Mantenimiento e ITV**

---

### 🎨 Características del Frontend

- **Dashboard Moderno** con estadísticas en tiempo real
- **Gestión de Vehículos** con formularios modales
- **Gestión de Conductores** y asociaciones
- **Sistema de Reservas** con validación de solapamientos
- **Mantenimiento e ITV** con alertas
- **Cumplimiento Normativo** (accidentes, multas, impuestos)
- **Diseño Responsivo** con TailwindCSS
- **Notificaciones** en tiempo real

---

### 🔧 Tecnologías Utilizadas

**Backend:**
- FastAPI (Python)
- SQLAlchemy ORM
- SQLite (desarrollo) / PostgreSQL (producción)
- JWT Authentication
- Pydantic para validación

**Frontend:**
- React 18 + TypeScript
- Vite
- TailwindCSS
- React Query
- Zustand (estado global)
- Lucide React (iconos)

---

### 📝 Próximos Pasos

1. **Explorar el Dashboard** - Ver estadísticas y actividad reciente
2. **Crear un Vehículo** - Usar el botón "Nuevo Vehículo"
3. **Gestionar Conductores** - Asociar conductores a vehículos
4. **Crear Reservas** - Probar el sistema de reservas
5. **Revisar la API** - Explorar la documentación en /docs

---

### 🐛 Solución de Problemas

**Error de puerto ocupado:**
```bash
# Backend (puerto 8000)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Frontend (puerto 3000)
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Reiniciar la base de datos:**
```bash
# Eliminar la base de datos actual
del gestion_vehiculos.db

# Volver a inicializar
python init_db.py
```

---

### 📚 Documentación Adicional

- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Código Fuente:** Revisar los archivos en `/app` y `/frontend/src`

---

### 🎯 Funcionalidades Implementadas

✅ Autenticación y autorización
✅ CRUD completo de vehículos
✅ CRUD completo de conductores
✅ Sistema de reservas con validación
✅ Registro de toma efectiva de vehículos
✅ Gestión de mantenimiento e ITV
✅ Gestión de cumplimiento normativo
✅ Dashboard con estadísticas
✅ Interfaz moderna y responsiva
✅ Base de datos SQLite para desarrollo
✅ Datos de prueba precargados

---

¡Disfruta usando el sistema! 🎉
