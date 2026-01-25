import torch
from torch.nn.functional import softmax
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM
import uuid
import os
from django.conf import settings

class StereotypeDetector:
    def __init__(self):
        self.DETECTOR_PATH = os.path.join(settings.BASE_DIR, "models", "stereotype_detector")
        self.REWRITER_PATH = os.path.join(settings.BASE_DIR, "models", "stereotype_fixer")
        self.THRESHOLD = 0.85

        try:
            self.detector_tokenizer = AutoTokenizer.from_pretrained(self.DETECTOR_PATH)
            self.detector_model = AutoModelForSequenceClassification.from_pretrained(self.DETECTOR_PATH)
            self.detector_model.eval()
        except Exception as e:
            print(f"FAILED to load Stereotype Classifier from {self.DETECTOR_PATH}. Error: {e}")
            self.detector_model = None

        try:
            self.rewriter_tokenizer = AutoTokenizer.from_pretrained(self.REWRITER_PATH)
            self.rewriter_model = AutoModelForSeq2SeqLM.from_pretrained(self.REWRITER_PATH)
            self.rewriter_model.eval()
        except Exception as e:
            print(f"FAILED to load Stereotype Rewriter from {self.REWRITER_PATH}. Error: {e}")
            self.rewriter_model = None

    def predict_bias(self, text):
        if not self.detector_model: return {"bias": False, "confidence": 0.0}

        inputs = self.detector_tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=128,
        )

        with torch.no_grad():
            logits = self.detector_model(**inputs).logits

        probs = softmax(logits, dim=-1)
        bias_score = probs[0, 1].item()

        return {
            "bias": bias_score >= self.THRESHOLD,
            "confidence": bias_score,
        }

    def fix_bias(self, text):
        if not self.rewriter_model: return "Model unavailable", text

        input_text = f"Fix Gender Bias: {text}"
        inputs = self.rewriter_tokenizer(input_text, return_tensors="pt")

        with torch.no_grad():
            outputs = self.rewriter_model.generate(
                **inputs,
                max_length=128,
                num_beams=4,
                early_stopping=True
            )

        result = self.rewriter_tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        reason = "Automated Rewrite"
        rewrite = result

        if "|" in result:
            parts = result.split("|")
            if len(parts) >= 2:
                reason_part = parts[0].strip()
                rewrite_part = parts[1].strip()
                reason = reason_part.replace("Reason:", "").strip()
                rewrite = rewrite_part.replace("Rewrite:", "").strip()
        elif "Rewrite:" in result:
            rewrite = result.split("Rewrite:")[-1].strip()
            
        return reason, rewrite

    def analyze_sentence(self, sentence):
        if not sentence.strip(): return None

        prediction = self.predict_bias(sentence)
        
        if prediction['bias']:
            reason, rewrite = self.fix_bias(sentence)

            if rewrite == "[MANUAL REWRITE]":
                return {
                    "id": str(uuid.uuid4()),
                    "text": sentence,
                    "type": "stereotype",
                    "description": reason,
                    "suggestion": "Consider removing generalizations based on gender.",
                    "alternatives": [],
                    "confidence": prediction["confidence"],
                    "position": {
                        "start": 0,
                        "end": len(sentence)
                    }
                }
            else:
                return {
                    "id": str(uuid.uuid4()),
                    "text": sentence, 
                    "type": "stereotype", 
                    "description": reason,
                    "suggestion": f"Consider rewriting the sentence to: {rewrite}",
                    "alternatives": [rewrite],
                    "confidence": prediction['confidence'],
                    "position": {
                        "start": 0,             
                        "end": len(sentence)    
                    }
                }

        return None