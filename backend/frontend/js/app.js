class EquityMirror {
    constructor() {
        this.currentBiases = [];
        this.currentText = '';
        this.currentAnalysis = null;
        
        this.initializeElements();
        this.bindEvents();
        this.initializeApp();
    }
    
    initializeElements() {
        // Input elements
        this.textInput = document.getElementById('text-input');
        this.highlightedOutput = document.getElementById('highlighted-text');
        this.fileUpload = document.getElementById('file-upload');
        this.fileName = document.getElementById('file-name');
        
        // Button elements
        this.analyzeBtn = document.getElementById('analyze-btn');
        this.clearBtn = document.getElementById('clear-btn');
        this.applyBtn = document.getElementById('apply-btn');
        
        // Score elements
        this.overallScore = document.getElementById('overall-score');
        this.pronounBalance = document.getElementById('pronoun-balance');
        this.biasCount = document.getElementById('bias-count');
        this.wordCount = document.getElementById('word-count');
        
        // Suggestion elements
        this.suggestionsContainer = document.getElementById('suggestions-container');
        this.suggestionDetails = document.getElementById('suggestion-details');
        this.suggestionTitle = document.getElementById('suggestion-title');
        this.suggestionDescription = document.getElementById('suggestion-description');
        this.alternativesList = document.getElementById('alternatives-list');
        this.replacementInput = document.getElementById('replacement-input');
        
        // Popup
        this.popup = document.getElementById('suggestion-popup');
        this.popupContent = document.getElementById('popup-content');
        this.closePopup = document.querySelector('.close-btn');
        
        // Score circle
        this.scoreCircle = document.querySelector('.score-circle');
    }
    
    bindEvents() {
        // Analyze button
        this.analyzeBtn.addEventListener('click', () => this.analyzeText());
        
        // Clear button
        this.clearBtn.addEventListener('click', () => this.clearText());
        
        // File upload
        this.fileUpload.addEventListener('change', (e) => this.handleFileUpload(e));
        
        // Apply suggestion
        this.applyBtn.addEventListener('click', () => this.applySuggestion());
        
        // Popup close
        this.closePopup.addEventListener('click', () => this.closeSuggestionPopup());
        
        // Close popup when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === this.popup) {
                this.closeSuggestionPopup();
            }
        });
        
        // Enter key in replacement input
        this.replacementInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.applySuggestion();
            }
        });
    }
    
    initializeApp() {
        // Set up initial score circle
        this.updateScoreCircle(100);
    }
    
    async analyzeText() {
        const text = this.textInput.value.trim();
        
        if (!text) {
            alert('Please enter some text to analyze.');
            return;
        }
        
        this.currentText = text;
        
        try {
            // Show loading state
            this.analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            this.analyzeBtn.disabled = true;
            
            // Call API
            const response = await fetch('/api/analyze/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });
            
            if (!response.ok) {
                throw new Error('Analysis failed');
            }
            
            const data = await response.json();
            this.currentAnalysis = data;
            this.currentBiases = data.biases;
            
            // Update UI
            this.updateTextDisplay(data.highlighted_text);
            this.updateScoreboard(data);
            this.setupBiasHighlights();
            
        } catch (error) {
            console.error('Error analyzing text:', error);
            alert('Failed to analyze text. Please try again.');
        } finally {
            // Reset button
            this.analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Text';
            this.analyzeBtn.disabled = false;
        }
    }
    
    updateTextDisplay(highlightedHtml) {
        // Hide textarea, show highlighted output
        this.textInput.style.display = 'none';
        this.highlightedOutput.innerHTML = highlightedHtml;
        this.highlightedOutput.style.display = 'block';
    }
    
    updateScoreboard(data) {
        // Update score
        this.overallScore.textContent = data.overall_score;
        this.updateScoreCircle(data.overall_score);
        
        // Update pronoun balance
        const balance = data.pronoun_stats?.pronoun_balance || 100;
        this.pronounBalance.textContent = `${balance}%`;
        
        // Update bias count
        this.biasCount.textContent = data.bias_count;
        
        // Update word count
        this.wordCount.textContent = data.word_count;
    }
    
    updateScoreCircle(score) {
        // Convert score to degrees (0-360)
        const degrees = (score / 100) * 360;
        this.scoreCircle.style.setProperty('--score-degree', `${degrees}deg`);
        
        // Update color based on score
        let color = '#06d6a0'; // Green for good
        if (score < 70) color = '#ffd166'; // Yellow for medium
        if (score < 40) color = '#ff6b6b'; // Red for poor
        
        this.scoreCircle.style.background = 
            `conic-gradient(${color} ${degrees}deg, #e0e0e0 0deg)`;
    }
    
    setupBiasHighlights() {
        // Clear any existing event listeners
        const highlights = this.highlightedOutput.querySelectorAll('.bias-highlight');
        highlights.forEach(highlight => {
            highlight.onclick = null;
        });
        
        // Add click handlers to bias highlights
        highlights.forEach(highlight => {
            highlight.onclick = (e) => {
                e.stopPropagation();
                const biasId = highlight.dataset.biasId;
                const biasType = highlight.dataset.biasType;
                const biasText = highlight.textContent;
                
                this.showBiasDetails(biasId, biasType, biasText);
            };
        });
    }
    
    showBiasDetails(biasId, biasType, biasText) {
        // Find the bias in current analysis
        const bias = this.currentBiases.find(b => b.id === biasId);
        
        if (!bias) {
            console.warn('Bias not found:', biasId);
            return;
        }
        
        // Update suggestion details
        this.suggestionTitle.textContent = `Fix ${biasType.replace('_', ' ')} Bias`;
        this.suggestionDescription.textContent = bias.suggestion;
        
        // Update alternatives
        this.alternativesList.innerHTML = '';
        if (bias.alternatives && bias.alternatives.length > 0) {
            bias.alternatives.forEach(alt => {
                const chip = document.createElement('div');
                chip.className = 'alternative-chip';
                chip.textContent = alt;
                chip.onclick = () => {
                    this.replacementInput.value = alt;
                };
                this.alternativesList.appendChild(chip);
            });
        }
        
        // Set replacement input placeholder
        this.replacementInput.placeholder = `Replace "${biasText}" with...`;
        this.replacementInput.dataset.biasId = biasId;
        this.replacementInput.dataset.originalText = biasText;
        
        // Show suggestion details
        this.suggestionDetails.style.display = 'block';
        
        // Scroll to suggestions
        this.suggestionDetails.scrollIntoView({ behavior: 'smooth' });
    }
    
    async applySuggestion() {
        const replacement = this.replacementInput.value.trim();
        const biasId = this.replacementInput.dataset.biasId;
        const originalText = this.replacementInput.dataset.originalText;
        
        if (!replacement) {
            alert('Please enter a replacement text.');
            return;
        }
        
        try {
            // In a real implementation, you would send this to the backend
            // For now, we'll update the UI directly
            
            // Find and replace in highlighted text
            const highlight = this.highlightedOutput.querySelector(`[data-bias-id="${biasId}"]`);
            if (highlight) {
                highlight.innerHTML = `<span style="text-decoration: line-through; color: #999">${originalText}</span> → <strong style="color: #06d6a0">${replacement}</strong>`;
                highlight.style.backgroundColor = '#e8f5e9';
                highlight.style.cursor = 'default';
                highlight.onclick = null;
            }
            
            // Update the original text
            if (this.currentAnalysis) {
                this.currentAnalysis.text = this.currentAnalysis.text.replace(
                    new RegExp(originalText, 'g'),
                    replacement
                );
            }
            
            // Clear input
            this.replacementInput.value = '';
            
            // Show success message
            alert('Suggestion applied successfully!');
            
        } catch (error) {
            console.error('Error applying suggestion:', error);
            alert('Failed to apply suggestion.');
        }
    }
    
    clearText() {
        this.textInput.value = '';
        this.highlightedOutput.innerHTML = '';
        this.highlightedOutput.style.display = 'none';
        this.textInput.style.display = 'block';
        
        this.suggestionDetails.style.display = 'none';
        this.replacementInput.value = '';
        
        // Reset scores
        this.overallScore.textContent = '100';
        this.updateScoreCircle(100);
        this.pronounBalance.textContent = '100%';
        this.biasCount.textContent = '0';
        this.wordCount.textContent = '0';
        
        this.currentBiases = [];
        this.currentAnalysis = null;
        
        // Focus on text input
        this.textInput.focus();
    }
    
    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        this.fileName.textContent = file.name;
        
        // Read file content
        const reader = new FileReader();
        
        reader.onload = (e) => {
            const content = e.target.result;
            this.textInput.value = content;
            
            // Auto-analyze if there's content
            if (content.trim()) {
                setTimeout(() => this.analyzeText(), 500);
            }
        };
        
        // Handle different file types
        if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
            reader.readAsText(file);
        } else if (file.type.includes('pdf')) {
            // For PDF files, you would need a PDF parser library
            alert('PDF parsing requires additional libraries. Please upload a text file.');
        } else {
            alert('Please upload a text file (.txt)');
        }
    }
    
    showSuggestionPopup(content) {
        this.popupContent.innerHTML = content;
        this.popup.style.display = 'flex';
    }
    
    closeSuggestionPopup() {
        this.popup.style.display = 'none';
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new EquityMirror();
    console.log('Equity Mirror initialized');
    
    // Example text for testing
    const exampleText = `The CEO announced his vision for the company. He was very aggressive in his approach and made decisive moves. The nurses in the hospital were always caring and emotional with patients.`;
    document.getElementById('text-input').value = exampleText;
});