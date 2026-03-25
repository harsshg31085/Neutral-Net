import re
import uuid
import math
from functools import lru_cache
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

        self.cached_agentic = lru_cache(maxsize=1024)(self.agentic_communal_detector.analyze_sentence)
        self.cached_stereotype = lru_cache(maxsize=1024)(self.stereotype_detector.analyze_sentence)

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
    
    def analyze_text(self, text: str, ignored_texts: List[str] = None) -> Dict[str, Any]:
        if ignored_texts is None: ignored_texts = []

        text = text.strip()
        if not text:
            return self.empty_result
        
        ignored_set = set(t.lower() for t in ignored_texts)
        
        biases = []
        blocked_ranges = []
        
        sentences = self.processor.extract_sentences(text)
        current_pos = 0
        
        for sentence in sentences:
            start_index = text.find(sentence, current_pos)
            if start_index == -1: continue            
            sent_end = start_index + len(sentence)
            
            try:
                cached_stereotype = self.cached_stereotype(sentence)
                if cached_stereotype:
                    stereotype_result = cached_stereotype.copy()
                    stereotype_result['position'] = cached_stereotype['position'].copy()                    
                    stereotype_result['position']['start'] += start_index
                    stereotype_result['position']['end'] += start_index                    
                    biases.append(stereotype_result)
                    blocked_ranges.append((start_index, sent_end))                    
                    current_pos = sent_end
                    continue 
            except Exception as e:
                print(f"Error in stereotype detection: {e}")

            cached_agentic_results = self.cached_agentic(sentence)
            
            for result in cached_agentic_results:
                res_copy = result.copy()
                res_copy['position'] = result['position'].copy()                
                start = res_copy['position']['start']
                end = res_copy['position']['end']
                res_copy['id'] = str(uuid.uuid4())
                res_copy['position']['start'] = start_index + start
                res_copy['position']['end'] = start_index + end
                biases.append(res_copy)
            
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

        filtered_biases = []
        for bias in biases:
            start = bias['position']['start']
            end = bias['position']['end']
            
            actual_text = text[start:end].lower()
            
            if actual_text not in ignored_set:
                filtered_biases.append(bias)
        
        biases = filtered_biases

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
        weights = {
            'stereotype': 15.0,
            'pronoun': 5.0,
            'gendered_terms': 5.0,
            'agentic_communal': 3.0
        }

        total_penalty = 0.0
        for bias in biases:
            bias_type = bias.get('type','other')
            weight = weights.get(bias_type, 5.0)

            confidence = bias.get('confidence') or 1.0
            if confidence > 1: confidence /= 100.0

            total_penalty += weight*confidence
        
        effective_length = max(word_count, 30)
        penalty_density = (total_penalty/effective_length)*100
        k_factor = 0.025
        bias_free_score = 100.0 * math.exp(-k_factor*penalty_density)

        pronoun_balance = pronoun_stats.get('pronoun_balance', 100.0)
        final_score = (bias_free_score*0.85) + (pronoun_balance*0.15)

        return int(max(0, min(100, final_score)))