from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.utils.helpers import parse_money
from app.utils.error_helpers import log_exception
from app.services.vehicle_service import VehicleService
from app.services.driver_service import DriverService
from app.services.organization_service import OrganizationService
from app.services.vehicle_assignment_service import VehicleAssignmentService
from app.models.vehicle_driver_association import VehicleDriverAssociation
from app.models.vehicle_assignment import VehicleAssignment, AssignmentType, PaymentStatus
from app.models.user import UserRole
from app.extensions import db

assignment_bp = Blueprint('assignments', __name__)

@assignment_bp.route('/')
@login_required
def list_assignments():
    """List all vehicle-driver assignments"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    assignments = VehicleDriverAssociation.query.filter_by(is_active=True).all()
    return render_template('assignments/list.html', assignments=assignments)

@assignment_bp.route('/assign', methods=['GET', 'POST'])
@login_required
def assign_vehicle():
    """Assign vehicle to driver"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            vehicle_id = int(request.form.get('vehicle_id'))
            driver_id = int(request.form.get('driver_id'))

            # Check if vehicle already has an active assignment
            existing_vehicle_assignment = VehicleDriverAssociation.query.filter_by(
                vehicle_id=vehicle_id, is_active=True
            ).first()

            if existing_vehicle_assignment:
                flash('Este vehículo ya tiene un conductor asignado. Desasigne el conductor actual antes de asignar uno nuevo.', 'error')
                return redirect(url_for('assignments.assign_vehicle'))

            # Check if assignment already exists (driver already assigned to this vehicle)
            existing = VehicleDriverAssociation.query.filter_by(
                vehicle_id=vehicle_id, driver_id=driver_id, is_active=True
            ).first()

            if existing:
                flash('Esta asignación ya existe.', 'error')
            else:
                assignment = VehicleDriverAssociation(
                    vehicle_id=vehicle_id,
                    driver_id=driver_id,
                    start_date=datetime.utcnow(),
                    created_by=current_user.id
                )
                db.session.add(assignment)
                db.session.commit()
                flash('Vehículo asignado exitosamente.', 'success')
                return redirect(url_for('assignments.list_assignments'))
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al asignar vehículo (id={err_id})', 'error')

    # Filter vehicles and drivers by organization unit for non-admin users
    if current_user.role in [UserRole.ADMIN, UserRole.FLEET_MANAGER]:
        vehicles = VehicleService.get_all_vehicles()
        drivers = DriverService.get_active_drivers()
    else:
        # Get organization unit from current user's driver profile
        user_driver = current_user.driver
        if user_driver:
            organization_unit_id = user_driver.organization_unit_id
            vehicles = VehicleService.get_all_vehicles(organization_unit_id=organization_unit_id)
            drivers = DriverService.get_all_drivers(organization_unit_id=organization_unit_id)
        else:
            vehicles = []
            drivers = []
            flash('Usuario no asociado a ninguna unidad organizacional', 'warning')

    return render_template('assignments/form.html', vehicles=vehicles, drivers=drivers)

@assignment_bp.route('/unassign/<int:assignment_id>', methods=['POST'])
@login_required
def unassign_vehicle(assignment_id):
    """Unassign vehicle from driver"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    assignment = VehicleDriverAssociation.query.get(assignment_id)
    if not assignment:
        flash('Asignación no encontrada.', 'error')
        return redirect(url_for('assignments.list_assignments'))
    else:
        assignment.is_active = False
        assignment.end_date = datetime.utcnow()
        db.session.commit()
        flash('Asignación eliminada exitosamente.', 'success')

    return redirect(url_for('assignments.list_assignments'))

# ============= Vehicle Assignment Routes (Cesión de vehículos) =============
@assignment_bp.route('/cesiones')
@login_required
def cesion_records():
    """Vehicle assignment records list"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    records = VehicleAssignmentService.get_all_assignments()
    return render_template('assignments/cesiones.html', records=records)

