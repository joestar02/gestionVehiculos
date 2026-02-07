"""Database logging and audit system"""
import logging
import time
import json
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask import g, has_request_context
from app.services.security_audit_service import SecurityAudit
from app.extensions import db

# Configure database logger
db_logger = logging.getLogger('database')
db_logger.setLevel(logging.INFO)

# File handler for database logs
db_handler = logging.FileHandler('database.log')
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - [%(user_id)s] %(username)s@%(ip_address)s - %(operation)s - %(table)s - %(details)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
db_handler.setFormatter(formatter)
db_logger.addHandler(db_handler)

# Console handler for development (only warnings and errors)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.WARNING)
db_logger.addHandler(console_handler)

class DatabaseAudit:
    """Database auditing and logging system"""

    _enabled = True
    _tracked_tables = set()
    _query_log = []

    @staticmethod
    def enable():
        """Enable database logging"""
        DatabaseAudit._enabled = True

    @staticmethod
    def disable():
        """Disable database logging"""
        DatabaseAudit._enabled = False

    @staticmethod
    def add_tracked_table(table_name):
        """Add a table to track for detailed auditing"""
        DatabaseAudit._tracked_tables.add(table_name.lower())

    @staticmethod
    def _get_request_context():
        """Get current request context if available"""
        if has_request_context():
            from flask_login import current_user
            return {
                'user_id': getattr(current_user, 'id', 'system') if current_user and current_user.is_authenticated else 'anonymous',
                'username': getattr(current_user, 'username', 'system') if current_user and current_user.is_authenticated else 'anonymous',
                'user_role': getattr(current_user, 'role', None).value if current_user and current_user.is_authenticated and current_user.role else 'none',
                'ip_address': getattr(g, 'ip_address', 'unknown') if hasattr(g, 'ip_address') else 'unknown',
                'session_id': getattr(g, 'session_id', 'unknown') if hasattr(g, 'session_id') else 'unknown'
            }
        return {
            'user_id': 'system',
            'username': 'system',
            'user_role': 'system',
            'ip_address': 'localhost',
            'session_id': 'background'
        }

    @staticmethod
    def _log_database_operation(operation, table, details, execution_time=None):
        """Log a database operation"""
        if not DatabaseAudit._enabled:
            return

        context = DatabaseAudit._get_request_context()

        log_data = {**context}
        log_data['operation'] = operation
        log_data['table'] = table
        log_data['details'] = json.dumps(details, default=str, ensure_ascii=False)

        if execution_time:
            log_data['execution_time_ms'] = round(execution_time * 1000, 2)

        message = f"{operation.upper()} - {table}"

        if operation in ['INSERT', 'UPDATE', 'DELETE'] and details:
            if 'record_id' in details:
                message += f" (ID: {details['record_id']})"
            elif 'affected_rows' in details:
                message += f" ({details['affected_rows']} filas)"

        db_logger.info(message, extra=log_data)

    @staticmethod
    def log_query(query, parameters=None, execution_time=None):
        """Log a SQL query execution"""
        if not DatabaseAudit._enabled:
            return

        # Only log slow queries or complex operations
        if execution_time and execution_time > 0.1:  # More than 100ms
            details = {
                'query': str(query).strip(),
                'parameters': parameters,
                'execution_time': execution_time
            }
            DatabaseAudit._log_database_operation('QUERY', 'system', details, execution_time)

    @staticmethod
    def log_transaction_start():
        """Log transaction start"""
        if not DatabaseAudit._enabled:
            return

        context = DatabaseAudit._get_request_context()
        db_logger.debug("TRANSACTION_START", extra={
            **context,
            'operation': 'TRANSACTION_START',
            'table': 'system',
            'details': json.dumps({'action': 'begin'})
        })

    @staticmethod
    def log_transaction_commit(changes=None):
        """Log transaction commit with changes"""
        if not DatabaseAudit._enabled:
            return

        details = {'action': 'commit'}
        if changes:
            details['changes'] = changes

        context = DatabaseAudit._get_request_context()
        db_logger.info("TRANSACTION_COMMIT", extra={
            **context,
            'operation': 'TRANSACTION_COMMIT',
            'table': 'system',
            'details': json.dumps(details)
        })

    @staticmethod
    def log_transaction_rollback(reason=None):
        """Log transaction rollback"""
        if not DatabaseAudit._enabled:
            return

        details = {'action': 'rollback'}
        if reason:
            details['reason'] = str(reason)

        context = DatabaseAudit._get_request_context()
        db_logger.warning("TRANSACTION_ROLLBACK", extra={
            **context,
            'operation': 'TRANSACTION_ROLLBACK',
            'table': 'system',
            'details': json.dumps(details)
        })

# SQLAlchemy Event Listeners

@event.listens_for(Engine, "before_execute")
def before_execute(conn, clauseelement, multiparams, params):
    """Log before query execution"""
    if not DatabaseAudit._enabled:
        return

    # Store start time for performance monitoring
    conn._query_start_time = time.time()

