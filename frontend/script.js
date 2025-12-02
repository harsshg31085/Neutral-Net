// const API_BASE_URL = "http://localhost:8000";

// let currentAnalysis = null;
// let highlightsMap = new Map();

// async function analyzeText(text) {
//     try {
//         console.log("Sending text for analysis:", text.substring(0, 50) + "...");
        
//         const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({
//                 text: text,
//                 return_suggestions: true
//             })
//         });
        
//         if (!response.ok) {
//             throw new Error(`API error: ${response.status}`);
//         }
        
//         const data = await response.json();
//         console.log("Analysis result:", data);
//         return data;
        
//     } catch (error) {
//         console.error("Analysis failed:", error);
//         return getMockAnalysis(text);
//     }
// }

// function getMockAnalysis(text) {
//     return {
//         overall_score: 75,
//         issues: [
//             {
//                 type: 'generic_masculine',
//                 text: 'his',
//                 target_pronoun: 'his',
//                 position: { start: 10, end: 13 },
//                 severity: 'medium',
//                 explanation: "Using 'his' as a default pronoun may exclude women and non-binary individuals.",
//                 suggestions: [
//                     {
//                         text: 'their',
//                         strategy: 'singular_they',
//                         confidence: 0.9
//                     }
//                 ]
//             }
//         ],
//         text_metadata: {
//             length: text.length,
//             word_count: text.split(/\s+/).length
//         }
//     };
// }

// function updateUIWithAnalysis(analysis) {
//     if (!analysis) return;
    
//     currentAnalysis = analysis;
    
//     const scoreElement = document.querySelector('.score-value');
//     if (scoreElement) {
//         scoreElement.textContent = Math.round(analysis.overall_score);
//         updateScoreCircle(analysis.overall_score);
//     }
    
//     const issueCountElement = document.getElementById('issue-count');
//     if (issueCountElement) {
//         issueCountElement.textContent = analysis.issues.length;
//     }
    
//     updateIssuesList(analysis.issues);
    
//     const text = document.getElementById('text-editor').innerText || document.getElementById('text-editor').textContent;
//     const wordCount = text.trim() === '' ? 0 : text.trim().split(/\s+/).length;
//     document.getElementById('word-count').textContent = wordCount;
    
//     applyHighlightsToEditor(analysis.issues, text);
// }

// function applyHighlightsToEditor(issues, fullText) {
//     console.log("DEBUG: Applying highlights, issues:", issues.length);
    
//     const editor = document.getElementById('text-editor');
//     if (!editor) {
//         console.error("Editor not found!");
//         return;
//     }
    
//     editor.innerHTML = '';
    
//     if (!issues || issues.length === 0) {
//         editor.textContent = fullText;
//         return;
//     }
    
//     const sortedIssues = [...issues].sort((a, b) => a.position.start - b.position.end);
    
//     const fragment = document.createDocumentFragment();
//     let lastIndex = 0;
    
//     highlightsMap.clear();
    
//     sortedIssues.forEach((issue, index) => {
//         const { start, end } = issue.position;
        
//         if (start < 0 || end > fullText.length || start >= end || start < lastIndex) {
//             console.warn("Invalid position for issue:", issue, {start, end, lastIndex});
//             return;
//         }
        
//         if (start > lastIndex) {
//             const textBefore = fullText.substring(lastIndex, start);
//             fragment.appendChild(document.createTextNode(textBefore));
//         }
        
//         const biasClass = getBiasClass(issue.type);
//         const span = document.createElement('span');
//         span.className = `bias-highlight ${biasClass}`;
//         span.setAttribute('data-issue-id', index);
//         span.textContent = fullText.substring(start, end);
        
//         span.style.cursor = 'pointer';
//         span.style.padding = '1px 0';
        
//         span.addEventListener('click', function(e) {
//             console.log("=== CLICK DEBUG ===");
//             console.log("1. Click event fired");
//             console.log("2. 'this' element:", this);
//             console.log("3. 'this' text:", this.textContent);
//             console.log("4. Issue ID:", this.getAttribute('data-issue-id'));
//             console.log("5. Current analysis exists:", !!currentAnalysis);
            
