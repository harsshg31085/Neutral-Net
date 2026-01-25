import re
import uuid
from typing import Dict, List, Any, Tuple
from .bias_patterns import BiasType, BiasPatterns

class TextProcessor:    
    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def find_word_positions(text: str, word: str) -> List[Tuple[int, int]]:
        positions = []
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        
        for match in pattern.finditer(text):
            positions.append((match.start(), match.end()))
        
        return positions
    
    @staticmethod
    def calculate_pronoun_stats(text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        
        stats = {
            "he": len(re.findall(r'\bhe\b', text_lower)),
            "she": len(re.findall(r'\bshe\b', text_lower)),
            "him": len(re.findall(r'\bhim\b', text_lower)),
            "her": len(re.findall(r'\bher\b', text_lower)),
            "his": len(re.findall(r'\bhis\b', text_lower)),
            "hers": len(re.findall(r'\bhers\b', text_lower)),
            "they": len(re.findall(r'\bthey\b', text_lower)),
            "them": len(re.findall(r'\bthem\b', text_lower)),
            "their": len(re.findall(r'\btheir\b', text_lower)),
        }
        
        masculine = stats["he"] + stats["him"] + stats["his"]
        feminine = stats["she"] + stats["her"] + stats["hers"]
        neutral = stats["they"] + stats["them"] + stats["their"]
        
        total_gendered = masculine + feminine
        if total_gendered > 0:
            pronoun_balance = min(masculine, feminine) / total_gendered
        else:
            pronoun_balance = 1.0
        
        return {
            **stats,
            "masculine_total": masculine,
            "feminine_total": feminine,
            "neutral_total": neutral,
            "pronoun_balance": round(pronoun_balance * 100, 2),
            "bias_score": round(pronoun_balance * 100)
        }
    
    @staticmethod
    def highlight_text_with_biases(text: str, biases: List[Dict]) -> str:
        biases.sort(key=lambda x: x['position']['start'])
        
        output = []
        last_idx = 0
        
        for bias in biases:
            start = bias['position']['start']
            end = bias['position']['end']
            
            start = max(0, start)
            end = min(len(text), end)

            if start < last_idx:
                continue
            
            output.append(text[last_idx:start])
            
            color = BiasPatterns.get_bias_color(bias['type'])
            bias_id = bias.get('id', str(uuid.uuid4()))
            biased_text = text[start:end]
            
            biased_text_escaped = biased_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            span = (
                f'<span class="bias-highlight" '
                f'data-bias-id="{bias_id}" '
                f'style="background-color: {color}; cursor: pointer; padding: 1px 0; border-radius: 3px; display: inline;">'
                f'{biased_text_escaped}'
                f'</span>'
            )
            output.append(span)
            
            last_idx = end
            
        output.append(text[last_idx:])
        
        return "".join(output)