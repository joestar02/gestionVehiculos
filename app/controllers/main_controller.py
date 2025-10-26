"""Main controller for general routes"""
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import date, timedelta
from calendar import monthrange
from app.services.reservation_service import ReservationService
from app.services.vehicle_service import VehicleService
from app.services.maintenance_service import MaintenanceService
from app.services.organization_service import OrganizationService
from app.models.user import UserRole

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page - Redirect to dashboard if authenticated, else to login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page"""
    # Get current date or use provided parameters
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
    start_of_month = current_date
    _, last_day = monthrange(year, month)
    end_of_month = date(year, month, last_day)

    reservations = ReservationService.get_reservations_by_date_range(start_of_month, end_of_month)

    # Ensure relationships are loaded
    for reservation in reservations:
        # Access relationships to trigger lazy loading
        _ = reservation.vehicle
        _ = reservation.driver

    # Group reservations by date
    reservations_by_date = {}
    for res in reservations:
        res_date = res.start_date.date()
        if res_date not in reservations_by_date:
            reservations_by_date[res_date] = []
        reservations_by_date[res_date].append(res)

    # Generate calendar with proper week alignment
    calendar_data = generate_calendar_grid(year, month, reservations_by_date)

    return render_template('dashboard.html',
                         user=current_user,
                         calendar_data=calendar_data,
                         current_month=current_date)

@main_bp.route('/calendar')
@login_required
def calendar():
    """Monthly calendar view for administrators"""
    if current_user.role == UserRole.DRIVER:
        return redirect(url_for('drivers.driver_dashboard'))

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
    start_of_month = current_date
    _, last_day = monthrange(year, month)
    end_of_month = date(year, month, last_day)

    reservations = ReservationService.get_reservations_by_date_range(start_of_month, end_of_month)

    # Ensure relationships are loaded
    for reservation in reservations:
        # Access relationships to trigger lazy loading
        _ = reservation.vehicle
        _ = reservation.driver

    # Group reservations by date
    reservations_by_date = {}
    for res in reservations:
        res_date = res.start_date.date()
        if res_date not in reservations_by_date:
            reservations_by_date[res_date] = []
        reservations_by_date[res_date].append(res)

    # Generate calendar with proper week alignment
    calendar_data = generate_calendar_grid(year, month, reservations_by_date)

    return render_template('main/calendar.html',
                         calendar_data=calendar_data,
                         current_month=current_date,
                         today=today)

def generate_calendar_grid(year, month, reservations_by_date):
    """Generate a proper calendar grid for the month"""
    from calendar import monthrange, weekday
    import datetime

    # Get the first day of the month and its weekday (0=Monday, 6=Sunday)
    first_day = datetime.date(year, month, 1)
    start_weekday = weekday(first_day.year, first_day.month, first_day.day)

    # Adjust for Monday as first day of week
    if start_weekday == 6:  # Sunday
        start_weekday = -1  # This will be handled as 6 (Sunday) but we'll treat it as the last day

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

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'service': 'Gestión de Vehículos'}, 200

@main_bp.route('/test-bootstrap')
@login_required
def test_bootstrap():
    """Test page for Bootstrap components"""
    return render_template('test_bootstrap.html')
