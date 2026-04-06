# Frontend: Client Side UI

The Neutral Net frontend is a lightweight web app hosted on Vercel. It is built entirely using **Javascript, HTML and CSS**

## 1. Core Tech
* **Javascript:** Handles state management, API calls, debouncing and DOM manipulation.
* **CSS:** Responsible for the theme and SVG animations.
* **Chart.js:** Renders the "Bias Distribution" bias chart.
* **FontAwesome:** Supplies icons for the UI

## 2. UI Layout and Architecture
The interface is designed as a split-pane dashboard to maximize the workspace, while allowing the user to access the analytics dashboards

### The Editor Panel
A dual-layered approach had to be used, since a standard `<textarea>` cannot render background colors.
1. **`contenteditable="true"` `<div>`:** The actual interactive surface where the user types text. It can safely render the bias highlight spans returned by the backend
2. **Hidden Textarea:** A hidden text area serves as a fallback and pure-text buffer.
3. **The Interactive Toolbar:**
    * **Upload:** Triggers `<input type="file">` restricted to `.docx` and `.pdf` files. Allows the user to upload pre-written text directly for analysis.
    * **Export:** Extracts the neutralized text and exports it as a `.txt` file
    * **Fix-All:** Applies the top suggestion for every single detected bias at once.

### The Analytics Panel
1. **The Score Pie Chart:** Animated pie chart showing the calculated bias score
2. **Bias Legend:** A real-time counter tracking the quantities of all different bias categories
3. **Radar Chart:** A Chart.js canvas the visually maps the specific distribution of biases across the document

## 3. State Management and Logic (app.js)
Since the application is stateless, the frontend acts as the single source of truth for the user's session.

### Traffic Control and Debouncing
To prevent applying corrections while the user is typing, the frontend uses a strict debounce timer of 500 ms. The API fetch requests are fired only when the user has actually stopped typing.

### Stale State Handling
When a user types rapidly, a network request might take 800ms to return. If the user continues typing during those 800ms, injecting the delayed server response would overwrite their newest words. The frontend prevents this by caching the exact text string sent to the server. When the response arrives, it compares the current editor state to the cached string. If they do not match, the response is discarded.

### Cursor Preservation
Since the backend returns the `<span>` elements, directly updating the text would shift the user's cursor. We calculate the exact offset that would be caused by the HTML formatting, and then shift the cursor accordingly, to keep typing smooth.

### Interactive Bias Resolution and Tooltips
When the backend identifies a bias, it wraps the text in a span with a unique ID.
* **Click Event:** Clicking a highlighted word intercepts the event listener, looks up the corresponding bias object and generates and displays the UI card
* **DOM Swapping:** If a user clicks on a replacement, we swap the biased span with the replacement, reset the cursor and recalculate the score.

### Local Memory (User Preferences)
User preferences are maintained without a database. If a user ignores a suggestion, the word is added to a `Set()`. This set is sent in the JSON payload in every API request

### XSS Failsafe
The backend converts HTML tags to safe entities, to avoid users from typing something like `<script> alert() </script>`