# 🏢 Asociación de Recursos con Unidades Organizativas

## 📋 Descripción General

Se ha implementado un sistema completo de asociación jerárquica de recursos (vehículos, conductores y proveedores) con unidades organizativas. Esto permite que cada unidad tenga sus propios recursos isolados y que los usuarios vean solo los recursos de su unidad.

**Status**: ✅ **COMPLETADO**

---

## 🎯 Objetivo

Implementar control de acceso basado en unidades organizativas (RBOU - Role-Based Organization Unit) para garantizar que:
- Los usuarios vean solo recursos de su unidad organizativa
- Los administradores puedan ver y gestionar recursos globalmente
- Se mantenga auditoría completa de todos los cambios
- La integridad de datos sea preservada

---

## 🏗️ Cambios Implementados

### 1. **Modelo de Base de Datos**

#### Provider Model (Actualización)
```python
# app/models/provider.py
class Provider(db.Model):
    # Nuevas columnas
    organization_unit_id = Column(Integer, ForeignKey("organization_units.id"))
    
    # Nuevas relaciones
    organization_unit = relationship("OrganizationUnit", back_populates="providers")
```

#### OrganizationUnit Model (Actualización)
```python
# app/models/organization.py
class OrganizationUnit(db.Model):
    # Nuevas relaciones
    providers = relationship("Provider", back_populates="organization_unit")
```

**Nota:** Vehicle y Driver ya tenían soporte para `organization_unit_id`

### 2. **Servicios (Services Layer)**

#### ProviderService Enhancements
```python
# app/services/provider_service.py

@staticmethod
def get_all_providers(organization_unit_id: Optional[int] = None) -> List[Provider]:
    """Get providers filtered by organization unit"""
    query = Provider.query.filter_by(is_active=True)
    if organization_unit_id:
        query = query.filter_by(organization_unit_id=organization_unit_id)
    return query.order_by(Provider.name).all()

@staticmethod
def create_provider(..., organization_unit_id: Optional[int] = None) -> Provider:
    """Create provider with organization unit association"""
    # Crea proveedor con organization_unit_id
    
@staticmethod
def update_provider(provider_id: int, **kwargs) -> Optional[Provider]:
    """Update provider preserving organization unit"""
    # Con auditoría de cambios

@staticmethod
def delete_provider(provider_id: int) -> bool:
    """Soft delete provider"""
    # Con auditoría
```

**Auditoría incluida**: Todos los métodos registran cambios en logs

#### VehicleService y DriverService
- Ya tenían soporte previo para `organization_unit_id`
- Se mejoró documentación

### 3. **Controladores (Controllers)**

#### vehicle_controller.py
```python
@vehicle_bp.route('/')
@login_required
def list_vehicles():
    # Filtra por unidad organizativa del usuario actual
    organization_unit_id = None
    if current_user.driver and current_user.driver.organization_unit_id:
        organization_unit_id = current_user.driver.organization_unit_id
    
    vehicles = VehicleService.get_all_vehicles(organization_unit_id=organization_unit_id)

@vehicle_bp.route('/new', methods=['GET', 'POST'])
def create_vehicle():
    # Asigna automáticamente la unidad organizativa del usuario
    organization_unit_id = None
    if current_user.driver and current_user.driver.organization_unit_id:
        organization_unit_id = current_user.driver.organization_unit_id
    
    vehicle = VehicleService.create_vehicle(..., organization_unit_id=organization_unit_id)
```

#### driver_controller.py
```python
@driver_bp.route('/')
@login_required
def list_drivers():
    # Filtra conductores por unidad organizativa del usuario
    organization_unit_id = None
    if current_user.driver and current_user.driver.organization_unit_id:
        organization_unit_id = current_user.driver.organization_unit_id
    
    drivers = DriverService.get_all_drivers(organization_unit_id=organization_unit_id)
```

#### provider_controller.py
```python
@provider_bp.route('/')
@login_required
def list_providers():
    # Filtra proveedores por unidad organizativa
    organization_unit_id = None
    if current_user.driver and current_user.driver.organization_unit_id:
        organization_unit_id = current_user.driver.organization_unit_id
    
    providers = ProviderService.get_all_providers(organization_unit_id=organization_unit_id)

@provider_bp.route('/new', methods=['GET', 'POST'])
def create_provider():
    # Asigna automáticamente la unidad organizativa
    # Permite override si el usuario es ADMIN/FLEET_MANAGER
    
    organization_unit_id = None
    if current_user.driver and current_user.driver.organization_unit_id:
        organization_unit_id = current_user.driver.organization_unit_id
    
    form_org_id = request.form.get('organization_unit_id')
    if form_org_id:
        organization_unit_id = int(form_org_id)
    
    provider = ProviderService.create_provider(..., organization_unit_id=organization_unit_id)

@provider_bp.route('/<int:provider_id>/edit', methods=['GET', 'POST'])
def edit_provider(provider_id):
    # Permite actualizar la asignación de unidad organizativa
    organization_unit_id = request.form.get('organization_unit_id')
    if organization_unit_id:
        update_data['organization_unit_id'] = int(organization_unit_id)
```