//             e.stopPropagation();
//             e.preventDefault();
            
//             const clickedIssueId = parseInt(this.getAttribute('data-issue-id'));
//             console.log("6. Parsed issue ID:", clickedIssueId);
            
//             if (currentAnalysis && currentAnalysis.issues[clickedIssueId]) {
//                 const clickedIssue = currentAnalysis.issues[clickedIssueId];
//                 console.log("7. Found issue:", clickedIssue);
//                 showSuggestionPopup(clickedIssue, clickedIssueId, this);
//             } else {
//                 console.error("8. Could not find issue data!");
//                 alert("Error: Could not find issue data. Please try again.");
//             }
//         });
        
//         fragment.appendChild(span);
        
//         highlightsMap.set(index, {
//             element: span,  
//             issue: issue,
//             position: { start, end }
//         });
        
//         lastIndex = end;
//     });
    
//     if (lastIndex < fullText.length) {
//         const remainingText = fullText.substring(lastIndex);
//         fragment.appendChild(document.createTextNode(remainingText));
//     }
    
//     editor.appendChild(fragment);
    
//     console.log("DEBUG: Highlights applied. Map size:", highlightsMap.size);
//     console.log("DEBUG: Actual DOM highlights:", editor.querySelectorAll('.bias-highlight').length);
// }

// function updateIssuesList(issues) {
//     const issuesList = document.getElementById('issues-list');
//     if (!issuesList) return;
    
//     issuesList.innerHTML = '';
    
//     issues.forEach((issue, index) => {
//         const issueCard = document.createElement('div');
//         issueCard.className = 'issue-card';
//         issueCard.setAttribute('data-issue-id', index);
        
//         const biasClass = getBiasClass(issue.type);
//         const severityClass = `severity-${issue.severity || 'medium'}`;
        
//         const firstSuggestion = issue.suggestions && issue.suggestions.length > 0 
//             ? issue.suggestions[0].text 
//             : 'No suggestion available';
        
//         issueCard.innerHTML = `
//             <div class="issue-header">
//                 <span class="issue-type ${biasClass}">
//                     ${issue.type.replace('_', ' ')}
//                 </span>
//                 <span class="issue-severity ${severityClass}">
//                     ${issue.severity || 'medium'}
//                 </span>
//             </div>
//             <div class="issue-text">
//                 "${issue.text}"
//             </div>
//             <p class="issue-explanation">
//                 ${issue.explanation || ''}
//             </p>
//             <div class="issue-actions">
//                 <button class="btn-apply" onclick="applySuggestion(${index}, 0)">
//                     Apply Fix
//                 </button>
//                 <button class="btn-learn" onclick="showExplanation(${index})">
//                     Learn More
//                 </button>
//             </div>
//         `;
        
//         issueCard.addEventListener('click', function(e) {
//             if (!e.target.classList.contains('btn-apply') && !e.target.classList.contains('btn-learn')) {
//                 highlightCorrespondingText(index);
//             }
//         });
        
//         issuesList.appendChild(issueCard);
//     });
// }

// function getBiasClass(biasType) {
//     const classMap = {
//         'generic_masculine': 'bias-lexical',
//         'pronoun_imbalance': 'bias-lexical',
//         'default': 'bias-lexical'
//     };
//     return classMap[biasType] || 'bias-lexical';
// }

// function updateScoreCircle(score) {
//     const circle = document.querySelector('.score-circle');
//     if (circle) {
//         if (score >= 80) {
//             circle.style.backgroundColor = '#4CAF50'; 
//         } else if (score >= 60) {
//             circle.style.backgroundColor = '#FFC107'; 
//         } else {
//             circle.style.backgroundColor = '#F44336'; 
//         }
//     }
// }

// function highlightCorrespondingText(issueId) {
//     const highlight = highlightsMap.get(parseInt(issueId));
//     if (highlight && highlight.element) {
//         highlight.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
//         highlight.element.style.backgroundColor = 'rgba(255, 107, 107, 0.4)';
//         setTimeout(() => {
//             highlight.element.style.backgroundColor = '';
//         }, 1000);
//     }
// }

