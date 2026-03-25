# Neutral Net
**Real-Time Language Bias Detection**

## Features
- **Real-Time Multi-Model Detection** - Analyzes text instantly as you type, powered by specialized AI models (Transformer-based classification, Zero-Shot NER, and Neural Coreference Resolution)

- **Bias Categorization** - Detects contextual bias across four categories:
  - **Stereotypes** - Blocks harmful generalizations at sentence/phrase level.
  - **Gendered-Terms** - Flags outdated roles ("chairman"), while ignoring safe contexts.
  - **Agentic/Communal Tone Skew** - Detects subtle, subconscious phrasing that diminishes technical roles or amplifies hostility.
  - **Pronoun Bias** - Maps pronouns back to original subjects to detect forced gender roles.

- **"Fix All" and Interactive Resolution** - Offers one-click neutralization of all fixable biases. Users can also click individual highlights for AI-generated synonyms, custom replacements or to "Ignore" a flag.

- **Document Support** - Parses and extracts text from uploaded PDFs (`.pdf`) and Word Documents (`.docx`) for bulk analysis.

- **Algorithmic Inclusivity Scoring** - Calculates a bias score using an Exponential Decay algorithm and severity weights, ensuring short sentences aren't unfairly penalized.

- **Live Analytics Dashboard** - Features a Radar Chart that visually maps the distribution of biases.

- **Export to TXT** - Instantly download the neutralized text as `.txt` with a single click.

- **Sub-Document LRU Caching** - An optimized backend infrastructure that caches inference result and reduces latency by over 80%.

## Local Setup Instructions
Follow these steps to run `Neutral Net` on your local machine.

### 1. Clone the Repository
```bash
git clone https://github.com/harsshg31085/Neutral-Net
cd backend
```

### 2. Create and activate a virtual environment
```bash
# Windows
py -3.11 -m venv venv
.\venv\Scripts\Activate

# Mac/Linux
python3.11 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Start the development server
In `backend`:
```bash
python manage.py runserver
```

In `frontend`:
```bash
npx http-server -p 3000
```