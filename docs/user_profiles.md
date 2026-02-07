# Perfiles de Usuario y Permisos

## Resumen Ejecutivo

Este documento detalla los perfiles de usuario implementados en el Sistema de Gestión de Flota de Vehículos, incluyendo sus permisos, responsabilidades y casos de uso.

**Archivo**: `docs/user_profiles.md`
**Última actualización**: Enero 2026
**Versión**: 1.0

## Usuarios de Prueba

| Usuario | Contraseña | Rol | Email |
|---------|------------|-----|-------|
| admin | admin123 | ADMIN | admin@juntadeandalucia.es |
| fleet_manager | fleet123 | FLEET_MANAGER | fleet.manager@juntadeandalucia.es |
| ops_manager | ops123 | OPERATIONS_MANAGER | operations.manager@juntadeandalucia.es |
| conductor1 | driver123 | DRIVER | conductor1@juntadeandalucia.es |
| visor | view123 | VIEWER | visor@juntadeandalucia.es |

## Matriz de Permisos por Rol

### Leyenda
- ✅ = Permiso concedido
- ❌ = Permiso denegado
- 🔒 = Acceso restringido (solo datos propios)

### Matriz Completa

| Permiso | ADMIN | FLEET_MANAGER | OPERATIONS_MANAGER | DRIVER | VIEWER |
|---------|-------|----------------|-------------------|--------|--------|
| **Vehículos** | | | | | |
| vehicle:view | ✅ | ✅ | ✅ | ✅ | ✅ |
| vehicle:create | ✅ | ✅ | ✅ | ❌ | ❌ |
| vehicle:edit | ✅ | ✅ | ✅ | ❌ | ❌ |
| vehicle:delete | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Reservas** | | | | | |
| reservation:view | ✅ | ✅ | ✅ | 🔒 | ✅ |
| reservation:create | ✅ | ✅ | ✅ | 🔒 | ❌ |
| reservation:edit | ✅ | ✅ | ✅ | ❌ | ❌ |
| reservation:cancel | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Conductores** | | | | | |
| driver:view | ✅ | ✅ | ✅ | ❌ | ✅ |
| driver:create | ✅ | ✅ | ✅ | ❌ | ❌ |
| driver:edit | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Asignaciones** | | | | | |
| assignment:view | ✅ | ✅ | ✅ | 🔒 | ✅ |
| assignment:create | ✅ | ✅ | ✅ | ❌ | ❌ |
| assignment:edit | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Mantenimientos** | | | | | |
| maintenance:view | ✅ | ✅ | ❌ | 🔒 | ✅ |
| maintenance:create | ✅ | ✅ | ❌ | ❌ | ❌ |
| maintenance:edit | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Proveedores** | | | | | |
| provider:view | ✅ | ✅ | ✅ | ❌ | ✅ |
| provider:create | ✅ | ✅ | ✅ | ❌ | ❌ |
| provider:edit | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Organizaciones** | | | | | |
| organization:view | ✅ | ✅ | ✅ | ❌ | ✅ |
| organization:create | ✅ | ✅ | ❌ | ❌ | ❌ |
| organization:edit | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Usuarios** | | | | | |
| user:view | ✅ | ❌ | ❌ | ❌ | ❌ |
| user:create | ✅ | ❌ | ❌ | ❌ | ❌ |
| user:edit | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Reportes** | | | | | |
| report:view | ✅ | ✅ | ✅ | ❌ | ✅ |
| report:create | ✅ | ✅ | ❌ | ❌ | ❌ |

## Detalle de Perfiles

### 1. ADMINISTRADOR (ADMIN)

#### Descripción
Usuario con acceso completo al sistema. Responsable de la configuración, mantenimiento y administración general de la aplicación.

#### Responsabilidades
- Configuración del sistema
- Gestión de usuarios y permisos
- Supervisión de todas las operaciones
- Generación de reportes ejecutivos
- Mantenimiento de datos maestros

#### Permisos Totales
- **26 permisos** de 9 módulos diferentes
- Acceso completo a todas las funcionalidades
- Capacidad para crear, editar y eliminar cualquier dato

#### Casos de Uso
- Administrador del sistema
- Gerente de TI
- Director de operaciones
- Personal de soporte técnico

### 2. GESTOR DE FLOTA (FLEET_MANAGER)

#### Descripción
Profesional responsable de la gestión integral de la flota vehicular, incluyendo inventario, asignaciones y mantenimiento operativo.

