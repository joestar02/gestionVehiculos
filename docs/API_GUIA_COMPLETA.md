# 🎯 API REST - Guía Completa de Ejecución

## ✅ Estado: API Implementada y Funcional

La API REST del Sistema de Gestión de Flota de Vehículos está completamente implementada y lista para usar.

---

## 🚀 Formas de Ejecutar la API

### Opción 1: API Simple Standalone (Recomendado)
```bash
python api_simple.py
```
- ✅ Ejecutable inmediatamente
- ✅ No requiere base de datos
- ✅ Perfecto para desarrollo y pruebas rápidas
- 📍 Accede en: http://localhost:8000/docs

### Opción 2: API con Pruebas Automáticas
```bash
python run_api_with_tests.py
```
- ✅ Inicia la API automáticamente
- ✅ Ejecuta suite de pruebas
- ✅ Detiene la API al finalizar
- 📊 Muestra resultados de pruebas

### Opción 3: Demo Interactiva
```bash
python run_demo.py
```
- ✅ Inicia la API automáticamente
- ✅ Ejecuta ejemplos de uso reales
- ✅ Demuestra CRUD para vehículos, conductores y reservas
- 📺 Salida formateada y fácil de leer

### Opción 4: Interfaz Web (Flask)
```bash
python run.py
```
- ✅ Accede en: http://localhost:5000
- ✅ Interfaz web completa
- ✅ Gestión visual de datos

---

## 📚 Documentación Interactiva

Una vez ejecutada la API, accede a:

| Recurso | URL | Descripción |
|---------|-----|-------------|
| Swagger UI | http://localhost:8000/docs | Documentación interactiva con pruebas |
| ReDoc | http://localhost:8000/redoc | Documentación alternativa |
| OpenAPI Schema | http://localhost:8000/openapi.json | Especificación completa en JSON |
| Health Check | http://localhost:8000/health | Estado de la API |

---

## 🔌 Endpoints Disponibles

### Vehículos
```bash
GET    /api/v1/vehicles              # Listar vehículos
POST   /api/v1/vehicles              # Crear vehículo
GET    /api/v1/vehicles/{id}         # Obtener vehículo
```

### Conductores
```bash
GET    /api/v1/drivers               # Listar conductores
POST   /api/v1/drivers               # Crear conductor
GET    /api/v1/drivers/{id}          # Obtener conductor
```

### Reservas
```bash
GET    /api/v1/reservations          # Listar reservas
POST   /api/v1/reservations          # Crear reserva
GET    /api/v1/reservations/{id}     # Obtener reserva
```

---

## 📝 Ejemplos de Uso con curl

### Verificar estado
```bash
curl http://localhost:8000/health
```

### Listar vehículos
```bash
curl http://localhost:8000/api/v1/vehicles
```

### Crear vehículo
```bash
curl -X POST http://localhost:8000/api/v1/vehicles \
  -H "Content-Type: application/json" \
  -d '{
    "license_plate": "MAL-1111",
    "make": "Renault",
    "model": "Master",
    "year": 2023
  }'
```

### Crear conductor
```bash
curl -X POST http://localhost:8000/api/v1/drivers \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Pedro",
    "last_name": "González",
    "license_number": "D1111111"
  }'
```

### Crear reserva
```bash
curl -X POST http://localhost:8000/api/v1/reservations \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "driver_id": 1,
    "start_date": "2026-02-10T08:00:00",
    "end_date": "2026-02-17T17:00:00"
  }'
```

---

## 🎓 Ejemplos de Uso con Python

```python
import requests

API_URL = "http://localhost:8000/api/v1"

# Listar vehículos
response = requests.get(f"{API_URL}/vehicles")
vehicles = response.json()
print(f"Total vehículos: {len(vehicles)}")

# Crear vehículo
new_vehicle = {
    "license_plate": "MAL-2222",
    "make": "Volvo",
    "model": "FH16",
    "year": 2022
}
response = requests.post(f"{API_URL}/vehicles", json=new_vehicle)
vehicle = response.json()
print(f"Vehículo creado: {vehicle['id']}")

# Obtener vehículo específico
response = requests.get(f"{API_URL}/vehicles/1")
vehicle = response.json()
print(f"Matrícula: {vehicle['license_plate']}")
```

