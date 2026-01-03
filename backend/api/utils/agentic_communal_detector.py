import os
import torch
import re
import uuid
from django.conf import settings
from transformers import pipeline, AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
from .bias_patterns import AGENTIC_LIST, COMMUNAL_LIST

class AgenticCommunalDetector:
    def __init__(self):        
        model_path = os.path.join(settings.BASE_DIR, 'models', 'agentic_communal_model')
        
        try:
            self.classifier = pipeline("text-classification", model=model_path, tokenizer=model_path)
        except Exception as e:
            raise e

        self.fill_mask = pipeline("fill-mask", model="roberta-base")
        
        self.sim_tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.sim_model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

        self.agentic_terms = AGENTIC_LIST
        self.communal_terms = COMMUNAL_LIST
        self.all_biased_terms = set(self.agentic_terms + self.communal_terms)

        self.blocklist = {
            "good", "great", "excellent", "amazing", "wonderful", "fantastic", 
            "awesome", "nice", "lovely", "perfect", "brilliant", "superb", 
            "outstanding", "incredible", "terrific", "fabulous", "exceptional",
            "bad", "terrible", "awful", "horrible", "poor", "dreadful", "lousy",
            "worse", "worst", "disappointing",
            "very", "really", "extremely", "highly", "totally", "completely", 
            "absolutely", "quite", "rather", "too", "so", "truly", "actual",
            "big", "huge", "large", "small", "tiny", "fine", "okay", "decent", 
            "average", "standard", "normal", "typical", "regular", "real",
            "serious", "important", "interesting", "known", "famous"
        }

        pattern_str = r'\b(' + '|'.join(map(re.escape, self.all_biased_terms)) + r')\b'
        self.bias_pattern = re.compile(pattern_str, re.IGNORECASE)

    def get_embedding(self, text):
        inputs = self.sim_tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.sim_model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()

    def analyze_sentence(self, text):
        res = self.classifier(text[:512])[0]
        model_says_biased = res['label'] in ["PERSONALITY", "LABEL_1"]
        
        if not model_says_biased:
            return None

        match = self.bias_pattern.search(text)
        if not match:
            return None 

        triggered_word = match.group(0).lower() 
        span_start, span_end = match.span()

        masked_text = text[:span_start] + "<mask>" + text[span_end:]
        predictions = self.fill_mask(masked_text, top_k=20) 
        
        candidates = []
        for p in predictions:
            word = p['token_str'].strip().lower()
            if word.isalpha() and len(word) > 2 and word != triggered_word:
                candidates.append(word)

        original_embedding = self.get_embedding(text)
        approved_suggestions = []

        for word in candidates:
            if word in self.blocklist or word in self.all_biased_terms:
                continue

            new_sentence = text[:span_start] + word + text[span_end:]
            new_embedding = self.get_embedding(new_sentence)
            similarity = cosine_similarity(original_embedding, new_embedding)[0][0]

            if similarity > 0.60: 
                approved_suggestions.append((word, similarity))

        approved_suggestions.sort(key=lambda x: x[1], reverse=True)
        top_alternatives = [x[0] for x in approved_suggestions[:3]]

        category = "Agentic" if triggered_word in self.agentic_terms else "Communal"
        opposite_gender = "men" if category == 'Agentic' else "women"
        impact = "collaborative contributions" if category == 'Agentic' else "leadership capabilities"
        
        reason = (f"The word '{triggered_word}' is coded as '{category}'. "
                  f"In professional contexts, this is statistically attributed more to {opposite_gender}, "
                  f"potentially minimizing {impact}.")

        return {
            "type": "agentic_communal",
            "target_text": text[span_start:span_end], 
            "position": {"start": span_start, "end": span_end},
            "description": reason,
            "suggestion": f"Consider using: {', '.join(top_alternatives)}" if top_alternatives else "Consider neutral phrasing",
            "alternatives": top_alternatives,
            "severity": "low",
            "confidence": res['score']
        }