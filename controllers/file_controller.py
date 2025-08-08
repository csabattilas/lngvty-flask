import os
import json
from datetime import datetime

class FileController:
    """Controller for file-related operations"""
    
    def __init__(self, json_storage_path, json_processing_service):
        """
        Initialize the controller with required dependencies
        
        Args:
            json_storage_path: Path to store JSON files
            json_processing_service: Service to process JSON data
        """
        self.json_storage_path = json_storage_path
        self.json_processing_service = json_processing_service
    
    def list_files(self):
        """
        List all JSON files in the storage directory
        
        Returns:
            Dictionary with list of files and metadata
        """
        try:
            # Get all JSON files in the storage directory
            files = []
            for filename in os.listdir(self.json_storage_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.json_storage_path, filename)
                    stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'createdAt': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'size': stat.st_size
                    })
            
            # Sort by creation time (newest first)
            files.sort(key=lambda x: x['createdAt'], reverse=True)
            
            return {
                'success': True,
                'files': files
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Failed to list files',
                'details': str(e)
            }, 500
    
    def get_file_content(self, filename):
        """
        Get content of a specific JSON file
        
        Args:
            filename: Name of the file to retrieve
            
        Returns:
            Dictionary with file content and metadata
        """
        try:
            # Sanitize filename to prevent directory traversal
            filename = os.path.basename(filename)
            file_path = os.path.join(self.json_storage_path, filename)
            
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': 'File not found'
                }, 404
            
            # Read file content
            with open(file_path, 'r') as f:
                content = json.load(f)
            
            return {
                'success': True,
                'fileName': filename,
                'content': content
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Failed to read file',
                'details': str(e)
            }, 500
    
    def process_file(self, filename, output_format='pdf'):
        """
        Process a specific JSON file
        
        Args:
            filename: Name of the file to process
            output_format: Format for the output (pdf or html)
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Sanitize filename
            filename = os.path.basename(filename)
            file_path = os.path.join(self.json_storage_path, filename)
            
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': 'File not found'
                }, 404
            
            # Read file content
            with open(file_path, 'r') as f:
                json_content = f.read()
            
            # Process the JSON
            result = self.json_processing_service.process_json(json_content, filename)
            
            if result.get('success') and result.get('data'):
                data = result.get('data', {})
                pdf_path = data.get('pdf_report_path', '')
                chart_path = data.get('chart_path', '')
                
                # Create response based on requested format
                if output_format == 'html':
                    return {
                        'success': result.get('success'),
                        'message': result.get('message'),
                        'chartUrl': f'/api/view-chart?path={chart_path}',
                        'data': data
                    }
                else:  # Default to PDF
                    return {
                        'success': result.get('success'),
                        'message': result.get('message'),
                        'pdfUrl': f'/api/download-pdf?path={pdf_path}',
                        'chartUrl': f'/api/view-chart?path={chart_path}',
                        'pdfPath': pdf_path,  # Add actual path for email functionality
                        'data': data
                    }
            
            return result
        except Exception as e:
            return {
                'success': False,
                'error': 'Failed to process file',
                'details': str(e)
            }, 500
