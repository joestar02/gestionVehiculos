"""Database session configuration for Flask-SQLAlchemy
This file is kept for backward compatibility but Flask-SQLAlchemy
handles the session management through the db extension.
"""
from app.extensions import db

# For backward compatibility
SessionLocal = db.session

def get_db():
    """Get database session - for compatibility with existing code"""
    return db.session
