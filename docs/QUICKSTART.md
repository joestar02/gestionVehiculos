# ⚡ Quick Start - API REST

## 30 segundos para tener la API funcionando

### 1️⃣ Opción A: API Simple (Lo más fácil)
```bash
python api_simple.py
```
Luego abre: http://localhost:8000/docs

### 2️⃣ Opción B: Con Demo Interactiva
```bash
python run_demo.py
```
Verás ejemplos de uso reales ejecutándose

### 3️⃣ Opción C: Con Pruebas Automáticas
```bash
python run_api_with_tests.py
```
Ejecuta suite completa de pruebas

---

## 📝 Ejemplo: Crear y Listar Vehículos

### Con curl
```bash
# Listar
curl http://localhost:8000/api/v1/vehicles

# Crear
curl -X POST http://localhost:8000/api/v1/vehicles \
  -H "Content-Type: application/json" \
  -d '{"license_plate":"MAL-1234","make":"Ford","model":"Transit","year":2022}'
```

### Con Python
```python
import requests

# Listar
r = requests.get('http://localhost:8000/api/v1/vehicles')
print(r.json())

# Crear
data = {'license_plate':'MAL-5678','make':'Mercedes','model':'Sprinter','year':2021}
r = requests.post('http://localhost:8000/api/v1/vehicles', json=data)
print(r.json())
```

---

## 🎯 URLs Importantes

| URL | Descripción |
|-----|-------------|
| http://localhost:8000 | API raíz |
| http://localhost:8000/docs | Swagger UI (prueba endpoints aquí) |
| http://localhost:8000/redoc | Documentación alternativa |
| http://localhost:8000/health | Health check |
| http://localhost:8000/openapi.json | Especificación OpenAPI |

---

## ✨ Lo que incluye

✅ 8 endpoints REST
✅ Documentación automática (Swagger)
✅ Validación de datos (Pydantic)
✅ CORS habilitado
✅ Ejemplos completos
✅ Pruebas incluidas
✅ Demo interactiva

---

## 🚀 Datos Iniciales

La API viene con datos de ejemplo:

**Vehículos**:
- MAL-1234: Ford Transit (2022)
- MAL-5678: Mercedes Sprinter (2021)

**Conductores**:
- Juan García (D1234567)
- María López (D7654321)

**Reservas**:
- Vehículo 1 + Conductor 1 (Feb 8-15, 2026)

---

## 📚 Para saber más

- `README.md` - Documentación completa
- `API_GUIA_COMPLETA.md` - Guía detallada
- `API_IMPLEMENTATION.md` - Detalles técnicos
- `IMPLEMENTACION_COMPLETA.md` - Resumen de cambios
- `demo_api.py` - Ejemplos de código

---

## ❓ Problemas?

1. **Puerto ocupado**: Cambia puerto en `api_simple.py`
2. **API no responde**: Asegúrate que está ejecutándose
3. **No ves datos**: Los datos están en memoria (se pierden al reiniciar)

---

**¡Listo! La API está funcionando. Accede a http://localhost:8000/docs** 🎉
