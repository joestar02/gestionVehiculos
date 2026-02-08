"""Provider controller"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.provider_service import ProviderService
from app.utils.organization_access import organization_protect
from app.models.provider import Provider
from app.services.organization_service import OrganizationService
from app.models.provider import ProviderType
from app.models.user import UserRole
from app.utils.error_helpers import log_exception
from urllib.parse import urlencode
from app.utils.pagination import paginate_list
from app.core.permissions import has_role, has_permission

provider_bp = Blueprint('providers', __name__)

@provider_bp.route('/')
@login_required
@has_role(UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER)
def list_providers():
    """List all providers"""
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 10))
    except ValueError:
        per_page = 10

    preserved_args = {k: v for k, v in request.args.items() if k != 'page'}
    base_list_url = url_for('providers.list_providers')
    preserved_qs = urlencode(preserved_args) if preserved_args else ''

    # Get user's organization unit
    organization_unit_id = None
    if current_user.driver and current_user.driver.organization_unit_id:
        organization_unit_id = current_user.driver.organization_unit_id

    all_providers = ProviderService.get_all_providers(organization_unit_id=organization_unit_id)
    providers, pagination = paginate_list(all_providers, page=page, per_page=per_page)
    return render_template('providers/list.html', providers=providers, pagination=pagination, base_list_url=base_list_url, preserved_qs=preserved_qs)

@provider_bp.route('/<int:provider_id>')
@login_required
@has_role(UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER)
@organization_protect(model=Provider, id_arg='provider_id')
def view_provider(provider_id):
    """View provider details"""
    provider = ProviderService.get_provider_by_id(provider_id)
    if not provider:
        flash('Proveedor no encontrado', 'error')
        return redirect(url_for('providers.list_providers'))

    return render_template('providers/detail.html', provider=provider)

@provider_bp.route('/new', methods=['GET', 'POST'])
@login_required
@has_role(UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER)
def create_provider():
    """Create new provider"""
    if request.method == 'POST':
        try:
            # Get user's organization unit
            organization_unit_id = None
            if current_user.driver and current_user.driver.organization_unit_id:
                organization_unit_id = current_user.driver.organization_unit_id
            
            # Allow override from form if user has permission
            form_org_id = request.form.get('organization_unit_id')
            if form_org_id:
                organization_unit_id = int(form_org_id)

            provider = ProviderService.create_provider(
                name=request.form.get('name'),
                provider_type=ProviderType(request.form.get('provider_type')),
                contact_person=request.form.get('contact_person'),
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                address=request.form.get('address'),
                website=request.form.get('website'),
                notes=request.form.get('notes'),
                organization_unit_id=organization_unit_id
            )
            flash(f'Proveedor {provider.name} creado exitosamente', 'success')
            return redirect(url_for('providers.view_provider', provider_id=provider.id))
        except ValueError as e:
            flash(str(e), 'warning')
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al crear proveedor (id={err_id})', 'error')

    organizations = OrganizationService.get_all_organizations()
    return render_template('providers/form.html', provider_types=ProviderType, organizations=organizations)

@provider_bp.route('/<int:provider_id>/edit', methods=['GET', 'POST'])
@login_required
@has_role(UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER)
@organization_protect(model=Provider, id_arg='provider_id')
def edit_provider(provider_id):
    """Edit provider"""
    provider = ProviderService.get_provider_by_id(provider_id)
    if not provider:
        flash('Proveedor no encontrado', 'error')
        return redirect(url_for('providers.list_providers'))

    if request.method == 'POST':
        try:
            update_data = {
                'name': request.form.get('name'),
                'provider_type': ProviderType(request.form.get('provider_type')),
                'contact_person': request.form.get('contact_person'),
                'phone': request.form.get('phone'),
                'email': request.form.get('email'),
                'address': request.form.get('address'),
                'website': request.form.get('website'),
                'notes': request.form.get('notes')
            }
            
            # Handle organization_unit_id if provided
            form_org_id = request.form.get('organization_unit_id')
            if form_org_id:
                update_data['organization_unit_id'] = int(form_org_id)
            
            ProviderService.update_provider(provider_id, **update_data)
            flash('Proveedor actualizado exitosamente', 'success')
            return redirect(url_for('providers.view_provider', provider_id=provider_id))
        except ValueError as e:
            flash(str(e), 'warning')
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al actualizar proveedor (id={err_id})', 'error')

    organizations = OrganizationService.get_all_organizations()
    return render_template('providers/edit.html', provider=provider, provider_types=ProviderType, organizations=organizations)

    return render_template('providers/form.html',
                         provider=provider,
                         provider_types=ProviderType)

@provider_bp.route('/<int:provider_id>/delete', methods=['POST'])
@login_required
@has_role(UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER)
@organization_protect(model=Provider, id_arg='provider_id')
def delete_provider(provider_id):
    """Delete provider"""
    try:
        ProviderService.delete_provider(provider_id)
        flash('Proveedor eliminado exitosamente', 'success')
    except Exception as e:
        err_id = log_exception(e, __name__)
        flash(f'Error al eliminar proveedor (id={err_id})', 'error')

    return redirect(url_for('providers.list_providers'))
