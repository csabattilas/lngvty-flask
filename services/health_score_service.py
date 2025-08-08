import json
import os
from models import PillarScores

class HealthScoreService:
    """Service for calculating health scores from typeform data"""
    
    def __init__(self):
        # Load answer map from JSON file
        answer_map_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'answer-map.json')
        
        try:
            with open(answer_map_path, 'r') as f:
                self._lookups = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback to default mappings if file not found or invalid
            print(f"Warning: Could not load answer map from {answer_map_path}. Using default mappings.")
            self._lookups = {}
        
        # Define pillar mappings
        self._pillar1 = [  # Muscles and Organ Fat
            "aa24a4d2-b1f2-408b-9d4a-4be80ec7508d",  # Waist Circumference
            "9c968d6d-e21b-448a-b8fb-30056f76ffff"   # Waist-Hip Ratio
        ]
        
        self._pillar2 = [  # Cardiovascular Health
            "27181fef-736e-4bee-ad31-7d8e983d61b3",  # Blood Pressure (Systolic)
            "ceb0b561-1793-43f1-9c76-11cc3964e48a"   # Blood Pressure (Diastolic)
        ]
        
        self._pillar3 = [  # Sleep
            "ccc73a31-d4f8-4856-8ebb-27647ff39a97",  # Sleep Duration
            "50b96cb1-243e-454b-aa01-0e8990fc507d"   # Sleep Quality
        ]
        
        self._pillar4 = [  # Cognitive Health
            "c714f3fd-a4ff-449b-9946-7badbdc59e03",  # Memory function score
            "15045302-e327-4069-bc9d-d0c0ab3cfaaa"   # Noticed memory changes
        ]
        
        self._pillar5 = [  # Metabolic Health and Nutrition
            "f9a247fc-e8d3-4bd8-b7e1-ae54f6766993"   # Protein intake
        ]
        
        self._pillar6 = [  # Emotional Well-being
            "2c99731f-7ee5-4181-82b5-48a4d876df59"   # Sense of purpose
        ]
    
    def calculate(self, typeform_payload):
        """Calculate health scores from typeform payload"""
        # Extract answers from the JSON
        answers = self._extract_answers(typeform_payload)
        
        # Calculate raw scores for each pillar (0-5 scale)
        raw_muscles_and_visceral_fat = self._calculate_pillar_score(answers, self._pillar1)
        raw_cardio_vascular = self._calculate_pillar_score(answers, self._pillar2)
        raw_sleep = self._calculate_pillar_score(answers, self._pillar3)
        raw_cognitive = self._calculate_pillar_score(answers, self._pillar4)
        raw_metabolic = self._calculate_pillar_score(answers, self._pillar5)
        raw_emotional = self._calculate_pillar_score(answers, self._pillar6)
        
        # Normalize scores to 0-100 scale
        muscles_and_visceral_fat = self._normalize_score(raw_muscles_and_visceral_fat)
        cardio_vascular = self._normalize_score(raw_cardio_vascular)
        sleep = self._normalize_score(raw_sleep)
        cognitive = self._normalize_score(raw_cognitive)
        metabolic = self._normalize_score(raw_metabolic)
        emotional = self._normalize_score(raw_emotional)
        
        # Calculate overall score (average of all pillars)
        overall = (muscles_and_visceral_fat + cardio_vascular + sleep + 
                   cognitive + metabolic + emotional) / 6.0
        
        # Return pillar scores
        return PillarScores(
            muscles_and_visceral_fat,
            cardio_vascular,
            sleep,
            cognitive,
            metabolic,
            emotional,
            round(overall, 1)
        )
    
    def _normalize_score(self, raw_score):
        """Convert from 0-5 scale to 0-100 scale"""
        return round(raw_score * 20, 1)
    
    def _extract_answers(self, payload):
        """Extract answers from typeform payload"""
        try:
            answers = payload.get('form_response', {}).get('answers', [])
            
            answer_map = {}
            for answer in answers:
                field_ref = answer.get('field', {}).get('ref', '')
                answer_type = answer.get('type', '')
                
                if answer_type == 'choice':
                    value = answer.get('choice', {}).get('label', '')
                elif answer_type == 'text':
                    value = answer.get('text', '')
                elif answer_type == 'number':
                    value = str(answer.get('number', 0))
                else:
                    value = ''
                
                answer_map[field_ref] = value
            
            return answer_map
        except Exception as e:
            print(f"Error extracting answers: {e}")
            return {}
    
    def _calculate_pillar_score(self, answers, pillar_uuids):
        """Calculate score for a specific pillar"""
        scores = []
        
        for uuid in pillar_uuids:
            if uuid in answers and uuid in self._lookups:
                answer = answers[uuid]
                # Try exact match first
                if answer in self._lookups[uuid]:
                    scores.append(self._lookups[uuid][answer])
                else:
                    # Try to find the best matching answer key
                    # This is useful when the answer format might vary slightly
                    best_match = None
                    for key in self._lookups[uuid].keys():
                        if answer.lower() in key.lower() or key.lower() in answer.lower():
                            best_match = key
                            break
                    
                    if best_match:
                        scores.append(self._lookups[uuid][best_match])
                    else:
                        print(f"Warning: No matching answer found for {uuid}: {answer}")
        
        if not scores:
            return 0
        
        return sum(scores) / len(scores)