---

## 🧪 Ejecución de Pruebas

Las pruebas incluyen:
- ✅ Health check de la API
- ✅ Verificación de documentación
- ✅ Validación de endpoints
- ✅ Pruebas de CRUD

```bash
# Ejecutar pruebas automáticas
python run_api_with_tests.py

# Resultado esperado:
# ✅ API Health Check: OK
# ✅ API Documentation: OK
# ✅ OpenAPI Schema: OK (8 endpoints)
# ✅ Protected Endpoint: OK (2 vehicles)
# 🎉 Pruebas de API completadas!
```

---

## 📁 Archivos Relacionados

| Archivo | Propósito |
|---------|-----------|
| `api_simple.py` | API FastAPI standalone principal |
| `api_app.py` | API FastAPI con integración Flask |
| `run_api_with_tests.py` | Ejecutor de API + pruebas |
| `run_demo.py` | Ejecutor de API + demostración |
| `demo_api.py` | Script de demostración interactiva |
| `scripts/test_api_rest.py` | Suite de pruebas |
| `README.md` | Documentación principal del proyecto |

---

## 🔧 Requisitos

```
FastAPI==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
requests==2.31.0
SQLAlchemy==2.0.0
```

Todos los requisitos están en `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## 🐛 Troubleshooting

### La API no inicia
```bash
# Verificar que el puerto 8000 está disponible
netstat -ano | findstr :8000

# Usar otro puerto
# Modifica api_simple.py línea final:
# uvicorn.run(app, host="127.0.0.1", port=8001)
```

### Error de conexión en pruebas
```bash
# Asegúrate de que la API está ejecutándose
curl http://localhost:8000/health

# Verifica que esperas lo suficiente en scripts
# run_api_with_tests.py espera automáticamente
```

### Pydantic errors
```bash
# Asegúrate de tener pydantic >= 2.0
pip install --upgrade pydantic
```

---

## 📊 Estructura de Datos de Ejemplo

### Vehicle
```json
{
  "id": 1,
  "license_plate": "MAL-1234",
  "make": "Ford",
  "model": "Transit",
  "year": 2022,
  "created_at": "2026-02-07T22:30:46.124706"
}
```

### Driver
```json
{
  "id": 1,
  "first_name": "Juan",
  "last_name": "García",
  "license_number": "D1234567",
  "created_at": "2026-02-07T22:30:46.124706"
}
```

### Reservation
```json
{
  "id": 1,
  "vehicle_id": 1,
  "driver_id": 1,
  "start_date": "2026-02-08T00:00:00",
  "end_date": "2026-02-15T00:00:00",
  "created_at": "2026-02-07T22:30:46.124706"
}
```

---

## ✨ Características

- ✅ API REST completa con FastAPI
- ✅ Documentación automática con Swagger
- ✅ Validación de datos con Pydantic
- ✅ CORS habilitado para desarrollo
- ✅ Health check endpoint
- ✅ OpenAPI schema
- ✅ Ejemplos de uso completos
- ✅ Pruebas automáticas

---

## 🚀 Próximos Pasos

1. **Base de datos real**: Conectar con SQLAlchemy
2. **Autenticación JWT**: Implementar en API Simple
3. **Más endpoints**: Agregar mantenimiento, compliance, etc.
4. **Validaciones avanzadas**: Reglas de negocio complejas
5. **Logging y monitoreo**: Integración con sistemas de observabilidad

---

## 📞 Soporte

Para más información:
- 📖 README.md - Documentación del proyecto
- 📋 API_IMPLEMENTATION.md - Detalles de implementación
- 🔗 Swagger UI - http://localhost:8000/docs
- 💬 Contacta al equipo de desarrollo

---

**Última actualización**: Febrero 7, 2026
**Estado**: ✅ Completado y Funcional
