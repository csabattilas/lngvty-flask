import os
import base64
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition, Content, MimeType

class EmailService:
    """Service for sending emails with PDF attachments and HTML content"""
    
    def __init__(self, api_key=None):
        """
        Initialize the email service
        
        Args:
            api_key: SendGrid API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv('SENDGRID_API_KEY')

        if not self.api_key:
            print("Warning: SENDGRID_API_KEY not set. Email functionality will not work.")
            
    def generate_html_content(self, user_name, pillar_scores, chart_path=None):
        """
        Generate HTML content for the email that mimics the PDF report
        
        Args:
            user_name: Name of the user for the report
            pillar_scores: PillarScores object or dictionary with health scores
            chart_path: Path to the chart image to include in the email
            
        Returns:
            HTML content as a string
        """
        # Convert chart path to base64 if provided
        chart_img_tag = ''
        if chart_path and os.path.exists(chart_path):
            try:
                with open(chart_path, 'rb') as f:
                    chart_data = f.read()
                    chart_base64 = base64.b64encode(chart_data).decode()
                    chart_img_tag = f'<img src="data:image/png;base64,{chart_base64}" style="max-width: 500px; width: 100%; height: auto;" alt="Health Score Chart" />'
            except Exception as e:
                print(f"Error embedding chart in email: {e}")
                
        # Handle both object and dictionary formats for pillar scores
        scores = {}
        if pillar_scores:
            if hasattr(pillar_scores, 'to_dict'):
                scores = pillar_scores.to_dict()
            elif isinstance(pillar_scores, dict):
                scores = pillar_scores
            else:
                # Try to access attributes directly
                try:
                    scores = {
                        'muscles_and_visceral_fat': getattr(pillar_scores, 'muscles_and_visceral_fat', 0),
                        'cardio_vascular': getattr(pillar_scores, 'cardio_vascular', 0),
                        'sleep': getattr(pillar_scores, 'sleep', 0),
                        'cognitive': getattr(pillar_scores, 'cognitive', 0),
                        'metabolic': getattr(pillar_scores, 'metabolic', 0),
                        'emotional': getattr(pillar_scores, 'emotional', 0),
                        'overall': getattr(pillar_scores, 'overall', 0)
                    }
                except Exception as e:
                    print(f"Error accessing pillar scores: {e}")
                    scores = {
                        'muscles_and_visceral_fat': 0,
                        'cardio_vascular': 0,
                        'sleep': 0,
                        'cognitive': 0,
                        'metabolic': 0,
                        'emotional': 0,
                        'overall': 0
                    }
        
        # Create extremely minimal HTML content to avoid email client clipping
        html = f"""
        <h2>Your Health Score Report</h2>
        <p>User: {user_name}</p>
        <p>Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div>
            {chart_img_tag}
        </div>
        
        <h3>Health Scores</h3>
        
        <p>Muscles and Visceral Fat: <strong>{scores['muscles_and_visceral_fat']}</strong></p>
        <p>Cardiovascular Health: <strong>{scores['cardio_vascular']}</strong></p>
        <p>Sleep: <strong>{scores['sleep']}</strong></p>
        <p>Cognitive Health: <strong>{scores['cognitive']}</strong></p>
        <p>Metabolic Health: <strong>{scores['metabolic']}</strong></p>
        <p>Emotional Well-being: <strong>{scores['emotional']}</strong></p>
        <p>Overall Score: <strong>{scores['overall']}</strong></p>
        
        <p>This report was generated automatically. Please do not reply to this email.</p>
        """
        
        return html
    
    def send_email_with_pdf(self, to_email, subject, body, pdf_path, from_email=None, html_content=None, chart_path=None, pillar_scores=None):
        """
        Send an email with a PDF attachment and optionally HTML content with chart
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body text (plain text version)
            pdf_path: Path to the PDF file to attach
            from_email: Sender email address (defaults to environment variable)
            html_content: Optional HTML content for the email body
            chart_path: Optional path to chart image to embed in email
            pillar_scores: Optional pillar scores object to include in email
            
        Returns:
            Dictionary with success status and details
        """
        try:
            # Check if API key is available
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'SendGrid API key not configured',
                    'details': 'Set SENDGRID_API_KEY environment variable or provide in constructor'
                }
                
            # Check if PDF exists
            if not os.path.exists(pdf_path):
                return {
                    'success': False,
                    'error': 'PDF file not found',
                    'details': f'File not found at path: {pdf_path}'
                }
            
            # Get sender email from environment if not provided
            sender = from_email or os.getenv('SENDGRID_FROM_EMAIL', 'no-reply@frontlab.io')
            
            # Read and encode the PDF file
            with open(pdf_path, 'rb') as f:
                data = f.read()
                encoded_file = base64.b64encode(data).decode()

            # Create the attachment
            attached_file = Attachment(
                FileContent(encoded_file),
                FileName(os.path.basename(pdf_path)),
                FileType('application/pdf'),
                Disposition('attachment')
            )

            # Create the email with HTML content if provided
            if html_content:
                message = Mail(
                    from_email=sender,
                    to_emails=to_email,
                    subject=subject,
                    plain_text_content=body,
                    html_content=Content(MimeType.html, html_content)
                )
            else:
                message = Mail(
                    from_email=sender,
                    to_emails=to_email,
                    subject=subject,
                    plain_text_content=body
                )
            
            # Add attachment
            message.attachment = attached_file

            # Send it
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            
            return {
                'success': True,
                'message': 'Email sent successfully',
                'status_code': response.status_code,
                'to_email': to_email,
                'subject': subject
            }
        except Exception as e:
            error_details = str(e)
            error_type = type(e).__name__
            
            # Try to extract more detailed information from SendGrid API errors
            response_body = None
            status_code = None
            
            # Check if it's a SendGrid API error with response details
            if hasattr(e, 'body') and e.body:
                try:
                    # Try to parse the response body as JSON
                    import json
                    response_body = json.loads(e.body.decode('utf-8') if isinstance(e.body, bytes) else e.body)
                except:
                    response_body = e.body.decode('utf-8') if isinstance(e.body, bytes) else str(e.body)
            
            # Get status code if available
            if hasattr(e, 'status_code'):
                status_code = e.status_code
                
            return {
                'success': False,
                'error': 'Failed to send email',
                'error_type': error_type,
                'status_code': status_code,
                'details': error_details,
                'response_body': response_body
            }
