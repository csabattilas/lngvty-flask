from flask import Blueprint, request, jsonify
import os
from controllers.file_controller import FileController

# Create blueprint
file_bp = Blueprint('file', __name__, url_prefix='/api')

# Store reference to controller
file_controller = None
email_service = None

def init_routes(storage_path, processing_service, email_svc=None):
    """Initialize routes with required dependencies"""
    global file_controller, email_service
    file_controller = FileController(storage_path, processing_service)
    email_service = email_svc

@file_bp.route('/files', methods=['GET'])
def get_files():
    """List all JSON files in storage directory"""
    try:
        # Delegate to controller
        result = file_controller.list_files()
        
        # Check if result includes status code
        if isinstance(result, tuple) and len(result) == 2:
            return jsonify(result[0]), result[1]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to list files',
            'details': str(e)
        }), 500

@file_bp.route('/files/<filename>', methods=['GET'])
def get_file_content(filename):
    """Get content of a specific JSON file"""
    try:
        # Delegate to controller
        result = file_controller.get_file_content(filename)
        
        # Check if result includes status code
        if isinstance(result, tuple) and len(result) == 2:
            return jsonify(result[0]), result[1]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to read file',
            'details': str(e)
        }), 500

@file_bp.route('/files/<filename>/process', methods=['POST'])
def process_file(filename):
    """Process a specific JSON file"""
    try:
        # Get output format from request
        data = request.json or {}
        output_format = data.get('outputFormat', 'pdf').lower()
        
        # Delegate to controller
        result = file_controller.process_file(filename, output_format)
        
        # Check if result includes status code
        if isinstance(result, tuple) and len(result) == 2:
            return jsonify(result[0]), result[1]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to process file',
            'details': str(e)
        }), 500

@file_bp.route('/files/<filename>/email', methods=['POST'])
def send_file_email(filename):
    """Send a processed file's PDF report via email"""
    try:
        # Check if email service is available
        if not email_service:
            return jsonify({
                'success': False,
                'error': 'Email service not available',
                'details': 'Email service is not configured in the application'
            }), 500
            
        # First, get the file content to process it
        file_result = file_controller.get_file_content(filename)
        
        # Check if file exists
        if isinstance(file_result, tuple) or not file_result.get('success'):
            return jsonify({
                'success': False,
                'error': 'File not found or could not be read',
                'details': 'The specified file does not exist or could not be read'
            }), 404
            
        # Extract email from the file content
        to_email = None
        if 'content' in file_result and isinstance(file_result['content'], dict):
            # Try to extract email from form_response structure (Typeform format)
            if 'form_response' in file_result['content'] and 'answers' in file_result['content']['form_response']:
                for answer in file_result['content']['form_response']['answers']:
                    if answer.get('type') == 'email' and 'field' in answer and answer['field'].get('ref') == '39f116ed-5403-407a-b506-c9625e9e6b2a':
                        to_email = answer.get('email')
                        break
        
        # Fallback to query parameter if email not found in file
        if not to_email:
            to_email = request.args.get('email')
            
        # Return error if no email found
        if not to_email:
            return jsonify({
                'success': False,
                'error': 'No email address found',
                'details': 'Could not extract email from file and no email provided as query parameter'
            }), 400
            
        # Process the file to get the PDF report
        process_result = file_controller.process_file(filename)
        
        # Check if processing was successful
        if not process_result.get('success') or 'pdfPath' not in process_result:
            return jsonify({
                'success': False,
                'error': 'Failed to process file',
                'details': 'Could not generate PDF report from the file'
            }), 500
            
        # Get PDF path
        pdf_path = process_result.get('pdfPath')
        if not os.path.exists(pdf_path):
            return jsonify({
                'success': False,
                'error': 'PDF file not found',
                'details': f'Generated PDF file not found at path: {pdf_path}'
            }), 500
            
        # Extract user name if available
        user_name = "User"
        if 'content' in file_result and isinstance(file_result['content'], dict):
            # Try to extract user name from various possible JSON structures
            if 'user' in file_result['content'] and 'name' in file_result['content']['user']:
                user_name = file_result['content']['user']['name']
            elif 'form_response' in file_result['content'] and 'definition' in file_result['content']['form_response']:
                user_name = f"User {filename}"
        
        # Get pillar scores and chart path from the process result
        pillar_scores = None
        chart_path = None
        if 'data' in process_result:
            pillar_scores = process_result['data'].get('pillar_scores')
            chart_path = process_result['data'].get('chart_path')
            
            # Convert pillar_scores to dictionary if it's not already
            if pillar_scores and hasattr(pillar_scores, 'to_dict'):
                pillar_scores = pillar_scores.to_dict()
        
        # Generate email content
        subject = f"Your Health Score Report - {filename}"
        body = f"Hello {user_name},\n\nThank you for using our Health Score service. Your health score report is attached.\n\nBest regards,\nThe Health Score Team"
        
        # Generate HTML content if we have the pillar scores and chart
        html_content = None
        if pillar_scores and chart_path and hasattr(email_service, 'generate_html_content'):
            try:
                html_content = email_service.generate_html_content(
                    user_name=user_name,
                    pillar_scores=pillar_scores,
                    chart_path=chart_path
                )
            except Exception as e:
                print(f"Error generating HTML content: {e}")
        
        # Send email with PDF attachment and HTML content
        email_result = email_service.send_email_with_pdf(
            to_email=to_email,
            subject=subject,
            body=body,
            pdf_path=pdf_path,
            html_content=html_content,
            chart_path=chart_path,
            pillar_scores=pillar_scores
        )
        
        return jsonify({
            'success': email_result.get('success', False),
            'message': 'Email sent successfully' if email_result.get('success', False) else 'Failed to send email',
            'filename': filename,
            'emailResult': email_result,
            'to_email': to_email  # Return the email address that was used
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to send email',
            'details': str(e)
        }), 500
