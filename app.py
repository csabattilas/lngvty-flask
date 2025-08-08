from flask import Flask, jsonify, send_from_directory
import os
from services.health_score_service import HealthScoreService
from services.health_score_orchestration_service import HealthScoreOrchestrationService
from services.chart_generation_service import ChartGenerationService
from services.pdf_report_service import PdfReportService
from services.json_processing_service import JsonProcessingService
from services.email_service import EmailService
from routes import blueprints
from routes.webhook_routes import init_routes as init_webhook_routes
from routes.file_routes import init_routes as init_file_routes
from routes.report_routes import init_routes as init_report_routes

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, static_folder='static')
    
    # Configuration
    JSON_STORAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'JsonData')
    PDF_STORAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'PdfData')
    
    # Ensure directories exist
    os.makedirs(JSON_STORAGE_PATH, exist_ok=True)
    os.makedirs(PDF_STORAGE_PATH, exist_ok=True)
    
    # Initialize services
    health_score_service = HealthScoreService()
    chart_service = ChartGenerationService()
    pdf_service = PdfReportService()
    email_service = EmailService()
    orchestration_service = HealthScoreOrchestrationService(chart_service, pdf_service)
    json_processing_service = JsonProcessingService(health_score_service, orchestration_service)
    
    # Store services in app config for access from routes
    app.config['email_service'] = email_service
    
    # Initialize route dependencies
    init_webhook_routes(JSON_STORAGE_PATH, json_processing_service, email_service)
    init_file_routes(JSON_STORAGE_PATH, json_processing_service, email_service)
    init_report_routes(PDF_STORAGE_PATH)
    
    # Register blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
        
    @app.route('/health')
    def health():
        return 'Health Score API is running!'
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
