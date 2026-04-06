import spacy
import torch
import uuid
import time
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from gliner import GLiNER

class AgenticCommunalDetector:
    """
    Detects subconscious tonal skew (Agentic vs Communal) in text relating to human subjects.

    The architecture relies on multiple models:
        - spacy: Grammatical dependency parsing and isolate adjectives and verbs.
        - gliner: Zero shot NER to identify human subjects.
        - sentence-transformers: Calculate cosine similarity of words against pre-defined 
        Agentic and Communal anchors.
        - distilroberta - Context-aware synonym generation for replacements.
    """
    def __init__(self):        
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            from spacy.cli import download
            download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.entity_model = GLiNER.from_pretrained("urchade/gliner_small-v2.1")
        self.fixer = pipeline("fill-mask", model="distilroberta-base")
                
        self.human_anchors = self.encoder.encode([
            "human", "person", "man", "woman", "someone", "people",
            "worker", "employee", "staff", "leader", "professional",
            "expert", "individual", "boy", "girl"
        ])
       
        self.non_human_anchors = self.encoder.encode([
            "animal", "creature", "species", "beast", "organism",
            "object", "machine", "tool", "software", "thing", "place", 
            "concept", "idea", "state", "abstract", "process",
            "plan", "method", "structure", "device", "document",
            "action", "effort", "work", "atmosphere", "environment", "condition",
            "market", "sensor", "detector", "system", "algorithm", "camera",
            "group", "team", "committee", "board", "management", "investors", "critics"
        ])

        self.agentic_concept = self.encoder.encode([
            "dominant", "aggressive", "ambitious", "forceful", "leader", "decisive", 
            "intellectual", "confident", "assertive", "competitive", "logical", "strategic",
            "command", "commands", "commanding", "imposing", "charge", 
            "defensive" 
        ])

        self.communal_concept = self.encoder.encode([
            "caring", "gentle", "supportive", "sensitive", "collaborative", "helper", 
            "compassionate", "honest", "understanding", "loyal", "kind", "emotional"
        ])

        self.functional_concept = self.encoder.encode([
            "direction", "movement", "speed", "quantity", "size", "time", "location", 
            "physical", "technical", "mechanical", "code", "software", "system",
            "future", "forward", "back", "clean"
        ])

        self.technical_containers = {
            "strategy", "timeline", "architecture", "approach", "framework", 
            "policy", "plan", "method", "system", "process", "tactic", 
            "output", "result", "deadline", "project", "market", "legislation",
            "sensor", "code", "database", "bond", "fund", "presentation"
        }
        
        self.last_subject = None
        self.last_subject_was_human = False

    def get_dynamic_subject_type(self, text, subject_text):
        """
        Uses GLINER to classify subject
        """
        if not subject_text: return "UNKNOWN"        
        labels = [
            "Person", "Job Role", "Family Member", "Individual", 
            "Animal", 
            "Group of People", "Organization", "Technology", "Inanimate Object", "Abstract Concept"
        ]       
        entities = self.entity_model.predict_entities(text, labels, threshold=0.3)       
        for ent in entities:
            if subject_text.lower() in ent['text'].lower() or ent['text'].lower() in subject_text.lower():
                label = ent['label']
                if label in ["Person", "Job Role", "Family Member", "Individual"]:
                    return "HUMAN"
                elif label in ["Animal"]:
                    return "ANIMAL"
                elif label in ["Group of People", "Organization", "Technology", "Inanimate Object", "Abstract Concept"]:
                    return "NON_HUMAN"                    
        return "UNKNOWN"

    def get_subject(self, text):
        """
        Uses spacy (dependency parsing) to extract the nominal subject
        """
        doc = self.nlp(text)
        candidates = []

        for token in doc:
            if "nsubj" in token.dep_:
                candidates.append(token)
       
        for cand in candidates:
            if cand.text.lower() in ["it", "this", "that", "which", "who", "whom"]:
                continue 
            
            if cand.text.lower() in ["he", "she", "they", "we", "i", "you"]: return cand.text
            if self.is_noun_human(cand.text): return cand.text
        
        for cand in candidates:
            if self.has_human_possessive(cand):
                for child in cand.children:
                    if child.dep_ == "poss" and child.text.lower() in ["her", "his", "their", "my", "our", "your"]:
                        return child.text

        return candidates[0].text if candidates else None
    
    def is_noun_human(self, noun):        
        noun_vec = self.encoder.encode(noun)
        human_sim = util.cos_sim(noun_vec, self.human_anchors).max().item()
        non_human_sim = util.cos_sim(noun_vec, self.non_human_anchors).max().item()
        return human_sim > (non_human_sim - 0.05)

    def is_explicitly_human(self, word):        
        vec = self.encoder.encode(word)
        human_sim = util.cos_sim(vec, self.human_anchors).max().item()
        non_human_sim = util.cos_sim(vec, self.non_human_anchors).max().item()
        return human_sim > 0.35 and human_sim > non_human_sim

    def has_human_possessive(self, token):
        for child in token.children:
            if child.dep_ == "poss" and child.text.lower() in ["her", "his", "their", "my", "our", "your"]:
                return True
        return False

    def find_biased_spans(self, text, skew_verdict, verbose=False):
        """
        Iterates through adjectives and verbs, calculates their semantic distance from bias anchors
        and flags them if they modify a human subject.
        """
        doc = self.nlp(text)
        spans = []
        
        for token in doc:
            if token.pos_ not in ["ADJ", "ADV", "VERB", "NOUN"]: continue
            if token.is_stop or len(token.text) < 3: continue
            if token.dep_ == 'pobj': continue
            if token.lemma_.lower() in self.technical_containers:
                continue
            if any(child.dep_ == 'neg' for child in token.children): continue
            
            target_noun = None
            
            if token.head.pos_ in ['NOUN', 'PRON', 'PROPN']:
                target_noun = token.head
            elif token.head.pos_ in ['VERB', 'AUX']:
                for child in token.head.children:
                    if child.dep_ in ['nsubj', 'nsubjpass']:
                        target_noun = child
                        break
            
            if target_noun:
                is_human_target = False
                if target_noun.text.lower() in ["he", "she", "they", "we", "i", "you"]:
                    is_human_target = True
                else:
                    is_human_target = self.is_noun_human(target_noun.text) or self.has_human_possessive(target_noun)
                
                if not is_human_target:
                    if verbose: print(f"[DEBUG] Skip '{token.text}': Target '{target_noun.text}' is a Group/Non-Human.")
                    continue
                elif verbose:
                    print(f"[DEBUG] Checking Word '{token.text}' -> Target '{target_noun.text}' is Valid Human")

            word_vec = self.encoder.encode(token.text)
            
            agentic_sim = util.cos_sim(word_vec, self.agentic_concept).mean().item()
            communal_sim = util.cos_sim(word_vec, self.communal_concept).mean().item()
            functional_sim = util.cos_sim(word_vec, self.functional_concept).mean().item() 
            
            max_bias = max(agentic_sim, communal_sim)
            if functional_sim > max_bias: continue

            bias_type = None
            score = 0
            
            if max_bias > 0.35:
                if verbose: print(f"[DEBUG] -> FLAGGED '{token.text}' (Score: {max_bias:.2f})")
                if agentic_sim > communal_sim:
                    bias_type = "Agentic"
                    score = agentic_sim
                else:
                    bias_type = "Communal"
                    score = communal_sim
            
            if bias_type:
                replacements = self.generate_replacements(text, token, bias_type)
                reason = self.generate_span_reason(token.text, bias_type, skew_verdict)
                
                start_char = token.idx
                end_char = token.idx + len(token.text)

                spans.append({
                    "word": token.text,
                    "span": [start_char, end_char],
                    "type": bias_type,
                    "score": round(score, 2),
                    "reason": reason,
                    "replacements": replacements
                })
        return spans
    
    def generate_span_reason(self, word, bias_type, skew_verdict):
        if bias_type == "Agentic":
            if skew_verdict == "Skewed Agentic":
                return f"'{word}' contributes to a heavy Agentic skew. In excess, this implies hostility rather than leadership."
            return f"'{word}' is Agentic. Ensure this trait is balanced with communal feedback."
        else: 
            if skew_verdict == "Skewed Communal":
                return f"'{word}' contributes to a heavy Communal skew. This can inadvertently minimize technical competence."
            return f"'{word}' is Communal. Ensure this doesn't overshadow leadership traits."

    def generate_replacements(self, text, token, bias_type):
        """
        Uses Distilroberta to generate contextual synonyms, and filters them
        via cosine similarity to ensure they are tonally neutral
        """
        masked_text = text[:token.idx] + self.fixer.tokenizer.mask_token + text[token.idx + len(token.text):]
        preds = self.fixer(masked_text, top_k=60)
        
        bad_concept = self.communal_concept if bias_type == "Communal" else self.agentic_concept
        original_vec = self.encoder.encode(token.text)
        original_sent_vec = self.encoder.encode(text)

        perfect_matches = []
        soft_matches = []
        
        for p in preds:
            word = p['token_str'].strip().lower()
            if not word.isalpha() or word == token.text.lower(): continue
            
            temp_text = text[:token.idx] + word + text[token.idx + len(token.text):]
            temp_doc = self.nlp(temp_text)
            if temp_doc[token.i].pos_ != token.pos_: continue

            word_vec = self.encoder.encode(word)
            cand_badness = util.cos_sim(word_vec, bad_concept).mean().item()
            if cand_badness >= 0.35: continue
            
            word_fidelity = util.cos_sim(original_vec, word_vec).mean().item()
            if word_fidelity < 0.5: continue 

            cand_sent_vec = self.encoder.encode(temp_text)
            context_fidelity = util.cos_sim(original_sent_vec, cand_sent_vec).item()
            if context_fidelity < 0.85: continue

            if word_fidelity > 0.6:
                perfect_matches.append(word)
            else:
                soft_matches.append(word)
        
        final_suggestions = perfect_matches
        if len(final_suggestions) < 3:
            needed = 3 - len(final_suggestions)
            final_suggestions.extend(soft_matches[:needed])
            
        return final_suggestions[:3] if final_suggestions else ["(No neutral synonym found)"]

    def analyze_sentence(self, text, verbose=False):
        """
        Resolves subjects, calculates global sentence skew and triggers targeted span extraction
        if threshold exceeded.
        """        
        raw_subject = self.get_subject(text)
        if verbose: print(f"[DEBUG] Raw Subject Found: '{raw_subject}'")
        
        is_pronoun = raw_subject and raw_subject.lower() in ["he", "she", "it", "they", "this", "that"]
        current_subject_is_human = True 
        dynamic_type = "UNKNOWN"
        
        if raw_subject:
            if is_pronoun: 
                if verbose: print(f"[DEBUG] Decision: Pronoun detected. Tracking back...")
                if self.last_subject and not self.last_subject_was_human:
                    if verbose: print(f"[DEBUG] -> Previous subject '{self.last_subject}' was Non-Human. Resetting.")
                    current_subject_is_human = False
                elif raw_subject.lower() in ["it", "this", "that"]:
                    current_subject_is_human = False
            else:
                dynamic_type = self.get_dynamic_subject_type(text, raw_subject)
                
                if dynamic_type == "HUMAN":
                    if verbose: print(f"[DEBUG] Decision: GLiNER classified '{raw_subject}' as HUMAN")
                    current_subject_is_human = True
                    self.last_subject = raw_subject
                    self.last_subject_was_human = True
                elif dynamic_type in ["NON_HUMAN", "ANIMAL"]:
                    if verbose: print(f"[DEBUG] Decision: GLiNER classified '{raw_subject}' as {dynamic_type}")
                    current_subject_is_human = False
                    self.last_subject = raw_subject
                    self.last_subject_was_human = False
                else:
                    if verbose: print(f"[DEBUG] GLiNER unsure. Falling back to Vector Space...")
                    noun_vec = self.encoder.encode(raw_subject)
                    h_sim = util.cos_sim(noun_vec, self.human_anchors).max().item()
                    nh_sim = util.cos_sim(noun_vec, self.non_human_anchors).max().item()
                    if verbose: print(f"[DEBUG] Vector Check: Human={h_sim:.3f} vs Non-Human={nh_sim:.3f}")
                    
                    current_subject_is_human = h_sim > nh_sim
                    self.last_subject = raw_subject
                    self.last_subject_was_human = current_subject_is_human

        if not current_subject_is_human:
            if verbose: print(f"[DEBUG] EXIT: Subject classified as Non-Human.")
            return [] 

        sent_vec = self.encoder.encode(text)
        agentic_score = util.cos_sim(sent_vec, self.agentic_concept).mean().item()
        communal_score = util.cos_sim(sent_vec, self.communal_concept).mean().item()
        
        if verbose: print(f"[DEBUG] Sentence Scores: Agentic={agentic_score:.3f}, Communal={communal_score:.3f}")

        is_strong_human = (dynamic_type == "HUMAN") if not is_pronoun else False
        if is_strong_human and verbose: print("[DEBUG] Strong Human detected -> BYPASSING THRESHOLD")

        if not is_strong_human:
            if max(agentic_score, communal_score) < 0.14:
                if verbose: print("[DEBUG] EXIT: Failed Global Threshold")
                return []

        total_intensity = agentic_score + communal_score
        if total_intensity < 0.01: communal_ratio = 0.5
        else: communal_ratio = communal_score / total_intensity
        
        skew_verdict = "Balanced"
        if communal_ratio > 0.65: skew_verdict = "Skewed Communal"
        elif communal_ratio < 0.35: skew_verdict = "Skewed Agentic"

        spans = self.find_biased_spans(text, skew_verdict, verbose)

        formatted_biases = []
        for s in spans:
            alts = s['replacements']
            if not alts or alts == ["(No neutral synonym found)"]:
                suggestion_text = "Consider rephrasing to be more neutral."
                alts = []
            else:
                suggestion_text = f"Consider using: {', '.join(alts)}"

            formatted_biases.append({
                "id": str(uuid.uuid4()),
                "type": "agentic_communal",
                "text": s["word"],
                "description": s["reason"],
                "suggestion": suggestion_text,
                "alternatives": alts,
                "position": {
                    "start": s["span"][0],
                    "end": s["span"][1]
                },
                "severity": "low",
                "confidence": s["score"]
            })

        if verbose:
            if formatted_biases:
                print(f"[DEBUG] DETECTED {len(formatted_biases)} agentic/communal biases.")
            else:
                print(f"[DEBUG] NEUTRAL. No biases found.")

        return formatted_biases