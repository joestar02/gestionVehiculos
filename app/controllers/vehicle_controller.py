"""Vehicle controller"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services.vehicle_service import VehicleService
from app.models.vehicle import VehicleType, OwnershipType, VehicleStatus
from app.utils.error_helpers import log_exception
from app.core.permissions import has_permission, audit_operation
from app.services.security_audit_service import SecurityAudit
from urllib.parse import urlencode
from app.utils.pagination import paginate_list

vehicle_bp = Blueprint('vehicles', __name__)

@vehicle_bp.route('/')
@login_required
def list_vehicles():
    """List all vehicles"""
    # pagination params
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 10))
    except ValueError:
        per_page = 10

    preserved_args = {k: v for k, v in request.args.items() if k != 'page'}
    base_list_url = url_for('vehicles.list_vehicles')
    preserved_qs = urlencode(preserved_args) if preserved_args else ''

    all_vehicles = VehicleService.get_all_vehicles()
    vehicles, pagination = paginate_list(all_vehicles, page=page, per_page=per_page)
    return render_template('vehicles/list.html', vehicles=vehicles, pagination=pagination, base_list_url=base_list_url, preserved_qs=preserved_qs)

@vehicle_bp.route('/<int:vehicle_id>')
@login_required
def view_vehicle(vehicle_id):
    """View vehicle details"""
    from app.services.vehicle_history_service import VehicleHistoryService
    
    vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
    if not vehicle:
        flash('Vehículo no encontrado', 'error')
        return redirect(url_for('vehicles.list_vehicles'))
    
    # Get vehicle history
    history = VehicleHistoryService.get_vehicle_history(vehicle_id)
    
    return render_template('vehicles/detail.html', 
                         vehicle=vehicle, 
                         history=history,
                         history_by_type={
                             'all': history,
                             'assignments': [h for h in history if h['type'] == 'assignment'],
                             'maintenance': [h for h in history if h['type'] == 'maintenance'],
                             'insurance': [h for h in history if h['type'] == 'insurance'],
                             'inspection': [h for h in history if h['type'] == 'inspection'],
                             'tax': [h for h in history if h['type'] == 'tax'],
                             'fine': [h for h in history if h['type'] == 'fine'],
                             'authorization': [h for h in history if h['type'] == 'authorization']
                         })

@vehicle_bp.route('/new', methods=['GET', 'POST'])
@login_required
@has_permission('vehicle:create')
@audit_operation('CREATE', 'vehicle')
def create_vehicle():
    """Create new vehicle"""
    if request.method == 'POST':
        try:
            # Capture old state (none for creation)
            old_values = None

            vehicle = VehicleService.create_vehicle(
                license_plate=request.form.get('license_plate'),
                make=request.form.get('make'),
                model=request.form.get('model'),
                year=int(request.form.get('year')),
                vehicle_type=VehicleType(request.form.get('vehicle_type')),
                ownership_type=OwnershipType(request.form.get('ownership_type')),
                color=request.form.get('color'),
                vin=request.form.get('vin'),
                fuel_type=request.form.get('fuel_type'),
                fuel_capacity=int(request.form.get('fuel_capacity')) if request.form.get('fuel_capacity') else None,
                notes=request.form.get('notes')
            )

            # Log successful creation with details
            SecurityAudit.log_data_operation(
                operation='CREATE',
                resource_type='vehicle',
                resource_id=str(vehicle.id),
                new_values={
                    'license_plate': vehicle.license_plate,
                    'make': vehicle.make,
                    'model': vehicle.model,
                    'year': vehicle.year,
                    'vehicle_type': vehicle.vehicle_type.value,
                    'ownership_type': vehicle.ownership_type.value,
                    'color': vehicle.color,
                    'vin': vehicle.vin,
                    'fuel_type': vehicle.fuel_type,
                    'fuel_capacity': vehicle.fuel_capacity,
                    'status': vehicle.status.value
                },
                details={
                    'created_by_user': current_user.username,
                    'user_role': current_user.role.value,
                    'form_data': dict(request.form)
                }
            )

            flash(f'Vehículo {vehicle.license_plate} creado exitosamente', 'success')
            return redirect(url_for('vehicles.view_vehicle', vehicle_id=vehicle.id))
        except Exception as e:
            # Log failed creation
            SecurityAudit.log_data_operation(
                operation='CREATE',
                resource_type='vehicle',
                resource_id='failed',
                details={
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'form_data': dict(request.form),
                    'created_by_user': current_user.username if current_user.is_authenticated else 'unknown'
                }
            )
            err_id = log_exception(e, __name__)
            flash(f'Error al crear vehículo (id={err_id})', 'error')

    return render_template('vehicles/form.html',
                         vehicle_types=VehicleType,
                         ownership_types=OwnershipType)

@vehicle_bp.route('/<int:vehicle_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):
    """Edit vehicle"""
    vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
    if not vehicle:
        flash('Vehículo no encontrado', 'error')
        return redirect(url_for('vehicles.list_vehicles'))
    
    if request.method == 'POST':
        try:
            update_data = {
                'make': request.form.get('make'),
                'model': request.form.get('model'),
                'year': int(request.form.get('year')),
                'color': request.form.get('color'),
                'vin': request.form.get('vin'),
                'vehicle_type': VehicleType(request.form.get('vehicle_type')),
                'ownership_type': OwnershipType(request.form.get('ownership_type')),
                'fuel_type': request.form.get('fuel_type'),
                'notes': request.form.get('notes')
            }
            
            if request.form.get('fuel_capacity'):
                update_data['fuel_capacity'] = int(request.form.get('fuel_capacity'))
            
            VehicleService.update_vehicle(vehicle_id, **update_data)
            flash('Vehículo actualizado exitosamente', 'success')
            return redirect(url_for('vehicles.view_vehicle', vehicle_id=vehicle_id))
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al actualizar vehículo (id={err_id})', 'error')
    
    return render_template('vehicles/form.html', 
                         vehicle=vehicle,
                         vehicle_types=VehicleType,
                         ownership_types=OwnershipType)

@vehicle_bp.route('/<int:vehicle_id>/delete', methods=['POST'])
@login_required
@has_permission('vehicle:delete')
@audit_operation('DELETE', 'vehicle')
def delete_vehicle(vehicle_id):
    """Delete vehicle"""
    # Get vehicle details before deletion for logging
    vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
    old_values = None

    if vehicle:
        old_values = {
            'id': vehicle.id,
            'license_plate': vehicle.license_plate,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'vehicle_type': vehicle.vehicle_type.value,
            'ownership_type': vehicle.ownership_type.value,
            'status': vehicle.status.value,
            'color': vehicle.color,
            'vin': vehicle.vin
        }

    success = VehicleService.delete_vehicle(vehicle_id)

    if success:
        # Log successful deletion
        SecurityAudit.log_data_operation(
            operation='DELETE',
            resource_type='vehicle',
            resource_id=str(vehicle_id),
            old_values=old_values,
            details={
                'deleted_by_user': current_user.username,
                'user_role': current_user.role.value,
                'vehicle_info': old_values
            }
        )
        flash('Vehículo eliminado exitosamente', 'success')
    else:
        # Log failed deletion
        SecurityAudit.log_data_operation(
            operation='DELETE',
            resource_type='vehicle',
            resource_id=str(vehicle_id),
            details={
                'error': 'Vehicle not found or deletion failed',
                'attempted_by_user': current_user.username,
                'user_role': current_user.role.value
            }
        )
        flash('Error al eliminar vehículo', 'error')

    return redirect(url_for('vehicles.list_vehicles'))

@vehicle_bp.route('/<int:vehicle_id>/status', methods=['POST'])
@login_required
@has_permission('vehicle:edit')
@audit_operation('UPDATE', 'vehicle_status')
def update_status(vehicle_id):
    """Update vehicle status"""
    try:
        # Get current vehicle state
        vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
        old_status = vehicle.status.value if vehicle else None

        status = VehicleStatus(request.form.get('status'))
        vehicle = VehicleService.update_vehicle_status(vehicle_id, status)

        if vehicle:
            # Log successful status update
            SecurityAudit.log_data_operation(
                operation='UPDATE',
                resource_type='vehicle',
                resource_id=str(vehicle_id),
                old_values={'status': old_status},
                new_values={'status': status.value},
                details={
                    'updated_by_user': current_user.username,
                    'user_role': current_user.role.value,
                    'status_change': f'{old_status} -> {status.value}',
                    'vehicle_info': {
                        'license_plate': vehicle.license_plate,
                        'make': vehicle.make,
                        'model': vehicle.model
                    }
                }
            )
            flash(f'Estado del vehículo actualizado a {status.value}', 'success')
        else:
            SecurityAudit.log_data_operation(
                operation='UPDATE',
                resource_type='vehicle',
                resource_id=str(vehicle_id),
                details={
                    'error': 'Vehicle not found',
                    'attempted_status': status.value,
                    'attempted_by_user': current_user.username
                }
            )
            flash('Vehículo no encontrado', 'error')
    except Exception as e:
        SecurityAudit.log_data_operation(
            operation='UPDATE',
            resource_type='vehicle',
            resource_id=str(vehicle_id),
            details={
                'error': str(e),
                'error_type': type(e).__name__,
                'attempted_status': request.form.get('status'),
                'attempted_by_user': current_user.username
            }
        )
        err_id = log_exception(e, __name__)
        flash(f'Error al actualizar estado (id={err_id})', 'error')

    return redirect(url_for('vehicles.view_vehicle', vehicle_id=vehicle_id))

@vehicle_bp.route('/search')
@login_required
def search_vehicles():
    """Search vehicles"""
    search_term = request.args.get('q', '')
    if search_term:
        vehicles = VehicleService.search_vehicles(search_term)
    else:
        vehicles = VehicleService.get_all_vehicles()

    # reuse pagination for search results as well
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 10))
    except ValueError:
        per_page = 10

    preserved_args = {k: v for k, v in request.args.items() if k != 'page'}
    base_list_url = url_for('vehicles.search_vehicles')
    preserved_qs = urlencode(preserved_args) if preserved_args else ''

    vehicles_page, pagination = paginate_list(vehicles, page=page, per_page=per_page)
    return render_template('vehicles/list.html', vehicles=vehicles_page, search_term=search_term, pagination=pagination, base_list_url=base_list_url, preserved_qs=preserved_qs)
