import os
from services.pdf_report_service import PdfReportService
from services.chart_generation_service import ChartGenerationService
from models import PillarScores

class ReportController:
    """Controller for report-related operations"""
    
    def __init__(self, pdf_storage_path):
        """
        Initialize the controller with required dependencies
        
        Args:
            pdf_storage_path: Path to store PDF files
        """
        self.pdf_storage_path = pdf_storage_path
        self.pdf_service = PdfReportService()
        self.chart_service = ChartGenerationService()
    
    def download_pdf(self, path):
        """
        Handle PDF download request
        
        Args:
            path: Path to the PDF file
            
        Returns:
            Path to the PDF file or error message
        """
        try:
            if not path or not os.path.exists(path):
                # If path is not provided or doesn't exist, return error
                return {
                    'success': False,
                    'message': 'PDF file not found or path is invalid'
                }, 404
            
            # Return the actual PDF file path for the route to serve
            return path
        except Exception as e:
            return {
                'success': False,
                'error': 'Failed to download PDF',
                'details': str(e)
            }, 500
    
    def view_chart(self, path):
        """
        Handle chart viewing request
        
        Args:
            path: Path to the chart file
            
        Returns:
            The chart file or error message
        """
        try:
            if not path or not os.path.exists(path):
                # Return an error message if the path is invalid
                return {
                    'success': False,
                    'message': 'Chart file not found or path is invalid',
                    'path': path
                }, 404
            
            # Return the actual chart file
            return path
        except Exception as e:
            return {
                'success': False,
                'error': 'Failed to view chart',
                'details': str(e)
            }, 500
