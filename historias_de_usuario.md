```markdown
# 📋 Historias de Usuario Detalladas - Sistema de Gestión de Flota

Este documento reescribe y amplía las historias de usuario del sistema. Para cada historia se incluye: rol, objetivo, criterios de aceptación (AC), precondiciones, pasos de la interfaz de usuario (UI), endpoints/API involucrados, estructura de datos esperada, reglas de negocio y casos borde.

---

## 🔐 Módulo: Autenticación y Autorización

### HU-01: Inicio de sesión seguro (Administrador / Usuario)
- Rol: Administrador o Usuario autenticable
- Objetivo: Iniciar sesión en la aplicación con credenciales válidas y recibir una sesión autenticada válida.
- Criterios de aceptación:
  1. AC1: El usuario puede acceder a `/auth/login` y enviar `username` y `password` junto con CSRF token.
  2. AC2: Con credenciales válidas, el servidor devuelve 302 a `/dashboard` (o token JWT válido para API) y establece cookie de sesión con flags Secure, HttpOnly y SameSite según configuración.
  3. AC3: Con credenciales inválidas, se muestra mensaje genérico sin revelar si el usuario existe y retorna 401/403.
  4. AC4: Se aplica rate limiting por IP/usuario (p.ej. 5 intentos/minuto).

- Precondiciones:
  - Cuenta creada y activa.
  - CSRF protection habilitada.

- Pasos UI:
  1. Usuario navega a la página de login.
  2. Introduce `username` y `password` y envía el formulario.
  3. Si 2FA está habilitado para el usuario, se muestra pantalla de código temporal.
  4. Tras autenticación correcta, redirección a `/dashboard`.

- Endpoints / API:
  - POST `/auth/login` (form-encoded). Request: { username, password, csrf_token }
  - POST `/auth/2fa` (si aplica). Request: { user_id, code }

- Datos / Modelos relevantes:
  - `User { id, username, email, password_hash, is_active, roles[] }`

- Reglas de negocio:
  - No revelar si username/email existe en mensajes de error.
  - Bloquear cuenta temporal tras N intentos fallidos; notificar a admin.

- Casos borde y errores:
  - Intento con CSRF inválido => 400 y registro de evento.
  - Sesiones concurrentes controladas por política (permitir/denegar según config).

### HU-02: Cierre de sesión seguro
- Rol: Usuario autenticado
- Objetivo: Invalidar la sesión actual y limpiar cookies de sesión.
- Criterios de aceptación:
  1. El endpoint POST `/auth/logout` invalida la sesión en servidor y borra cookie.
  2. Redirigir a la página pública de inicio.

- Pasos UI:
  1. Usuario pulsa "Cerrar sesión".
  2. Se envía petición POST con CSRF y, tras éxito, se redirige a `/`.

### HU-03: Gestión de roles y permisos (Administrador)
- Rol: Administrador
- Objetivo: Crear, editar y asignar roles que controlen accesos a módulos.
- Criterios de aceptación:
  - AC1: Existe UI/Admin para crear roles (`/admin/roles`) y asignar permisos (CRUD por recurso).
  - AC2: Cambios surten efecto sin reinicio (control por claims en sesión o revalidación de token).

- Reglas de negocio:
  - No permitir crear roles con privilegios superiores al creador.
  - Auditoría: registrar quien creó/ modificó roles.

---

## 🚗 Módulo: Vehículos

### HU-10: Registrar nuevo vehículo
- Rol: Administrador de flota
- Objetivo: Añadir un vehículo con todos los metadatos obligatorios para inventario.
- Criterios de aceptación:
  1. La UI `/vehicles/new` permite introducir: matrícula, marca, modelo, año, tipo, combustible, número de bastidor (VIN), kilometraje inicial, estado, unidad organizativa, proveedor y documento/expediente asociado.
  2. Validaciones: matrícula única, VIN único, campos obligatorios no vacíos, año razonable (1900..current_year+1).
  3. Tras guardar, el vehículo aparece en la lista `/vehicles` y en la API GET `/api/vehicles/{id}` devuelve el objeto creado.

- API/Request:
  - POST `/api/vehicles` {
      registration_plate, vin, brand, model, year, vehicle_type, fuel_type, mileage, organization_unit_id, provider_id
    }

- Modelo de respuesta esperado:
  - Vehicle { id, registration_plate, vin, brand, model, year, type, fuel_type, mileage, status, organization_unit_id }

- Reglas de negocio:
  - Si `vehicle_type == 'renting'` se debe vincular contrato de renting (campo contract_id obligatorio).
  - Si `status == 'in_service'`, no debe permitir nuevas reservas hasta cambiar estado.

- Casos borde:
  - Matrícula duplicada -> 400 con error de validación.
  - VIN con formato inválido -> 400.

### HU-11: Consultar lista de vehículos y filtros
- Rol: Usuario autorizado
- Objetivo: Visualizar y filtrar vehículos por estado, tipo, unidad organizativa, y disponibilidad.
- Criterios de aceptación:
  - AC1: GET `/vehicles` muestra listado paginado.
  - AC2: Parámetros GET soportados: `?status=&type=&org_id=&available_from=&available_to=&q=`.
  - AC3: Filtros combinados aplican lógicamente (AND) y la respuesta incluye total_count y páginas.

- UI Steps:
  1. Usuario abre `/vehicles`.
 2. Aplica filtros y la lista se actualiza vía AJAX.

### HU-12: Ficha detallada del vehículo y historial
- Rol: Usuario autorizado / técnico
- Objetivo: Consultar ficha completa, historial de asignaciones, mantenimientos, inspecciones, impuestos, multas y autorizaciones.
- Criterios de aceptación:
  - AC1: Página `/vehicles/{id}` muestra pestañas: General, Historial, Documentos, Mantenimiento.
  - AC2: Historial está ordenado por fecha (desc) y agrupa por tipo con posibilidad de filtro.

- Reglas de negocio:
  - Si faltan fechas en eventos históricos, usar `created_at` como fallback para ordenamiento.

---

## 👥 Módulo: Conductores

### HU-20: Registrar conductor
- Rol: Administrador / RRHH
- Objetivo: Añadir datos del conductor y permisos (carnet, categorías, fechas de vencimiento).
- Criterios de aceptación:
  - AC1: Formulario con: nombre, apellidos, NIF, email, teléfono, tipo (funcionario, eventual, externo), carnets (lista con tipo y fecha de vencimiento), organismo asignado.
  - AC2: Si carnet vencido, el conductor aparece con estado `no_autorizado` hasta renovación.

- Reglas:
  - Validar NIF/ NIE formato; enviar aviso 30 días antes de vencimiento.

### HU-21: Asignación y liberación de conductor a vehículo
- Rol: Responsable de asignaciones
- Objetivo: Asignar conductor a vehículo por rango de fechas y kilometraje previsto.
- Criterios de aceptación:
  - AC1: POST `/api/assignments` con { vehicle_id, driver_id, start_date, end_date, notes } crea asignación si no existe solapamiento.
  - AC2: Si existe solapamiento de asignaciones para el mismo vehículo, devolver 409 con detalles del conflicto.

---

## 📅 Módulo: Reservas

### HU-30: Solicitar reserva
- Rol: Empleado
- Objetivo: Solicitar un vehículo indicando rango horario, destino y justificación.
- Criterios de aceptación:
  - AC1: Formulario valida que `start < end`, que el vehículo está disponible en ese rango y que el request contiene CSRF.
  - AC2: Guardar la solicitud en estado `pending` y notificar por email al supervisor.

- Flujo UI / Backend:
  1. GET `/reservations/new` muestra formulario con calendario y selección de vehículo/alternativas.
 2. POST `/reservations` crea reserva en estado `pending`.
 3. Supervisor recibe notificación y puede aprobar/rechazar en `/reservations/{id}/review`.

- Reglas de negocio:
  - Políticas de aprobación según unidad organizativa y tipo de viaje.
  - Si la solicitud excede umbral de kilometraje o duración, requiere doble aprobación.

### HU-31: Aprobar / Rechazar reserva (Supervisor)
- Rol: Supervisor
- Objetivo: Revisar y decidir sobre solicitudes de reserva.
- Criterios de aceptación:
  - AC1: PATCH `/api/reservations/{id}` con { status: approved|rejected, comments } cambia estado y notifica solicitante.
  - AC2: En caso de approving, bloquear vehículo en el rango y crear asignación temporal.

---

## 🔧 Módulo: Mantenimiento

### HU-40: Registrar intervención de mantenimiento
- Rol: Técnico de mantenimiento
- Objetivo: Registrar trabajos preventivos y correctivos con coste, kilometraje y piezas utilizadas.
- Criterios de aceptación:
  - AC1: POST `/api/maintenance` con { vehicle_id, type, description, performed_at, mileage, cost, provider_id } crea registro y actualiza historial del vehículo.
  - AC2: Si coste > umbral, generar alerta a finanzas.

- Reglas:
  - Programaciones periódicas basadas en kilometraje o tiempo; sistema genera tareas programadas.

---

## ⚖️ Módulo: Cumplimiento Normativo (ITV, seguros, impuestos, multas, autorizaciones)

### HU-50: Registrar ITV y alertas de vencimiento
- Rol: Responsable de cumplimiento
- Objetivo: Mantener registros de inspecciones técnicas con fechas de vencimiento y generar alertas.
- Criterios de aceptación:
  - AC1: Cada `VehicleItv { vehicle_id, date, expiry_date, station, document_url }` puede ser creado y listado.
  - AC2: El sistema envía notificaciones configurables (email/ dashboard ) X días antes del vencimiento.

### HU-51: Registrar pago de impuestos y controlar estado
- Rol: Administrador financiero
- Objetivo: Registrar impuestos pagados y su estado.
- Criterios de aceptación:
  - AC1: POST `/api/taxes` crea registro con { vehicle_id, period, amount, payment_status }
  - AC2: Visualización en `/vehicles/{id}/compliance` con estado `paid|pending|overdue`.

### HU-52: Gestión de multas
- Rol: Coordinador de flota
- Objetivo: Registrar multas, asignarlas a conductor o vehículo, y llevar seguimiento de pago/ recurso.
- Criterios de aceptación:
  - AC1: POST `/api/fines` con { vehicle_id, driver_id?, date, amount, fine_type, status }
  - AC2: Si asignada a conductor, marcar impacto en su perfil (estadísticas, historial).

### HU-53: Autorizaciones de acceso especial (zonas restringidas)
- Rol: Responsable de cumplimiento
- Objetivo: Gestionar autorizaciones temporales o permanentes con metadatos (zona, alcance, fecha fin).
- Criterios de aceptación:
  - AC1: Crear autorización con { vehicle_id, authorization_type, zone, start_date, end_date, issuing_authority }
  - AC2: Mostrar autorización en ficha de vehículo y permitir búsqueda por zona/vehículo.

---

## 🏢 Módulo: Organizaciones

### HU-60: Crear y estructurar unidades organizativas
- Rol: Administrador
- Objetivo: Definir jerarquía de unidades (organigrama) y asociar vehículos/usuarios.
- Criterios de aceptación:
  - AC1: UI para CRUD de unidades con padre/opciones y ordenamiento jerárquico.
  - AC2: Exportar árbol en JSON para apps externas.

---

## 📊 Módulo: Dashboard y Reportes

### HU-70: Dashboard operativo
- Rol: Administrador / Supervisor
- Objetivo: Ver métricas clave (vehículos disponibles, reservas pendientes, vencimientos próximos, coste de mantenimiento)
- Criterios de aceptación:
  - AC1: Panel con widgets actualizables y enlaces a filtros preaplicados.
  - AC2: Exportar reportes CSV/PDF con filtros por fecha y unidad.

---

## Reglas generales y consideraciones transversales
- Autorizaciones y permisos evaluados por middleware en cada endpoint.
- Internacionalización (i18n): textos parametrizables para múltiples idiomas.
- Seguridad: todas las modificaciones importantes deben auditarse (who/when/what).
- Validaciones: tanto cliente como servidor; servidor es la autoridad.

## Plantillas de aceptación para desarrollo y testing
- Cada historia deberá entregarse con:
  1. Escenario/s de aceptación (Given/When/Then) en `tests/` o archivo BDD.
  2. Mock de API minimal para integración frontend.
  3. Documentación de endpoints y muestras de request/response.

---

Si quieres, puedo:
- Generar los escenarios Given/When/Then para cada historia principal.
- Crear plantillas de tests pytest (happy path + 1 caso borde) por historia.
- Extraer de aquí un backlog priorizado (MVP, v1, v2) y estimaciones de esfuerzo.

```