@event.listens_for(Engine, "after_execute")
def after_execute(conn, clauseelement, multiparams, params, result):
    """Log after query execution"""
    if not DatabaseAudit._enabled:
        return

    execution_time = time.time() - getattr(conn, '_query_start_time', time.time())

    # Extract table name from query
    table_name = 'unknown'
    try:
        if hasattr(clauseelement, 'table'):
            table_name = clauseelement.table.name
        elif hasattr(clauseelement, 'froms') and clauseelement.froms:
            table_name = clauseelement.froms[0].name
    except:
        pass

    # Determine operation type
    query_str = str(clauseelement).upper()
    if query_str.startswith('INSERT'):
        operation = 'INSERT'
    elif query_str.startswith('UPDATE'):
        operation = 'UPDATE'
    elif query_str.startswith('DELETE'):
        operation = 'DELETE'
    elif query_str.startswith('SELECT'):
        operation = 'SELECT'
    else:
        operation = 'QUERY'

    # Log detailed operations for tracked tables
    if table_name.lower() in DatabaseAudit._tracked_tables:
        details = {
            'query': str(clauseelement).strip(),
            'parameters': str(params) if params else None,
            'execution_time': execution_time
        }

        # Try to extract record ID for INSERT/UPDATE/DELETE
        if operation in ['INSERT', 'UPDATE', 'DELETE']:
            try:
                if hasattr(clauseelement, 'parameters') and clauseelement.parameters:
                    if 'id' in clauseelement.parameters:
                        details['record_id'] = clauseelement.parameters['id']
            except:
                pass

        DatabaseAudit._log_database_operation(operation, table_name, details, execution_time)
    else:
        # Log slow queries even for non-tracked tables
        DatabaseAudit.log_query(clauseelement, params, execution_time)

@event.listens_for(db.session, "before_commit")
def before_commit(session):
    """Log before transaction commit"""
    if not DatabaseAudit._enabled:
        return

    # Collect information about changes
    changes = {
        'new': len(session.new),
        'dirty': len(session.dirty),
        'deleted': len(session.deleted)
    }

    # Store changes info for after_commit
    session._audit_changes = changes
    DatabaseAudit.log_transaction_start()

@event.listens_for(db.session, "after_commit")
def after_commit(session):
    """Log after transaction commit"""
    if not DatabaseAudit._enabled:
        return

    changes = getattr(session, '_audit_changes', None)
    DatabaseAudit.log_transaction_commit(changes)

@event.listens_for(db.session, "after_rollback")
def after_rollback(session):
    """Log transaction rollback"""
    if not DatabaseAudit._enabled:
        return

    DatabaseAudit.log_transaction_rollback()

@event.listens_for(db.session, "before_flush")
def before_flush(session, flush_context, instances):
    """Log before session flush"""
    if not DatabaseAudit._enabled:
        return

    # This captures the actual changes being made
    changes = {
        'new_objects': [f"{obj.__class__.__name__}: {getattr(obj, 'id', 'new')}" for obj in session.new],
        'dirty_objects': [f"{obj.__class__.__name__}: {getattr(obj, 'id', 'unknown')}" for obj in session.dirty],
        'deleted_objects': [f"{obj.__class__.__name__}: {getattr(obj, 'id', 'unknown')}" for obj in session.deleted]
    }

    if any(changes.values()):  # Only log if there are actual changes
        context = DatabaseAudit._get_request_context()
        db_logger.debug("SESSION_FLUSH", extra={
            **context,
            'operation': 'SESSION_FLUSH',
            'table': 'system',
            'details': json.dumps(changes)
        })

def init_database_logging(app):
    """Initialize database logging for the Flask app"""
    # Configure SQLAlchemy logging level
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)  # Reduce SQLAlchemy noise
    logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)

    # Add tracked tables - these will get detailed logging
    tracked_tables = [
        'user', 'vehicle', 'reservation', 'driver', 'vehicle_assignment',
        'maintenance', 'provider', 'organization', 'permission', 'role_permission'
    ]

    for table in tracked_tables:
        DatabaseAudit.add_tracked_table(table)

    # Store IP address in Flask g for database logging
    @app.before_request
    def store_request_info():
        from flask import request
        g.ip_address = request.remote_addr if request else 'unknown'
        g.session_id = f"{time.time()}_{id(g)}"

    with app.app_context():
        # Test database connection and logging
        try:
            from sqlalchemy import text
            # Use db.session to execute the query
            db.session.execute(text('SELECT 1'))
            db_logger.info("Database logging initialized successfully", extra={
                'user_id': 'system',
                'username': 'system',
                'user_role': 'system',
                'ip_address': 'localhost',
                'operation': 'INIT',
                'table': 'system',
                'details': json.dumps({'message': 'Database audit system initialized'})
            })
        except Exception as e:
            db_logger.error(f"Database logging initialization failed: {e}", extra={
                'user_id': 'system',
                'username': 'system',
                'user_role': 'system',
                'ip_address': 'localhost',
                'operation': 'INIT_ERROR',
                'table': 'system',
                'details': json.dumps({'error': str(e)})
            })