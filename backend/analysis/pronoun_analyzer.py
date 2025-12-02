def analyze_pronouns(text: str):
    pronouns = {
        'male': ['he', 'him', 'his', 'himself'],
        'female': ['she', 'her', 'hers', 'herself'],
        'neutral': ['they', 'them', 'their', 'theirs', 'themself', 'themselves']
    }

    text_lower = text.lower()
    words = text_lower.split()

    counts = {gender: 0 for gender in pronouns}
    positions = {gender: [] for gender in pronouns}

    for index, word in enumerate(words):
        word_clean = word.strip('.,!?;:"\'()[{]}')

        for gender, pronoun_list in pronouns.items():
            if word_clean in pronoun_list:
                counts[gender] += 1
                positions[gender].append({
                    'start': index,
                    'word': word_clean
                })
    
    total_gendered = counts['male'] + counts['female']
    if total_gendered > 0:
        male_ratio = counts['male'] / total_gendered
    else:
        male_ratio = 0
    
    return {
        'counts': counts,
        'positions': positions,
        'male_ratio': male_ratio,
        'has_imbalance': male_ratio > 0.7 or male_ratio < 0.3
    }