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
        """
        Acts as the core inference engine. It segments the input text, and uses cached
        transformer models for phrase-level bias detection (Agentic/Communal and Stereotype)
        and document-level models for pronoun and gendered-term bias detection.

        Enforces coordinate safe zones to ensure biases may never overlap.

        Args:
            text (str): The raw input string to be analyzed.
            ignored_texts (List[str]): A list of words/phrases that the user has explicitly chosen to bypass.
            Defaults to None.
        
        Returns:
            Dict[str, Any]: An analysis containing:
                - text (str): The original input text
                - highlighted_text (str): HTML string with detected biases wrapped in UI spans.
                - biases (List[Dict]): Detailed list of all biased objects.
                - bias_count (int): Total count of biased objects.
                - overall_score (int): The inclusivity score. Ranges from 0-100, inclusive.
                - pronoun_stats (Dict): Distribution of used pronouns 
                - word_count (int): Total words in analyzed text.
                - sentence_count (int): Total sentences in analyzed text.
        """
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
                    
                    """ 
                    Tracking sentence level flags to stop word-level flags from operating on them.
                    Prevents double highlighting issues. 
                    """

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
        overall_score = self._calculate_overall_score(biases, word_count)

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
    
    def _calculate_overall_score(self, biases: List[Dict], word_count: int) -> int:
        """
        Calculates a length-normalized inclusivity score using exponential-decay functions.

        Applies pre-defined severity weights and normalizes the total penalty against the word count.
        Exponential Decay guarantees the score never drops below zero.

        Args:
            biases (List[Dict]): A list of detected bias dictionaries, each containing 'type' and 'confidence'
            keys.

            word_count (int): Total number of words in the analyzed text.
        
        Returns:
            int: Final inclusivity score, boynded between 0 and 100.
        """

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
        
        # Having a baseline of 30 words prevents score explosions for small inputs
        effective_length = max(word_count, 30)
        penalty_density = (total_penalty/effective_length)*100
        k_factor = 0.025
        final_score = 100.0 * math.exp(-k_factor*penalty_density)

        return int(final_score)