// function showSuggestionPopup(issue, issueId, element) {
//     console.log("Showing popup for issue:", issue);
    
//     const existingPopup = document.getElementById('suggestionPopup');
//     if (existingPopup) {
//         existingPopup.remove();
//     }
    
//     const popup = document.createElement('div');
//     popup.id = 'suggestionPopup';
//     popup.className = 'suggestion-popup';
    
//     const rect = element.getBoundingClientRect();
//     const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
//     const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
    
//     popup.style.position = 'absolute';
//     popup.style.top = `${rect.bottom + scrollTop + 5}px`;
//     popup.style.left = `${rect.left + scrollLeft}px`;
//     popup.style.zIndex = '10000';
    
//     let suggestionsHTML = '';
//     let hasRealSuggestions = false;
    
//     if (issue.suggestions && issue.suggestions.length > 0) {
//         hasRealSuggestions = true;
//         suggestionsHTML = issue.suggestions.map((suggestion, index) => `
//             <div class="suggestion-option ${index === 0 ? 'selected' : ''}" data-index="${index}">
//                 <div class="suggestion-strategy">
//                     ${suggestion.strategy || 'Suggestion'} 
//                     <span class="confidence">(${(suggestion.confidence * 100).toFixed(0)}% confidence)</span>
//                 </div>
//                 <div class="suggestion-text">${suggestion.text}</div>
//                 ${suggestion.description ? `<div class="suggestion-desc">${suggestion.description}</div>` : ''}
//                 <button class="btn-apply-popup" onclick="applySuggestionFromPopup(${issueId}, ${index})">
//                     Apply This
//                 </button>
//             </div>
//         `).join('');
//     } else {
//         suggestionsHTML = `
//             <div class="no-suggestions">
//                 <p>No specific suggestions available for this issue.</p>
//                 <p class="hint">Try rephrasing with gender-neutral language.</p>
//             </div>
//         `;
//     }
    
//     popup.innerHTML = `
//         <div class="popup-header">
//             <h3 class="popup-title">${formatIssueType(issue.type)}</h3>
//             <button class="popup-close" onclick="closeSuggestionPopup()">
//                 <i class="fas fa-times"></i>
//             </button>
//         </div>
//         <div class="popup-content">
//             <p class="popup-explanation">
//                 ${issue.explanation || 'This text may contain gender bias.'}
//             </p>
            
//             <div class="popup-suggestions">
//                 <h4>Suggested Fixes:</h4>
//                 ${suggestionsHTML}
//             </div>
            
//             <div class="popup-actions">
//                 <button class="btn btn-secondary btn-small" onclick="showMoreInfo(${issueId})">
//                     <i class="fas fa-info-circle"></i> Learn More
//                 </button>
//                 ${hasRealSuggestions ? '' : `
//                 <button class="btn btn-primary btn-small" onclick="manualEdit(${issueId})">
//                     <i class="fas fa-edit"></i> Edit Manually
//                 </button>
//                 `}
//             </div>
//         </div>
//     `;
    
//     document.body.appendChild(popup);
    
//     setTimeout(() => {
//         document.addEventListener('click', closePopupOnOutsideClick);
//     }, 10);
    
//     document.addEventListener('keydown', closePopupOnEsc);
// }

// function handleClickOutside(event) {
//     const popup = document.getElementById('suggestionPopup');
//     if (popup && !popup.contains(event.target) && 
//         !event.target.classList.contains('bias-highlight')) {
//         closeSuggestionPopup();
//     }
// }

// function formatIssueType(type) {
//     return type
//         .split('_')
//         .map(word => word.charAt(0).toUpperCase() + word.slice(1))
//         .join(' ');
// }

// function closePopupOnOutsideClick(event) {
//     const popup = document.getElementById('suggestionPopup');
//     if (popup && !popup.contains(event.target) && !event.target.classList.contains('bias-highlight')) {
//         closeSuggestionPopup();
//     }
// }

