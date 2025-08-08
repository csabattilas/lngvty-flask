class PillarScores:
    """Class to store health score pillar values"""
    
    def __init__(self, muscles_and_visceral_fat=0, cardio_vascular=0, sleep=0, 
                 cognitive=0, metabolic=0, emotional=0, overall=0):
        self.muscles_and_visceral_fat = muscles_and_visceral_fat
        self.cardio_vascular = cardio_vascular
        self.sleep = sleep
        self.cognitive = cognitive
        self.metabolic = metabolic
        self.emotional = emotional
        self.overall = overall
    
    def to_dict(self):
        """Convert the pillar scores to a dictionary"""
        return {
            'muscles_and_visceral_fat': self.muscles_and_visceral_fat,
            'cardio_vascular': self.cardio_vascular,
            'sleep': self.sleep,
            'cognitive': self.cognitive,
            'metabolic': self.metabolic,
            'emotional': self.emotional,
            'overall': self.overall
        }
