from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import re

from analysis.pronoun_analyzer import analyze_pronouns
from suggestions.pronoun_suggestions import suggest_replacement

router = APIRouter()

class AnalysisRequest(BaseModel):
    text: str
    return_suggestions: bool = True

class SuggestionRequest(BaseModel):
    original_text: str
    issue_id: int
    suggestion_index: int

@router.post("/analyze")
async def analyze_text(request: AnalysisRequest):
    try:
        text = request.text
        
        analysis_result = analyze_pronouns(text)
        
        issues = []
        
        if analysis_result['has_imbalance']:
            issues.append({
                'type': 'pronoun_imbalance',
                'text': f"Male pronouns: {analysis_result['counts']['male']}, Female pronouns: {analysis_result['counts']['female']}",
                'severity': 'medium',
                'explanation': f"Pronoun ratio skewed: {analysis_result['male_ratio']:.1%} male pronouns",
                'suggestions': [{
                    'text': 'Consider using more gender-neutral pronouns',
                    'strategy': 'awareness',
                    'confidence': 0.8,
                    'description': 'Balance pronoun usage'
                }]
            })
        
        words = text.lower().split()
        original_words = text.split()  
        
        for gender, positions in analysis_result['positions'].items():
            for pos_info in positions:
                start_idx = pos_info['start']
                
                char_pos = find_character_position(text, start_idx)
                
                if start_idx < len(original_words):
                    original_word = original_words[start_idx]
                    
                    if gender == 'male' and pos_info['word'] in ['he', 'him', 'his', 'himself']:
                        context_start = max(0, start_idx - 2)
                        context_end = min(len(words), start_idx + 3)
                        context_words = original_words[context_start:context_end]
                        context_sentence = ' '.join(context_words)
                        
                        full_sentence = extract_sentence_at_position(text, char_pos)
                        
                        issue = {
                            'type': 'generic_masculine',
                            'text': original_word,
                            'target_pronoun': pos_info['word'],
                            'position': {
                                'start': char_pos,
                                'end': char_pos + len(original_word)
                            },
                            'severity': 'medium',
                            'explanation': f"Using '{pos_info['word']}' as a default pronoun may exclude women and non-binary individuals.",
                            'context': full_sentence[:100]  
                        }
                        
                        if request.return_suggestions:
                            suggestions = suggest_replacement(full_sentence, pos_info['word'])
                            issue['suggestions'] = suggestions
                        
                        issues.append(issue)
        
        total_issues = len(issues)
        overall_score = max(0, 100 - (total_issues * 10))
        
        return {
            'overall_score': overall_score,
            'issues': issues,
            'text_metadata': {
                'length': len(text),
                'word_count': len(text.split()),
                'pronoun_counts': analysis_result['counts']
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_sentence_at_position(text: str, position: int) -> str:
    start = position
    while start > 0 and text[start-1] not in '.!?\n':
        start -= 1
    
    end = position
    while end < len(text) and text[end] not in '.!?\n':
        end += 1
    
    if end < len(text) and text[end] in '.!?':
        end += 1
    
    sentence = text[start:end].strip()
    
    if len(sentence.split()) < 3:
        extra_start = max(0, start - 20)
        extra_end = min(len(text), end + 20)
        sentence = text[extra_start:extra_end].strip()
    
    return sentence

@router.post("/apply-suggestion")
async def apply_suggestion(request: SuggestionRequest):
    try:
        words = request.original_text.split()
        
        corrected_text = request.original_text
        
        return {
            'corrected_text': corrected_text,
            'message': 'Suggestion would be applied here'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def find_character_position(text: str, word_index: int) -> int:
    """Find character position of a word by its index"""
    words = text.split()
    if word_index >= len(words):
        return 0
    
    before_words = words[:word_index]
    if before_words:
        return len(' '.join(before_words)) + 1
    return 0