// function closePopupOnEsc(event) {
//     if (event.key === 'Escape') {
//         closeSuggestionPopup();
//     }
// }

// function closeSuggestionPopup() {
//     const popup = document.getElementById('suggestionPopup');
//     if (popup) {
//         popup.remove();
//     }
//     document.removeEventListener('click', closePopupOnOutsideClick);
//     document.removeEventListener('keydown', closePopupOnEsc);
// }

// function showExplanation(issueId) {
//     if (currentAnalysis && currentAnalysis.issues[issueId]) {
//         const issue = currentAnalysis.issues[issueId];
//         alert(`Issue Explanation:\n\nType: ${issue.type}\n\n${issue.explanation || 'No detailed explanation available.'}`);
//     }
// }

// function applySuggestionFromPopup(issueId, suggestionIndex) {
//     console.log(`Applying suggestion ${suggestionIndex} for issue ${issueId}`);
    
//     if (!currentAnalysis || !currentAnalysis.issues[issueId]) {
//         alert('Issue data not found. Please refresh the page.');
//         return;
//     }
    
//     const issue = currentAnalysis.issues[issueId];
//     const suggestion = issue.suggestions && issue.suggestions[suggestionIndex];
    
//     if (!suggestion) {
//         alert('Suggestion not found.');
//         return;
//     }
    
//     const editor = document.getElementById('text-editor');
//     const currentText = editor.textContent || editor.innerText;
    
//     const start = issue.position.start;
//     const end = issue.position.end;
    
//     if (start >= 0 && end <= currentText.length) {
//         const before = currentText.substring(0, start);
//         const after = currentText.substring(end);
//         const newText = before + suggestion.text + after;
        
//         editor.textContent = newText;
        
//         setTimeout(async () => {
//             const newAnalysis = await analyzeText(newText);
//             updateUIWithAnalysis(newAnalysis);
//         }, 300);
        
//         closeSuggestionPopup();
        
//         showToast('Suggestion applied successfully!');
//     } else {
//         alert('Could not apply suggestion: invalid text position.');
//     }
// }

// function replaceTextAtPosition(original, start, end, replacement) {
//     return original.substring(0, start) + replacement + original.substring(end);
// }

// function showMoreInfo(issueId) {
//     if (currentAnalysis && currentAnalysis.issues[issueId]) {
//         const issue = currentAnalysis.issues[issueId];
//         alert(`More Information:\n\nType: ${issue.type}\n\n${issue.explanation || 'No additional information available.'}`);
//     }
// }

// function manualEdit(issueId) {
//     alert('Manual edit mode would open here. For now, edit the text directly in the editor.');
// }

// function showToast(message) {
//     const toast = document.createElement('div');
//     toast.className = 'toast-notification';
//     toast.textContent = message;
//     toast.style.cssText = `
//         position: fixed;
//         bottom: 20px;
//         right: 20px;
//         background: #4CAF50;
//         color: white;
//         padding: 12px 20px;
//         border-radius: 4px;
//         z-index: 10000;
//         box-shadow: 0 2px 10px rgba(0,0,0,0.2);
//         animation: fadeIn 0.3s;
//     `;
    
//     document.body.appendChild(toast);
    
//     setTimeout(() => {
//         toast.style.animation = 'fadeOut 0.3s';
//         setTimeout(() => toast.remove(), 300);
//     }, 3000);
// }

// const style = document.createElement('style');
// style.textContent = `
//     @keyframes fadeIn {
//         from { opacity: 0; transform: translateY(10px); }
//         to { opacity: 1; transform: translateY(0); }
//     }
    
//     @keyframes fadeOut {
//         from { opacity: 1; transform: translateY(0); }
//         to { opacity: 0; transform: translateY(10px); }
//     }
    
//     .toast-notification {
//         animation: fadeIn 0.3s;
//     }
// `;
// document.head.appendChild(style);

// let analyzeTimeout;
// const editor = document.getElementById('text-editor');

// if (editor) {
//     editor.addEventListener('input', function() {
//         clearTimeout(analyzeTimeout);
        
