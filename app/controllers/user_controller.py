"""User management controller"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.auth_service import AuthService
from app.services.organization_service import OrganizationService
from app.models.user import User, UserRole
from app.extensions import db
from app.utils.error_helpers import log_exception
from app.core.permissions import has_role, has_permission
from urllib.parse import urlencode
from app.utils.pagination import paginate_list

user_bp = Blueprint('users', __name__)

@user_bp.route('/')
@login_required
@has_role(UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER, UserRole.DRIVER, UserRole.VIEWER)
def list_users():
    """List all users - Admin only"""
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 10))
    except ValueError:
        per_page = 10

    preserved_args = {k: v for k, v in request.args.items() if k != 'page'}
    base_list_url = url_for('users.list_users')
    preserved_qs = urlencode(preserved_args) if preserved_args else ''

    # Get users: admins see all, others only see users of their organization unit
    if current_user.role == UserRole.ADMIN:
        all_users = User.query.filter_by(is_active=True).order_by(User.created_at.desc()).all()
    else:
        org_id = getattr(current_user, 'organization_unit_id', None)
        if org_id is None:
            # If user not associated to an org, show only themselves
            all_users = User.query.filter_by(id=current_user.id).all()
        else:
            all_users = User.query.filter_by(is_active=True, organization_unit_id=org_id).order_by(User.created_at.desc()).all()
    users, pagination = paginate_list(all_users, page=page, per_page=per_page)
    
    return render_template('users/list.html', users=users, pagination=pagination, 
                         base_list_url=base_list_url, preserved_qs=preserved_qs)

@user_bp.route('/<int:user_id>')
@login_required
@has_role(UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER, UserRole.DRIVER, UserRole.VIEWER)
def view_user(user_id):
    """View user details - Admin only"""
    user = User.query.get(user_id)
    if not user:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('users.list_users'))

    # Non-admins can only view users in their own organization
    if current_user.role != UserRole.ADMIN:
        org_id = getattr(current_user, 'organization_unit_id', None)
        if org_id is None or user.organization_unit_id != org_id:
            flash('Acceso denegado: solo puedes ver usuarios de tu unidad organizativa', 'error')
            return redirect(url_for('users.list_users'))

    return render_template('users/detail.html', user=user)

@user_bp.route('/new', methods=['GET', 'POST'])
@login_required
@has_role(UserRole.ADMIN)
def create_user():
    """Create new user - Admin only"""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            password = request.form.get('password', '')
            password_confirm = request.form.get('password_confirm', '')
            role = request.form.get('role', UserRole.VIEWER.value)
            organization_unit_id = request.form.get('organization_unit_id')

            # Validations
            if not username or len(username) < 3:
                flash('El nombre de usuario debe tener al menos 3 caracteres', 'warning')
                return redirect(url_for('users.create_user'))

            if not email or '@' not in email:
                flash('Email válido es requerido', 'warning')
                return redirect(url_for('users.create_user'))

            if not password or len(password) < 6:
                flash('La contraseña debe tener al menos 6 caracteres', 'warning')
                return redirect(url_for('users.create_user'))

            if password != password_confirm:
                flash('Las contraseñas no coinciden', 'warning')
                return redirect(url_for('users.create_user'))

            # Check if user already exists
            if User.query.filter_by(username=username).first():
                flash('El nombre de usuario ya existe', 'warning')
                return redirect(url_for('users.create_user'))

            if User.query.filter_by(email=email).first():
                flash('El email ya existe', 'warning')
                return redirect(url_for('users.create_user'))

            # Validate role
            try:
                role_enum = UserRole(role)
            except ValueError:
                flash('Rol inválido', 'warning')
                return redirect(url_for('users.create_user'))

            # Validate organization unit if provided
            org_unit_id = None
            if organization_unit_id:
                try:
                    org_unit_id = int(organization_unit_id)
                    from app.models.organization import OrganizationUnit
                    if not OrganizationUnit.query.get(org_unit_id):
                        flash('Unidad de organización inválida', 'warning')
                        return redirect(url_for('users.create_user'))
                except (ValueError, TypeError):
                    flash('Unidad de organización inválida', 'warning')
                    return redirect(url_for('users.create_user'))

            # Create user
            new_user = AuthService.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role_enum,
                organization_unit_id=org_unit_id
            )

            flash(f'Usuario {username} creado exitosamente', 'success')
            return redirect(url_for('users.view_user', user_id=new_user.id))

        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al crear usuario (id={err_id})', 'error')
            return redirect(url_for('users.create_user'))

    organizations = OrganizationService.get_organizations_with_levels()
    return render_template('users/form.html', user_roles=UserRole, organizations=organizations)

@user_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@has_role(UserRole.ADMIN)
def edit_user(user_id):
    """Edit user - Admin only"""
    user = User.query.get(user_id)
    if not user:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('users.list_users'))

    if request.method == 'POST':
        try:
            # Update basic info
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            role = request.form.get('role', UserRole.VIEWER.value)
            email = request.form.get('email', '').strip()

            # Validate email
            if not email or '@' not in email:
                flash('Email válido es requerido', 'warning')
                return redirect(url_for('users.edit_user', user_id=user_id))

            # Check if email is already used by another user
            existing_email = User.query.filter(
                User.email == email,
                User.id != user_id
            ).first()
            if existing_email:
                flash('El email ya existe', 'warning')
                return redirect(url_for('users.edit_user', user_id=user_id))

            # Validate role
            try:
                role_enum = UserRole(role)
            except ValueError:
                flash('Rol inválido', 'warning')
                return redirect(url_for('users.edit_user', user_id=user_id))

            # Update user
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.role = role_enum

            # Handle password change if provided
            password = request.form.get('password', '').strip()
            if password:
                if len(password) < 6:
                    flash('La contraseña debe tener al menos 6 caracteres', 'warning')
                    return redirect(url_for('users.edit_user', user_id=user_id))

                password_confirm = request.form.get('password_confirm', '').strip()
                if password != password_confirm:
                    flash('Las contraseñas no coinciden', 'warning')
                    return redirect(url_for('users.edit_user', user_id=user_id))

                from app.extensions import bcrypt
                user.hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            db.session.commit()
            flash(f'Usuario {user.username} actualizado exitosamente', 'success')
            return redirect(url_for('users.view_user', user_id=user_id))

        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al actualizar usuario (id={err_id})', 'error')
            return redirect(url_for('users.edit_user', user_id=user_id))

    organizations = OrganizationService.get_organizations_with_levels()
    return render_template('users/form.html', user=user, user_roles=UserRole, organizations=organizations)
    

@user_bp.route('/<int:user_id>/deactivate', methods=['POST'])
@login_required
@has_role(UserRole.ADMIN)
def deactivate_user(user_id):
    """Deactivate user (soft delete) - Admin only"""
    user = User.query.get(user_id)
    if not user:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('users.list_users'))

    if user.id == current_user.id:
        flash('No puedes desactivar tu propia cuenta', 'warning')
        return redirect(url_for('users.view_user', user_id=user_id))

    try:
        user.is_active = False
        db.session.commit()
        flash(f'Usuario {user.username} desactivado', 'success')
    except Exception as e:
        err_id = log_exception(e, __name__)
        flash(f'Error al desactivar usuario (id={err_id})', 'error')

    return redirect(url_for('users.list_users'))

@user_bp.route('/<int:user_id>/activate', methods=['POST'])
@login_required
@has_role(UserRole.ADMIN)
def activate_user(user_id):
    """Activate user - Admin only"""
    user = User.query.get(user_id)
    if not user:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('users.list_users'))

    try:
        user.is_active = True
        db.session.commit()
        flash(f'Usuario {user.username} activado', 'success')
    except Exception as e:
        err_id = log_exception(e, __name__)
        flash(f'Error al activar usuario (id={err_id})', 'error')

    return redirect(url_for('users.list_users'))
