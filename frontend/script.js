let currentAnalysis = null;
let isAnalyzing = false;

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
        
        if (lastCursorPosition.node && document.contains(lastCursorPosition.node)) {
            range.setStart(lastCursorPosition.node, lastCursorPosition.offset);
            range.collapse(true);
            selection.removeAllRanges();
            selection.addRange(range);
            return;
        }
        
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

async function analyzeText(text) {
    if (isAnalyzing || !text || text.trim() === '' || text === 'Start typing here...') {
        return null;
    }
    
    try {
        isAnalyzing = true;
        updateStatus('Analyzing...');
        
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
    
    let hisIndex = -1;
    while ((hisIndex = lowerText.indexOf(' his ', hisIndex + 1)) !== -1) {
        const start = hisIndex + 1;
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

function applyHighlights(issues, text) {
    const editor = document.getElementById('text-editor');
    if (!editor || !text || text === 'Start typing here...') return;
    
    saveCursor();
    
    editor.textContent = text;
    
    if (!issues || issues.length === 0) {
        restoreCursor();
        return;
    }
    
    const validIssues = issues.filter(issue => {
        if (!issue || !issue.position) return false;
        const { start, end } = issue.position;
        return start >= 0 && end <= text.length && start < end;
    });
    
    if (validIssues.length === 0) {
        restoreCursor();
        return;
    }
    
    const fragment = document.createDocumentFragment();
    let lastIndex = 0;
    
    const sortedIssues = [...validIssues].sort((a, b) => a.position.start - b.position.start);
    
    sortedIssues.forEach((issue, index) => {
        const { start, end } = issue.position;
        
        if (start > lastIndex) {
            const beforeText = text.substring(lastIndex, start);
            fragment.appendChild(document.createTextNode(beforeText));
        }
        
        const span = document.createElement('span');
        span.className = 'bias-highlight';
        span.setAttribute('data-issue-id', index);
        span.textContent = text.substring(start, end);
        
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
        
        span.addEventListener('click', function(e) {
            e.stopPropagation();
            if (currentAnalysis && currentAnalysis.issues[index]) {
                showSuggestionPopup(currentAnalysis.issues[index], index, this);
            }
        });
        
        fragment.appendChild(span);
        lastIndex = end;
    });
    
    if (lastIndex < text.length) {
        const remainingText = text.substring(lastIndex);
        fragment.appendChild(document.createTextNode(remainingText));
    }
    
    editor.innerHTML = '';
    editor.appendChild(fragment);
    
    setTimeout(restoreCursor, 10);
}

function updateUI(analysis) {
    if (!analysis) return;
    
    currentAnalysis = analysis;
    
    const score = Math.round(analysis.overall_score);
    document.getElementById('score-value').textContent = score;
    updateScoreCircle(score);
    
    const desc = document.getElementById('score-description');
    if (desc) {
        desc.textContent = analysis.issues.length === 0 
            ? 'No issues detected' 
            : `${analysis.issues.length} issue${analysis.issues.length !== 1 ? 's' : ''} detected`;
    }
    
    document.getElementById('issue-count').textContent = analysis.issues.length;
    
    const editor = document.getElementById('text-editor');
    if (editor) {
        const text = editor.textContent;
        const words = text.split(/\s+/).filter(w => w.length > 0 && w !== 'Start typing here...');
        document.getElementById('word-count').textContent = words.length;
        
        applyHighlights(analysis.issues, text);
    }
    
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

function showSuggestionPopup(issue, issueId, element) {
    document.getElementById('suggestion-popup')?.remove();
    
    const popup = document.createElement('div');
    popup.id = 'suggestion-popup';
    
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
    
    if (start < 0 || end > currentText.length || start >= end) {
        showToast('Cannot apply suggestion');
        return;
    }
    
    saveCursor();
    
    const before = currentText.substring(0, start);
    const after = currentText.substring(end);
    const newText = before + suggestion.text + after;
    
    editor.textContent = newText;
    
    closePopup();
    
    showToast(`Changed "${issue.text}" to "${suggestion.text}"`);
    
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

function showToast(message) {
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

document.addEventListener('DOMContentLoaded', function() {
    const editor = document.getElementById('text-editor');
    if (!editor) return;
    
    updatePlaceholder();
    
    let analyzeTimeout;
    
    editor.addEventListener('input', function() {
        const text = this.textContent;
        
        if (this.classList.contains('placeholder')) {
            this.classList.remove('placeholder');
            this.textContent = text.replace('Start typing here...', '');
        }
        
        if (text.trim() === '') {
            updatePlaceholder();
            return;
        }
        
        saveCursor();
        
        clearTimeout(analyzeTimeout);
        analyzeTimeout = setTimeout(async () => {
            const analysis = await analyzeText(text);
            if (analysis) {
                updateUI(analysis);
            }
        }, 600);
    });
    
    editor.addEventListener('focus', function() {
        if (this.classList.contains('placeholder')) {
            this.textContent = '';
            this.classList.remove('placeholder');
        }
    });
    
    setTimeout(() => {
        editor.focus();
        const range = document.createRange();
        const selection = window.getSelection();
        range.selectNodeContents(editor);
        range.collapse(true);
        selection.removeAllRanges();
        selection.addRange(range);
    }, 100);

});