//         analyzeTimeout = setTimeout(async () => {
//             const text = this.innerText || this.textContent;
//             if (text.trim().length >= 3) {
//                 document.querySelector('.score-value').textContent = '...';
                
//                 const analysis = await analyzeText(text);
//                 updateUIWithAnalysis(analysis);
//             }
//         }, 800); 
//     });
    
//     setTimeout(() => {
//         const sampleText = "A programmer should test his code. He must ensure his work is perfect.";
//         editor.textContent = sampleText;
        
//         setTimeout(async () => {
//             const analysis = await analyzeText(sampleText);
//             updateUIWithAnalysis(analysis);
//         }, 1000);
//     }, 500);
// }
/**
 * Equity Mirror - Gender Bias Detection
 * FINAL WORKING VERSION - November 2024
 */

// State
let currentAnalysis = null;
let isAnalyzing = false;

// ========== CURSOR PRESERVATION ==========
let lastCursorPosition = { node: null, offset: 0 };

function saveCursor() {
    const selection = window.getSelection();
    if (!selection.rangeCount) return;
    
    const range = selection.getRangeAt(0);
    lastCursorPosition = {
        node: range.startContainer,
        offset: range.startOffset
    };
}

function restoreCursor() {
    try {
        const selection = window.getSelection();
        const range = document.createRange();
        
        // If we have a saved position, use it
        if (lastCursorPosition.node && document.contains(lastCursorPosition.node)) {
            range.setStart(lastCursorPosition.node, lastCursorPosition.offset);
            range.collapse(true);
            selection.removeAllRanges();
            selection.addRange(range);
            return;
        }
        
        // Otherwise, put cursor at end of editor
        const editor = document.getElementById('text-editor');
        if (!editor) return;
        
        range.selectNodeContents(editor);
        range.collapse(false);
        selection.removeAllRanges();
        selection.addRange(range);
    } catch (e) {
        console.warn("Could not restore cursor:", e);
    }
}

// ========== PLACEHOLDER HANDLING ==========
function updatePlaceholder() {
    const editor = document.getElementById('text-editor');
    if (!editor) return;
    
    const hasText = editor.textContent.trim() !== '' && 
                    editor.textContent !== 'Start typing here...';
    
    if (hasText) {
        editor.classList.remove('placeholder');
    } else {
        editor.classList.add('placeholder');
        editor.textContent = 'Start typing here...';
    }
}

// ========== TEXT ANALYSIS ==========
async function analyzeText(text) {
    if (isAnalyzing || !text || text.trim() === '' || text === 'Start typing here...') {
        return null;
    }
    
    try {
        isAnalyzing = true;
        updateStatus('Analyzing...');
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 200));
        
        return getMockAnalysis(text);
        
    } catch (error) {
        console.error("Analysis error:", error);
        return null;
    } finally {
        isAnalyzing = false;
        updateStatus('Ready');
    }
}

