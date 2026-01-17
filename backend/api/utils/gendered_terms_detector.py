import spacy
from sentence_transformers import CrossEncoder
import warnings
import uuid

warnings.filterwarnings("ignore")

class GenderedTermsDetector:
    def __init__(self):
        print("Loading Gendered Terms NLI Model... (this may take a moment)")
        self.nli_model = CrossEncoder('cross-encoder/nli-deberta-v3-base')
        
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spacy model 'en_core_web_sm'...")
            from spacy.cli import download
            download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

        self.safe_dets = {'the', 'this', 'that', 'these', 'those', 'my', 'our', 'your', 'his', 'her', 'its', 'their'}
        
        self.term_map = {
            "anchorman": "anchor",
            "businessman": "business executive",
            "businesswoman": "business executive",
            "cameraman": "camera operator",
            "chairman": "chairperson",
            "chairwoman": "chairperson",
            "draftsman": "drafter",
            "foreman": "supervisor",
            "freshman": "first-year student",
            "headmaster": "head of school",
            "headmistress": "head of school",
            "journeyman": "skilled worker",
            "landlord": "property owner",   
            "landlady": "property owner",   
            "layman": "layperson",
            "middleman": "intermediary",
            "newsman": "journalist",
            "newswoman": "journalist",
            "ombudsman": "ombuds",
            "postmaster": "postal manager",
            "salesman": "salesperson",
            "saleswoman": "salesperson",
            "spokesman": "spokesperson",
            "spokeswoman": "spokesperson",
            "statesman": "diplomat",
            "weatherman": "meteorologist",
            "workman": "worker",
            "barman": "bartender",
            "barmaid": "bartender",
            "bellman": "bell attendant",
            "bellboy": "bellhop",
            "busboy": "busser",
            "cleaning lady": "cleaner",
            "craftsman": "artisan",         
            "deliveryman": "courier",
            "delivery boy": "courier",
            "delivery girl": "courier",
            "doorman": "door attendant",
            "dustman": "refuse collector",
            "fireman": "firefighter",
            "fisherman": "fisher",
            "garbage man": "sanitation worker",
            "groundsman": "groundskeeper",
            "handyman": "maintenance worker",
            "housemaid": "housekeeper",
            "janitress": "custodian",
            "lineman": "line worker",
            "longshoreman": "stevedore",
            "lumberjack": "logger",
            "maid": "housekeeper",
            "mailman": "letter carrier",
            "milkman": "milk deliverer",
            "paperboy": "newspaper carrier",
            "pitman": "miner",
            "postman": "postal worker",
            "repairman": "technician",
            "seamstress": "tailor",         
            "sheetmetal worker": "sheet metal worker",
            "shopman": "shop assistant",
            "stableboy": "stable hand",
            "stewardess": "flight attendant",
            "steward": "flight attendant",
            "storeman": "storekeeper",
            "tradesman": "tradesperson",
            "trashman": "sanitation worker",
            "utility man": "utility worker",
            "waiter": "server",
            "waitress": "server",
            "warehouseman": "warehouse worker",
            "watchman": "security guard",
            "alderman": "council member",
            "assemblyman": "assembly member",
            "assemblywoman": "assembly member",
            "bondsman": "bonding agent",
            "congressman": "representative",
            "congresswoman": "representative",
            "councilman": "council member",
            "councilwoman": "council member",
            "countryman": "compatriot",
            "flagman": "flagger",
            "guardsman": "guard",
            "juryman": "juror",
            "kinsman": "relative",          
            "lawman": "law enforcement officer",
            "patrolman": "patrol officer",
            "policeman": "police officer",
            "policewoman": "police officer",
            "selectman": "select board member",
            "taxman": "tax collector",
            "townsman": "town resident",
            "airman": "aviator",           
            "boatman": "boater",           
            "coastguardsman": "coast guard member",
            "corpsman": "medic",
            "crewman": "crew member",
            "frogman": "scuba diver",
            "gunman": "shooter",
            "helmsman": "helm",
            "infantryman": "infantry soldier",
            "marksman": "sharpshooter",
            "midshipman": "cadet",
            "militiaman": "militia member",
            "oarsman": "rower",
            "rifleman": "rifle shooter",
            "seaman": "sailor",            
            "serviceman": "service member",
            "spaceman": "astronaut",
            "spearman": "spear carrier",
            "swordsman": "sword fighter",
            "yachtsman": "yachting enthusiast",
            "yeoman": "clerk",             
            "brotherhood": "solidarity",
            "common man": "average person",
            "fatherland": "homeland",
            "forefathers": "ancestors",
            "founding fathers": "founders",
            "gentleman's agreement": "unwritten agreement",
            "man-hours": "person-hours",
            "man-made": "artificial",
            "manhole": "maintenance hole", 
            "mankind": "humanity",
            "manning": "staffing",
            "manpower": "workforce",
            "mastery": "expertise",
            "mother tongue": "native language",
            "motherland": "homeland",
            "no man's land": "buffer zone",
            "one-man show": "solo show",
            "right-hand man": "chief assistant",
            "salesmanship": "sales technique",
            "sportsmanship": "fair play",
            "straw man": "straw figure",
            "unmanned": "uncrewed",
            "actress": "actor",
            "ballerina": "ballet dancer",   
            "comedienne": "comedian",
            "cowboy": "rancher",
            "cowgirl": "rancher",           
            "diva": "singer",               
            "heroine": "hero",
            "hostess": "host",
            "housewife": "homemaker",
            "househusband": "homemaker",    
            "maiden name": "birth name",
            "priestess": "priest",          
            "showman": "entertainer",
            "snowman": "snow figure",
            "stuntman": "stunt performer",
            "usherette": "usher",
            "villainess": "villain",
        }

    def checks_out_as_specific(self, sentence, term_token):
        term = term_token.text
        is_plural = term_token.tag_ == 'NNS'
        
        if is_plural:
            hypothesis = f"There are specific, real people who are the {term}."
        else:
            hypothesis = f"There is a specific, real person who is the {term}."
        
        scores = self.nli_model.predict([(sentence, hypothesis)])
        result = scores[0]
        
        contradiction = result[0]
        entailment = result[1]
        neutral = result[2]
        
        return (entailment > neutral) and (entailment > contradiction)

    def analyze(self, text):
        biases = []
        doc = self.nlp(text)
        
        for sent in doc.sents:
            sent_text = sent.text
            
            for token in sent:
                root = token.lemma_.lower()
                
                if root in self.term_map:
                    
                    dets = [c.text.lower() for c in token.children if c.dep_ in ('det', 'poss')]
                    if any(d in self.safe_dets for d in dets):
                        continue 
                    
                    if not self.checks_out_as_specific(sent_text, token):
                        replacement_word = str(self.term_map[root])
                        biases.append({
                            "id": str(uuid.uuid4()),
                            "text": str(token.text),
                            "type": "gendered_terms",
                            "description": f"'{token.text}' appears to be used in a generic context.",
                            "suggestion": f'Consider usage of a neutral form of the word, like: {replacement_word}',
                            "alternatives": [replacement_word],                            
                            "position": {
                                "start": int(token.idx),
                                "end": int(token.idx + len(token.text))
                            }
                        })
                        
        return biases