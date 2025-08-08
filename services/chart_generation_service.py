import os
import uuid
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

class ChartGenerationService:
    """Service for generating health score radar charts"""
    
    def __init__(self):
        # Create charts directory if it doesn't exist
        self.charts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'PdfData', 'charts')
        os.makedirs(self.charts_dir, exist_ok=True)
        
        # Set matplotlib to use a non-interactive backend
        plt.switch_backend('Agg')
    
    def generate_chart(self, pillar_scores):
        """
        Generate a radar chart visualization of health scores
        
        Args:
            pillar_scores: PillarScores object with health scores
            
        Returns:
            Path to the generated chart image file
        """
        # Extract scores from the pillar_scores object
        categories = ['Muscles & Visceral Fat', 'Cardiovascular', 'Sleep', 
                      'Cognitive', 'Metabolic', 'Emotional']
        
        values = [
            pillar_scores.muscles_and_visceral_fat,
            pillar_scores.cardio_vascular,
            pillar_scores.sleep,
            pillar_scores.cognitive,
            pillar_scores.metabolic,
            pillar_scores.emotional
        ]
        
        # Normalize values to 0-1 for plotting (extend to 0-120 scale)
        values = [v / 120 for v in values]
        
        # Number of variables
        N = len(categories)
        
        # Create angles for each category (divide the circle into equal parts)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Close the loop
        
        # Add the values for the chart (and close the loop)
        values += values[:1]
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        
        # Remove the circular grid lines and frame
        ax.grid(False)
        ax.spines['polar'].set_visible(False)
        
        # Draw one axis per variable and add labels
        plt.xticks(angles[:-1], categories, size=14)
        
        # Draw the y-axis labels (0-120)
        plt.yticks([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], 
                  ['12', '24', '36', '48', '60', '72', '84', '96', '108', '120'], 
                  color='grey', size=12)
        
        # Add radial grid lines from center to each category point
        for angle in angles[:-1]:
            ax.plot([0, angle], [0, 1], color='grey', 
                   linestyle='--', linewidth=0.5, alpha=0.5)
        
        # Add grid lines at every 12 units (0.1 in normalized scale)
        for i in range(1, 11):
            level = i / 10.0
            # Create points for the polygon at this level
            grid_values = [level] * len(angles)
            # Plot the polygon line connecting all points at this level
            ax.plot(angles, grid_values, color='grey', 
                   linestyle='--', linewidth=0.5, alpha=0.5)
        
        # Plot data
        ax.plot(angles, values, linewidth=2, linestyle='solid', color='#1aaf6c')
        
        # Fill area
        ax.fill(angles, values, alpha=0.25, color='#1aaf6c')
        
        # Add dots and value labels at each point where polygon touches axes
        for i in range(len(categories)):
            # Get the x,y coordinates
            angle = angles[i]
            value = values[i]
            
            # Convert to cartesian coordinates for annotation placement
            x = value * np.cos(angle)
            y = value * np.sin(angle)
            
            # Add a small square marker at the point instead of a circle
            ax.plot(angle, value, marker='s', markersize=8, color='#1aaf6c', markeredgecolor='white', markeredgewidth=1, zorder=10)
            
            # Add the value label
            # Adjust the position slightly based on the angle to avoid overlap
            ha = 'center'
            va = 'center'
            offset_x = 0
            offset_y = 0
            
            # Adjust position based on angle
            if angle == 0:  # Right
                ha = 'left'
                offset_x = 0.05
            elif angle == np.pi/2:  # Top
                va = 'bottom'
                offset_y = 0.05
            elif angle == np.pi:  # Left
                ha = 'right'
                offset_x = -0.05
            elif angle == 3*np.pi/2:  # Bottom
                va = 'top'
                offset_y = -0.05
            elif 0 < angle < np.pi/2:  # Top-right quadrant
                ha = 'left'
                va = 'bottom'
                offset_x = 0.05
                offset_y = 0.05
            elif np.pi/2 < angle < np.pi:  # Top-left quadrant
                ha = 'right'
                va = 'bottom'
                offset_x = -0.05
                offset_y = 0.05
            elif np.pi < angle < 3*np.pi/2:  # Bottom-left quadrant
                ha = 'right'
                va = 'top'
                offset_x = -0.05
                offset_y = -0.05
            else:  # Bottom-right quadrant
                ha = 'left'
                va = 'top'
                offset_x = 0.05
                offset_y = -0.05
            
            # Add the value label (convert back to 0-120 scale)
            ax.annotate(f'{int(value * 120)}', 
                       (angle, value),
                       xytext=(angle + offset_x, value + offset_y),
                       textcoords='data',
                       ha=ha, va=va,
                       fontsize=12,
                       fontweight='bold',
                       bbox=dict(boxstyle='square,pad=0.3', fc='white', alpha=0.7))
        
        # Add a title
        plt.title('Your Health Score', size=20, y=1.1)
        
        # Adjust the layout
        plt.tight_layout()
        
        # Generate a unique filename
        filename = f"chart_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}.png"
        filepath = os.path.join(self.charts_dir, filename)
        
        # Save the figure
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)  # Close the figure to free memory
        
        return filepath
