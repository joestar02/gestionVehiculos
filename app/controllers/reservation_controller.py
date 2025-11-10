"""Reservation controller"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.services.reservation_service import ReservationService
from app.services.vehicle_service import VehicleService
from app.services.driver_service import DriverService
from app.models.reservation import ReservationStatus
from app.models.user import UserRole
from app.utils.error_helpers import log_exception
from app.services.reservation_service import ReservationService as RService
from urllib.parse import urlencode

reservation_bp = Blueprint('reservations', __name__)

@reservation_bp.route('/')
@login_required
def list_reservations():
    """List all reservations"""
    # Optional date filter (YYYY-MM-DD) to show reservations for a specific day
    date_str = request.args.get('date')
    if date_str:
        from datetime import datetime, timedelta
        try:
            day = datetime.strptime(date_str, '%Y-%m-%d').date()
            start = datetime.combine(day, datetime.min.time())
            end = start + timedelta(days=1)
        except Exception:
            start = None
            end = None
    else:
        start = None
        end = None

    # pagination params
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 20))
    except ValueError:
        per_page = 20

    # preserved query params (all except page) to keep filters when navigating pages
    preserved_args = {k: v for k, v in request.args.items() if k != 'page'}
    # Build a base URL and a preserved querystring for safe use in templates
    base_list_url = url_for('reservations.list_reservations')
    preserved_qs = urlencode(preserved_args) if preserved_args else ''

    if current_user.role == UserRole.DRIVER:
        # Drivers can only see their own reservations
        driver = current_user.driver
        if not driver:
            flash('No se encontró conductor asociado.', 'error')
            return redirect(url_for('main.index'))
        if start and end:
            pagination = ReservationService.get_reservations_by_driver_and_date_range_paginated(driver.id, start, end, page=page, per_page=per_page)
        else:
            pagination = ReservationService.get_reservations_by_driver_paginated(driver.id, page=page, per_page=per_page)
    else:
        # Admins and managers see all reservations
        if start and end:
            pagination = ReservationService.get_reservations_by_date_range_paginated(start, end, page=page, per_page=per_page)
        else:
            pagination = ReservationService.get_all_reservations_paginated(page=page, per_page=per_page)

    # pagination is a Pagination object from Flask-SQLAlchemy
    reservations = pagination.items if hasattr(pagination, 'items') else []
    return render_template('reservations/list.html', reservations=reservations, pagination=pagination, preserved_args=preserved_args, base_list_url=base_list_url, preserved_qs=preserved_qs)

@reservation_bp.route('/<int:reservation_id>')
@login_required
def view_reservation(reservation_id):
    """View reservation details"""
    reservation = ReservationService.get_reservation_by_id(reservation_id)
    if not reservation:
        flash('Reserva no encontrada', 'error')
        return redirect(url_for('reservations.list_reservations'))
    return render_template('reservations/detail.html', reservation=reservation)

@reservation_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_reservation():
    """Create new reservation"""
    if request.method == 'POST':
        try:
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%dT%H:%M')
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%dT%H:%M')
            
            # For official drivers, suggest their assigned vehicle
            vehicle_id = int(request.form.get('vehicle_id'))
            driver_id = int(request.form.get('driver_id'))
            
            # If driver is official and no vehicle specified, use assigned vehicle
            if current_user.role == UserRole.DRIVER and not vehicle_id:
                driver = current_user.driver
                if driver and driver.driver_type.value == 'official':
                    # Find assigned vehicle
                    from app.models.vehicle_driver_association import VehicleDriverAssociation
                    association = VehicleDriverAssociation.query.filter_by(
                        driver_id=driver.id, is_active=True
                    ).first()
                    if association:
                        vehicle_id = association.vehicle_id
            
            reservation = ReservationService.create_reservation(
                vehicle_id=vehicle_id,
                driver_id=driver_id,
                start_date=start_date,
                end_date=end_date,
                purpose=request.form.get('purpose'),
                destination=request.form.get('destination'),
                notes=request.form.get('notes'),
                user_id=current_user.id,
                organization_unit_id=current_user.driver.organization_unit_id if current_user.role == UserRole.DRIVER else int(request.form.get('organization_unit_id', 0))
            )
            flash('Reserva creada exitosamente', 'success')
            return redirect(url_for('reservations.view_reservation', reservation_id=reservation.id))
        except ValueError as ve:
            # overlap detected - try to extract the conflicting reservation id from the message
            msg = str(ve)
            import re
            m = re.search(r'id=(\d+)', msg)
            conflict = None
            if m:
                conflict = ReservationService.get_reservation_by_id(int(m.group(1)))
            data = dict(
                vehicle_id=vehicle_id,
                driver_id=driver_id,
                start_date=request.form.get('start_date'),
                end_date=request.form.get('end_date'),
                purpose=request.form.get('purpose'),
                destination=request.form.get('destination'),
                notes=request.form.get('notes')
            )
            return render_template('reservations/conflict.html', conflict=conflict, data=data, action='create')
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al crear reserva (id={err_id})', 'error')
    
    vehicles = VehicleService.get_available_vehicles()
    drivers = DriverService.get_active_drivers()
    
    # If user is a driver, only show themselves as driver option
    if current_user.role == UserRole.DRIVER:
        drivers = [current_user.driver] if current_user.driver else []
    
    return render_template('reservations/form.html', vehicles=vehicles, drivers=drivers)


@reservation_bp.route('/<int:reservation_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_reservation(reservation_id):
    """Edit reservation"""
    reservation = ReservationService.get_reservation_by_id(reservation_id)
    if not reservation:
        flash('Reserva no encontrada', 'error')
        return redirect(url_for('reservations.list_reservations'))

    if request.method == 'POST':
        try:
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%dT%H:%M')
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%dT%H:%M')

            update_kwargs = dict(
                vehicle_id=int(request.form.get('vehicle_id')),
                driver_id=int(request.form.get('driver_id')),
                start_date=start_date,
                end_date=end_date,
                purpose=request.form.get('purpose'),
                destination=request.form.get('destination'),
                notes=request.form.get('notes'),
                organization_unit_id=int(request.form.get('organization_unit_id', reservation.organization_unit_id or 0))
            )

            ReservationService.update_reservation(reservation_id, **update_kwargs)
            flash('Reserva actualizada exitosamente', 'success')
            return redirect(url_for('reservations.view_reservation', reservation_id=reservation_id))
        except ValueError as ve:
            msg = str(ve)
            import re
            m = re.search(r'id=(\d+)', msg)
            conflict = None
            if m:
                conflict = ReservationService.get_reservation_by_id(int(m.group(1)))
            data = dict(
                vehicle_id=request.form.get('vehicle_id'),
                driver_id=request.form.get('driver_id'),
                start_date=request.form.get('start_date'),
                end_date=request.form.get('end_date'),
                purpose=request.form.get('purpose'),
                destination=request.form.get('destination'),
                notes=request.form.get('notes')
            )
            return render_template('reservations/conflict.html', conflict=conflict, data=data, action='edit')
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al actualizar reserva (id={err_id})', 'error')

    vehicles = VehicleService.get_available_vehicles()
    drivers = DriverService.get_active_drivers()
    if current_user.role == UserRole.DRIVER:
        drivers = [current_user.driver] if current_user.driver else []

    return render_template('reservations/form.html', vehicles=vehicles, drivers=drivers, reservation=reservation)


@reservation_bp.route('/requests/<int:reservation_id>/change', methods=['POST'])
@login_required
def request_change(reservation_id):
    """Placeholder: request change for a conflicting reservation (could notify owner)."""
    # For now, simply flash a message and redirect to the conflicting reservation
    flash('Solicitud de cambio enviada al propietario de la reserva conflictiva', 'success')
    return redirect(url_for('reservations.view_reservation', reservation_id=reservation_id))


@reservation_bp.route('/force', methods=['POST'])
@login_required
def force_reservation():
    """Force creating/updating a reservation bypassing overlap checks - restricted to admins/managers."""
    # Check permission
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER]:
        flash('Acceso denegado para forzar reservas', 'error')
        return redirect(url_for('reservations.list_reservations'))

    # Read hidden fields sent from conflict form
    try:
        vehicle_id = int(request.form.get('vehicle_id'))
        driver_id = int(request.form.get('driver_id'))
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%dT%H:%M')
        purpose = request.form.get('purpose')
        destination = request.form.get('destination')
        notes = request.form.get('notes')

        # Direct DB insert bypassing overlap checker by creating object and committing
        from app.extensions import db as _db
        from app.models.reservation import Reservation, ReservationStatus
        r = Reservation(
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            start_date=start_date,
            end_date=end_date,
            purpose=purpose,
            destination=destination,
            notes=notes,
            user_id=current_user.id,
            organization_unit_id=current_user.driver.organization_unit_id if current_user.role == UserRole.DRIVER else 0,
            status=ReservationStatus.PENDING
        )
        _db.session.add(r)
        _db.session.commit()
        flash('Reserva forzada creada correctamente', 'success')
        return redirect(url_for('reservations.view_reservation', reservation_id=r.id))
    except Exception as e:
        err_id = log_exception(e, __name__)
        flash(f'Error al forzar reserva (id={err_id})', 'error')
        return redirect(url_for('reservations.list_reservations'))

@reservation_bp.route('/<int:reservation_id>/confirm', methods=['POST'])
@login_required
def confirm_reservation(reservation_id):
    """Confirm a reservation"""
    reservation = ReservationService.confirm_reservation(reservation_id)
    if reservation:
        flash('Reserva confirmada exitosamente', 'success')
    else:
        flash('Error al confirmar reserva', 'error')
    return redirect(url_for('reservations.view_reservation', reservation_id=reservation_id))

@reservation_bp.route('/<int:reservation_id>/start', methods=['POST'])
@login_required
def start_reservation(reservation_id):
    """Start a reservation"""
    try:
        actual_start_mileage = int(request.form.get('actual_start_mileage'))
        reservation = ReservationService.start_reservation(reservation_id, actual_start_mileage)
        if reservation:
            flash('Reserva iniciada exitosamente', 'success')
        else:
            flash('Error al iniciar reserva', 'error')
    except Exception as e:
        err_id = log_exception(e, __name__)
        flash(f'Error: (id={err_id})', 'error')
    return redirect(url_for('reservations.view_reservation', reservation_id=reservation_id))

@reservation_bp.route('/<int:reservation_id>/complete', methods=['POST'])
@login_required
def complete_reservation(reservation_id):
    """Complete a reservation"""
    try:
        actual_end_mileage = int(request.form.get('actual_end_mileage'))
        notes = request.form.get('completion_notes')
        reservation = ReservationService.complete_reservation(reservation_id, actual_end_mileage, notes)
        if reservation:
            flash('Reserva completada exitosamente', 'success')
        else:
            flash('Error al completar reserva', 'error')
    except Exception as e:
        err_id = log_exception(e, __name__)
        flash(f'Error: (id={err_id})', 'error')
    return redirect(url_for('reservations.view_reservation', reservation_id=reservation_id))

@reservation_bp.route('/<int:reservation_id>/cancel', methods=['POST'])
@login_required
def cancel_reservation(reservation_id):
    """Cancel a reservation"""
    cancellation_reason = request.form.get('cancellation_reason')
    if not cancellation_reason:
        flash('Debe proporcionar un motivo de cancelación', 'error')
        return redirect(url_for('reservations.view_reservation', reservation_id=reservation_id))
    
    reservation = ReservationService.cancel_reservation(reservation_id, cancellation_reason)
    if reservation:
        flash('Reserva cancelada exitosamente', 'success')
    else:
        flash('Error al cancelar reserva', 'error')
    return redirect(url_for('reservations.view_reservation', reservation_id=reservation_id))
