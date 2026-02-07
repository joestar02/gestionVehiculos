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
   # 📋 Historias de Usuario (Cobertura completa del código y plantillas detectadas)

   Esta versión amplía las historias de usuario para cubrir la totalidad de rutas, modelos y plantillas detectadas en el repositorio (`app/controllers`, `app/models`, `app/templates`). Para cada área incluyo: rol, objetivo, criterios de aceptación (AC), endpoints/API, reglas de negocio y casos borde. Además añado historias para operaciones de import/export, archivos y auditoría.

   Notas sobre alcance y metodología
   - He revisado los controladores y plantillas del proyecto para identificar comportamientos visibles (CRUD, formularios, páginas y APIs). Las historias cubren: vehículos, transferencias, reservas, asignaciones, mantenimientos, ITV/seguros/impuestos/multas/autorizaciones, conductores, organizaciones, proveedores, pickups, cesiones y operaciones auxiliares (auth, dashboard, uploads, reportes).
   - Si detectas un caso concreto que no aparezca aquí (un endpoint nuevo o una plantilla especial), dímelo y lo añado.

   ---

   ## 🔐 Módulo: Autenticación y Usuarios

   HU-A1: Inicio de sesión seguro (form & API)
   - Rol: Usuario autenticado
   - Objetivo: Permitir login seguro por formulario y por API (si aplica). Protege CSRF y rate-limit.
   - AC:
     - POST `/auth/login` acepta `username`/`password`+CSRF en UI; para API acepta credenciales y devuelve token.
     - Errores 401/403 en credenciales inválidas; 400 en CSRF inválido.
     - Soporta 2FA (cuando configurado).
   - Casos borde: bloqueo temporal de cuenta, sesión inválida, token expired.

   HU-A2: Logout
   - POST `/auth/logout` invalida sesión y limpia cookies.

   HU-A3: Gestión de usuarios y roles
   - CRUD de usuarios (`/admin/users`), asignación de roles y reestablecimiento de contraseñas.
   - Auditoría de cambios (who/when/what).

   ---

   ## 🚗 Módulo: Vehículos (completo)

   HU-V1: Crear/Editar/Eliminar vehículo (full)
   - Rol: Administrador de flota
   - Endpoints: GET/POST `/vehicles/new`, POST `/api/vehicles`, GET/POST `/vehicles/{id}/edit`, DELETE `/vehicles/{id}` (o POST con acción). Templates: `vehicles/form.html`, `vehicles/list.html`, `vehicles/detail.html`.
   - AC:
     - Validaciones: matrícula única, VIN único, VIN formato, año válido, si `vehicle_type == renting` entonces `contract_id` obligatorio.
     - Al crear: redirigir a ficha; en API devuelve 201 con Location.
     - Al eliminar: eliminar archivos relacionados (documentos) y registros históricos opcionales.
   - Casos borde: intento de crear con matrícula duplicada (400), VIN mal formado, falta de provider/organization.

   HU-V2: Transferencia de vehículo entre unidades
   - Rol: Administrador
   - Endpoints: `/vehicle_transfers` (controller `vehicle_transfer_controller.py`), forms para `cesion`/transfer (`assignments/cesion_form.html`).
   - AC:
     - Crear transferencia que registra origen/destino, motivo, fecha y responsable.
     - Actualiza `organization_unit_id` del vehículo y registra evento en historial.
     - Validar permisos y notificar a responsables.

   HU-V3: Historial completo y export
   - Página: `vehicles/detail.html` muestra pestañas para historial, impuestos, multas, autorizaciones, mantenimientos.
   - AC:
     - Historial ordenado por fecha desc; fallback `created_at` si falta fecha.
     - Filtrado por tipo y export CSV del historial.

   HU-V4: Búsqueda, filtros y paginación
   - Endpoints: `/vehicles` con query params `status,type,org_id,available_from,available_to,q,page,size`.
   - AC: respuesta incluye `total_count`, `page`, `page_size` y `items`.

   ---

   ## 👥 Módulo: Conductores y permisos

   HU-D1: CRUD conductores
   - Templates: `drivers/form.html`, `drivers/list.html`, `drivers/detail.html`.
   - Campos: nombre, apellidos, NIF, email, teléfono, tipo, carnets (lista con tipo y fecha de vencimiento), organización.
   - Reglas: validación NIF/NIE, notificaciones 30 días antes de vencimiento.

   HU-D2: Asignación de conductor (assignments)
   - Controller: `assignment_controller.py`; templates `assignments/form.html`, `assignments/list.html`.
   - AC: crear asignación con `vehicle_id, driver_id, start_date, end_date`; validar solapamientos y devolver 409 con detalles si hay conflicto.

   HU-D3: Estadísticas del conductor
   - Página `driver/dashboard.html` incluye conteos de multas, asignaciones, incapacidades y vencimientos de carnets.

   ---

   ## 📅 Módulo: Reservas

   HU-R1: Crear reserva y validar disponibilidad
   - Templates: `reservations/form.html`, `reservations/list.html`, `reservations/detail.html`, `reservations/conflict.html`.
   - Validaciones:
     - `start < end`; vehículo no reservado/ocupado en el rango; CSRF.
     - Si conflicto, página `reservations/conflict.html` muestra conflictos y alternativas.

   HU-R2: Aprobación / Rechazo
   - PATCH `/api/reservations/{id}` cambia estado y notifica solicitante (email/internal notification). En approving crea asignación temporal y bloquea vehículo.

   HU-R3: Políticas de aprobación avanzada
   - Reglas: doble aprobación si duración o kilometraje excede umbral; reglas por unidad organizativa.

   ---

   ## 🔧 Módulo: Mantenimiento y pickups

   HU-M1: Registrar intervención (Mantenimiento)
   - Controller: `maintenance_controller.py`; templates `maintenance/form.html`, `maintenance/list.html`, `maintenance/detail.html`.
   - Campos: tipo, descripción, fecha, mileage, cost, provider_id, piezas usadas (lista).
   - Reglas: si `cost > threshold` crear alerta a finanzas.

   HU-M2: Pickups y entregas
   - Controller: `pickup_controller.py`; templates `pickups/list.html`, `pickups/detail.html`.
   - AC: registrar recogida y entrega de vehículo con firma/usuario responsable y kilometraje.

   ---

   ## ⚖️ Módulo: Cumplimiento (ITV, Seguros, Impuestos, Multas, Autorizaciones)

   HU-C1: ITV y seguros
   - Controllers: `compliance_controller.py`; templates en `app/templates/compliance/itv*.html`, `insurance_*.html`.
   - AC: crear/listar ITV e insurances con documentos adjuntos (file uploads) y alertas programadas antes de vencimiento.

   HU-C2: Impuestos
   - Templates: `compliance/taxes.html`, `tax_form.html`, `tax_detail.html`.
   - AC: registrar pagos, visualizar estado `paid|pending|overdue` y exportar histórico.

   HU-C3: Multas
   - Templates: `compliance/fines.html`, `fine_form.html`, `fine_detail.html`.
   - AC: crear multa, permitir asignación a `driver_id` o `vehicle_id`, marcar estado `open|paid|contested` y registrar recursos.

   HU-C4: Autorizaciones especiales
   - Templates: `compliance/authorizations.html`, `authorization_form.html`, `authorization_detail.html`.
   - AC: crear autorización con metadatos de zona, alcance y fechas; búsqueda por zona.

   ---

   ## 🏢 Módulo: Organizaciones y árbol

   HU-O1: CRUD Unidades organizativas y árbol
   - Templates: `organizations/form_with_tree.html`, `organizations/tree.html`, `organizations/list.html`.
   - AC: CRUD completo, arrastrar/ordenar en la UI (si aplica), export JSON del árbol para integraciones.

   HU-O2: Permisos basados en unidad
   - Reglas: herencia de permisos, alcance de supervisores y responsables por unidad.

   ---

   ## 🧾 Módulo: Proveedores

   HU-P1: CRUD proveedores
   - Templates: `providers/form.html`, `providers/list.html`, `providers/detail.html`.
   - AC: registrar proveedor con datos de contacto, servicios ofrecidos y contratos.

   ---

   ## 🚚 Módulo: Transferencias y cesiones

   HU-T1: Cesiones / Transferencias entre unidades o usuarios
   - Templates: `assignments/cesion_form.html`, `assignments/cesion_detail.html`, `assignments/cesiones.html`.
   - AC: registrar cesión con fechas, motivos, vehículo y responsable; actualizar estado del vehículo y su ubicación administrativa.

   ---

   ## 📁 Módulo: Archivos, uploads y documentos

   HU-F1: Subir documentos asociados a vehículo/itv/insurance/tax
   - Reglas: validar tipo (pdf,jpg,png), tamaño máximo, almacenar en `static/uploads` y registrar metadata en DB (who/when/path).

   HU-F2: Descargas seguras
   - El endpoint de descarga debe verificar permisos y servir con headers correctos; no exponer paths absolutos.

   ---

   ## 📊 Módulo: Dashboard, Reportes y Export

   HU-DASH1: Dashboard operativo
   - Templates: `dashboard.html` y `compliance/dashboard.html`.
   - AC: widgets con métricas (véase HU-70 original), filtros por periodo y unidad, enlaces a listados filtrados.

   HU-DASH2: Exportes
   - CSV/PDF para listados (vehicles, reservations, maintenance, fines) con parámetros de filtrado.

   ---

   ## 🧪 Observabilidad, errores y límites

   HU-S1: Manejo de errores y páginas de status
   - Templates: `errors/400.html`, `errors/403.html`, `errors/404.html`, `errors/429.html`, `errors/500.html` deben mostrarse apropiadamente.

   HU-S2: Rate limiting y seguridad
   - Reglas: endpoints sensibles (auth, file upload) deben aplicar limitación y validación estricta.

   HU-S3: Auditoría
   - Todas las operaciones CRUD importantes deben registrar `who, when, what`.

   ---

   ## Reglas transversales y validaciones
   - CSRF obligatorio en formularios.
   - Validación de entradas tanto en frontend como en backend (servidor autoridad).
   - Internacionalización (i18n) en strings; plantillas deben poder recibir traducciones.
   - Paginación y filtros en endpoints listados.
   - Manejo de concurrencia en reservas/asignaciones para evitar solapamientos (bloqueos optimistas o checks transaccionales).

   ---

   ## Entregables por historia
   - Cada HU deberá entregarse con:
     1. Escenarios Given/When/Then en `tests/` o archivos BDD.
     2. Tests pytest (happy path + 1–2 casos borde): validaciones, conflictos y permisos.
     3. Mock o contrato API (OpenAPI/Swagger fragment mínimo).

   ---

   Si quieres, procedo a cualquiera de las siguientes acciones (elige una o varias):

   1) Generar los escenarios Given/When/Then para todas las historias nuevas (puedo crear archivos `.feature` o tests pytest en `tests/`).
   2) Crear plantillas de tests pytest (un test por historia: happy path + 1 caso borde) y ubicarlas en `tests/`.
   3) Extraer un backlog priorizado (MVP / v1 / v2) con estimaciones rápidas.
   4) Añadir casos concretos que quieras garantizar (por ejemplo: excluir `gestion_vehiculos.db` y `security.log` de los backups/archives).

   Dime qué prefieres y lo hago: (a) generar BDD, (b) crear tests pytest, (c) priorizar backlog, (d) otra cosa.
- Internacionalización (i18n): textos parametrizables para múltiples idiomas.
