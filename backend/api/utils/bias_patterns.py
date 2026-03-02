from enum import Enum
from typing import Dict, List, Set, Tuple

AGENTIC_LIST = [
    "active", "adventurous", "aggressive", "ambitious",
    "assertive", "autonomous", "bold", "bossy",
    "calculating", "challenging", "commanding", "competitive",
    "confident", "confrontational", "controlling", "courageous",
    "daring", "demanding", "determined",
    "dominant", "domineering", "driven", "enterprising",
    "fearless", "forceful", "goal-oriented", "hard-headed",
    "independent", "individualistic", "industrious",
    "influential", "instrumental", "leader-like",
    "masterful", "objective", "opinionated", "opportunistic",
    "outgoing", "overbearing", "persistent", "persuasive",
    "powerful", "pragmatic", "proactive", "pushy",
    "rational", "relentless", "resilient", "resolute",
    "risk-taking", "ruthless", "self-assured", "self-directed",
    "self-reliant", "self-sufficient", "status-seeking",
    "strategic", "strong", "task-focused", "tough",
    "uncompromising", "unwavering", "vigorous", "willful",
    "abrasive", "blunt", "direct", "outspoken", "forceful",
    "headstrong", "high-handed", "imperial", "in-charge",
    "managerial", "top-down", "directive",
    "action-oriented", "dynamic", "energetic", "fierce",
    "go-getter", "hard-driving", "high-achieving",
    "high-performing", "intense", "tenacious", "tireless",
    "astute", "incisive", "insightful", "methodical",
    "sharp", "shrewd", "systematic", "visionary"
]

COMMUNAL_LIST = [
    "accommodating", "affable", "affectionate", "agreeable", "altruistic",
    "amiable", "benevolent", "caring", "collaborative",
    "communal", "compassionate", "conciliatory", "connected",
    "considerate", "cooperative", "cordial",
    "deferential", "diplomatic",
    "empathetic", "encouraging", "forgiving",
    "friendly", "generous", "gentle", "giving",
    "harmonious", "helpful", "honest", "humane",
    "humble", "inclusive", "interpersonal", "intuitive",
    "kind", "loyal", "merciful", "modest",
    "moral", "nurturing", "obliging",
    "open-hearted", "patient", "polite", "prosocial",
    "relational", "selfless", "sensitive", "sharing",
    "sincere", "social", "soft-spoken",
    "supportive", "sympathetic", "tactful", "tender",
    "thoughtful", "trustworthy", "understanding",
    "unselfish", "warm", "yielding",
    "docile", "meek", "submissive", "servile",
    "passive", "dependent", "timid", "unassuming",
    "reserved", "quiet"
]

GENDERED_ROLES = {
    "rifleman": "M", "policeman": "M", "fireman": "M", "king": "M", "actor": "M",
    "waiter": "M", "steward": "M", "hero": "M", "uncle": "M", "father": "M", 
    "brother": "M", "son": "M", "man": "M", "boy": "M", "gentleman": "M",
    "lad": "M", "guy": "M", "fellow": "M", "chap": "M", "bloke": "M", "mr": "M", 
    "sir": "M", "lord": "M", "prophet": "M", "monk": "M", "prince": "M",
    "husband": "M", "groom": "M", "grandson": "M",
    
    "riflewoman": "F", "policewoman": "F", "firewoman": "F", "queen": "F", 
    "actress": "F", "waitress": "F", "stewardess": "F", "heroine": "F",
    "aunt": "F", "mother": "F", "sister": "F", "daughter": "F", "woman": "F",
    "girl": "F", "lady": "F", "mrs": "F", "ms": "F", "madam": "F", "nun": "F",
    "princess": "F", "wife": "F", "bride": "F", "granddaughter": "F"
}

PRONOUN_MAP = {
    "he": "M", "him": "M", "his": "M", "himself": "M",
    "she": "F", "her": "F", "hers": "F", "herself": "F"
}

MALE_MODIFIERS = {"male", "man", "boy", "gentleman", "mr", "mr.", "masculine"}
FEMALE_MODIFIERS = {"female", "woman", "lady", "girl", "mrs", "mrs.", "ms", "ms.", "feminine"}

FREQUENCY_ADVERBS = {
    "always", "constantly", "continually", "forever", "usually", "often", 
    "never", "typically", "generally", "frequently", "rarely", "seldom"
}

OBLIGATION_MODALS = {"should", "must", "ought", "need"} 
PREDICTION_MODALS = {"will", "would", "can", "could", "may", "might", "shall"}
ALL_MODALS = OBLIGATION_MODALS | PREDICTION_MODALS
CONDITIONAL_MARKERS = {"if", "unless", "whenever", "whether"}

class BiasType(str, Enum):
    PRONOUN = "pronoun"
    AGENTIC_COMMUNAL = "agentic_communal"
    GENDERED_TERMS = "gendered_terms"
    SEMANTIC = "semantic"
    STEREOTYPE = "stereotype"

class BiasPatterns:    
    BIAS_COLORS: Dict[BiasType, str] = {
        BiasType.PRONOUN: "#ff6b6b",  
        BiasType.AGENTIC_COMMUNAL: "#ffd166",  
        BiasType.GENDERED_TERMS: "#06d6a0",  
        BiasType.SEMANTIC: "#118ab2",  
        BiasType.STEREOTYPE: "#9d4edd",  
    }
    
    @classmethod
    def get_bias_color(cls, bias_type: BiasType) -> str:
        return cls.BIAS_COLORS.get(bias_type, "#cccccc")