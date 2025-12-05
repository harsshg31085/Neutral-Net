from enum import Enum
from typing import Dict, List, Set, Tuple

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
    
    AGENTIC_TERMS: Dict[str, Dict] = {
        "aggressive": {"suggestion": "Consider 'assertive' or 'determined'"},
        "assertive": {"suggestion": "Consider 'confident' or 'clear'"},
        "competitive": {"suggestion": "Consider 'driven' or 'ambitious'"},
        "dominant": {"suggestion": "Consider 'influential' or 'leading'"},
        "visionary": {"suggestion": "Consider 'innovative' or 'forward-thinking'"},
    }
    
    COMMUNAL_TERMS: Dict[str, Dict] = {
        "emotional": {"suggestion": "Consider 'passionate' or 'empathetic'"},
        "nurturing": {"suggestion": "Consider 'supportive' or 'developing'"},
        "sensitive": {"suggestion": "Consider 'perceptive' or 'attentive'"},
        "supportive": {"suggestion": "Consider 'collaborative' or 'helpful'"},
    }
    
    STEREOTYPE_PATTERNS: List[Tuple[str, str, str]] = [
        ('nurse', "female", "Consider removing gender assumption - nurses can be any gender"),
        ('engineer', "male", "Consider removing gender assumption - engineers can be any gender"),
        ('secretary', "female", "Consider 'administrative professional(s)'"),
        ('chairman', "male", "Consider 'chairperson' or 'chair'"),
        ('policeman', "male", "Consider 'police officer(s)'"),
        ('stewardess', "female", "Consider 'flight attendant(s)'"),
        ('waitress', "female", "Consider 'server(s)' or 'waitstaff'"),
        ('actress', "female", "Consider 'actor(s)'"),
        ('firemen', "male", "Consider 'firefighter(s)'"),
        ('mailmen', "male", "Consider 'mail carrier(s)' or 'postal worker(s)'"),
        ('mankind', "male", "Consider 'humankind' or 'humanity'"),
        ('manpower', "male", "Consider 'workforce' or 'personnel'"),
        ('salesmen', "male", "Consider 'salesperson' or 'sales representative(s)'"),
        ('congressmen', "male", "Consider 'member(s) of congress' or 'legislator(s)'"),
    ]
    
    @classmethod
    def get_bias_color(cls, bias_type: BiasType) -> str:
        return cls.BIAS_COLORS.get(bias_type, "#cccccc")