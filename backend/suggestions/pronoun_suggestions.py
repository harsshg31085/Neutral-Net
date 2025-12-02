import re

def suggest_replacement(sentence: str, target_pronoun: str):
    suggestions = []
    
    they_map = {
        'he': 'they',
        'him': 'them', 
        'his': 'their',
        'himself': 'themself',
        'she': 'they',
        'her': 'them',
        'hers': 'theirs', 
        'herself': 'themself'
    }
    
    if target_pronoun in they_map:
        words = sentence.split()
        replaced_words = []
        
        for word in words:
            if word.lower() == target_pronoun.lower():
                if word[0].isupper():
                    replacement = they_map[target_pronoun].capitalize()
                else:
                    replacement = they_map[target_pronoun]
                replaced_words.append(replacement)
            else:
                replaced_words.append(word)
        
        replaced_sentence = ' '.join(replaced_words)
        suggestions.append({
            'text': replaced_sentence,
            'strategy': 'singular_they',
            'confidence': 0.9,
            'description': f'Replace "{target_pronoun}" with "{they_map[target_pronoun]}"'
        })
    
    if target_pronoun in ['his', 'her']:
        pattern1 = r'^A (\w+) (should|must|can|will|might|may) (\w+) (his|her) (\w+)$'
        if re.search(pattern1, sentence, re.IGNORECASE):
            pluralized = re.sub(pattern1, r'\1s \2 \3 their \5', sentence, flags=re.IGNORECASE)
            suggestions.append({
                'text': pluralized,
                'strategy': 'plural_subject',
                'confidence': 0.85,
                'description': 'Pluralize the subject and use "their"'
            })
        
        pattern2 = r'^The (\w+) (\w+)s? (his|her) (\w+)$'
        if re.search(pattern2, sentence, re.IGNORECASE):
            match = re.match(pattern2, sentence, re.IGNORECASE)
            if match:
                noun = match.group(1)
                verb = match.group(2)
                obj = match.group(4)
                pluralized = f"{noun.capitalize() if noun[0].isupper() else noun}s {verb} their {obj}"
                suggestions.append({
                    'text': pluralized,
                    'strategy': 'plural_subject',
                    'confidence': 0.8,
                    'description': f'Change "The {noun} {verb}s {target_pronoun} {obj}" to "{noun}s {verb} their {obj}"'
                })
    
    if target_pronoun in ['his', 'her']:
        pattern = r'\b(his|her)\s+(\w+)\b'
        if re.search(pattern, sentence, re.IGNORECASE):
            removed = re.sub(pattern, r'the \2', sentence, flags=re.IGNORECASE)
            
            if removed != sentence and makes_sense(removed):
                suggestions.append({
                    'text': removed,
                    'strategy': 'remove_possessive',
                    'confidence': 0.7,
                    'description': 'Use "the" instead of a possessive pronoun'
                })
    
    if target_pronoun in ['he', 'him', 'his'] and is_role_context(sentence, target_pronoun):
        role_suggestions = suggest_neutral_role(sentence, target_pronoun)
        suggestions.extend(role_suggestions)
    
    unique_suggestions = []
    seen_texts = set()
    for suggestion in suggestions:
        if suggestion['text'] not in seen_texts:
            unique_suggestions.append(suggestion)
            seen_texts.add(suggestion['text'])
    
    return unique_suggestions[:3]  

def makes_sense(sentence: str) -> bool:
    words = sentence.split()
    if len(words) < 3:
        return False
    
    if 'the the ' in sentence.lower() or 'a a ' in sentence.lower():
        return False
    
    return True

def is_role_context(sentence: str, pronoun: str) -> bool:
    role_indicators = ['chairman', 'policeman', 'fireman', 'businessman', 'salesman', 
                       'postman', 'fisherman', 'craftsman', 'workman', 'repairman']
    
    sentence_lower = sentence.lower()
    for role in role_indicators:
        if role in sentence_lower:
            return True
    return False

def suggest_neutral_role(sentence: str, pronoun: str):
    role_map = {
        'chairman': ['chairperson', 'chair', 'moderator'],
        'policeman': ['police officer', 'officer'],
        'fireman': ['firefighter'],
        'businessman': ['businessperson', 'executive', 'entrepreneur'],
        'salesman': ['salesperson', 'sales representative'],
        'postman': ['mail carrier', 'postal worker'],
        'fisherman': ['fisher', 'angler'],
        'craftsman': ['artisan', 'craftsperson'],
        'workman': ['worker', 'laborer'],
        'repairman': ['repair technician', 'technician']
    }
    
    suggestions = []
    sentence_lower = sentence.lower()
    
    for gendered_role, neutral_alternatives in role_map.items():
        if gendered_role in sentence_lower:
            for alternative in neutral_alternatives[:2]:  
                if gendered_role[0].isupper():
                    alternative = alternative.capitalize()
                
                replaced = sentence.replace(gendered_role, alternative)
                replaced = replaced.replace(gendered_role.capitalize(), alternative.capitalize())
                
                suggestions.append({
                    'text': replaced,
                    'strategy': 'neutral_role',
                    'confidence': 0.9,
                    'description': f'Use gender-neutral "{alternative}" instead of "{gendered_role}"'
                })
    
    return suggestions