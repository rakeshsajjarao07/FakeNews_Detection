## Fake News Detector

A Flask-based web app that predicts whether a news article headline is REAL or FAKE from a given URL. It scrapes the page headline, detects and translates non‑English text to English, vectorizes with TF‑IDF, and classifies using Logistic Regression. Authenticated users have their analyzed URLs saved to MySQL.

### Table of Contents
- Features
- Project Workflow
- Architecture and Modules
- Technologies Used
- Project Structure
- Setup and Installation
- Running the App
- API Reference
- Data and Model
- Database
- Frontend UI
- Troubleshooting and Notes

---

## Features
- Headline scraping from a provided URL.
- Language detection and auto-translation to English.
- TF‑IDF + Logistic Regression classification.
- Email-less authentication (username + password).
- Saves analyzed URLs for signed-in users.
- Simple responsive UI (HTML/CSS/vanilla JS).

## Project Workflow
1. App startup
   - Loads `dataset.csv` with columns `news` and `label` (0 = REAL, 1 = FAKE).
   - Trains an in-memory scikit‑learn pipeline: `TfidfVectorizer` + `LogisticRegression`.
   - Initializes MySQL database and tables if missing.

2. User interaction
   - User opens `/` and sees a single-page interface.
   - Optional: user signs up or signs in.

3. URL analysis
   - User submits a news article URL.
   - Server fetches the page (requests) and parses `<h1>` (BeautifulSoup).
   - Detects headline language (langdetect) and translates to English if needed (deep-translator).
   - Runs the trained model to classify as REAL or FAKE.

4. Persistence (if authenticated)
   - Saves the submitted URL along with `username` and `full_name` into MySQL.

5. Response
   - Returns JSON with `headline`, `result` ("REAL" or "FAKE"), `language`, and whether it was saved.

## Architecture and Modules
- Web Server (Flask)
  - Routes:
    - `/` (GET): Renders the UI.
    - `/api/me` (GET): Returns current session user.
    - `/api/signup` (POST): Creates user; starts a session.
    - `/api/signin` (POST): Authenticates; starts a session.
    - `/api/signout` (POST): Clears session.
    - `/detect` (POST): Core inference endpoint.
  - Session: Flask server-side session using `secret_key`.

- Scraper
  - `requests` to fetch the URL with a standard user-agent and timeout.
  - `BeautifulSoup` to extract the first `<h1>` as the headline.

- Language Handling
  - `langdetect` to detect language of the headline.
  - `deep-translator` (GoogleTranslator) to translate to English if not English.

- ML Pipeline
  - `TfidfVectorizer` for text feature extraction.
  - `LogisticRegression(max_iter=1000)` for binary classification.
  - Trained at startup on `dataset.csv` and kept in memory.

- Persistence (MySQL via PyMySQL)
  - `users` table: stores username, full name, password hash.
  - `url_entries` table: stores username, full name, and submitted URL.
  - Auto-creates DB and tables if missing.

- Auth
  - Signup/signin forms (username, password; plus full name for signup).
  - Passwords hashed with Werkzeug `generate_password_hash`.
  - Session tracks `username` and `full_name`.

- Frontend UI
  - `templates/index.html`: Single-page app with modals and fetch-based API calls.
  - `static/styles.css`: Modern glassmorphism styles.
  - Vanilla JS for form handling and API requests.

## Technologies Used
- Backend: Flask, Python 3
- ML/NLP: scikit‑learn (Pipeline, TF‑IDF, Logistic Regression), pandas
- Web Scraping: requests, BeautifulSoup4
- Language: langdetect, deep-translator (GoogleTranslator)
- Database: MySQL (PyMySQL)
- Frontend: HTML, CSS, vanilla JavaScript
- Other: Werkzeug (password hashing)

## Project Structure
- `app.py`: Flask app, ML pipeline, routes, DB init, and handlers.
- `templates/index.html`: Frontend page with forms, modals, and client JS.
- `static/styles.css`: UI styles.
- `dataset.csv`: Training data with `news,label`.
- `requirements.txt`: Python dependencies.
- `venv/`: (local virtual environment, optional)

## Setup and Installation
1. Prerequisites
   - Python 3.10+ recommended.
   - MySQL Server accessible from your machine.
   - Windows users can use Command Prompt or PowerShell.

2. Create and activate a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Optional: set a secret key for sessions
```bash
set FLASK_SECRET_KEY=your_very_secret_key
```

5. Ensure MySQL is running and credentials in `app.py` match your setup
- Host, port, user, password, and DB name are defined in `app.py`.
- The app will create the database `final_project` and required tables if they don’t exist.

## Running the App
```bash
python app.py
```
- Server: `http://127.0.0.1:4000`
- On startup:
  - `dataset.csv` is loaded and the model is trained.
  - MySQL database/tables are initialized if needed.

## API Reference
- GET `/api/me`
  - Response: current session user or `null`.
```json
{ "username": "john", "full_name": "John Doe" }
```

- POST `/api/signup` (x-www-form-urlencoded or JSON)
  - Fields: `username`, `full_name`, `password`
  - Response: `{ ok: true, username, full_name }` or `{ error }`

- POST `/api/signin` (x-www-form-urlencoded or JSON)
  - Fields: `username`, `password`
  - Response: `{ ok: true, username, full_name }` or `{ error }`

- POST `/api/signout`
  - Response: `{ ok: true }`

- POST `/detect` (x-www-form-urlencoded)
  - Fields: `url`
  - Response:
```json
{
  "headline": "Detected or translated headline text",
  "result": "REAL",
  "language": "en",
  "saved": true
}
```
  - Errors:
```json
{ "error": "URL fetch failed: ..." }
{ "error": "No headline found" }
{ "error": "Model prediction failed: ..." }
```

### Example cURL
```bash
curl -X POST http://127.0.0.1:4000/detect ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  --data-urlencode "url=https://example.com/news-article"
```

## Data and Model
- Dataset file: `dataset.csv` with headers:
  - `news` (string): headline or news text
  - `label` (int): 0 = REAL, 1 = FAKE
- Training:
  - Happens at app startup.
  - Pipeline: `TfidfVectorizer` → `LogisticRegression(max_iter=1000)`.
- Prediction:
  - Scraped/translated headline passed into the pipeline.
  - Output mapped to `"REAL"` for `0`, `"FAKE"` for `1`.

## Database
- Connection: MySQL, credentials defined in `app.py`.
- Database: `final_project` (auto-created if missing).
- Tables (auto-created):
  - `users(id, username UNIQUE, full_name, password_hash, created_at)`
  - `url_entries(id, username, full_name, url, created_at, INDEX(username))`

## Frontend UI
- Single page (`/`) with:
  - URL input and "Analyze" button.
  - Results area showing headline, result, and errors.
  - Sign In / Sign Up modals and session-aware navbar.
- Client JS calls:
  - `/api/me`, `/api/signup`, `/api/signin`, `/api/signout`, `/detect`.

## Troubleshooting and Notes
- Dataset issues: Ensure `dataset.csv` exists with columns `news,label`. Missing/invalid data will be logged on startup.
- Headline scraping: Relies on the first `<h1>` element. Sites without `<h1>` may fail.
- Network/translation: External requests (page fetch and translation) may timeout or fail.
- MySQL access: Ensure correct host/port/credentials and that the user has permissions to create DB and tables.
- Security:
  - Update the MySQL credentials in `app.py` to match your environment.
  - Set `FLASK_SECRET_KEY` in production.
  - Do not expose this development configuration directly to the internet.
- Retraining: Update `dataset.csv` and restart the app to retrain the model.

---
