# Neutral Net
**Real-Time Language Bias Detection**

Neutral Net is an AI-powered editor designed to detect, categorize and neutralize unconscious bias in professional writing. It is built for the Lady Ada Lovelace Challenge organized by the Programming Club at IIT Kanpur.

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

## Demo and Usage
- **Live Website:** [neutral-net.vercel.app](https://neutral-net.vercel.app) or [Alternate Link](https://neutral-net-git-main-harsshg31085s-projects.vercel.app/) *(If neither of the links open, try using mobile hotspot. IITK wifi may block them)*
- **Backend API:** [Hugging Face Space](https://huggingface.co/spaces/Harssh3108/neutral-net-api) 

*(Note: The API may take a while to boot up from sleep on the first request).*

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
```

### 4. Start the development server
In `backend`:
```bash
python manage.py runserver
```

In a new terminal, navigate to `frontend`:
```bash
cd frontend
npx http-server -p 3000
```

## Tech Stack
  - **Frontend:** Javascript, HTML5, CSS3 (Hosted on Vercel)

  - **Backend:** Python 3.11, Django, Django REST Frameworks (Containerized on Huggingface Spaces)

  - **AI and NLP Engine:**
    - **Transformers:** Contextual sequence classification.
    - **GLiNER:** Generalist and Lightweight Named Entity Recognition
    - **fastcoref:** Fast neural coreference resolution
    - **spaCy:** Grammatical dependency parsing
  
## Documentation
For a much more comprehensive coverage Neutral Net's architecture and inner workings, check out [Documentation Folder](./docs/):
  - **[Architecture Diagram](./docs/architecture.md)**
  - **[API Endpoints](./docs/api.md)**