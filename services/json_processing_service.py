import json
from models import ProcessingResult

class JsonProcessingService:
    """Service for processing JSON data from webhook"""
    
    def __init__(self, health_score_service, orchestration_service):
        """
        Initialize the JSON processing service
        
        Args:
            health_score_service: HealthScoreService instance
            orchestration_service: HealthScoreOrchestrationService instance
        """
        self.health_score_service = health_score_service
        self.orchestration_service = orchestration_service
    
    def process_json(self, json_content, filename=None):
        """
        Process JSON content to calculate health scores and generate reports
        
        Args:
            json_content: JSON string to process
            filename: Optional filename for reference
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Parse JSON
            payload = json.loads(json_content)
            
            # Extract user name if available
            user_name = self._extract_user_name(payload)
            
            # Calculate health scores
            pillar_scores = self.health_score_service.calculate(payload)
            
            # Process health scores to generate chart and PDF
            result_data = self.orchestration_service.process_health_scores(pillar_scores, user_name)
            
            if result_data:
                return {
                    'success': True,
                    'message': 'JSON processed successfully',
                    'data': result_data
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to process health scores'
                }
        except Exception as e:
            print(f"Error processing JSON: {e}")
            return {
                'success': False,
                'message': f'Error processing JSON: {str(e)}'
            }
    
    def _extract_user_name(self, payload):
        """
        Extract user name from payload if available
        
        Args:
            payload: JSON payload
            
        Returns:
            User name or default value
        """
        try:
            # Try to extract user name from form response
            # This is a placeholder implementation - adjust based on actual JSON structure
            answers = payload.get('form_response', {}).get('answers', [])
            
            # Look for name field in answers
            for answer in answers:
                # This is a placeholder - adjust based on actual field reference for name
                if answer.get('field', {}).get('ref', '') == 'name_field_ref':
                    return answer.get('text', 'User')
            
            return "User"
        except Exception:
            return "User"