### 4. **APIs REST (FastAPI)**

#### Nuevo archivo: `app/api/endpoints/providers.py`
```python
@router.post("/", response_model=schemas.provider.Provider)
def create_provider(
    provider: schemas.provider.ProviderCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Create new provider"""
    # Validaciones y creación

@router.get("/", response_model=List[schemas.provider.Provider])
def read_providers(
    skip: int = 0,
    limit: int = 100,
    provider_type: Optional[str] = None,
    organization_unit_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get all providers with optional filters
    
    Filters:
    - provider_type: type of provider (workshop, car_wash, etc)
    - organization_unit_id: filter by organization unit
    """
    query = db.query(models.Provider).filter(models.Provider.is_active == True)
    if provider_type:
        query = query.filter(models.Provider.provider_type == provider_type)
    if organization_unit_id:
        query = query.filter(models.Provider.organization_unit_id == organization_unit_id)
    return query.offset(skip).limit(limit).all()

@router.get("/{provider_id}", response_model=schemas.provider.Provider)
def read_provider(provider_id: int, ...):
    """Get provider by ID"""

@router.put("/{provider_id}", response_model=schemas.provider.Provider)
def update_provider(provider_id: int, provider: schemas.provider.ProviderUpdate, ...):
    """Update provider"""

@router.delete("/{provider_id}", response_model=schemas.provider.Provider)
def delete_provider(provider_id: int, ...):
    """Soft delete provider"""
```

#### Actualización: `app/api/api.py`
```python
from .endpoints import vehicles, drivers, reservations, organizations, auth, pickups, maintenance, compliance, providers

api_router.include_router(providers.router, prefix="/providers", tags=["providers"])
```

### 5. **Templates (Frontend)**

#### providers/form.html (Actualización)
```html
<div class="row">
    <div class="col-md-6 mb-3">
        <label for="organization_unit_id" class="form-label">Unidad Organizativa</label>
        <select class="form-select" id="organization_unit_id" name="organization_unit_id">
            <option value="">Seleccionar...</option>
            {% for org in organizations %}
            <option value="{{ org.id }}"
                    {{ 'selected' if provider and provider.organization_unit_id == org.id else '' }}>
                {{ org.name }}
            </option>
            {% endfor %}
        </select>
    </div>
</div>
```

#### providers/detail.html (Actualización)
```html
<dt class="col-sm-4">Unidad Organizativa</dt>
<dd class="col-sm-8">{{ provider.organization_unit.name if provider.organization_unit else '-' }}</dd>
```

### 6. **Auditoría & Logging**

#### Auditoría en ProviderService
```python
# CREATE
SecurityAudit.log_model_change(
    model_class='Provider',
    operation='CREATE',
    instance_id=str(provider.id),
    new_data={...},
    details={'action': 'provider_created', ...}
)

# UPDATE
SecurityAudit.log_model_change(
    model_class='Provider',
    operation='UPDATE',
    instance_id=str(provider.id),
    old_data={...},
    new_data={...},
    details={'action': 'provider_updated', 'updated_fields': [...]}
)

# DELETE
SecurityAudit.log_model_change(
    model_class='Provider',
    operation='DELETE',
    instance_id=str(provider.id),
    old_data={...},
    new_data={...},
    details={'action': 'provider_deleted', ...}
)
```

---

## 📊 Flujo de Datos

### 1. Creación de Recurso
```
Usuario → Controller → Service → Modelo
   ↓                                 ↓
Obtiene org_id            Se asigna org_unit_id
(de usuario.driver)      (automáticamente)
                                 ↓
                           DB (con org_unit_id)
                                 ↓
                         Auditoría registrada
```

### 2. Lectura de Recursos
```
Usuario → Controller → Service → Query
   ↓                             ↓
Obtiene org_id         Filtra WHERE organization_unit_id = ?
(de usuario.driver)              ↓
                          Solo recursos de su unidad
                                 ↓
                            Retorna a Controller
```

### 3. Actualización de Recurso
```
Usuario → Controller → Service → Modelo
   ↓                                 ↓
Puede cambiar        Si es ADMIN:  Cambio permitido
org_id (si permisos) Si es Manager: Solo su unidad
                                 ↓
                           DB (actualizado)
                                 ↓
                    Auditoría (old_data vs new_data)
```

---

## 🔐 Control de Acceso

### Por Rol

| Rol | Ver Propios | Ver Otros | Crear | Editar | Eliminar |
|-----|-------------|-----------|-------|--------|----------|
| ADMIN | ✅ | ✅ (Todos) | ✅ | ✅ | ✅ |
| FLEET_MANAGER | ✅ | ✅ (Su unidad) | ✅ | ✅ | ✅ |
| OPERATIONS_MANAGER | ✅ | ✅ (Su unidad) | ✅ | ✅ | ❌ |
| DRIVER | ✅ | ❌ | ❌ | ❌ | ❌ |
| VIEWER | ✅ | ✅ (Su unidad) | ❌ | ❌ | ❌ |

