"""Driver controller"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from calendar import monthrange
from app.services.driver_service import DriverService
from app.services.organization_service import OrganizationService
from app.services.reservation_service import ReservationService
from app.models.driver import DriverType, DriverStatus
from app.models.user import UserRole
from app.utils.error_helpers import log_exception

driver_bp = Blueprint('drivers', __name__)

@driver_bp.route('/')
@login_required
def list_drivers():
    """List all drivers"""
    drivers = DriverService.get_all_drivers()
    return render_template('drivers/list.html', drivers=drivers)

@driver_bp.route('/<int:driver_id>')
@login_required
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
    """Create new driver"""
    if request.method == 'POST':
        try:
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
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                address=request.form.get('address'),
                notes=request.form.get('notes')
            )
            flash(f'Conductor {driver.full_name} creado exitosamente', 'success')
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
def delete_driver(driver_id):
    """Delete driver"""
    if DriverService.delete_driver(driver_id):
        flash('Conductor eliminado exitosamente', 'success')
    else:
        flash('Error al eliminar conductor', 'error')
    return redirect(url_for('drivers.list_drivers'))

@driver_bp.route('/<int:driver_id>/status', methods=['POST'])
@login_required
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
    
    return render_template('drivers/list.html', drivers=drivers, search_term=search_term)

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