function getMockAnalysis(text) {
    const issues = [];
    const lowerText = text.toLowerCase();
    
    // Find "his" with word boundaries
    let hisIndex = -1;
    while ((hisIndex = lowerText.indexOf(' his ', hisIndex + 1)) !== -1) {
        const start = hisIndex + 1; // +1 for the space before "his"
        const end = start + 3;
        
        if (start < text.length && end <= text.length) {
            issues.push({
                type: 'generic_masculine',
                text: text.substring(start, end),
                target_pronoun: 'his',
                position: { start, end },
                severity: 'medium',
                explanation: "Using 'his' as a default pronoun may exclude women and non-binary individuals.",
                suggestions: [{
                    text: 'their',
                    strategy: 'singular_they',
                    confidence: 0.9
                }]
            });
        }
    }
    
    // Find "he" with word boundaries
    let heIndex = -1;
    while ((heIndex = lowerText.indexOf(' he ', heIndex + 1)) !== -1) {
        const start = heIndex + 1;
        const end = start + 2;
        
        if (start < text.length && end <= text.length) {
            issues.push({
                type: 'generic_masculine',
                text: text.substring(start, end),
                target_pronoun: 'he',
                position: { start, end },
                severity: 'medium',
                explanation: "Using 'he' as a default pronoun may exclude women and non-binary individuals.",
                suggestions: [{
                    text: 'they',
                    strategy: 'singular_they',
                    confidence: 0.9
                }]
            });
        }
    }
    
    // Also check start of text
    if (lowerText.startsWith('his ')) {
        issues.push({
            type: 'generic_masculine',
            text: text.substring(0, 3),
            target_pronoun: 'his',
            position: { start: 0, end: 3 },
            severity: 'medium',
            explanation: "Using 'his' as a default pronoun may exclude women and non-binary individuals.",
            suggestions: [{
                text: 'their',
                strategy: 'singular_they',
                confidence: 0.9
            }]
        });
    }
    
    if (lowerText.startsWith('he ')) {
        issues.push({
            type: 'generic_masculine',
            text: text.substring(0, 2),
            target_pronoun: 'he',
            position: { start: 0, end: 2 },
            severity: 'medium',
            explanation: "Using 'he' as a default pronoun may exclude women and non-binary individuals.",
            suggestions: [{
                text: 'they',
                strategy: 'singular_they',
                confidence: 0.9
            }]
        });
    }
    
    // Calculate score
    const score = issues.length === 0 ? 100 : Math.max(50, 100 - (issues.length * 10));
    
    return {
        overall_score: score,
        issues: issues,
        text_metadata: {
            length: text.length,
            word_count: text.split(/\s+/).filter(w => w.length > 0).length
        }
    };
}

// ========== HIGHLIGHTING (FIXED) ==========
function applyHighlights(issues, text) {
    const editor = document.getElementById('text-editor');
    if (!editor || !text || text === 'Start typing here...') return;
    
    // Save cursor before any changes
    saveCursor();
    
    // Clear editor and set plain text
    editor.textContent = text;
    
    if (!issues || issues.length === 0) {
        restoreCursor();
        return;
    }
    
    // Filter valid issues
    const validIssues = issues.filter(issue => {
        if (!issue || !issue.position) return false;
        const { start, end } = issue.position;
        return start >= 0 && end <= text.length && start < end;
    });
    
    if (validIssues.length === 0) {
        restoreCursor();
        return;
    }
    
    // Create a document fragment for better performance
    const fragment = document.createDocumentFragment();
    let lastIndex = 0;
    
    // Sort issues by position
    const sortedIssues = [...validIssues].sort((a, b) => a.position.start - b.position.start);
    
    sortedIssues.forEach((issue, index) => {
        const { start, end } = issue.position;
        
        // Add text before this issue
        if (start > lastIndex) {
            const beforeText = text.substring(lastIndex, start);
            fragment.appendChild(document.createTextNode(beforeText));
        }
        
        // Create highlight span
        const span = document.createElement('span');
        span.className = 'bias-highlight';
        span.setAttribute('data-issue-id', index);
        span.textContent = text.substring(start, end);
        
        // IMPORTANT: Minimal styling to prevent layout shifts
        span.style.cssText = `
            background-color: rgba(255, 107, 107, 0.15);
            border-bottom: 2px solid #ff6b6b;
            cursor: pointer;
            display: inline;
            padding: 0;
            margin: 0;
            line-height: inherit;
            vertical-align: baseline;
        `;
        
        // Add click handler
        span.addEventListener('click', function(e) {
            e.stopPropagation();
            if (currentAnalysis && currentAnalysis.issues[index]) {
                showSuggestionPopup(currentAnalysis.issues[index], index, this);
            }
        });
        
        fragment.appendChild(span);
        lastIndex = end;
    });
    
    // Add remaining text
    if (lastIndex < text.length) {
        const remainingText = text.substring(lastIndex);
        fragment.appendChild(document.createTextNode(remainingText));
    }
    
    // Clear and append fragment
    editor.innerHTML = '';
    editor.appendChild(fragment);
    
    // Restore cursor after a brief delay
    setTimeout(restoreCursor, 10);
}

