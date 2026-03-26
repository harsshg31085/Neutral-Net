const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE_URL = isLocalhost 
    ? 'http://localhost:8000' 
    : 'https://Harssh3108-neutral-net-api.hf.space';

class NeutralNet {
    constructor() {
        this.currentText = '';
        this.currentBiases = [];
        this.ignoredBiases = new Set(); 
        this.debounceTimer = null;
        this.currentSuggestion = null;
        this.lastCursorPosition = null;
        this.isUpdatingHighlights = false;
        this.shouldSkipNextAnalysis = false; 
        
        this.initializeElements();
        this.bindEvents();
        this.setupEventListeners();
        this.loadInitialDemo();
        
        this.adjustEditorHeight();
        this.initChart();
    }
    
    initializeElements() {
        this.textInput = document.getElementById('text-input'); 
        this.editableDiv = document.getElementById('editable-text'); 
        this.scoreCircle = document.getElementById('score-circle');
        this.scoreValue = document.getElementById('score-value');
        this.realTimeScore = document.getElementById('real-time-score');
        this.realTimeWords = document.getElementById('real-time-words');
        this.realTimeBiases = document.getElementById('real-time-biases');
        this.wordCount = document.getElementById('word-count');
        this.statusIndicator = document.getElementById('status-indicator');
        this.suggestionsContainer = document.getElementById('suggestions-container');
        this.editorPanel = document.querySelector('.editor-panel');
        this.fileInput = document.getElementById('file-upload');
        this.uploadBtn = document.getElementById('upload-btn');
        this.exportBtn = document.getElementById('export-btn');
        
        this.biasCounts = {
            'pronoun': document.getElementById('count-pronoun'),
            'agentic_communal': document.getElementById('count-agentic'),
            'gendered_terms': document.getElementById('count-gendered'),
            'stereotype': document.getElementById('count-stereotype'),
            'stereotyped': document.getElementById('count-stereotype')
        };
    }
    
    bindEvents() {
        this.editableDiv.addEventListener('keyup', () => this.saveCursorPosition());
        this.editableDiv.addEventListener('mouseup', () => this.saveCursorPosition());
        this.editableDiv.addEventListener('click', () => this.saveCursorPosition());
        
        this.editableDiv.addEventListener('input', (e) => this.handleTextInput(e));
        this.editableDiv.addEventListener('keydown', (e) => this.handleKeyDown(e));
        this.editableDiv.addEventListener('keypress', (e) => this.handleKeyPress(e));
        this.editableDiv.addEventListener('paste', (e) => this.handlePaste(e));
        
        this.editableDiv.addEventListener('compositionstart', () => this.isComposing = true);
        this.editableDiv.addEventListener('compositionend', () => {
            this.isComposing = false;
            this.handleTextInput();
        });

        this.uploadBtn.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
        this.exportBtn.addEventListener('click', () => this.exportText());
        
        window.addEventListener('resize', () => this.adjustEditorHeight());
        
        document.getElementById('clear-btn').addEventListener('click', () => this.clearText());
        document.getElementById('demo-btn').addEventListener('click', () => this.loadDemoText());
        document.getElementById('fix-all-btn').addEventListener('click', () => this.fixAllBiases()); 
    }
    
    setupEventListeners() {
        document.addEventListener('click', (e) => {
            if (!e.target.classList.contains('bias-highlight')) {
                this.closeAllTooltips();
            }
        });
    }
    
    loadInitialDemo() {
        setTimeout(() => {
            if (this.editableDiv.textContent === '') {
                this.loadDemoText();
            }
        }, 1000);
    }
    
    adjustEditorHeight() {
        const windowHeight = window.innerHeight;
        const headerHeight = document.querySelector('.header').offsetHeight;
        const resultsPanel = document.querySelector('.results-panel');
        const availableHeight = windowHeight - headerHeight - 100; 
        
        this.editorPanel.style.minHeight = availableHeight + 'px';
        this.editableDiv.style.minHeight = (availableHeight - 100) + 'px';
        
        if (resultsPanel) {
            resultsPanel.style.minHeight = availableHeight + 'px';
        }
    }
    
