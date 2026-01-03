import re
import uuid
from typing import Dict, List, Any
from .bias_patterns import BiasType, BiasPatterns
from .text_processor import TextProcessor
from .agentic_communal_detector import AgenticCommunalDetector

class BiasDetector:
    def __init__(self):
        self.processor = TextProcessor()

        self.compiled_pronouns = []
        for pattern_str, info in BiasPatterns.PRONOUN_PATTERNS.items():
            self.compiled_pronouns.append({
                "regex": re.compile(pattern_str, re.IGNORECASE),
                "info": info,
                "pattern_str": pattern_str
            })
        
        self.agentic_communal_ai = AgenticCommunalDetector()
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        text = text.strip()
        if not text:
            return self._get_empty_result()
        
        biases = []
        
        biases.extend(self._detect_pronoun_biases(text))
        biases.extend(self._detect_stereotype_biases(text))
        biases.extend(self._detect_semantic_biases(text))
        
        sentences = self.processor.extract_sentences(text)
        current_pos = 0
        
        for sentence in sentences:
            start_index = text.find(sentence, current_pos)
            if start_index == -1: continue
            
            ai_result = self.agentic_communal_ai.analyze_sentence(sentence)
            
            if ai_result:
                local_start = ai_result['position']['start']
                local_end = ai_result['position']['end']
                
                ai_result['id'] = str(uuid.uuid4())
                ai_result['position']['start'] = start_index + local_start
                ai_result['position']['end'] = start_index + local_end
                
                biases.append(ai_result)
            
            current_pos = start_index + len(sentence)

        pronoun_stats = self.processor.calculate_pronoun_stats(text)
        overall_score = self._calculate_overall_score(biases, pronoun_stats)
        highlighted_text = self.processor.highlight_text_with_biases(text, biases)
        
        return {
            "text": text,
            "highlighted_text": highlighted_text,
            "biases": biases,
            "bias_count": len(biases),
            "overall_score": overall_score,
            "pronoun_stats": pronoun_stats,
            "word_count": len(text.split()),
            "sentence_count": len(sentences)
        }
    
    def _detect_pronoun_biases(self, text: str) -> List[Dict]:
        biases = []
                
        for item in self.compiled_pronouns:
            pattern = item["regex"]
            pattern_info = item["info"]
            
            for match in pattern.finditer(text):
                start, end = match.start(), match.end()
                biased_text = text[start:end]
                
                if self._is_false_positive(text, start, end, biased_text.lower()):
                    continue
                
                biases.append({
                    "id": str(uuid.uuid4()),
                    "type": BiasType.PRONOUN,
                    "target_text": biased_text,
                    "position": {"start": start, "end": end},
                    "description": f"Gender-specific pronoun detected: '{biased_text}'",
                    "suggestion": pattern_info["suggestion"],
                    "alternatives": pattern_info["alternatives"],
                    "severity": "medium"
                })
        
        return biases

    def _is_false_positive(self, text: str, start: int, end: int, word: str) -> bool:        
        false_positive_map = {
            "he": ["the", "here", "there", "where", "hence"],
            "her": ["there", "where", "here", "adhere", "cohere"],
            "his": ["this", "history", "historian", "whisper"],
            "him": ["whim", "shim", "brim", "trim"]
        }
        
        if word not in false_positive_map:
            return False
        
        context_start = max(0, start - 3)
        context_end = min(len(text), end + 3)
        context = text[context_start:context_end].lower()
        
        for false_word in false_positive_map[word]:
            if false_word in context:
                if false_word != word and word in false_word:
                    return True
        
        return False
    
    def _detect_stereotype_biases(self, text: str) -> List[Dict]:
        biases = []
        
        for pattern, gender, suggestion in BiasPatterns.STEREOTYPE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start, end = match.start(), match.end()
                biased_text = text[start:end]
                
                biases.append({
                    "id": str(uuid.uuid4()),
                    "type": BiasType.STEREOTYPE,
                    "target_text": biased_text,
                    "position": {"start": start, "end": end},
                    "description": f"Gender-stereotyped term: '{biased_text}' - often associated with {gender}",
                    "suggestion": suggestion,
                    "alternatives": [],
                    "severity": "high",
                    "color": BiasPatterns.get_bias_color(BiasType.STEREOTYPE)
                })
        
        return biases
    
    def _detect_semantic_biases(self, text: str) -> List[Dict]:
        biases = []
        sentences = self.processor.extract_sentences(text)
        
        current_pos = 0
        for sentence in sentences:
            lower_sentence = sentence.lower()
            
            if ("only" in lower_sentence or "always" in lower_sentence) and \
               ("he" in lower_sentence or "she" in lower_sentence):
                
                start = current_pos + text[current_pos:].find(sentence)
                end = start + len(sentence)
                
                biases.append({
                    "id": str(uuid.uuid4()),
                    "type": BiasType.SEMANTIC,
                    "target_text": sentence,
                    "position": {"start": start, "end": end},
                    "description": "Potential semantic bias: Sentence makes absolute gender associations",
                    "suggestion": "Consider rephrasing to avoid absolute statements about gender",
                    "alternatives": [],
                    "severity": "medium"
                })
            
            current_pos += len(sentence) + 1
        
        return biases
    
    def _calculate_overall_score(self, biases: List[Dict], pronoun_stats: Dict) -> int:
        base_score = 100
        
        for bias in biases:
            if bias["severity"] == "high":
                base_score -= 10
            elif bias["severity"] == "medium":
                base_score -= 5
            else:  
                base_score -= 2
        
        pronoun_balance = pronoun_stats.get("pronoun_balance", 100)
        base_score = (base_score + pronoun_balance) / 2
        
        return max(0, min(100, int(base_score)))
    
    def _get_empty_result(self):
        return {
            "text": "", "highlighted_text": "", "biases": [], 
            "bias_count": 0, "overall_score": 100, 
            "pronoun_stats": {}, "word_count": 0, "sentence_count": 0
        }