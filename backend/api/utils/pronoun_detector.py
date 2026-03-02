import spacy
import uuid
from fastcoref import FCoref
from .bias_patterns import (
    GENDERED_ROLES, PRONOUN_MAP, MALE_MODIFIERS, FEMALE_MODIFIERS,
    FREQUENCY_ADVERBS, OBLIGATION_MODALS, PREDICTION_MODALS, ALL_MODALS, CONDITIONAL_MARKERS
)

class PronounBiasDetector:
    def __init__(self):
        print("Loading Pronoun Coreference Models...")
        self.resolver = FCoref(device='cpu', enable_progress_bar=False)
        
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            from spacy.cli import download
            download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    @staticmethod
    def get_best_head_span(spans):
        best_span = spans[0]
        best_score = 0
        for span in spans:
            root = span.root
            score = 0
            if root.ent_type_:
                score = 2
            elif root.pos_ in ["NOUN", "PROPN"]:
                score = 1
            if score > best_score:
                best_score = score
                best_span = span
        return best_span

    @staticmethod
    def get_governing_verb(token):
        head = token.head
        while head.pos_ not in ["VERB", "AUX"] and head.head != head:
            head = head.head
        return head if head.pos_ in ["VERB", "AUX"] else None

    @staticmethod
    def get_modifier_gender(span):
        for child in span.root.children:
            if child.lower_ in MALE_MODIFIERS:
                return "M"
            if child.lower_ in FEMALE_MODIFIERS:
                return "F"
        return None

    @staticmethod
    def has_present_aux(verb):
        for child in verb.children:
            if child.dep_ in ["aux", "auxpass"] and child.lemma_ == "be":
                if child.tag_ in ["VBZ", "VBP"]:
                    return True
        return False

    @staticmethod
    def has_frequency_adverb(verb):
        for child in verb.children:
            if child.dep_ == "advmod" and child.lemma_.lower() in FREQUENCY_ADVERBS:
                return True
        return False

    @classmethod
    def is_strictly_episodic(cls, verb):
        if not verb: return False
        if cls.has_frequency_adverb(verb): return False
        for child in verb.children:
            if child.dep_ == "aux" and child.lemma_.lower() in ALL_MODALS:
                return False
        if verb.tag_ == "VBD": return True
        if verb.tag_ == "VBG" and cls.has_present_aux(verb): return True
        return False

    @staticmethod
    def is_role_noun(span):
        root = span.root
        if root.pos_ != "NOUN": return False
        if root.ent_type_ in ["PERSON", "ORG", "GPE"]: return False
        return True

    @classmethod
    def is_generic_context(cls, verb, is_anchored_entity, is_definite, recursion_depth=0):
        if not verb or recursion_depth > 5: return False
        
        if verb.dep_ in ["xcomp", "ccomp", "advcl", "conj"]:
            parent = cls.get_governing_verb(verb)
            if parent and parent != verb:
                if not cls.is_generic_context(parent, is_anchored_entity, is_definite, recursion_depth + 1):
                    return False

        found_modal = None
        for child in verb.children:
            if child.dep_ == "aux" and child.lemma_.lower() in ALL_MODALS:
                found_modal = child.lemma_.lower()
                break

        if found_modal:
            if found_modal in OBLIGATION_MODALS: return not is_anchored_entity
            if found_modal in PREDICTION_MODALS: return not (is_anchored_entity or is_definite)

        for child in verb.children:
            if child.dep_ == "mark" and child.lemma_.lower() in CONDITIONAL_MARKERS: return True
            if child.dep_ == "advcl":
                for g in child.children:
                    if g.dep_ == "mark" and g.lemma_.lower() in CONDITIONAL_MARKERS: return True

        if verb.tag_ in ["VBP", "VBZ"] and not is_anchored_entity: return True
        if verb.tag_ == "VBN" and cls.has_present_aux(verb) and not is_anchored_entity: return True
        
        return False

    def analyze(self, text: str):
        if not text.strip(): return []
        
        preds = self.resolver.predict(texts=[text], is_split_into_words=False)
        clusters = preds[0].get_clusters(as_strings=False)
        
        doc = self.nlp(text)
        biases = []

        suggestion_map = {
            "he": "they", "she": "they",
            "him": "them", "her": "them",
            "his": "their", "hers": "their",
            "himself": "themselves", "herself": "themselves"
        }

        for cluster_indices in clusters:
            spans = [doc.char_span(s[0], s[1]) for s in cluster_indices if doc.char_span(s[0], s[1]) is not None]
            if not spans: continue

            cluster_words = {s.text.lower() for s in spans}
            if not any(p in cluster_words for p in PRONOUN_MAP): continue

            head_span = self.get_best_head_span(spans)
            head_root = head_span.root

            is_anchored_entity, is_definite = False, False
            for span in spans:
                root = span.root
                if root.ent_type_ in ["PERSON", "ORG", "GPE"]:
                    is_anchored_entity = True
                    break
                if root.pos_ in ["NOUN", "PROPN"]:
                    for child in root.children:
                        if child.lemma_ in ["this", "that", "my", "your", "our"]:
                            is_anchored_entity = True
                            break
                        if child.lemma_ == "the":
                            is_definite = True
                if is_anchored_entity: break

            if not is_anchored_entity:
                for span in spans:
                    verb = self.get_governing_verb(span.root)
                    if self.is_strictly_episodic(verb):
                        is_anchored_entity = True
                        break

            role_gender = GENDERED_ROLES.get(head_root.lemma_.lower())
            mod_gender = self.get_modifier_gender(head_span)
            if mod_gender: role_gender = mod_gender

            has_male = any(w in PRONOUN_MAP and PRONOUN_MAP[w] == "M" for w in cluster_words)
            has_female = any(w in PRONOUN_MAP and PRONOUN_MAP[w] == "F" for w in cluster_words)
            if has_male and has_female: continue

            for span in spans:
                token = span.root
                word = token.text.lower()

                if word not in PRONOUN_MAP: continue

                pronoun_gender = PRONOUN_MAP[word]
                if role_gender and role_gender == pronoun_gender: continue

                verb = self.get_governing_verb(token)
                is_bias = False
                reason_text = ""

                if (self.is_role_noun(head_span) and verb is not None and not is_anchored_entity
                    and not self.is_strictly_episodic(verb) and 
                    (verb.tag_ in ["VBP", "VBZ"] or any(c.dep_ == "aux" and c.lemma_.lower() in OBLIGATION_MODALS for c in verb.children))):
                    is_bias = True
                    reason_text = f"The pronoun '{word}' is tied to a generic role rather than a specific person."
                
                elif self.is_generic_context(verb, is_anchored_entity, is_definite):
                    is_bias = True
                    reason_text = f"The pronoun '{word}' is used in a generic context."

                if is_bias:
                    alt_word = suggestion_map.get(word, "they")
                    
                    biases.append({
                        "id": str(uuid.uuid4()),
                        "type": "pronoun",
                        "text": str(token.text),
                        "description": reason_text,
                        "suggestion": f"Consider using a gender-neutral pronoun like '{alt_word}'.",
                        "alternatives": [alt_word],
                        "position": {
                            "start": span.start_char,
                            "end": span.end_char
                        }
                    })

        return biases