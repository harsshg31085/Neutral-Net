import torch
from torch.nn.functional import softmax
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM
import uuid
import os
from django.conf import settings

class StereotypeDetector:
    """
    Detects and rewrites gender stereotypes using a dual-model custom pipeline

    The engine relies on two models, both fine tuned specifically for this application:
        - Sequence classification model to determine the probability of a stereotype.
        - Seq2Seq Language Model to generate rewrites and reasons for the stereotype
    """
    def __init__(self):
        # Both the models are hosted on huggingface
        self.HF_REPO_ID = "Harssh3108/neutral-net-models"
        self.THRESHOLD = 0.85

        try:
            self.detector_tokenizer = AutoTokenizer.from_pretrained(self.HF_REPO_ID, subfolder="stereotype_detector")
            self.detector_model = AutoModelForSequenceClassification.from_pretrained(self.HF_REPO_ID, subfolder="stereotype_detector")
            self.detector_model.eval()
        except Exception as e:
            self.detector_model = None

        try:
            self.rewriter_tokenizer = AutoTokenizer.from_pretrained(self.HF_REPO_ID, subfolder="stereotype_fixer")
            self.rewriter_model = AutoModelForSeq2SeqLM.from_pretrained(self.HF_REPO_ID, subfolder="stereotype_fixer")
            self.rewriter_model.eval()
        except Exception as e:
            self.rewriter_model = None

    def predict_bias(self, text):
        """
        Calculates the probability that a sentence contains a gender stereotype.

        Uses a fine-tuned classification model to generate logits, applies
        softmax activation to generate probabilities, and checks against a threshold
        """
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
        """
        Generates neutral rewrite and reasoning for the bias.

        Uses beam search encoding on the Seq2Seq model to ensure high quality,
        grammatically correct outputs.
        """
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
        """
        Evaluates a sentences, combining the response of both the models
        """
        if not sentence.strip(): return None

        prediction = self.predict_bias(sentence)
        
        if prediction['bias']:
            reason, rewrite = self.fix_bias(sentence)

            if rewrite == "[MANUAL REWRITE]": # Model response when it deems a sentence unfixable
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