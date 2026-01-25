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
    
    PRONOUN_PATTERNS: Dict[str, Dict] = {
        r"\bhe\b": {
            "type": BiasType.PRONOUN,
            "suggestion": "Consider using 'they' for gender-neutral reference",
            "alternatives": ["they", "the person", "the individual"]
        },
        r"\bshe\b": {
            "type": BiasType.PRONOUN,
            "suggestion": "Consider using 'they' for gender-neutral reference",
            "alternatives": ["they", "the person", "the individual"]
        },
        r"\bhim\b": {
            "type": BiasType.PRONOUN,
            "suggestion": "Consider using 'them' for gender-neutral reference",
            "alternatives": ["them", "the person", "the individual"]
        },
        r"\bher\b": {
            "type": BiasType.PRONOUN,
            "suggestion": "Consider using 'them' for gender-neutral reference",
            "alternatives": ["them", "the person", "the individual"]
        },
        r"\bhis\b": {
            "type": BiasType.PRONOUN,
            "suggestion": "Consider using 'their' for gender-neutral reference",
            "alternatives": ["their", "the person's", "the individual's"]
        },
        r"\bhers\b": {
            "type": BiasType.PRONOUN,
            "suggestion": "Consider using 'theirs' for gender-neutral reference",
            "alternatives": ["theirs", "the person's", "the individual's"]
        }
    }
    
    @classmethod
    def get_bias_color(cls, bias_type: BiasType) -> str:
        return cls.BIAS_COLORS.get(bias_type, "#cccccc")