"""Provider controller"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.provider_service import ProviderService
from app.models.provider import ProviderType
from app.models.user import UserRole
from app.utils.error_helpers import log_exception

provider_bp = Blueprint('providers', __name__)

@provider_bp.route('/')
@login_required
def list_providers():
    """List all providers"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    providers = ProviderService.get_all_providers()
    return render_template('providers/list.html', providers=providers)

@provider_bp.route('/<int:provider_id>')
@login_required
def view_provider(provider_id):
    """View provider details"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    provider = ProviderService.get_provider_by_id(provider_id)
    if not provider:
        flash('Proveedor no encontrado', 'error')
        return redirect(url_for('providers.list_providers'))

    return render_template('providers/detail.html', provider=provider)

@provider_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_provider():
    """Create new provider"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            provider = ProviderService.create_provider(
                name=request.form.get('name'),
                provider_type=ProviderType(request.form.get('provider_type')),
                contact_person=request.form.get('contact_person'),
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                address=request.form.get('address'),
                website=request.form.get('website'),
                notes=request.form.get('notes')
            )
            flash(f'Proveedor {provider.name} creado exitosamente', 'success')
            return redirect(url_for('providers.view_provider', provider_id=provider.id))
        except ValueError as e:
            flash(str(e), 'warning')
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al crear proveedor (id={err_id})', 'error')

    return render_template('providers/form.html', provider_types=ProviderType)

@provider_bp.route('/<int:provider_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_provider(provider_id):
    """Edit provider"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    provider = ProviderService.get_provider_by_id(provider_id)
    if not provider:
        flash('Proveedor no encontrado', 'error')
        return redirect(url_for('providers.list_providers'))

    if request.method == 'POST':
        try:
            ProviderService.update_provider(
                provider_id,
                name=request.form.get('name'),
                provider_type=ProviderType(request.form.get('provider_type')),
                contact_person=request.form.get('contact_person'),
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                address=request.form.get('address'),
                website=request.form.get('website'),
                notes=request.form.get('notes')
            )
            flash('Proveedor actualizado exitosamente', 'success')
            return redirect(url_for('providers.view_provider', provider_id=provider_id))
        except ValueError as e:
            flash(str(e), 'warning')
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al actualizar proveedor (id={err_id})', 'error')

    return render_template('providers/form.html',
                         provider=provider,
                         provider_types=ProviderType)

@provider_bp.route('/<int:provider_id>/delete', methods=['POST'])
@login_required
def delete_provider(provider_id):
    """Delete provider"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    try:
        ProviderService.delete_provider(provider_id)
        flash('Proveedor eliminado exitosamente', 'success')
    except Exception as e:
        err_id = log_exception(e, __name__)
        flash(f'Error al eliminar proveedor (id={err_id})', 'error')

    return redirect(url_for('providers.list_providers'))