#### Responsabilidades
- Gestión del inventario de vehículos
- Coordinación de reservas y asignaciones
- Supervisión de conductores
- Programación de mantenimientos
- Gestión de proveedores de servicios
- Análisis de rendimiento de flota

#### Permisos Clave
- Gestión completa de vehículos, reservas y asignaciones
- Administración de conductores
- Control de mantenimientos y proveedores
- Acceso a reportes y análisis

#### Limitaciones
- No puede gestionar usuarios del sistema
- No puede eliminar vehículos

#### Casos de Uso
- Gerente de flota
- Coordinador de transporte
- Supervisor de vehículos
- Jefe de operaciones de flota

### 3. GESTOR DE OPERACIONES (OPERATIONS_MANAGER)

#### Descripción
Profesional enfocado en las operaciones diarias, coordinación de servicios y gestión de proveedores externos.

#### Responsabilidades
- Coordinación de operaciones diarias
- Gestión de reservas y asignaciones operativas
- Supervisión de proveedores externos
- Monitoreo de cumplimiento operativo
- Reportes de rendimiento operativo

#### Permisos Clave
- Gestión de reservas y asignaciones
- Administración de proveedores
- Acceso a información de vehículos y conductores
- Consultas de reportes

#### Limitaciones
- No puede crear/editar mantenimientos
- No puede gestionar organizaciones
- No puede crear usuarios

#### Casos de Uso
- Supervisor de operaciones
- Coordinador de servicios
- Gestor de proveedores
- Jefe de operaciones diarias

### 4. CONDUCTOR (DRIVER)

#### Descripción
Usuario operativo que utiliza el sistema para consultar información relevante a sus actividades de conducción.

#### Responsabilidades
- Consulta de vehículos disponibles
- Gestión de sus propias reservas
- Consulta de asignaciones personales
- Revisión de mantenimientos de vehículos asignados

#### Permisos Clave
- Consulta de información básica
- Creación de reservas personales
- Acceso limitado a datos relacionados con su trabajo

#### Limitaciones
- No puede modificar datos del sistema
- Acceso restringido a información sensible
- No puede gestionar otros módulos

#### Casos de Uso
- Conductor profesional
- Personal operativo de transporte
- Usuario final con necesidades básicas

### 5. OBSERVADOR (VIEWER)

#### Descripción
Usuario con acceso de solo lectura para consulta de información, auditorías y supervisión.

#### Responsabilidades
- Consulta de información del sistema
- Revisión de reportes y estadísticas
- Auditoría de operaciones
- Supervisión de procesos

#### Permisos Clave
- Acceso de lectura a todos los módulos
- Consulta de reportes y análisis
- Visualización de datos históricos

#### Limitaciones
- No puede modificar ningún dato
- Solo lectura en todo el sistema

#### Casos de Uso
- Auditores internos
- Supervisores
- Personal administrativo
- Consultores externos

## Implementación Técnica

### Archivos Relacionados
- `app/models/permission.py`: Modelos de permisos y roles
- `app/core/permissions.py`: Decoradores de control de acceso
- `app/core/permission_config.py`: Configuración de permisos por rol
- `scripts/create_sample_users.py`: Creación de usuarios de prueba
- `scripts/init_permissions.py`: Inicialización de permisos

### Sistema de Control de Acceso
- **Basado en roles**: Asignación de permisos por rol de usuario
- **Granular**: 26 permisos específicos organizados por módulos
- **Extensible**: Fácil agregar nuevos permisos y roles
- **Decorator-based**: Control de acceso mediante decoradores en rutas

### Seguridad
- Autenticación mediante username/email y contraseña
- Hashing seguro de contraseñas (bcrypt)
- Control de acceso por permisos específicos
- Auditoría de acciones (implementado parcialmente)

## Mantenimiento y Evolución

### Agregar Nuevos Permisos
1. Definir el permiso en `PERMISSIONS` en `permission_config.py`
2. Asignar el permiso a los roles apropiados en `ROLE_PERMISSIONS`
3. Usar el decorador `@has_permission('nuevo:permiso')` en controladores

### Crear Nuevos Roles
1. Agregar el rol al enum `UserRole` en `app/models/user.py`
2. Definir permisos para el nuevo rol en `permission_config.py`
3. Actualizar documentación

### Modificar Permisos Existentes
1. Editar la asignación en `ROLE_PERMISSIONS`
2. Ejecutar `python scripts/init_permissions.py` para actualizar la base de datos
3. Probar cambios con usuarios de prueba

## Contacto y Soporte

Para consultas sobre perfiles de usuario o permisos, contactar al equipo de desarrollo.