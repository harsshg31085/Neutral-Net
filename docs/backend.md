# Backend: ML Inference and API Infrastructure

The Neutral Net backend is a stateless Python application built with **Django REST Framework**. It makes use of a multi-model ML pipeline using **Pytorch**, **Transformers**, **fastcoref**, **spacy** along with various fine-tuned models.

## 1. API Gateway
### Stateless Architecture
The backend is designed without the use of databases. When a POST request arrives, the server holds the text and user preferences only for the duration of the inference. Once the JSON response is dispatched, memory is cleared. This removes any risk of cross-user contamination.

### Sub Document Caching
To achieve real-time latency while making use of heavy neural networks, the backend makes use of `functools.lru_cache`. The pipeline tokenizes the incoming words and hashes them. Only newly modified/added sentences are sent for inference, the others are loaded in from the cache. This drastically reduces inference times and compute costs.

### Safe Zones
Since many NLP models work on the same pieces of text simultaneously, it is important to ensure that their results do not collide with each other. Thus, if the stereotype model flags an entire sentence as biased, the other models can no longer highlight those sentences, preventing highlight collisions.

## 2. AI Inference Engines
Neutral Net utilizes four specialized NLP pipelines for core bias detection

### I. Pronoun Bias Detection Pipeline
**Primary Tech Stack:** `fastcoref` (Neural Coreference Resolution), `spacy` (Dependency parsing)

#### What?
This pipeline detects sentences that assume a specific gender for a generic role/profession through pronouns.

For example consider: `A developer must test his code`. 

It flags the bias pronoun (`his`), and suggests a neutral alternative (`their`) while also making sure the grammar surrounding the sentence is structurally sound.

#### But Why?
Using naive regex based "find-and-replace" algorithms for pronoun detection and replacement gives rise to two fatal flaws:
1. **False Positives on Anchored Objects:** Consider the sentences `John is a developer. He is good at Python`. A naive regex based script may flag `He` just because it follows developer.
2. **Grammatical Inaccuracy:** If a script naively replaces `he` with `they` whenever it finds bias, it will turn `he is coding` into `they is coding`, which is grammatically incorrect.

All of these issues are addressed by the Pronoun Bias Detection Pipeline

#### How?
1. **Coreference Resolution:** The engine first maps every pronoun to its nominal subject, making use of neural coreference (`fastcoref`)

2. **Grammatical Anchoring:** Once the pronoun and the noun are linked, the engine uses `spacy` to check if the noun is an "anchored" entity.
* It checks the `ent_type_` to see if the object is a specific `PERSON` or `ORG`
* It checks for definite determiners that prove the text is talking about a real and specific invidual.
* If the subject is a real person, the pipeline ignores the pronoun.

3. **Contextual Evaluation:** If the subject is a generic role, the engine evaluates the verb tense and modals.
* If the text describes a specific past event, it is treated as non-generic and left alone.
* If the text uses obligation modals or conditional markers, the text is assumed to have a generic context, and the engine flags the bias.

4. **Verb Conjugation:** When generating the replacement suggestion, the pipeline traverses the syntax tree to find the `governing_verb` attached to the bias pronoun. The `_get_pronoun_and_verb` method conjugates the auxiliary verbs.
* *e.g. "he was" $\rightarrow$ "they were"*
* *e.g. "she cries" $\rightarrow$ "they cry"*

### II. Gendered Terms Bias Detection Pipeline
**Primary Tech Stack:** `deberta-v3` (Natural Language Inference), `spacy` (Grammar parsing)

#### What?
This pipeline identifies exclusionary gendered terminology and suggests inclusive alternatives

#### Why?
The fatal flaw of dictionary-based bias detectors is the excessive flagging. Consider the sentence: `Our chairman should be arriving any minute`. A simple check for the word "chairman" would immediately flag the sentence, however in this scenario it should not be flagged due to its specific nature.

#### How?
1. **The Gatekeeper:** Running neural network inference on every single noun of the document would grind the entire backend to a halt. As an optimization, we sacrifice some accuracy by maintaining a hardcoded list `self.term_map`. The engine cross-references the lemma of every word against it. If a word doesn't appear in this list, it is skipped entirely.