@assignment_bp.route('/cesiones/<int:assignment_id>')
@login_required
def view_cesion(assignment_id):
    """View vehicle assignment details"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    record = VehicleAssignmentService.get_assignment_by_id(assignment_id)
    if not record:
        flash('Registro de cesión no encontrado', 'error')
        return redirect(url_for('assignments.cesion_records'))
    return render_template('assignments/cesion_detail.html', record=record)

@assignment_bp.route('/cesiones/new', methods=['GET', 'POST'])
@login_required
def create_cesion():
    """Create new vehicle assignment"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')

            record = VehicleAssignmentService.create_assignment(
                vehicle_id=int(request.form.get('vehicle_id')),
                driver_id=int(request.form.get('driver_id')),
                organization_unit_id=int(request.form.get('organization_unit_id')),
                assignment_type=AssignmentType(request.form.get('assignment_type')),
                start_date=start_date,
                end_date=end_date,
                assignment_fee=parse_money(request.form.get('assignment_fee')),
                purpose=request.form.get('purpose'),
                destination=request.form.get('destination'),
                notes=request.form.get('notes')
            )
            flash('Cesión de vehículo creada exitosamente', 'success')
            return redirect(url_for('assignments.view_cesion', assignment_id=record.id))
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al crear cesión (id={err_id})', 'error')

    # Filter vehicles and drivers by organization unit for non-admin users
    if current_user.role in [UserRole.ADMIN, UserRole.FLEET_MANAGER]:
        vehicles = VehicleService.get_all_vehicles()
        drivers = DriverService.get_active_drivers()
        organization_units = OrganizationService.get_all_organization_units()
    else:
        # Get organization unit from current user's driver profile
        user_driver = current_user.driver
        if user_driver:
            organization_unit_id = user_driver.organization_unit_id
            vehicles = VehicleService.get_all_vehicles(organization_unit_id=organization_unit_id)
            drivers = DriverService.get_all_drivers(organization_unit_id=organization_unit_id)
            # For non-admin users, only show their organization unit
            organization_units = [user_driver.organization_unit]
        else:
            vehicles = []
            drivers = []
            organization_units = []
            flash('Usuario no asociado a ninguna unidad organizacional', 'warning')

    return render_template('assignments/cesion_form.html',
                         vehicles=vehicles,
                         drivers=drivers,
                         organization_units=organization_units,
                         assignment_types=AssignmentType)

@assignment_bp.route('/cesiones/<int:assignment_id>/pay', methods=['POST'])
@login_required
def pay_cesion(assignment_id):
    """Mark vehicle assignment as paid"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    try:
        payment_date = datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d')
        VehicleAssignmentService.mark_as_paid(
            assignment_id,
            payment_date,
            request.form.get('payment_method'),
            request.form.get('payment_reference')
        )
        flash('Cesión marcada como pagada', 'success')
    except Exception as e:
        err_id = log_exception(e, __name__)
        flash(f'Error: (id={err_id})', 'error')
    return redirect(url_for('assignments.view_cesion', assignment_id=assignment_id))

@assignment_bp.route('/cesiones/<int:assignment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_cesion(assignment_id):
    """Edit vehicle assignment"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    record = VehicleAssignmentService.get_assignment_by_id(assignment_id)
    if not record:
        flash('Registro de cesión no encontrado', 'error')
        return redirect(url_for('assignments.cesion_records'))

    if request.method == 'POST':
        try:
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')

            VehicleAssignmentService.update_assignment(
                assignment_id,
                assignment_type=AssignmentType(request.form.get('assignment_type')),
                start_date=start_date,
                end_date=end_date,
                assignment_fee=parse_money(request.form.get('assignment_fee')),
                purpose=request.form.get('purpose'),
                destination=request.form.get('destination'),
                notes=request.form.get('notes')
            )
            flash('Cesión actualizada exitosamente', 'success')
            return redirect(url_for('assignments.view_cesion', assignment_id=assignment_id))
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al actualizar cesión (id={err_id})', 'error')

    # Filter vehicles and drivers by organization unit for non-admin users
    if current_user.role in [UserRole.ADMIN, UserRole.FLEET_MANAGER]:
        vehicles = VehicleService.get_all_vehicles()
        drivers = DriverService.get_active_drivers()
        organization_units = OrganizationService.get_all_organization_units()
    else:
        # Get organization unit from current user's driver profile
        user_driver = current_user.driver
        if user_driver:
            organization_unit_id = user_driver.organization_unit_id
            vehicles = VehicleService.get_all_vehicles(organization_unit_id=organization_unit_id)
            drivers = DriverService.get_all_drivers(organization_unit_id=organization_unit_id)
            # For non-admin users, only show their organization unit
            organization_units = [user_driver.organization_unit]
        else:
            vehicles = []
            drivers = []
            organization_units = []
            flash('Usuario no asociado a ninguna unidad organizacional', 'warning')

    return render_template('assignments/cesion_form.html',
                         record=record,
                         vehicles=vehicles,
                         drivers=drivers,
                         organization_units=organization_units,
                         assignment_types=AssignmentType)

@assignment_bp.route('/cesiones/<int:assignment_id>/delete', methods=['POST'])
@login_required
def delete_cesion(assignment_id):
    """Delete vehicle assignment"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    try:
        VehicleAssignmentService.delete_assignment(assignment_id)
        flash('Cesión eliminada exitosamente', 'success')
    except Exception as e:
        err_id = log_exception(e, __name__)
        flash(f'Error al eliminar cesión (id={err_id})', 'error')
    return redirect(url_for('assignments.cesion_records'))
