"""Application entry point"""
from app.main import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Use environment variables for configuration in production
    host = os.environ.get('HOST', '0.0.0.0')  
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'

    app.run(host=host, port=port, debug=debug)
