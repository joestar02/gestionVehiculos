"""Driver controller"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from calendar import monthrange
from app.services.driver_service import DriverService
from app.utils.organization_access import organization_protect
from app.models.driver import Driver
from app.services.organization_service import OrganizationService
from app.services.reservation_service import ReservationService
from app.services.auth_service import AuthService
from app.models.driver import DriverType, DriverStatus
from app.models.user import UserRole, User
from app.utils.error_helpers import log_exception
from urllib.parse import urlencode
from app.utils.pagination import paginate_list

driver_bp = Blueprint('drivers', __name__)

@driver_bp.route('/')
@login_required
def list_drivers():
    """List all drivers (users with DRIVER role)"""
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 20))
    except ValueError:
        per_page = 20

    preserved_args = {k: v for k, v in request.args.items() if k != 'page'}
    base_list_url = url_for('drivers.list_drivers')
    preserved_qs = urlencode(preserved_args) if preserved_args else ''

    # Get user's organization unit
    organization_unit_id = None
    if current_user.driver and current_user.driver.organization_unit_id:
        organization_unit_id = current_user.driver.organization_unit_id

    # Get only drivers with DRIVER role users
    all_user_drivers = User.query.filter_by(role=UserRole.DRIVER, is_active=True).all()
    # Get associated drivers and filter by organization unit if needed
    all_drivers = [u.driver for u in all_user_drivers if u.driver and u.driver.is_active]
    if organization_unit_id:
        all_drivers = [d for d in all_drivers if d.organization_unit_id == organization_unit_id]
    all_drivers = sorted(all_drivers, key=lambda d: (d.last_name, d.first_name))
    
    drivers, pagination = paginate_list(all_drivers, page=page, per_page=per_page)
    return render_template('drivers/list.html', drivers=drivers, pagination=pagination, base_list_url=base_list_url, preserved_qs=preserved_qs)

@driver_bp.route('/<int:driver_id>')
@login_required
@organization_protect(model=Driver, id_arg='driver_id')
def view_driver(driver_id):
    """View driver details"""
    driver = DriverService.get_driver_by_id(driver_id)
    if not driver:
        flash('Conductor no encontrado', 'error')
        return redirect(url_for('drivers.list_drivers'))
    return render_template('drivers/detail.html', driver=driver)

@driver_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_driver():
    """Create new driver with associated user account"""
    if request.method == 'POST':
        try:
            # Validate user data
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            password_confirm = request.form.get('password_confirm', '')
            
            if not username or len(username) < 3:
                flash('El nombre de usuario debe tener al menos 3 caracteres', 'warning')
                organizations = OrganizationService.get_all_organizations()
                return render_template('drivers/form.html', driver_types=DriverType, organizations=organizations)
            
            if not email or '@' not in email:
                flash('Email válido es requerido', 'warning')
                organizations = OrganizationService.get_all_organizations()
                return render_template('drivers/form.html', driver_types=DriverType, organizations=organizations)
            
            if not password or len(password) < 6:
                flash('La contraseña debe tener al menos 6 caracteres', 'warning')
                organizations = OrganizationService.get_all_organizations()
                return render_template('drivers/form.html', driver_types=DriverType, organizations=organizations)
            
            if password != password_confirm:
                flash('Las contraseñas no coinciden', 'warning')
                organizations = OrganizationService.get_all_organizations()
                return render_template('drivers/form.html', driver_types=DriverType, organizations=organizations)
            
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                flash('El nombre de usuario ya existe', 'warning')
                organizations = OrganizationService.get_all_organizations()
                return render_template('drivers/form.html', driver_types=DriverType, organizations=organizations)
            
            if User.query.filter_by(email=email).first():
                flash('El email ya existe', 'warning')
                organizations = OrganizationService.get_all_organizations()
                return render_template('drivers/form.html', driver_types=DriverType, organizations=organizations)
            
            # Create user with DRIVER role
            user = AuthService.create_user(
                username=username,
                email=email,
                password=password,
                first_name=request.form.get('first_name'),
                last_name=request.form.get('last_name'),
                role=UserRole.DRIVER
            )
            
            # Create driver linked to user
            license_expiry = datetime.strptime(request.form.get('driver_license_expiry'), '%Y-%m-%d') if request.form.get('driver_license_expiry') else None

            driver = DriverService.create_driver(
                first_name=request.form.get('first_name'),
                last_name=request.form.get('last_name'),
                document_type=request.form.get('document_type'),
                document_number=request.form.get('document_number'),
                driver_license_number=request.form.get('driver_license_number'),
                driver_license_expiry=license_expiry,
                driver_type=DriverType(request.form.get('driver_type')),
                organization_unit_id=int(request.form.get('organization_unit_id')) if request.form.get('organization_unit_id') else None,
                email=email,
                phone=request.form.get('phone'),
                address=request.form.get('address'),
                notes=request.form.get('notes'),
                user_id=user.id
            )
            flash(f'Conductor {driver.full_name} y usuario {username} creados exitosamente', 'success')
            return redirect(url_for('drivers.view_driver', driver_id=driver.id))
        except ValueError as e:
            flash(str(e), 'warning')
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error inesperado al crear conductor (id={err_id})', 'error')

    organizations = OrganizationService.get_all_organizations()
    return render_template('drivers/form.html',
                         driver_types=DriverType,
                         organizations=organizations)

@driver_bp.route('/<int:driver_id>/edit', methods=['GET', 'POST'])
@login_required
@organization_protect(model=Driver, id_arg='driver_id')
def edit_driver(driver_id):
    """Edit driver"""
    driver = DriverService.get_driver_by_id(driver_id)
    if not driver:
        flash('Conductor no encontrado', 'error')
        return redirect(url_for('drivers.list_drivers'))
    
    if request.method == 'POST':
        try:
            license_expiry = datetime.strptime(request.form.get('driver_license_expiry'), '%Y-%m-%d')

            update_data = {
                'first_name': request.form.get('first_name'),
                'last_name': request.form.get('last_name'),
                'document_type': request.form.get('document_type'),
                'driver_license_number': request.form.get('driver_license_number'),
                'driver_license_expiry': license_expiry,
                'driver_type': DriverType(request.form.get('driver_type')),
                'email': request.form.get('email'),
                'phone': request.form.get('phone'),
                'address': request.form.get('address'),
                'notes': request.form.get('notes')
            }

            if request.form.get('organization_unit_id'):
                update_data['organization_unit_id'] = int(request.form.get('organization_unit_id'))

            DriverService.update_driver(driver_id, **update_data)
            flash('Conductor actualizado exitosamente', 'success')
            return redirect(url_for('drivers.view_driver', driver_id=driver_id))
        except ValueError as e:
            flash(str(e), 'warning')
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al actualizar conductor (id={err_id})', 'error')
    
    organizations = OrganizationService.get_all_organizations()
    return render_template('drivers/form.html', 
                         driver=driver,
                         driver_types=DriverType,
                         organizations=organizations)

@driver_bp.route('/<int:driver_id>/delete', methods=['POST'])
@login_required
@organization_protect(model=Driver, id_arg='driver_id')
def delete_driver(driver_id):
    """Delete driver"""
    if DriverService.delete_driver(driver_id):
        flash('Conductor eliminado exitosamente', 'success')
    else:
        flash('Error al eliminar conductor', 'error')
    return redirect(url_for('drivers.list_drivers'))

@driver_bp.route('/<int:driver_id>/status', methods=['POST'])
@login_required
@organization_protect(model=Driver, id_arg='driver_id')
def update_status(driver_id):
    """Update driver status"""
    try:
        status = DriverStatus(request.form.get('status'))
        driver = DriverService.update_driver_status(driver_id, status)
        if driver:
            flash(f'Estado del conductor actualizado a {status.value}', 'success')
        else:
            flash('Conductor no encontrado', 'error')
    except Exception as e:
        err_id = log_exception(e, __name__)
        flash(f'Error al actualizar estado (id={err_id})', 'error')
    
    return redirect(url_for('drivers.view_driver', driver_id=driver_id))

@driver_bp.route('/search')
@login_required
def search_drivers():
    """Search drivers"""
    search_term = request.args.get('q', '')
    if search_term:
        drivers = DriverService.search_drivers(search_term)
    else:
        drivers = DriverService.get_all_drivers()

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 20))
    except ValueError:
        per_page = 20

    preserved_args = {k: v for k, v in request.args.items() if k != 'page'}
    base_list_url = url_for('drivers.search_drivers')
    preserved_qs = urlencode(preserved_args) if preserved_args else ''

    drivers_page, pagination = paginate_list(drivers, page=page, per_page=per_page)
    return render_template('drivers/list.html', drivers=drivers_page, search_term=search_term, pagination=pagination, base_list_url=base_list_url, preserved_qs=preserved_qs)

# Driver-specific routes for logged-in drivers
@driver_bp.route('/dashboard')
@login_required
def driver_dashboard():
    """Driver dashboard with monthly calendar"""
    if current_user.role != UserRole.DRIVER:
        flash('Acceso denegado. Solo conductores pueden acceder.', 'error')
        return redirect(url_for('main.index'))

    driver = current_user.driver
    if not driver:
        flash('No se encontró conductor asociado.', 'error')
        return redirect(url_for('main.index'))

    today = date.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)

    # Ensure month is within valid range
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    current_date = date(year, month, 1)
    _, last_day = monthrange(year, month)

    reservations = ReservationService.get_reservations_by_driver_and_date_range(
        driver.id, current_date, date(year, month, last_day)
    )

    # Group reservations by date
    reservations_by_date = {}
    for res in reservations:
        res_date = res.start_date.date()
        if res_date not in reservations_by_date:
            reservations_by_date[res_date] = []
        reservations_by_date[res_date].append(res)

    # Generate calendar grid
    calendar_data = generate_calendar_grid(year, month, reservations_by_date)

    return render_template('driver/dashboard.html',
                         driver=driver,
                         calendar_data=calendar_data,
                         current_month=current_date,
                         today=today)

@driver_bp.route('/my-reservations')
@login_required
def my_reservations():
    """List driver's reservations"""
    if current_user.role != UserRole.DRIVER:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    driver = current_user.driver
    if not driver:
        flash('No se encontró conductor asociado.', 'error')
        return redirect(url_for('main.index'))

    reservations = ReservationService.get_reservations_by_driver(driver.id)
    return render_template('driver/reservations.html', reservations=reservations)

