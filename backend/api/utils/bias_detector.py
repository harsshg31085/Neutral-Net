import re
import uuid
from typing import Dict, List, Any
from .bias_patterns import BiasType, BiasPatterns
from .text_processor import TextProcessor
from .agentic_communal_detector import AgenticCommunalDetector
from .gendered_terms_detector import GenderedTermsDetector
from .stereotype_detector import StereotypeDetector
from .pronoun_detector import PronounBiasDetector

class BiasDetector:
    def __init__(self):
        self.processor = TextProcessor()
        
        self.agentic_communal_detector = AgenticCommunalDetector()
        self.gendered_terms_detector = GenderedTermsDetector()
        self.stereotype_detector = StereotypeDetector()
        self.pronoun_detector = PronounBiasDetector()

        self.empty_result = {
            "text": "",
            "highlighted_text": "",
            "biases": [], 
            "bias_count": 0,
            "overall_score": 100, 
            "pronoun_stats": {},
            "word_count": 0,
            "sentence_count": 0
        }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        text = text.strip()
        if not text:
            return self.empty_result
        
        biases = []
        blocked_ranges = []
        
        sentences = self.processor.extract_sentences(text)
        current_pos = 0
        
        for sentence in sentences:
            start_index = text.find(sentence, current_pos)
            if start_index == -1: continue
            
            sent_end = start_index + len(sentence)
            
            try:
                stereotype_result = self.stereotype_detector.analyze_sentence(sentence)
                if stereotype_result:
                    stereotype_result['position']['start'] += start_index
                    stereotype_result['position']['end'] += start_index
                    
                    biases.append(stereotype_result)
                    blocked_ranges.append((start_index, sent_end))
                    
                    current_pos = sent_end
                    continue 
            except Exception as e:
                print(f"Error in stereotype detection: {e}")

            agentic_communal_results = self.agentic_communal_detector.analyze_sentence(sentence)
            
            for result in agentic_communal_results:
                start = result['position']['start']
                end = result['position']['end']

                result['id'] = str(uuid.uuid4())
                result['position']['start'] = start_index + start
                result['position']['end'] = start_index + end

                biases.append(result)
            
            current_pos = sent_end

        def is_safe(b_start, b_end):
            for block_start, block_end in blocked_ranges:
                if not (b_end <= block_start or b_start >= block_end):
                    return False
            return True

        try:
            raw_pronouns = self.pronoun_detector.analyze(text)
            for b in raw_pronouns:
                if is_safe(b['position']['start'], b['position']['end']):
                    biases.append(b)
        except Exception as e:
            print(f"Error in pronoun coref detection: {e}")
        
        try:
            gendered_biases = self.gendered_terms_detector.analyze(text)
            for b in gendered_biases:
                if is_safe(b['position']['start'], b['position']['end']):
                    biases.append(b)
        except Exception as e:
            print(f"Error in gendered detection: {e}")

        pronoun_stats = self.processor.calculate_pronoun_stats(text)

        word_count = len(text.split())
        overall_score = self._calculate_overall_score(biases, word_count, pronoun_stats)

        highlighted_text = self.processor.highlight_text_with_biases(text, biases)
        
        return {
            "text": text,
            "highlighted_text": highlighted_text,
            "biases": biases,
            "bias_count": len(biases),
            "overall_score": overall_score,
            "pronoun_stats": pronoun_stats,
            "word_count": word_count,
            "sentence_count": len(sentences)
        }
    
    def _calculate_overall_score(self, biases: List[Dict], word_count: int, pronoun_stats: Dict) -> int:
        effective_length = max(word_count, 60)
        
        weights = {
            'stereotype': 30,         
            'gendered_terms': 10,     
            'agentic_communal': 5,    
            'pronoun': 5
        }
        
        total_penalty_points = 0
        for bias in biases:
            b_type = bias.get('type', 'other')
            total_penalty_points += weights.get(b_type, 5)

        density_penalty = (total_penalty_points / effective_length) * 100
        
        bias_free_score = max(0, 100 - density_penalty)

        pronoun_score = pronoun_stats.get("pronoun_balance", 100)

        final_score = (bias_free_score * 0.8) + (pronoun_score * 0.2)
        
        return int(final_score)