Feature: Historias de Usuario - Escenarios completos Given/When/Then
  Archivo BDD completo que cubre las historias detectadas en el código y plantillas.

  # -----------------
  # Módulo: Autenticación y Usuarios
  # -----------------
  Scenario: HU-A1 - Inicio de sesión seguro (happy path)
    Given un usuario registrado activo con username "user1" y contraseña "CorrectHorseBatteryStaple"
    And el token CSRF válido está presente en la página de login
    When el usuario envía POST a "/auth/login" con username, password y csrf_token
    Then la respuesta es 302 y redirige a "/dashboard"
    And la cookie de sesión está establecida con flags Secure y HttpOnly

  Scenario: HU-A1 - Inicio de sesión con 2FA requerido (caso borde)
    Given un usuario con 2FA habilitado
    When envía credenciales válidas
    Then el servidor solicita código 2FA
    When el usuario envía el código 2FA válido
    Then la sesión se crea y redirige a "/dashboard"

  Scenario: HU-A2 - Logout e invalidación (happy path)
    Given un usuario autenticado con sesión válida
    When envía POST a "/auth/logout" con CSRF válido
    Then la sesión se invalida en servidor
    And la cookie de sesión es eliminada
    And el usuario es redirigido a "/"

  Scenario: HU-A3 - Gestión de usuarios y roles (happy path)
    Given un Administrador autenticado
    When crea un usuario nuevo via POST a "/admin/users" y asigna roles via "/admin/roles"
    Then el usuario aparece en GET "/admin/users"
    And las acciones quedan registradas en la tabla de auditoría

  # -----------------
  # Módulo: Vehículos y Transferencias
  # -----------------
  Scenario: HU-V1 - Crear vehículo con renting (happy path)
    Given un Administrador en "/vehicles/new"
    When completa el formulario con vehicle_type="renting" y contract_id válido
    Then POST /api/vehicles retorna 201 y el Vehicle incluye contract_id

  Scenario: HU-V1 - Crear vehículo sin contract_id cuando renting (caso borde)
    Given formulario con vehicle_type="renting" y contract_id ausente
    When envía el formulario
    Then servidor responde 400 con error indicando que contract_id es obligatorio

  Scenario: HU-V2 - Transferir vehículo entre unidades (happy path)
    Given un vehículo con organization_unit_id=A
    When crea una transferencia a organization B mediante /vehicle_transfers
    Then el vehicle.organization_unit_id es B
    And se registra evento de transferencia en historial

  Scenario: HU-V3 - Historial export CSV (happy path)
    Given un vehículo con historial
    When solicita GET /vehicles/{id}/history?format=csv
    Then se recibe CSV con cabecera y filas de eventos

  Scenario: HU-V4 - Búsqueda avanzada y paginación (caso borde)
    Given una flota grande
    When solicita GET /vehicles?status=available&page=10&size=25&q=modelo
    Then la respuesta incluye items, total_count, page y page_size

  # -----------------
  # Módulo: Conductores y Asignaciones
  # -----------------
  Scenario: HU-D1 - Crear conductor y validación de NIF (happy path)
    Given un Administrador en "/drivers/new"
    When completa NIF correcto y campos obligatorios
    Then POST /api/drivers retorna 201 y el driver aparece en la lista

  Scenario: HU-D1 - NIF inválido (caso borde)
    Given formulario con NIF mal formado
    When se envía
    Then servidor devuelve 400 con mensaje de validación

  Scenario: HU-D2 - Asignación sin solapamiento (happy path)
    Given vehículo y conductor libres
    When POST /api/assignments con fechas válidas
    Then la asignación queda registrada

  Scenario: HU-D2 - Asignación con solapamiento (caso borde)
    Given asignación existente en rango R
    When intenta crear selección que solapa R
    Then API devuelve 409 con detalles del conflicto

  Scenario: HU-D3 - Estadísticas del conductor (happy path)
    Given conductor con multas y asignaciones previas
    When visita /driver/{id}/dashboard
    Then se muestran estadísticas y links a historial

  # -----------------
  # Módulo: Reservas
  # -----------------
  Scenario: HU-R1 - Crear reserva (happy path)
    Given usuario autenticado en /reservations/new
    When envía POST con start<end y vehículo disponible
    Then la reserva queda en estado pending y notifica al supervisor

  Scenario: HU-R1 - Reserva con rango inválido (caso borde)
    Given start >= end
    When envía
    Then el servidor devuelve 400

  Scenario: HU-R2 - Aprobar reserva (happy path)
    Given reserva pending y supervisor autorizado
    When PATCH /api/reservations/{id} con status=approved
    Then la reserva pasa a approved y se crea asignación temporal

  Scenario: HU-R2 - Rechazar por conflicto (caso borde)
    Given reserva que solapa con otra aprobada
    When intenta aprobar
    Then API devuelve 409 y se informa del conflicto

  # -----------------
  # Módulo: Mantenimiento y Pickups
  # -----------------
  Scenario: HU-M1 - Crear mantenimiento con piezas (happy path)
    Given técnico en /maintenance/new
    When sube datos y piezas, cost y mileage
    Then POST /api/maintenance retorna 201 y se registra evento

  Scenario: HU-M1 - Coste alto -> alerta (caso borde)
    Given cost > threshold
    When guarda
    Then alerta a finanzas es registrada

  Scenario: HU-M2 - Registro pickup (happy path)
    Given empleado realiza pickup
    When registra salida y llegada
    Then registro queda en DB con kilometrajes registrados

  # -----------------
  # Módulo: Cumplimiento
  # -----------------
  Scenario: HU-C1 - Crear ITV con upload (happy path)
    Given responsable en /compliance/itv/new
    When sube PDF y guarda expiry_date
    Then archivo se guarda y registro queda en DB

  Scenario: HU-C1 - Upload inválido (caso borde)
    Given upload con extensión no permitida
    When intenta subir
    Then servidor responde 400

  Scenario: HU-C2 - Registrar impuesto y overdue
    Given impuesto con due_date pasado
    When consulta compliance
    Then aparece overdue y alerta se genera

  Scenario: HU-C3 - Crear multa y asignarla a conductor
    Given multa con driver_id
    When POST /api/fines
    Then multa aparece en historial del driver

  Scenario: HU-C3 - Recurso de multa
    Given multa en estado pending
    When conductor presenta recurso
    Then estado pasa a contested y se registra histórico

  Scenario: HU-C4 - Crear autorización y búsqueda por zona
    Given autorización para ZONA_X
    When GET /api/authorizations?zone=ZONA_X
    Then autorización aparece en resultados

  # -----------------
  # Módulo: Organizaciones
  # -----------------
  Scenario: HU-O1 - Crear y exportar árbol (happy path)
    Given administrador crea unidades
    When solicita export JSON
    Then se obtiene árbol con jerarquía correcta

  Scenario: HU-O1 - Importar JSON inválido (caso borde)
    Given JSON malformado
    When POST /api/organizations/import
    Then responde 400 y no aplica cambios

  # -----------------
  # Módulo: Proveedores
  # -----------------
  Scenario: HU-P1 - Crear proveedor (happy path)
    Given administrador en /providers/new
    When crea proveedor con datos válidos
    Then proveedor aparece en listado

  Scenario: HU-P1 - Eliminar proveedor en uso (caso borde)
    Given proveedor asociado a registros activos
    When intenta eliminar
    Then servidor devuelve 409

  # -----------------
  # Módulo: Transferencias y Cesiones
  # -----------------
  Scenario: HU-T1 - Registrar cesión (happy path)
    Given cesión planeada entre unidades
    When crea cesión
    Then vehículo cambia estado y se registra cesión

  Scenario: HU-T1 - Cesión sin fecha (caso borde)
    Given formulario incompleto
    When guarda
    Then 400 validación

  # -----------------
  # Módulo: Archivos y Descargas
  # -----------------
  Scenario: HU-F1 - Subir documento (happy path)
    Given usuario autorizado en /vehicles/{id}/documents/new
    When sube documento válido
    Then archivo está en static/uploads y metadata en DB

  Scenario: HU-F2 - Descargar con permiso (happy path)
    Given usuario con permiso
    When solicita descarga
    Then servidor devuelve archivo con headers seguros

  Scenario: HU-F2 - Descargar sin permiso (caso borde)
    Given usuario sin permiso
    When solicita descarga
    Then el servidor responde 403

  # -----------------
  # Módulo: Dashboard y Export
  # -----------------
  Scenario: HU-DASH1 - Widgets del dashboard
    Given datos de flota
    When visita /dashboard
    Then widgets muestran métricas y enlaces

  Scenario: HU-DASH2 - Export filtros
    Given filtros aplicados
    When solicita export CSV
    Then se entrega archivo correspondiente

  # -----------------
  # Observabilidad, Límite y Errores
  # -----------------
  Scenario: HU-S1 - Páginas de error (404)
    Given petición a recurso inexistente
    When servidor responde
    Then muestra template errors/404.html

  Scenario: HU-S2 - Rate limiting (login)
    Given múltiples intentos fallidos
    When supera umbral
    Then login responde 429

  Scenario: HU-S3 - Auditoría CRUD
    Given administrador realiza cambios
    When crea/edita/elimina recursos
    Then auditoría registra who/when/what
