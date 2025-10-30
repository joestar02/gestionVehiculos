Feature: Historias de Usuario - Escenarios Given/When/Then
  Archivo de escenarios BDD para las historias principales del Sistema de Gestión de Flota.

  # -----------------
  # Módulo: Autenticación
  # -----------------
  Scenario: HU-01 - Inicio de sesión seguro (happy path)
    Given un usuario registrado activo con username "user1" y contraseña "CorrectHorseBatteryStaple"
    And el token CSRF válido está presente en la página de login
    When el usuario envía POST a "/auth/login" con username, password y csrf_token
    Then la respuesta es 302 y redirige a "/dashboard"
    And la cookie de sesión está establecida con flags Secure y HttpOnly

  Scenario: HU-01 - Inicio de sesión con credenciales inválidas (caso borde)
    Given un intento de login con username "user1" y contraseña incorrecta
    When se envía POST a "/auth/login" con datos inválidos
    Then la respuesta es 401 o 403
    And el cuerpo contiene un mensaje de error genérico que no indica si el usuario existe
    And no se crea cookie de sesión

  Scenario: HU-02 - Cierre de sesión (happy path)
    Given un usuario autenticado con sesión válida
    When envía POST a "/auth/logout" con CSRF válido
    Then la sesión se invalida en servidor
    And la cookie de sesión es eliminada
    And el usuario es redirigido a "/"

  Scenario: HU-03 - Gestión de roles (happy path)
    Given un Administrador autenticado
    When crea un rol nuevo via POST a "/admin/roles" con permisos CRUD para recursos X
    Then el rol queda persistido y listado en GET "/admin/roles"
    And la auditoría registra quién creó el rol

  # -----------------
  # Módulo: Vehículos
  # -----------------
  Scenario: HU-10 - Registrar nuevo vehículo (happy path)
    Given un Administrador en la página "/vehicles/new"
    When completa el formulario con matrícula única y VIN válido y envía
    Then POST /api/vehicles retorna 201 y el body contiene el Vehicle con id
    And el vehículo aparece en GET /vehicles

  Scenario: HU-10 - Registrar vehículo con matrícula duplicada (caso borde)
    Given un vehículo existente con matrícula "ABC-1234"
    When el administrador intenta crear otro vehículo con la misma matrícula
    Then el servidor responde 400 con error de validación indicando duplicidad

  Scenario: HU-11 - Filtrar lista de vehículos (happy path)
    Given varios vehículos con distintos estados y unidades organizativas
    When el usuario solicita GET /vehicles?status=available&type=turismo
    Then la respuesta contiene solo vehículos que cumplan los filtros
    And la respuesta incluye total_count y paginación

  Scenario: HU-12 - Ver ficha detallada y historial (happy path)
    Given un vehículo con eventos históricos (asignación, mantenimiento, multa)
    When visita GET /vehicles/{id}
    Then la página muestra pestañas: General, Historial, Documentos, Mantenimiento
    And el historial está ordenado por fecha descendente

  Scenario: HU-12 - Eventos sin fecha concreta (caso borde)
    Given un evento histórico sin fecha pero con created_at
    When se muestra el historial
    Then el evento aparece ordenado usando created_at como fallback

  # -----------------
  # Módulo: Conductores
  # -----------------
  Scenario: HU-20 - Registrar conductor (happy path)
    Given un Administrador en "/drivers/new"
    When completa los campos obligatorios y añade carnets con fechas de vencimiento
    Then POST /api/drivers retorna 201 y el driver aparece en la lista

  Scenario: HU-20 - Registrar conductor con NIF inválido (caso borde)
    Given un formulario con NIF mal formado
    When se envía el formulario
    Then el servidor responde 400 con mensaje de validación sobre NIF

  Scenario: HU-21 - Asignación de conductor (happy path)
    Given un vehículo disponible y un conductor con carnet válido
    When POST /api/assignments con start_date y end_date no solapados
    Then se crea la asignación y GET /vehicles/{id}/assignments incluye la nueva entrada

  Scenario: HU-21 - Asignación con solapamiento (caso borde)
    Given una asignación existente que cubre 2025-11-01..2025-11-05
    When se intenta crear otra asignación para el mismo vehículo que solapa esas fechas
    Then el servidor responde 409 con detalles del conflicto

  # -----------------
  # Módulo: Reservas
  # -----------------
  Scenario: HU-30 - Solicitar reserva (happy path)
    Given un empleado autenticado en /reservations/new
    When rellena fechas válidas start < end y selecciona vehículo disponible
    And hace POST /reservations con CSRF
    Then la reserva queda en estado pending y se notifica al supervisor

  Scenario: HU-30 - Solicitar reserva con rango inválido (caso borde)
    Given start_date >= end_date
    When el empleado envía el formulario
    Then el servidor responde 400 con error de validación "start must be before end"

  Scenario: HU-31 - Aprobar reserva (happy path)
    Given una reserva en estado pending y un supervisor autorizado
    When el supervisor PATCH /api/reservations/{id} con status=approved
    Then la reserva pasa a approved
    And se crea bloqueo en el vehículo para ese rango
    And el solicitante recibe notificación

  Scenario: HU-31 - Rechazar reserva por conflicto (caso borde)
    Given otra reserva aprobada solapando el mismo rango
    When el supervisor intenta aprobar la reserva pending
    Then la API devuelve 409 y el estado permanece en pending o pasa a rejected según política

  # -----------------
  # Módulo: Mantenimiento
  # -----------------
  Scenario: HU-40 - Registrar intervención de mantenimiento (happy path)
    Given un técnico en /maintenance/new
    When crea un registro con vehicle_id, performed_at, mileage y cost
    Then POST /api/maintenance retorna 201
    And el historial del vehículo incluye la intervención

  Scenario: HU-40 - Registrar intervención con coste alto (caso borde)
    Given un coste > umbral configurado
    When se guarda la intervención
    Then el sistema genera alerta hacia finanzas (registro / notificación)

  # -----------------
  # Módulo: Cumplimiento Normativo
  # -----------------
  Scenario: HU-50 - Registrar ITV y alertas (happy path)
    Given un responsable crea VehicleItv con expiry_date en 12 meses
    When guarda el registro
    Then en la configuración aparece tarea/alerta para X días antes del expiry

  Scenario: HU-51 - Registrar impuesto pagado (happy path)
    Given un registro de impuesto con payment_status=paid
    When se crea POST /api/taxes
    Then GET /vehicles/{id}/compliance muestra status `paid` para el periodo

  Scenario: HU-51 - Impuesto pendiente/overdue (caso borde)
    Given un impuesto con due_date pasado y payment_status=pending
    When se consulta compliance
    Then aparece como `overdue` y se genera notificación según reglas

  Scenario: HU-52 - Registrar multa (happy path)
    Given una multa emitida asociada a un vehículo
    When POST /api/fines con datos válidos
    Then la multa se crea con estado `pending` y aparece en el perfil del vehículo

  Scenario: HU-52 - Multa sin conductor asociado (caso borde)
    Given multa sin driver_id
    When se registra la multa
    Then la multa se asocia sólo al vehículo y no se aplica impacto a conductor

  Scenario: HU-53 - Crear autorización especial (happy path)
    Given responsable crea autorización con start_date y end_date válidos
    When POST /api/authorizations
    Then autorización aparece en /vehicles/{id}/authorizations y se puede buscar por zona

  Scenario: HU-53 - Crear autorización con end_date anterior a start_date (caso borde)
    Given end_date < start_date
    When intenta crear autorización
    Then servidor responde 400 con error de validación

  # -----------------
  # Módulo: Organizaciones
  # -----------------
  Scenario: HU-60 - CRUD de unidades organizativas (happy path)
    Given un administrador en /organizations
    When crea una unidad padre y luego una unidad hija vinculada al padre
    Then GET /api/organizations devuelve la jerarquía con relación padre->hijo

  Scenario: HU-60 - Importar árbol JSON inválido (caso borde)
    Given un JSON malformado enviado para importar árbol
    When se realiza la importación
    Then el servidor responde 400 y no modifica la jerarquía existente

  # -----------------
  # Módulo: Dashboard y Reportes
  # -----------------
  Scenario: HU-70 - Dashboard operativo (happy path)
    Given datos de flota con vehículos, reservas y vencimientos
    When el usuario accede a /dashboard
    Then los widgets muestran métricas calculadas y enlaces a vistas filtradas

  Scenario: HU-70 - Exportar reporte con filtros (caso borde)
    Given filtros que devuelven 0 resultados
    When el usuario solicita export CSV/PDF
    Then el archivo se genera (vacío o con cabeceras) y la operación no falla
