from enum import Enum
from typing import Dict, List, Set, Tuple

AGENTIC_LIST = [
    "active", "adventurous", "aggressive", "ambitious", "analytical", 
    "arrogant", "assertive", "authoritative", "autocratic", "autonomous", 
    "boastful", "bold", "bossy", "calculating", "cerebral", 
    "challenging", "commanding", "compelling", "competent", "competitive", 
    "confident", "confrontational", "controlling", "courageous", "daring", 
    "decisive", "demanding", "determined", "dictatorial", "dominant", 
    "domineering", "driven", "efficacious", "efficient", "egotistical", 
    "enterprising", "fearless", "forceful", "goal-oriented", "hard-headed", 
    "independent", "individualistic", "industrious", "influential", "innovative", 
    "intellectual", "instrumental", "intrusive", "leader-like", "logical", 
    "masterful", "monopolizing", "objective", "opinionated", "opportunistic", 
    "outgoing", "overbearing", "persistent", "persuasive", "powerful", 
    "pragmatic", "proactive", "pushy", "rational", "relentless", 
    "resilient", "resolute", "risk-taking", "ruthless", "self-assured", 
    "self-centered", "self-directed", "self-reliant", "self-sufficient", "status-seeking", 
    "strategic", "strong", "task-focused", "tough", "uncompromising", 
    "unwavering", "vigorous", "willful","abrasive", "strident", "shrill", "cold", "frigid", "hostile", 
    "impulsive", "reckless", "combative", "obstinate", "rigid","rockstar", "ninja", "wizard", "hardcore", "maverick",
    "astute", "brilliant", "expert", "genius", "incisive", 
    "insightful", "knowledgeable", "methodical", "sharp", "shrewd", 
    "skilled", "smart", "systematic", "technical", "visionary",
    "alpha", "chief", "coercive", "directive", "executive", 
    "headstrong", "hierarchical", "high-handed", "imperial", "in-charge", 
    "managerial", "presidential", "principal", "superior", "top-down",
    "action-oriented", "blunt", "candid", "cutthroat", "direct", 
    "disruptive", "disruptor", "dynamic", "energetic", "explosive", 
    "extreme", "fierce", "frank", "go-getter", "hard-driving", 
    "high-achieving", "high-performing", "intense", "mighty", "outspoken", 
    "potent", "robust", "straightforward", "tenacious", "tireless",
    "aloof", "detached", "impersonal", "indifferent", "stoic", 
    "unemotional", "unsentimental", "withdrawn",
    "architect", "builder", "closer", "crusher", "guru", 
    "hustler", "killer", "kingpin", "legend", "pioneer", 
    "rainmaker", "shark", "titan", "trailblazer", "tycoon", "warrior"
]

COMMUNAL_LIST = [
    "accommodating", "affable", "affectionate", "agreeable", "altruistic", 
    "amiable", "benevolent", "caring", "chatty", "collaborative", 
    "communal", "compassionate", "conciliatory", "connected", "considerate", 
    "cooperative", "cordial", "deferential", "dependable", "diplomatic", 
    "docile", "empathetic", "encouraging", "faithful", "forgiving", 
    "friendly", "generous", "gentle", "giving", "gossipy", 
    "gullible", "harmonious", "helpful", "honest", "humane", 
    "humble", "inclusive", "interpersonal", "intuitive", "kind", 
    "loyal", "maternal", "meek", "merciful", "modest", 
    "moral", "naive", "nurturing", "obedient", "obliging", 
    "open-hearted", "paternal", "patient", "polite", "prosocial", 
    "relational", "selfless", "sensitive", "sentimental", "sharing", 
    "sincere", "social", "soft", "soft-spoken", "submissive", 
    "supportive", "sympathetic", "tactful", "tender", "thoughtful", 
    "trustworthy", "understanding", "unselfish", "warm", "yielding",
    "emotional", "moody", "hysterical", "dramatic", "fragile", 
    "clingy", "nagging", "irrational", "airheaded", "ditzy", 
    "fickle", "indecisive", "over-sensitive", "needy", "whiny",
    "adorable", "approachable", "bubbly", "charming", "cheerful", 
    "chipper", "delightful", "enthusiastic", "gracious", "likable", 
    "lovely", "nice", "perky", "pleasant", "smiley", 
    "sunny", "sweet", "upbeat", "vivacious", "winsome",
    "assistant-like", "committed", "conscientious", "dedicated", "devoted", 
    "diligent", "dutiful", "hard-working", "loyalist", "organized", 
    "reliable", "responsible", "self-sacrificing", "servile", "steadfast",
    "bashful", "cautious", "demure", "dependent", "fearful", 
    "feeble", "hesitant", "insecure", "mild", "passive", 
    "quiet", "reserved", "retiring", "shy", "timid", 
    "unassuming", "uncertain", "unsure", "weak", "withdrawn",
    "flustered", "frantic", "high-maintenance", "high-strung", "hypersensitive", 
    "neurotic", "over-emotional", "over-reactive", "panicky", "scatterbrained", 
    "tearful", "teary", "temperamental", "volatile",
    "domestic", "family-oriented", "homemaker", "matronly", "motherly"
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