def generate_calendar_data(year, month, reservations):
    """Generate calendar data for the month"""
    cal = []
    _, last_day = monthrange(year, month)
    reservations_by_date = {}

    for res in reservations:
        res_date = res.start_date.date()
        if res_date not in reservations_by_date:
            reservations_by_date[res_date] = []
        reservations_by_date[res_date].append(res)

    for day in range(1, last_day + 1):
        day_date = date(year, month, day)
        cal.append({
            'date': day_date,
            'reservations': reservations_by_date.get(day_date, []),
            'is_today': day_date == date.today()
        })
    return cal

def generate_calendar_grid(year, month, reservations_by_date):
    """Generate a proper calendar grid for the month"""
    from calendar import monthrange, weekday
    import datetime

    # Get the first day of the month and its weekday (0=Monday, 6=Sunday)
    first_day = datetime.date(year, month, 1)
    start_weekday = weekday(first_day.year, first_day.month, first_day.day)

    # Adjust for Monday as first day of week
    if start_weekday == 6:  # Sunday
        start_weekday = -1

    _, last_day = monthrange(year, month)

    calendar_grid = []
    day = 1

    # Create 6 weeks (some months need 6 rows)
    for week in range(6):
        week_data = []
        for weekday in range(7):  # 0=Monday, 6=Sunday
            if week == 0 and weekday < start_weekday:
                # Empty cells before the first day of the month
                week_data.append({
                    'date': None,
                    'day': '',
                    'reservations': [],
                    'is_today': False,
                    'is_current_month': False
                })
            elif day <= last_day:
                current_date = datetime.date(year, month, day)
                week_data.append({
                    'date': current_date,
                    'day': day,
                    'reservations': reservations_by_date.get(current_date, []),
                    'is_today': current_date == datetime.date.today(),
                    'is_current_month': True
                })
                day += 1
            else:
                # Empty cells after the last day of the month
                week_data.append({
                    'date': None,
                    'day': '',
                    'reservations': [],
                    'is_today': False,
                    'is_current_month': False
                })

        calendar_grid.append(week_data)

        # Stop if we've filled all days
        if day > last_day:
            break

    return calendar_grid
