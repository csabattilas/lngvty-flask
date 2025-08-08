import os
import json
import uuid
from datetime import datetime

class WebhookController:
    """Controller for webhook-related operations"""
    
    def __init__(self, json_storage_path, json_processing_service, email_service):
        """
        Initialize the controller with required dependencies
        
        Args:
            json_storage_path: Path to store JSON files
            json_processing_service: Service to process JSON data
        """
        self.json_storage_path = json_storage_path
        self.json_processing_service = json_processing_service
        self.email_service = email_service
        
    def _extract_email_from_payload(self, payload):
        """
        Extract email address from payload with reference ID 39f116ed-5403-407a-b506-c9625e9e6b2a
        
        Args:
            payload: JSON payload from webhook
            
        Returns:
            Email address if found, None otherwise
        """
        try:
            # Check if payload has form_response structure
            if 'form_response' in payload and 'answers' in payload['form_response']:
                # Look for email field with specific reference ID
                for answer in payload['form_response']['answers']:
                    if answer.get('type') == 'email' and \
                       'field' in answer and \
                       answer['field'].get('ref') == '39f116ed-5403-407a-b506-c9625e9e6b2a':
                        return answer.get('email')
            return None
        except Exception as e:
            print(f"Error extracting email: {e}")
            return None
    
    def process_webhook(self, payload):
        """
        Process incoming webhook data
        
        Args:
            payload: JSON payload from webhook
            
        Returns:
            Dictionary with processing results and metadata
        """
        try:
            # Generate a unique filename
            filename = f"Webhook_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}.json"
            filepath = os.path.join(self.json_storage_path, filename)
            
            # Save JSON to file
            with open(filepath, 'w') as f:
                json.dump(payload, f, indent=2)
            
            # Process the JSON immediately
            json_content = json.dumps(payload)
            processing_result = self.json_processing_service.process_json(json_content)
            
            # Return response
            return {
                'success': True,
                'message': 'Webhook received, saved, and processed successfully',
                'fileName': filename,
                'processingResult': processing_result
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Failed to process webhook',
                'details': str(e)
            }, 500
    
    def process_webhook_to_pdf(self, payload):
        """
        Process incoming webhook data and generate PDF directly
        
        Args:
            payload: JSON payload from webhook
            
        Returns:
            Dictionary with PDF path or error information
        """
        try:
            # Generate a unique filename
            filename = f"Webhook_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}.json"
            filepath = os.path.join(self.json_storage_path, filename)
            
            # Save JSON to file
            with open(filepath, 'w') as f:
                json.dump(payload, f, indent=2)
            
            # Process the JSON immediately
            json_content = json.dumps(payload)
            processing_result = self.json_processing_service.process_json(json_content)
            
            # Extract PDF path from processing result
            if processing_result.get('success') and 'data' in processing_result:
                pdf_path = processing_result['data'].get('pdf_report_path')
                if pdf_path and os.path.exists(pdf_path):
                    return {
                        'success': True,
                        'message': 'Webhook processed and PDF generated successfully',
                        'fileName': filename,
                        'pdf_path': pdf_path
                    }
            
            # If we get here, something went wrong with PDF generation
            return {
                'success': False,
                'error': 'Failed to generate PDF from webhook data',
                'processingResult': processing_result
            }, 500
        except Exception as e:
            return {
                'success': False,
                'error': 'Failed to save webhook data',
                'details': str(e)
            }, 500
            
    def process_webhook_and_email(self, payload, to_email=None):
        """
        Process incoming webhook data, generate PDF, and send via email
        
        Args:
            payload: JSON payload from webhook
            to_email: Email address to send the PDF to (optional, will extract from payload if not provided)
            
        Returns:
            Dictionary with processing results and email status
        """
        try:
            # Generate a unique filename
            filename = f"Webhook_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}.json"
            filepath = os.path.join(self.json_storage_path, filename)
            
            # Save JSON to file
            with open(filepath, 'w') as f:
                json.dump(payload, f, indent=2)
            
            # Process the JSON immediately
            json_content = json.dumps(payload)
            processing_result = self.json_processing_service.process_json(json_content)
            
            # Extract PDF path and user name from processing result
            if processing_result.get('success') and 'data' in processing_result:
                pdf_path = processing_result['data'].get('pdf_report_path')
                user_name = processing_result['data'].get('user_name', 'User')
                
                # If email not provided, try to extract from payload
                recipient_email = to_email
                if not recipient_email:
                    recipient_email = self._extract_email_from_payload(payload)
                    
                if not recipient_email:
                    return {
                        'success': False,
                        'error': 'No email address provided or found in payload',
                        'details': 'Please provide an email address or ensure the payload contains an email field with reference ID 39f116ed-5403-407a-b506-c9625e9e6b2a'
                    }, 400
                
                if pdf_path and os.path.exists(pdf_path):
                    # Send email with PDF attachment
                    subject = f"Your Health Score Report - {datetime.utcnow().strftime('%Y-%m-%d')}"
                    body = f"Hello {user_name},\n\nThank you for using our Health Score service. Your health score report is attached.\n\nBest regards,\nThe Health Score Team"
                    
                    email_result = self.email_service.send_email_with_pdf(
                        to_email=recipient_email,
                        subject=subject,
                        body=body,
                        pdf_path=pdf_path
                    )
                    
                    # Return combined result
                    return {
                        'success': email_result.get('success', False),
                        'message': 'Webhook processed and email sent successfully' if email_result.get('success', False) else 'Failed to send email',
                        'fileName': filename,
                        'processingResult': processing_result,
                        'emailResult': email_result
                    }
            
            # If we get here, something went wrong with PDF generation
            return {
                'success': False,
                'error': 'Failed to generate PDF from webhook data',
                'processingResult': processing_result
            }, 500
        except Exception as e:
            return {
                'success': False,
                'error': 'Failed to process webhook and send email',
                'details': str(e)
            }, 500