// ========== UI UPDATES ==========
function updateUI(analysis) {
    if (!analysis) return;
    
    currentAnalysis = analysis;
    
    // Update score
    const score = Math.round(analysis.overall_score);
    document.getElementById('score-value').textContent = score;
    updateScoreCircle(score);
    
    // Update description
    const desc = document.getElementById('score-description');
    if (desc) {
        desc.textContent = analysis.issues.length === 0 
            ? 'No issues detected' 
            : `${analysis.issues.length} issue${analysis.issues.length !== 1 ? 's' : ''} detected`;
    }
    
    // Update counts
    document.getElementById('issue-count').textContent = analysis.issues.length;
    
    const editor = document.getElementById('text-editor');
    if (editor) {
        const text = editor.textContent;
        const words = text.split(/\s+/).filter(w => w.length > 0 && w !== 'Start typing here...');
        document.getElementById('word-count').textContent = words.length;
        
        // Apply highlights
        applyHighlights(analysis.issues, text);
    }
    
    // Update issues list
    updateIssuesList(analysis.issues);
}

function updateIssuesList(issues) {
    const list = document.getElementById('issues-list');
    if (!list) return;
    
    list.innerHTML = '';
    
    if (!issues || issues.length === 0) {
        list.innerHTML = '<div class="no-issues">No gender bias issues detected.</div>';
        return;
    }
    
    issues.forEach((issue, index) => {
        const card = document.createElement('div');
        card.className = 'issue-card';
        
        const suggestion = issue.suggestions?.[0];
        
        card.innerHTML = `
            <div class="issue-header">
                <span class="issue-type">${issue.type?.replace('_', ' ') || 'Bias'}</span>
                <span class="issue-severity">${issue.severity || 'medium'}</span>
            </div>
            <div class="issue-text">"${issue.text || ''}"</div>
            <p style="font-size:0.875rem; color:#666; margin:0.5rem 0;">
                ${issue.explanation || ''}
            </p>
            <div class="issue-actions">
                <button class="btn-apply btn-small" onclick="applySuggestion(${index})">
                    Change to "${suggestion?.text || 'their'}"
                </button>
                <button class="btn-learn btn-small" onclick="showExplanation(${index})">
                    Learn More
                </button>
            </div>
        `;
        
        list.appendChild(card);
    });
}

function updateScoreCircle(score) {
    const circle = document.querySelector('.score-circle');
    if (!circle) return;
    
    if (score >= 80) circle.style.backgroundColor = '#4CAF50';
    else if (score >= 60) circle.style.backgroundColor = '#FFC107';
    else circle.style.backgroundColor = '#F44336';
}

function updateStatus(status) {
    const el = document.getElementById('status');
    if (!el) return;
    
    if (status === 'Analyzing...') {
        el.innerHTML = '<span class="loading"></span> Analyzing...';
    } else {
        el.textContent = status;
    }
}

