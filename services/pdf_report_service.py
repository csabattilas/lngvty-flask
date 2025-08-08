import os
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class PdfReportService:
    """Placeholder service for PDF report generation"""
    
    def __init__(self):
        # Create PDF directory if it doesn't exist
        self.pdf_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'PdfData', 'reports')
        os.makedirs(self.pdf_dir, exist_ok=True)
    
    def generate_pdf_report(self, pillar_scores, chart_path, user_name="User"):
        """
        Generate a PDF report with health scores and chart
        
        Args:
            pillar_scores: PillarScores object with health scores
            chart_path: Path to the chart image to include in the report
            user_name: Name of the user for the report
            
        Returns:
            Path to the generated PDF file
        """
        # Generate a unique filename
        filename = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}.pdf"
        filepath = os.path.join(self.pdf_dir, filename)
        
        # Create the PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=24,
            alignment=1,  # Center alignment
            spaceAfter=20
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Heading2'],
            fontSize=16,
            alignment=1,  # Center alignment
            spaceAfter=12
        )
        
        normal_style = styles["Normal"]
        heading_style = styles["Heading2"]
        
        # Build the document content
        content = []
        
        # Add title
        content.append(Paragraph("Your Health Score Report", title_style))
        content.append(Spacer(1, 0.25 * inch))
        
        # Add user info and date
        content.append(Paragraph(f"User: {user_name}", subtitle_style))
        content.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
        content.append(Spacer(1, 0.5 * inch))
        
        # Add chart image
        if os.path.exists(chart_path):
            img_width = 6 * inch
            img = Image(chart_path, width=img_width, height=img_width)
            content.append(img)
            content.append(Spacer(1, 0.5 * inch))
        
        # Add pillar scores section
        content.append(Paragraph("Detailed Health Scores", heading_style))
        content.append(Spacer(1, 0.25 * inch))
        
        # Create a table for the scores
        data = [
            ["Health Pillar", "Score"],
            ["Muscles and Visceral Fat", f"{pillar_scores.muscles_and_visceral_fat}"],
            ["Cardiovascular Health", f"{pillar_scores.cardio_vascular}"],
            ["Sleep", f"{pillar_scores.sleep}"],
            ["Cognitive Health", f"{pillar_scores.cognitive}"],
            ["Metabolic Health", f"{pillar_scores.metabolic}"],
            ["Emotional Well-being", f"{pillar_scores.emotional}"],
            ["Overall Score", f"{pillar_scores.overall}"]
        ]
        
        table = Table(data, colWidths=[4*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ]))
        
        content.append(table)
        content.append(Spacer(1, 0.5 * inch))
        
        # Build the PDF
        doc.build(content)
        
        return filepath
