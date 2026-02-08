from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user
from app.models.user import UserRole


def _current_user_org_id():
    # Try to get organization from user, fall back to driver.profile if present
    org = getattr(current_user, 'organization_unit_id', None)
    if org:
        return org
    driver = getattr(current_user, 'driver', None)
    if driver:
        return getattr(driver, 'organization_unit_id', None)
    return None


def organization_protect(model=None, id_arg='id', loader=None):
    """Decorator to ensure the current_user may access a resource by organization.

    - If `loader` is provided it will be called with the resource id and must return
      the resource instance (or None).
    - Otherwise `model` must be a SQLAlchemy model and the instance will be
      loaded via `model.query.get(id)`.

    The decorator checks for `instance.organization_unit_id`. If missing, it will
    try to inspect related attributes (vehicle, driver, provider) to find an
    organization_unit_id. Admin users bypass the check.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Admins bypass organization checks
            try:
                if getattr(current_user, 'role', None) == UserRole.ADMIN:
                    return f(*args, **kwargs)
            except Exception:
                pass

            rid = kwargs.get(id_arg)
            if rid is None:
                flash('Acceso denegado: recurso inválido', 'error')
                return redirect(request.referrer or url_for('main.index'))

            instance = None
            try:
                if loader:
                    instance = loader(rid)
                elif model:
                    instance = model.query.get(rid)
            except Exception:
                instance = None

            if not instance:
                flash('Recurso no encontrado', 'error')
                return redirect(request.referrer or url_for('main.index'))

            # Try to obtain organization id from instance
            resource_org = getattr(instance, 'organization_unit_id', None)
            if resource_org is None:
                # Try common related attributes
                for rel in ('vehicle', 'driver', 'provider', 'organization', 'organization_unit'):
                    related = getattr(instance, rel, None)
                    if related is not None:
                        resource_org = getattr(related, 'organization_unit_id', None) or getattr(related, 'organization_unit_id', None) or getattr(related, 'organization_unit', None)
                        # If related is an organization object, break with its id if available
                        if hasattr(resource_org, 'id'):
                            resource_org = resource_org.id
                        if resource_org is not None:
                            break

            user_org = _current_user_org_id()

            if user_org is None:
                # User without organization cannot access org-scoped resources
                flash('Acceso denegado: no estás asignado a una unidad organizativa', 'error')
                return redirect(request.referrer or url_for('main.index'))

            if resource_org is None:
                # Unable to determine resource org — deny by default
                flash('Acceso denegado: recurso sin unidad organizativa', 'error')
                return redirect(request.referrer or url_for('main.index'))

            if int(resource_org) != int(user_org):
                flash('Acceso denegado: recurso fuera de tu unidad organizativa', 'error')
                return redirect(request.referrer or url_for('main.index'))

            return f(*args, **kwargs)
        return wrapped
    return decorator
