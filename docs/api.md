# API Documentation

The Neutral Net backend contains a REST API built with Django. It handles real-time text analysis and document extraction.

**Base URL (Production):** `https://Harssh3108-neutral-net-api.hf.space`

**Base URL (Local):** `http://localhost:8000`

## 1. Real Time Analysis
**Endpoint:** `/api/real-time-analyze/`
**Method:** `POST`

Accepts raw text, processes it through the NLP pipeline, and returns the inclusivity score alongside the HTML-formatted text for the frontend.

### Request Payload (`application/json`)
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `text` | `string` | The raw text to be analyzed. |
| `ignored_texts` | `array` | A list of strings (words/phrases) the user has explicitly chosen to ignore. The detector will bypass these. |
---
**Example Request:**
```json
{
    "text": "The businessman walked into the meeting.",
    "ignored_texts": ["chairman"]
}
```

**Response (`200 OK`):**
| Key | Type | Description |
| :--- | :--- | :--- |
| `text` | `string` | The original raw text. |
| `highlighted_html` | `string` | The text wrapped in HTML `<span>` tags with background colors based on type |
| `biases` | `array` | A list of detected bias objects, containing the `id`, `type`, `description`, `suggestion`, `alternatives` and character `position` |
| `score` | `int` | The calculated inclusivity score from 0-100 |
| `pronoun_stats` | `object` | Breakdown of pronoun usage |
| `word_count` | `integer` | Number of words analyzed. |

---
**Error Handling (`500 Internal Server Error`):**
If the AI pipeline fails, the server falls back safely to prevent crashing the frontend.
```json
{
    "error": "Error trace string",
    "text": "",
    "highlighted_html": "",
    "biases": [],
    "score": 100
}
```

## 2. Document Upload
**Endpoint:** `/api/upload-document`
**Method:** `POST`

Extracts plain text from uploaded text for analysis.

**Request Payload:** (`multipart/form-data`)
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `file` | `file` | The document to be parsed. Supports `.pdf` and `.docx`. |

**Response (`200 OK`):**
```json
{
    "success": true,
    "text": "Extracted plain text"
}
```
**Error Handling**
* `400 Bad Request`: Returned if `file` is missing, or if an unsupported file format is uploaded.
* `500 Internal Server Error`: Returned if the extraction libraries (`pypdf` or `docx`) fail to parse the file.

## 3. Apply Suggestion
**Endpoint:** `/api/apply-suggestion/`
**Method:** `POST`

Triggered when a user explicitly clicks to apply a suggested fix.

**Request Payload:** (`application/json`)
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `original_text` | `string` | The state of the text before the fix. |
| `bias-id` | `string` | The UUID of the string being fixed. |
| `replacement` | `string` | The fixed text |

**Response (`200 OK`)**:
```json
{
  "success": true,
  "message": "Suggestion applied",
  "bias_id": "uuid-string",
  "replacement": "replacement string"
}
```