// ========== SUGGESTION APPLICATION ==========
function showSuggestionPopup(issue, issueId, element) {
    // Remove existing popup
    document.getElementById('suggestion-popup')?.remove();
    
    const popup = document.createElement('div');
    popup.id = 'suggestion-popup';
    
    // Position near element
    const rect = element.getBoundingClientRect();
    popup.style.cssText = `
        position: fixed;
        top: ${rect.bottom + window.scrollY + 5}px;
        left: ${rect.left + window.scrollX}px;
        background: white;
        border: 2px solid #4A6FA5;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        min-width: 300px;
        max-width: 400px;
    `;
    
    const suggestion = issue.suggestions?.[0];
    
    popup.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; padding-bottom:10px; border-bottom:1px solid #eee;">
            <h3 style="margin:0; color:#4A6FA5; font-size:16px;">SUGGESTION</h3>
            <button onclick="closePopup()" style="background:none; border:none; font-size:24px; cursor:pointer; color:#666;">×</button>
        </div>
        <div>
            <p style="margin-bottom:15px; color:#666;">${issue.explanation || 'Potential bias detected.'}</p>
            ${suggestion ? `
            <div style="border:1px solid #ddd; border-radius:4px; padding:10px; background:#f9f9f9;">
                <div style="font-family:monospace; font-size:14px; margin:5px 0;">
                    Change <strong>"${issue.text}"</strong> to <strong>"${suggestion.text}"</strong>
                </div>
                <button onclick="applySuggestion(${issueId})" 
                    style="background:#4CAF50; color:white; border:none; padding:8px 16px; border-radius:4px; cursor:pointer; width:100%; margin-top:10px;">
                    Apply This Change
                </button>
            </div>
            ` : '<p>No suggestions available.</p>'}
        </div>
    `;
    
    document.body.appendChild(popup);
    
    // Close on click outside
    setTimeout(() => {
        document.addEventListener('click', (e) => {
            if (!popup.contains(e.target) && !e.target.classList.contains('bias-highlight')) {
                closePopup();
            }
        });
    }, 10);
}

function closePopup() {
    document.getElementById('suggestion-popup')?.remove();
}

function applySuggestion(issueId) {
    if (!currentAnalysis?.issues?.[issueId]) {
        showToast('Issue not found');
        return;
    }
    
    const issue = currentAnalysis.issues[issueId];
    const suggestion = issue.suggestions?.[0];
    
    if (!suggestion) {
        showToast('Suggestion not found');
        return;
    }
    
    const editor = document.getElementById('text-editor');
    if (!editor) return;
    
    const currentText = editor.textContent;
    const { start, end } = issue.position;
    
    // Validate
    if (start < 0 || end > currentText.length || start >= end) {
        showToast('Cannot apply suggestion');
        return;
    }
    
    // Save cursor
    saveCursor();
    
    // Create new text
    const before = currentText.substring(0, start);
    const after = currentText.substring(end);
    const newText = before + suggestion.text + after;
    
    // Update editor
    editor.textContent = newText;
    
    // Close popup
    closePopup();
    
    // Show success
    showToast(`Changed "${issue.text}" to "${suggestion.text}"`);
    
    // Re-analyze
    setTimeout(async () => {
        const analysis = await analyzeText(newText);
        updateUI(analysis);
        restoreCursor();
    }, 300);
}

function showExplanation(issueId) {
    if (currentAnalysis?.issues?.[issueId]) {
        const issue = currentAnalysis.issues[issueId];
        alert(issue.explanation || 'No explanation available.');
    }
}

// ========== UTILITIES ==========
function showToast(message) {
    // Remove existing toast
    document.querySelector('.toast')?.remove();
    
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

function clearEditor() {
    const editor = document.getElementById('text-editor');
    if (editor) {
        editor.textContent = '';
        updatePlaceholder();
        updateUI({
            overall_score: 100,
            issues: [],
            text_metadata: { length: 0, word_count: 0 }
        });
    }
}

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', function() {
    const editor = document.getElementById('text-editor');
    if (!editor) return;
    
    // Initialize placeholder
    updatePlaceholder();
    
    let analyzeTimeout;
    
    // Handle input
    editor.addEventListener('input', function() {
        const text = this.textContent;
        
        // Remove placeholder if present
        if (this.classList.contains('placeholder')) {
            this.classList.remove('placeholder');
            this.textContent = text.replace('Start typing here...', '');
        }
        
        // Update placeholder state
        if (text.trim() === '') {
            updatePlaceholder();
            return;
        }
        
        // Save cursor before analysis
        saveCursor();
        
        // Debounce analysis
        clearTimeout(analyzeTimeout);
        analyzeTimeout = setTimeout(async () => {
            const analysis = await analyzeText(text);
            if (analysis) {
                updateUI(analysis);
            }
        }, 600);
    });
    
    // Handle focus to clear placeholder immediately
    editor.addEventListener('focus', function() {
        if (this.classList.contains('placeholder')) {
            this.textContent = '';
            this.classList.remove('placeholder');
        }
    });
    
    // Initial focus
    setTimeout(() => {
        editor.focus();
        // Put cursor at start
        const range = document.createRange();
        const selection = window.getSelection();
        range.selectNodeContents(editor);
        range.collapse(true);
        selection.removeAllRanges();
        selection.addRange(range);
    }, 100);
});