2. **Grammatical Shortcut:** Once a flagged term is found, the engine maps the dependency tree using `spacy` and uses specific determiners to filter out any non-generic cases (like `my salesman, our chairman`)

3. **Hypothesis Testing:** If the grammar is ambiguous, the engine hands the context over to `deberta-v3` and presents a hypothesis (`"There is a specific, real person who is the [term]"`) to it.

4. **NLI Response Evaluation:** The NLI model compares the user's sentence to the hypothesis and returns probability scores along 3 vectors:
* **Entailment:** The premise proves the hypothesis is true. The word is marked safe.
* **Contradiction/Neutral:** The premise does not prove a specific person exists. The word is flagged, and the replacement is pushed using the dictionary

### III. Agentic/Communal Type Bias Detection Pipeline
**Primary Tech Stack:** `SentenceTransformers` (Semantic Embeddings), `GLiNER` (Zero-Shot NER), `spacy` (Dependency parsing), `DistilRoberta` (Masked Language Modeling)

#### What?
This pipeline detects subconscious tonal skew in text, specifically when human subjects are described with disproportionate "Agentic" or "Communal" traits and suggests tonally neutral alternatives.

#### Why?
Unlike gendered terms, the words themselves are not the problem, it is based on *who* or *what* is being modified.
1. **The Target Problem:** An "aggressive marketing strategy" is a valid business term. An "aggressive female executive" is a genuine example of tonal skew. 
2. **The Context Problem:** A simple thesaurus check may suggest `hostile` as an alternative to `aggressive`, which may not fit the context. 

#### How?
1. **Subject Extraction:** As before, the engine uses `spacy` dependency parsing to isolate the nominal subject of the sentence and map all adjectives and verbs modifying that subject.

2. **Entity Classification:** Before analyzing the tone, the engine must prove the subject is a living person. It uses **GLiNER** to run a zero-shot classification on the subject against labels like "Person" or "Job Role". If the subject is classified as "Technology" or an "Abstract Concept" (e.g., a "strategy" or "market"), the engine immediately halts, preventing false positives on standard technical jargon.

3. **Vector Space Anchoring:** If the target is human, the modifying words are embedded into high-dimensional semantic vectors using `all-MiniLM-L6-v2`. The engine calculates the **Cosine Similarity** of the word against three predefined anchor spaces:
* *Agentic Anchors* (e.g., "dominant", "forceful")
* *Communal Anchors* (e.g., "gentle", "emotional")
* *Functional Anchors* (e.g., "mechanical", "speed")

If the word's vector lands too close to the Agentic or Communal anchors (exceeding a strict `0.35` similarity threshold) and isn't overridden by a Functional context, it is flagged as a skewed bias.

4. **Synonym Generation:** The pipeline uses `Distilroberta` `fill-mask` model for generating contextually-fitting synonyms. It masks the biased word and asks the model to predict 60 fitting replacements. Finally, it runs those 60 predictions back through the `SentenceTransformer` vector space, discarding any words that still carry agentic or communal skew and returns only the top 3 perfectly neutral synonyms.

### IV. Stereotype Bias Detection Pipeline
**Primary Tech Stack:** `Deberta-v3-base` (Sequence Classification), `FLAN-T5` (Seq2Seq Generation)

#### What?
The pipeline identifies and attempts to neutralize sentence-level gender stereotypes.

#### Why?
Stereotype biases never have a single keyword that needs to be replaced in order to neutralize it, it is always a phrase or the sentence as a whole. Moreover, none of the words need to be "dangerous" in order to constitute a stereotype. Hence, deep semantic understanding is required to classify and correct them.

#### How?
Neutral Net uses a dual model architecture to address the issues listed above.

