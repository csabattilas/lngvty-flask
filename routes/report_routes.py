import os
from flask import Blueprint, request, jsonify, send_file
from controllers.report_controller import ReportController

# Create blueprint
report_bp = Blueprint('report', __name__, url_prefix='/api')

# Store reference to controller
report_controller = None

def init_routes(pdf_storage_path):
    """Initialize routes with required dependencies"""
    global report_controller
    report_controller = ReportController(pdf_storage_path)

@report_bp.route('/download-pdf', methods=['GET'])
def download_pdf():
    """Download PDF report"""
    try:
        path = request.args.get('path', '')
        
        # Delegate to controller
        result = report_controller.download_pdf(path)
        
        # Check if result includes status code
        if isinstance(result, tuple) and len(result) == 2:
            return jsonify(result[0]), result[1]
        
        # If result is a path string, serve the file
        if isinstance(result, str) and os.path.exists(result):
            return send_file(result, mimetype='application/pdf', as_attachment=True, 
                           download_name=os.path.basename(result))
            
        # Otherwise return as JSON
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to download PDF',
            'details': str(e)
        }), 500

@report_bp.route('/view-chart', methods=['GET'])
def view_chart():
    """View chart"""
    try:
        path = request.args.get('path', '')
        
        # Delegate to controller
        result = report_controller.view_chart(path)
        
        # Check if result is a tuple (error with status code)
        if isinstance(result, tuple) and len(result) == 2:
            return jsonify(result[0]), result[1]
        
        # If result is a path string, serve the file
        if isinstance(result, str) and os.path.exists(result):
            return send_file(result, mimetype='image/png')
            
        # Otherwise return as JSON
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to view chart',
            'details': str(e)
        }), 500
