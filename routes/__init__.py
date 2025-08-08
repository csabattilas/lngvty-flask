# Import all routes to make them available when importing the routes package
from routes.webhook_routes import webhook_bp
from routes.file_routes import file_bp
from routes.report_routes import report_bp

# List of all blueprints to register with the Flask app
blueprints = [webhook_bp, file_bp, report_bp]
