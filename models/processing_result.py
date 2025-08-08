class ProcessingResult:
    """Class to store processing results"""
    
    def __init__(self, success=False, message="", data=None):
        self.success = success
        self.message = message
        self.data = data
    
    def to_dict(self):
        """Convert the processing result to a dictionary"""
        return {
            'success': self.success,
            'message': self.message,
            'data': self.data
        }