    saveCursorPosition() {
        if (this.isUpdatingHighlights || this.isComposing) return;
        
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            
            if (this.cursorMarker) {
                this.cursorMarker.remove();
            }
            
            this.cursorMarker = document.createElement('span');
            this.cursorMarker.id = 'cursor-marker';
            this.cursorMarker.style.display = 'none';
            this.cursorMarker.textContent = '\u200B'; 
            
            range.insertNode(this.cursorMarker);
            
            range.setStartAfter(this.cursorMarker);
            range.collapse(true);
            selection.removeAllRanges();
            selection.addRange(range);
        }
    }
    
    restoreCursorPosition() {
        if (!this.cursorMarker || !this.cursorMarker.parentNode) {
            this.setCursorToEnd();
            return;
        }
        
        try {
            const selection = window.getSelection();
            const range = document.createRange();
            
            range.setStartBefore(this.cursorMarker);
            range.collapse(true);
            
            selection.removeAllRanges();
            selection.addRange(range);
            
            setTimeout(() => {
                if (this.cursorMarker && this.cursorMarker.parentNode) {
                    this.cursorMarker.remove();
                    this.cursorMarker = null;
                }
            }, 0);
            
            this.editableDiv.focus();
        } catch (e) {
            console.warn('Could not restore cursor position:', e);
            this.setCursorToEnd();
        }
    }

    initChart() {
        const ctx = document.getElementById('biasChart').getContext('2d');
        this.biasChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Agentic Tone', 'Communal Tone', 'Gendered Terms', 'Pronoun Skew', 'Stereotypes'],
                datasets: [{
                    label: 'Bias Intensity',
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: 'rgba(79, 70, 229, 0.2)',
                    borderColor: 'rgba(79, 70, 229, 1)',
                    pointBackgroundColor: 'rgba(79, 70, 229, 1)',
                    borderWidth: 2,
                    pointRadius: 3
                }]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        angleLines: { color: 'rgba(0, 0, 0, 0.1)' },
                        grid: { color: 'rgba(0, 0, 0, 0.1)' },
                        pointLabels: { font: { size: 11, family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif" } },
                        ticks: { display: false, min: 0, max: 10} 
                    }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    exportText() {
        const text = this.getPlainTextFromEditable();
        if (!text.trim()) {
            alert("The editor is empty. Nothing to export.");
            return;
        }
        const blob = new Blob([text], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'download.txt'; 
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        this.updateStatus('success');
        this.statusIndicator.textContent = '● Exported successfully';
    }
    
    handleTextInput(e) {
        if (this.isComposing) return;
        
        if (this.shouldSkipNextAnalysis) {
            this.shouldSkipNextAnalysis = false;
            
            const plainText = this.getPlainTextFromEditable();
            const words = plainText.trim() ? plainText.trim().split(/\s+/).length : 0;
            this.wordCount.textContent = words;
            this.realTimeWords.textContent = words;
            return;
        }
        
        this.saveCursorPosition();
        
        const plainText = this.getPlainTextFromEditable();
        this.currentText = plainText;
        this.textInput.value = plainText;
        
        const words = plainText.trim() ? plainText.trim().split(/\s+/).length : 0;
        this.wordCount.textContent = words;
        this.realTimeWords.textContent = words;
        
        this.statusIndicator.textContent = '● Analyzing...';
        this.statusIndicator.style.color = '#f59e0b';
        
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        this.debounceTimer = setTimeout(() => {
            this.analyzeText(plainText);
        }, 500);
    }
    
    getPlainTextFromEditable() {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = this.editableDiv.innerHTML;
        
        const marker = tempDiv.querySelector('#cursor-marker');
        if (marker) {
            marker.remove();
        }
        
        let text = tempDiv.textContent || tempDiv.innerText || '';
        text = text.replace(/\n/g, ' ').replace(/\s+/g, ' ').trim();
        return text;
    }
    
    async analyzeText(text) {
        if (!text.trim()) {
            this.updateUIWithEmptyResults();
            this.editableDiv.textContent = '';
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/real-time-analyze/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({ 
                    text: text,
                    ignored_texts: Array.from(this.ignoredBiases) 
                })
            });
            
            if (!response.ok) {
                throw new Error(`Analysis failed: ${response.status}`);
            }
            
            const data = await response.json();
            this.currentBiases = data.biases || [];
            
            this.isUpdatingHighlights = true;
            await this.updateEditableWithHighlights(data.highlighted_html || data.highlighted_text, text);
            
            this.updateScore(data.overall_score || data.score);
            this.updateBiasCounts(data.biases);
            this.updateSuggestions(data.biases);
            this.updateStatus('success');
            
            setTimeout(() => {
                this.restoreCursorPosition();
                this.isUpdatingHighlights = false;
            }, 10);
            
        } catch (error) {
            console.error('Error analyzing text:', error);
            this.updateStatus('error');
            this.editableDiv.textContent = text;
            this.isUpdatingHighlights = false;
        }
    }
    
    async updateEditableWithHighlights(highlightedHtml, originalText) {
        if (highlightedHtml && highlightedHtml.includes('bias-highlight')) {
            const scrollTop = this.editableDiv.scrollTop;
            
            let processedHtml = highlightedHtml
                .replace(/&nbsp;/g, ' ')
                .replace(/\s+/g, ' ');
            
            this.editableDiv.innerHTML = processedHtml;
            this.editableDiv.scrollTop = scrollTop;
            this.editableDiv.setAttribute('contenteditable', 'true');
            
            this.setupBiasClickHandlers();
        } else {
            this.editableDiv.textContent = originalText;
        }
    }
    
    setupBiasClickHandlers() {
        const biasElements = this.editableDiv.querySelectorAll('.bias-highlight');
        biasElements.forEach(element => {
            const biasId = element.dataset.biasId;
            if (biasId) {
                element.onclick = null;
                
                element.onclick = (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    showBiasSuggestion(biasId);
                };
                
                element.addEventListener('mouseenter', () => {
                    element.style.transform = 'translateY(-1px)';
                    element.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
                });
                
                element.addEventListener('mouseleave', () => {
                    element.style.transform = '';
                    element.style.boxShadow = '';
                });
            }
        });
    }
    
    setCursorToEnd() {
        try {
            const range = document.createRange();
            const selection = window.getSelection();
            
            if (this.editableDiv.childNodes.length > 0) {
                const lastNode = this.editableDiv.lastChild;
                if (lastNode.nodeType === Node.TEXT_NODE) {
                    range.setStart(lastNode, lastNode.length);
                } else {
                    range.setStartAfter(lastNode);
                }
                range.collapse(true);
            } else {
                range.selectNodeContents(this.editableDiv);
                range.collapse(false);
            }
            
            selection.removeAllRanges();
            selection.addRange(range);
            this.editableDiv.focus();
        } catch (e) {
            console.warn("Cursor reposition skipped (normal during popup dismissals).");
        }
    }
    
    handlePaste(e) {
        e.preventDefault();
        this.saveCursorPosition();
        const text = e.clipboardData.getData('text/plain');
        document.execCommand('insertText', false, text);
        this.editableDiv.dispatchEvent(new Event('input'));
    }
    
    handleKeyDown(e) {
        if (this.isComposing) return;
        
        if (e.key === 'Tab') {
            e.preventDefault();
            this.saveCursorPosition();
            document.execCommand('insertText', false, '    ');
            this.editableDiv.dispatchEvent(new Event('input'));
            return false;
        }
        
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.saveCursorPosition();
            document.execCommand('insertHTML', false, '<br><br>');
            this.editableDiv.dispatchEvent(new Event('input'));
            return false;
        }
        
        if (e.key === ' ') {
            this.shouldSkipNextAnalysis = true;
        }
    }
    
    handleKeyPress(e) {
        if (e.key !== ' ' && e.key !== 'Enter' && e.key !== 'Tab') {
            this.shouldSkipNextAnalysis = false;
        }
    }

    fixAllBiases() {
        if (!this.currentBiases || this.currentBiases.length === 0) {
            return;
        }
        
        let currentText = this.getPlainTextFromEditable();
        
        let changesMade = false;

        const fixableBiases = this.currentBiases.filter((bias, index) => {
            const hasAlt = bias.alternatives && bias.alternatives.length > 0;
            const firstAlt = hasAlt ? bias.alternatives[0] : "NONE";
            const isValidAlt = firstAlt && !firstAlt.startsWith('(');
            const hasPosition = bias.position && typeof bias.position.start !== 'undefined';           
            return hasAlt && isValidAlt && hasPosition;
        });
        if (fixableBiases.length === 0) {
            alert("No automatic fixes available. The remaining issues require manual rephrasing.");
            return;
        }

        fixableBiases.sort((a, b) => b.position.start - a.position.start);

        fixableBiases.forEach(bias => {
            const replacement = bias.alternatives[0];
            const start = bias.position.start;
            const end = bias.position.end;
            
            currentText = currentText.slice(0, start) + replacement + currentText.slice(end);
            changesMade = true;
        });

        if (changesMade) {
            this.editableDiv.textContent = currentText;
            this.textInput.value = currentText;
            
            setTimeout(() => {
                this.editableDiv.dispatchEvent(new Event('input'));
            }, 100);
        }
    }
    
    updateScore(score) {
        const safeScore = Math.max(0, Math.min(100, score || 100));
        const circumference = 2 * Math.PI * 16; 
        const offset = circumference - (safeScore / 100) * circumference;
        this.scoreCircle.style.strokeDashoffset = offset;
        
        this.scoreValue.textContent = safeScore;
        this.realTimeScore.textContent = safeScore;
        
        let color = '#10b981'; 
        if (safeScore < 70) color = '#f59e0b'; 
        if (safeScore < 40) color = '#ef4444';
        this.scoreCircle.style.stroke = color;
    }
    
    updateBiasCounts(biases) {
        Object.values(this.biasCounts).forEach(el => {
            if (el && el.textContent !== undefined) {
                el.textContent = '0';
            }
        });
        this.realTimeBiases.textContent = '0';
        
        let chartData = { agentic: 0, communal: 0, gendered: 0, pronoun: 0, stereotype: 0 };

        if (!biases || biases.length === 0) {
            this.updateChartData(chartData);
            return;
        }
        
        const typeMapping = {
            'pronoun': 'pronoun',
            'agentic_communal': 'agentic_communal',
            'gendered_terms': 'gendered_terms', 
            'stereotype': 'stereotype',
            'stereotyped': 'stereotype' 
        };
        
        const counts = {};
        biases.forEach(bias => {
            const backendType = bias.type || 'unknown';
            
            if (backendType === 'agentic_communal') {
                if (bias.description && bias.description.includes("Agentic")) chartData.agentic++;
                else chartData.communal++;
            }
            if (backendType === 'gendered_terms') chartData.gendered++;
            if (backendType === 'pronoun') chartData.pronoun++;
            if (backendType === 'stereotype' || backendType === 'stereotyped') chartData.stereotype++;

            const frontendType = typeMapping[backendType] || backendType;
            counts[frontendType] = (counts[frontendType] || 0) + 1;
        });
        
        Object.entries(counts).forEach(([type, count]) => {
            if (this.biasCounts[type]) {
                this.biasCounts[type].textContent = count;
            }
        });
        
        this.realTimeBiases.textContent = biases.length;
        
        this.updateChartData(chartData);
    }

    updateChartData(data) {
        if (!this.biasChart) return;
        this.biasChart.data.datasets[0].data = [
            data.agentic, 
            data.communal, 
            data.gendered, 
            data.pronoun, 
            data.stereotype
        ];
        this.biasChart.update();
    }
    
    updateSuggestions(biases) {
        if (!biases || biases.length === 0) {
            this.showEmptySuggestions();
            return;
        }
        const recentBiases = biases.slice(0, 3);
        this.renderSuggestions(recentBiases);
    }
    
    renderSuggestions(biases) {
        this.suggestionsContainer.innerHTML = '';
        
        biases.forEach((bias, index) => {
            const suggestion = document.createElement('div');
            suggestion.className = 'suggestion-item';
            suggestion.dataset.biasId = bias.id;
            
            suggestion.innerHTML = `
                <div class="suggestion-text">
                    <strong>${(bias.type || 'bias').replace('_', ' ').toUpperCase()}:</strong>
                    "${bias.target_text || bias.targetText || ''}" - ${bias.description || 'Bias detected'}
                </div>
                <div class="suggestion-actions">
                    <input type="text" 
                        class="suggestion-replace" 
                        placeholder="Replace with..."
                        value="${(bias.alternatives && bias.alternatives[0]) || ''}">
                    <button class="btn btn-primary btn-small" onclick="applySuggestionFromList('${bias.id}', this)">
                        Apply
                    </button>
                </div>
            `;
            this.suggestionsContainer.appendChild(suggestion);
        });
    }
    
    showEmptySuggestions() {
        this.suggestionsContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-check-circle"></i>
                <p>Great! No biases detected in your text.</p>
            </div>
        `;
    }
    
    updateUIWithEmptyResults() {
        this.updateScore(100);
        this.updateBiasCounts([]);
        this.showEmptySuggestions();
        this.updateStatus('ready');
    }
    
    updateStatus(status) {
        const statusConfig = {
            ready: { text: '● Ready', color: '#10b981' },
            analyzing: { text: '● Analyzing...', color: '#f59e0b' },
            success: { text: '● Analysis complete', color: '#10b981' },
            error: { text: '● Error analyzing', color: '#ef4444' }
        };
        
        const config = statusConfig[status] || statusConfig.ready;
        this.statusIndicator.textContent = config.text;
        this.statusIndicator.style.color = config.color;
    }
    
    loadDemoText() {
        this.saveCursorPosition();
        
        const demoText = "We are looking to hire a new salesman for the lead position. The ideal candidate must be highly aggressive in client negotiations. Furthermore, every developer must test his own code before deployment. She is quite a good developer for a woman.";

        this.editableDiv.textContent = demoText;
        
        setTimeout(() => {
            this.editableDiv.dispatchEvent(new Event('input'));
        }, 100);
        
        setTimeout(() => {
            this.editableDiv.focus();
            this.setCursorToEnd();
        }, 200);
    }
    
    clearText() {
        this.editableDiv.innerHTML = '';
        this.textInput.value = '';
        this.currentText = '';
        this.currentBiases = [];
        this.ignoredBiases.clear(); 
        this.lastCursorPosition = null;
        this.shouldSkipNextAnalysis = false;
        
        if (this.cursorMarker) {
            this.cursorMarker.remove();
            this.cursorMarker = null;
        }
        
        this.updateUIWithEmptyResults();

        const wordCountEl = document.getElementById('word-count') || this.wordCount;
        if(wordCountEl){
            wordCountEl.textContent = '0';
        }

        const wordCountTop = document.getElementById('real-time-words');
        if(wordCountTop){
            wordCountTop.textContent = '0';
        }

        this.updateBiasCounts([]);
        
        setTimeout(() => {
            this.editableDiv.focus();
            this.setCursorToEnd();
        }, 100);
    }

    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        event.target.value = '';

        this.updateStatus('analyzing');
        this.statusIndicator.textContent = '● Extracting text...';

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_BASE_URL}/api/upload-document/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.ignoredBiases.clear();
                this.editableDiv.textContent = data.text;
                
                setTimeout(() => {
                    this.editableDiv.dispatchEvent(new Event('input'));
                }, 100);
                
                setTimeout(() => {
                    this.editableDiv.focus();
                    this.setCursorToEnd();
                }, 200);
            } else {
                alert('Error extracting text: ' + data.error);
                this.updateStatus('error');
            }
        } catch (error) {
            console.error('Upload failed:', error);
            alert('Failed to connect to the server for upload.');
            this.updateStatus('error');
        }
    }
    
    closeAllTooltips() {
        document.querySelectorAll('.bias-tooltip').forEach(tooltip => {
            tooltip.classList.remove('show');
        });
    }
    
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

function showBiasSuggestion(biasId) {
    closeAllPopups();
    
    const bias = neutralNet.currentBiases.find(b => b.id === biasId);
    if (!bias) return;
    
    const popup = document.createElement('div');
    popup.className = 'bias-popup';
    popup.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        z-index: 1000;
        max-width: 400px;
        width: 90%;
    `;
    
    popup.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h3 style="margin: 0; color: #4f46e5;">Fix Bias</h3>
            <button onclick="closeAllPopups()" style="background: none; border: none; font-size: 20px; cursor: pointer; color: #666;">×</button>
        </div>
        <div style="margin-bottom: 16px;">
            <p><strong>Issue:</strong> ${bias.description}</p>
            <p><strong>Suggestion:</strong> ${bias.suggestion}</p>
        </div>
        ${bias.alternatives && bias.alternatives.length > 0 ? `
            <div style="margin-bottom: 16px;">
                <p><strong>Alternatives:</strong></p>
                <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">
                    ${bias.alternatives.map(alt => 
                        `<span style="background: #f1f5f9; padding: 6px 12px; border-radius: 6px; cursor: pointer;" 
                                onclick="applySuggestion('${biasId}', '${alt.replace(/'/g, "\\'")}')">
                            ${alt}
                            </span>`
                    ).join('')}
                </div>
            </div>
        ` : ''}
        <div>
            <input type="text" 
                    id="custom-replace-${biasId}" 
                    placeholder="Or enter custom replacement..." 
                    style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 12px;">
            <div style="display: flex; gap: 8px;">
                <button onclick="applyCustomSuggestion('${biasId}')" 
                        style="flex: 2; padding: 12px; background: #4f46e5; color: white; border: none; border-radius: 6px; cursor: pointer;">
                    Apply Change
                </button>
                <button onclick="ignoreBias('${biasId}')" 
                        style="flex: 1; padding: 12px; background: #e2e8f0; color: #475569; border: none; border-radius: 6px; cursor: pointer; font-weight: 600;">
                    Ignore
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(popup);
    
    const overlay = document.createElement('div');
    overlay.className = 'popup-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 999;
    `;
    overlay.onclick = closeAllPopups;
    document.body.appendChild(overlay);
}

function closeAllPopups() {
    document.querySelectorAll('.bias-popup, .popup-overlay').forEach(el => el.remove());
}

function applySuggestion(biasId, replacement) {
    const bias = neutralNet.currentBiases.find(b => b.id === biasId);
    if (!bias) return;
    
    const editor = neutralNet.editableDiv;
    const biasElement = editor.querySelector(`span[data-bias-id="${biasId}"]`);
    
    if (biasElement) {
        const replacementSpan = document.createElement('span');
        replacementSpan.textContent = replacement;
        replacementSpan.style.color = '#059669';
        replacementSpan.style.fontWeight = '600';
        biasElement.replaceWith(replacementSpan);
    } else {
        const currentText = editor.textContent || editor.innerText;
        const targetText = bias.text || bias.target_text || bias.targetText || "";
        const escapedText = targetText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        
        if (escapedText) {
            const updatedText = currentText.replace(new RegExp(escapedText, 'g'), replacement);
            editor.textContent = updatedText;
        }
    }
    
    const plainText = neutralNet.getPlainTextFromEditable();
    neutralNet.textInput.value = plainText;
    
    setTimeout(() => {
        editor.dispatchEvent(new Event('input'));
    }, 100);
    
    closeAllPopups();
}

function applySuggestionFromList(biasId, buttonElement) {
    const suggestionItem = buttonElement.closest('.suggestion-item');
    const replacementInput = suggestionItem.querySelector('.suggestion-replace');
    const replacement = replacementInput.value.trim();
    
    if (!replacement) {
        alert('Please enter a replacement text.');
        return;
    }
    applySuggestion(biasId, replacement);
}

function applyCustomSuggestion(biasId) {
    const input = document.getElementById(`custom-replace-${biasId}`);
    if (input && input.value.trim()) {
        applySuggestion(biasId, input.value.trim());
    }
}

function ignoreBias(biasId) {
    console.log("--- IGNORE BUTTON CLICKED ---");
    
    const bias = neutralNet.currentBiases.find(b => b.id === biasId);
    if (!bias) {
        console.warn("ABORT: Could not find bias ID in current array.");
        return;
    }

    let wordToIgnore = bias.text || bias.target_text || bias.targetText;

    if (!wordToIgnore && bias.position) {
        console.warn("Text keys missing! Falling back to coordinate extraction...");
        const currentText = neutralNet.getPlainTextFromEditable();
        wordToIgnore = currentText.slice(bias.position.start, bias.position.end);
    }

    if (wordToIgnore) {
        const cleanWord = wordToIgnore.toLowerCase().trim();
        console.log(`Successfully extracted word to ignore: "${cleanWord}"`);
        
        neutralNet.ignoredBiases.add(cleanWord);
        console.log("Current Ignored List being sent to backend:", Array.from(neutralNet.ignoredBiases));
        
        neutralNet.statusIndicator.textContent = '● Updating...';
        neutralNet.statusIndicator.style.color = '#f59e0b';
        
        const currentText = neutralNet.getPlainTextFromEditable();
        neutralNet.analyzeText(currentText);
    } else {
        console.error("CRITICAL: Could not determine what text to ignore from this bias object:", bias);
    }
    
    closeAllPopups();
}

window.showBiasSuggestion = showBiasSuggestion;
window.closeAllPopups = closeAllPopups;
window.applySuggestion = applySuggestion;
window.applyCustomSuggestion = applyCustomSuggestion;
window.ignoreBias = ignoreBias; 

let neutralNet;
document.addEventListener('DOMContentLoaded', () => {
    neutralNet = new NeutralNet();
    window.neutralNet = neutralNet; 
});