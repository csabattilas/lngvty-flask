from flask import Blueprint, request, jsonify, send_file
import os
from controllers.webhook_controller import WebhookController

# Create blueprint
webhook_bp = Blueprint('webhook', __name__, url_prefix='/api')

# Store reference to controller
webhook_controller = None

def init_routes(storage_path, processing_service, email_service):
    """Initialize routes with required dependencies"""
    global webhook_controller
    webhook_controller = WebhookController(storage_path, processing_service, email_service)

@webhook_bp.route('/webhook', methods=['POST'])
def receive_webhook():
    """Receive webhook data, save to file, and process"""
    try:
        # Get JSON payload
        payload = request.json
        
        # Delegate to controller
        result = webhook_controller.process_webhook(payload)
        
        # Check if result includes status code
        if isinstance(result, tuple) and len(result) == 2:
            return jsonify(result[0]), result[1]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to process webhook',
            'details': str(e)
        }), 500

@webhook_bp.route('/webhook-to-pdf', methods=['POST'])
def receive_webhook_and_generate_pdf():
    """Receive webhook data, save to file, process, and return PDF directly"""
    try:
        # Get JSON payload
        payload = request.json
        
        # Delegate to controller for processing with PDF generation
        result = webhook_controller.process_webhook_to_pdf(payload)
        
        # Check if result is a tuple (error with status code)
        if isinstance(result, tuple) and len(result) == 2:
            return jsonify(result[0]), result[1]
        
        # If result contains a PDF path, serve the file
        if isinstance(result, dict) and 'pdf_path' in result and os.path.exists(result['pdf_path']):
            return send_file(result['pdf_path'], mimetype='application/pdf', as_attachment=True,
                           download_name=os.path.basename(result['pdf_path']))
        
        # Otherwise return as JSON
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to process webhook and generate PDF',
            'details': str(e)
        }), 500

@webhook_bp.route('/webhook-to-email', methods=['POST'])
def receive_webhook_and_send_email():
    """Receive webhook data, save to file, process, and send PDF via email"""
    try:
        # Get JSON payload
        payload = request.json
        
        # Get email parameters from request (optional now)
        to_email = request.args.get('email')
            
        # Delegate to controller for processing with email sending
        # The controller will extract email from payload if not provided
        result = webhook_controller.process_webhook_and_email(payload, to_email)
        
        # Return result as JSON
        if isinstance(result, tuple) and len(result) == 2:
            return jsonify(result[0]), result[1]
            
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to process webhook and send email',
            'details': str(e)
        }), 500