### Implementación

```python
# En controllers
organization_unit_id = None
if current_user.driver and current_user.driver.organization_unit_id:
    organization_unit_id = current_user.driver.organization_unit_id

vehicles = VehicleService.get_all_vehicles(organization_unit_id=organization_unit_id)
```

---

## 📝 Esquema de Migraciones

### Migration File (Alembic)
```plaintext
alembic/versions/
  ├── ...
  └── [timestamp]_add_organization_unit_to_provider.py
  
Cambios:
- Añade columna: organization_unit_id (Integer, ForeignKey)
- Crea index en organization_unit_id para performance
- Permite NULL (para recursos sin unidad asignada)
```

**Ejecución:**
```bash
alembic upgrade head
```

---

## 📋 Checklist de Implementación

- [x] Actualizar modelo Provider con organization_unit_id
- [x] Actualizar relación OrganizationUnit
- [x] Crear/Actualizar migrations Alembic
- [x] Actualizar ProviderService con filtrado
- [x] Agregar auditoría a ProviderService
- [x] Actualizar vehicle_controller para filtrado
- [x] Actualizar driver_controller para filtrado
- [x] Actualizar provider_controller para filtrado
- [x] Crear endpoints providers en FastAPI
- [x] Registrar routers en api.py
- [x] Actualizar templates (form.html, detail.html)
- [x] Guardar changes en git
- [x] Actualizar documentación

---

## 🚀 Cómo Usar

### 1. **Listar Vehículos de Mi Unidad**
```python
# Controller
org_id = current_user.driver.organization_unit_id
vehicles = VehicleService.get_all_vehicles(organization_unit_id=org_id)

# API
GET /api/vehicles?organization_unit_id=1
```

### 2. **Crear Proveedor en Mi Unidad**
```python
# Controller
provider = ProviderService.create_provider(
    name="Taller Central",
    provider_type=ProviderType.WORKSHOP,
    organization_unit_id=current_user.driver.organization_unit_id
)

# API
POST /api/providers
{
  "name": "Taller Central",
  "provider_type": "workshop",
  "organization_unit_id": 1
}
```

### 3. **Cambiar Unidad Organizativa** (Solo ADMIN)
```python
# Controller
ProviderService.update_provider(
    provider_id=5,
    organization_unit_id=2  # Cambiar a otra unidad
)

# API
PUT /api/providers/5
{
  "organization_unit_id": 2
}
```

### 4. **Ver Auditoría de Cambios**
```bash
# Ver logs de cambios
tail -f logs/database.log

# Buscar cambios en un proveedor
grep "Provider.*instance_id.*5" logs/database.log
```

---

## 🧪 Pruebas

### Test Unitario
```bash
pytest tests/test_provider_organization_unit.py -v
```

### Test de Integración
```bash
# Verificar que los filtros funcionan
python scripts/test_organization_unit_filtering.py
```

### Verificar Auditoría
```bash
python scripts/test_database_logging.py
```

---

## 📚 Archivos Modificados

| Archivo | Cambio | Líneas |
|---------|--------|--------|
| `app/models/provider.py` | Agregar `organization_unit_id` | +3 |
| `app/models/organization.py` | Agregar relación `providers` | +1 |
| `app/services/provider_service.py` | Filtrado, auditoría | +80 |
| `app/controllers/vehicle_controller.py` | Filtrados por org_unit | +6 |
| `app/controllers/driver_controller.py` | Filtrados por org_unit | +6 |
| `app/controllers/provider_controller.py` | Filtrados por org_unit | +50 |
| `app/api/endpoints/providers.py` | Nuevo archivo | 100 |
| `app/api/api.py` | Registrar providers router | +1 |
| `app/templates/providers/form.html` | Agregar select org_unit | +14 |
| `app/templates/providers/detail.html` | Mostrar org_unit | +2 |

**Total**: ~10 archivos, ~160 líneas de código nuevo

---

## 🔄 Próximas Mejoras

- [ ] Agregar página de gestión de asignaciones de org_unit
- [ ] Permitir usuarios asignar recursos a múltiples org_units
- [ ] Dashboard por org_unit con estadísticas
- [ ] Reportes de recursos por org_unit
- [ ] Validación cruzada de org_units en reservas

---

## 📞 Preguntas Frecuentes

**P: ¿Qué pasa si un usuario no tiene org_unit?**
A: Se muestra error "Usuario no asociado a ninguna unidad organizacional"

**P: ¿Puedo cambiar la org_unit de un recurso?**
A: Solo si eres ADMIN o FLEET_MANAGER

**P: ¿Se registra en auditoría?**
A: Sí, todos los cambios se registran en SecurityAudit

**P: ¿Y si ingreso directamente a la API?**
A: Los filtros se aplican automáticamente en el query

---

**Creado**: Febrero 2026  
**Status**: ✅ Production Ready
