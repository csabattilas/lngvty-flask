import json
from models import ProcessingResult

class HealthScoreOrchestrationService:
    """Service for orchestrating the health score processing workflow"""
    
    def __init__(self, chart_service, pdf_service):
        """
        Initialize the orchestration service
        
        Args:
            chart_service: ChartGenerationService instance
            pdf_service: PdfReportService instance
        """
        self.chart_service = chart_service
        self.pdf_service = pdf_service
    
    def process_health_scores(self, pillar_scores, user_name="User"):
        """
        Process health scores to generate chart and PDF report
        
        Args:
            pillar_scores: PillarScores object with health scores
            user_name: Name of the user for the report
            
        Returns:
            Dictionary with paths to generated files
        """
        try:
            # Generate chart
            chart_path = self.chart_service.generate_chart(pillar_scores)
            
            # Generate PDF report
            pdf_path = self.pdf_service.generate_pdf_report(pillar_scores, chart_path, user_name)
            
            # Return paths to generated files
            return {
                'chart_path': chart_path,
                'pdf_report_path': pdf_path,
                'user_name': user_name,
                'pillar_scores': pillar_scores.to_dict()
            }
        except Exception as e:
            print(f"Error in orchestration service: {e}")
            return None