1. **Probabilistic Detection:** The first layer is a custom fine-tuned Sequence Classifier. It processes the embeddings and generates logits. Applying a softmax activation function ($\text{softmax}(z_i) = \frac{e^{z_i}}{\sum_{j} e^{z_j}}$), it calculates the exact probability that the sentence contains a harmful stereotype. If the confidence exceeds a certain threshold (`0.85`), the sentence is flagged as biased.

2. **Replacement Generation:** Once a sentence is flagged, it is passed to a custom fine-tuned Seq2Seq Language based on Google's Flan-T5. The model is prompted to fix the bias in the text. Using Beam Search encoding, the model evaluates multiple potential trajectories to generate the best rewrites while strictly following the 2 listed rules:
* **Debiased Rewrites:** The rewrite itself must not be biased.
* **Semantic Preservation:** The rewrited sentence must not lose semantic meaning.

Incase the rewriter cannot come up with a sentence that satisfies **both** the rules, it returns `[MANUAL REWRITE]`. In the backend, this is reflected as having no replacement suggestions.

3. **Parsing the Response:** The Seq2Seq model was explicitly fine-tuned to return a structured output format containing both the AI's internal reasoning and the suggested text (e.g., `Reason: [explanation] | Rewrite: [suggestion]`). The Python backend parses this string, separating the reason from the actual string-replacement logic for the frontend UI.

## 3. Bias Scoring
Neutral Net makes use of a **length normalized inclusivity score using an exponential decay algorithm**

1. **Severity Weighing:** Different biases, by their nature, carry different penalty. For example, stereotype biases carry a much higher penalty than other more subtle forms of biases, like agentic-communal type biases.
2. **Penalty Density:** The total weighted penalty is divided by the total document's word count to find the concentration of bias. A baseline of `30` words is set to avoid disproportionately penalizing short sentences.
3. **Exponential Decay:** The final score is calculated using the following formula:
$$S = 100\cdot e^{-k\rho}$$
*(Here, k denotes the tuning constant, set at `0.025` and $\rho$ denotes the `penalty density`)*

## 4. Limitations
This section discusses some of the limitations this backend architecture gives rise to.

* **Memory Heavy:** The backend concurrently holds multiple models into memory. This leads to high memory consumption and latency-spikes

* **Caching vs Coreference:** Since coreference relies heavily on sentence to sentence context, the current caching system, which only sends modified/new sentences for analysis may not end up linking the subjects correctly.

* **Incorrect Dependency Parsing:** The pronoun pipeline makes use of spacy's `en_core_web_sm` to navigate dependency trees and conjugate verbs. While this is fast, the model can misidentify root verbs or misinterpret speech in high complex or nested sentences. 

* **Masked LM Synonym Hallucinations:** The `AgenticCommunalDetector` utilizes `distilroberta-base` via a `fill-mask` pipeline to generate neutral alternative words. Because Masked LMs predict the most statistically probable token for a blank space rather than a strict synonym, the model may suggest bizarre or grammatically incorrect replacements that technically fit the sentence structure but change the meaning.

* **Multi-phrasal Sentences:** The stereotype detector struggles to detect biases in highly complex sentences, notably multi-phrasal sentences. Moreover, the rewriter also struggles to rewrite these sentences if bias is detected.

* **Hardcoded Dictionary for Gendered Terms:** If any term outside the dictionary shows up, the pipeline will completely ignore it, even it does constitute a bias.

* **Invoked vs Reported:** In all of the models except for stereotype, biases that are reported will be flagged as if they were directly invoked.

* **Representative Bias:** The stereotype detectors and rewriters are both trained using custom-made datasets, which have a significant probability of having representative bias (Such cases were encountered frequently).

* **Inference Traffic:** If multiple users send inference requests at the same time, they get queued up instead of processing in parallel, causing huge traffic.

* **Token Limits:** Most of the pre-trained models (like `all-MiniLM-L6-v2`) have strict maximum token limits. If a sentence exceeds this threshold, the models may behave weirdly.

* **Inherent Bias in Foundation Models:** Since a lot of this project relies on ready-made models, it is also subject to some of the biases ingrained in said models. For example, when using the `fill-mask` pipeline, the model may suggest statistically common, but potentially biased replacements. 