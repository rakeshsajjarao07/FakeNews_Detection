from flask import Flask, render_template, request, jsonify, session
from deep_translator import GoogleTranslator
from bs4 import BeautifulSoup
import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from langdetect import detect, DetectorFactory
import warnings
import os
import pymysql
from pymysql.err import OperationalError
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key_change_me")

# Fix for langdetect consistency
DetectorFactory.seed = 0
warnings.filterwarnings("ignore")

# Construct absolute path to dataset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, 'dataset.csv')

# Load and preprocess dataset
try:
    data = pd.read_csv(DATASET_PATH)
    data.columns = ['news', 'label']  # Force correct column names
    data['news'] = data['news'].fillna("")
    X = data['news']
    y = data['label']
    
    # Model pipeline
    model = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', LogisticRegression(max_iter=1000))
    ])
    model.fit(X, y)
except Exception as e:
    print(f"⚠️ Dataset Error: {str(e)}")
    print(f"ℹ️ Ensure {DATASET_PATH} exists with columns: 'news', 'label'")

# ========================
# MySQL configuration
# ========================
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Rakeshyadav@07'
MYSQL_DB = 'final_project'


def _connect(db: str | None = None):
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=db,
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )


def init_db():
    try:
        # Ensure database exists
        conn = _connect(None)
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.close()

        # Create tables if not exist
        conn2 = _connect(MYSQL_DB)
        with conn2.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(150) UNIQUE NOT NULL,
                    full_name VARCHAR(255) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB;
                """
            )
            # As requested: a table storing username, fullname, url
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS url_entries (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(150) NOT NULL,
                    full_name VARCHAR(255) NOT NULL,
                    url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX(username)
                ) ENGINE=InnoDB;
                """
            )
        conn2.close()
    except OperationalError as e:
        print(f"⚠️ MySQL connection error: {e}")


def get_db_conn():
    try:
        return _connect(MYSQL_DB)
    except OperationalError:
        init_db()
        return _connect(MYSQL_DB)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/me', methods=['GET'])
def api_me():
    if 'username' in session:
        return jsonify({
            'username': session.get('username'),
            'full_name': session.get('full_name')
        })
    return jsonify(None), 200


@app.route('/api/signup', methods=['POST'])
def api_signup():
    username = request.form.get('username') or (request.json and request.json.get('username'))
    full_name = request.form.get('full_name') or (request.json and request.json.get('full_name'))
    password = request.form.get('password') or (request.json and request.json.get('password'))

    if not username or not full_name or not password:
        return jsonify({'error': 'username, full_name and password are required'}), 400

    password_hash = generate_password_hash(password)
    conn = get_db_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        existing = cur.fetchone()
        if existing:
            return jsonify({'error': 'Username already exists'}), 400
        cur.execute(
            "INSERT INTO users (username, full_name, password_hash) VALUES (%s, %s, %s)",
            (username, full_name, password_hash)
        )
    conn.close()
    session['username'] = username
    session['full_name'] = full_name
    return jsonify({'ok': True, 'username': username, 'full_name': full_name})


@app.route('/api/signin', methods=['POST'])
def api_signin():
    username = request.form.get('username') or (request.json and request.json.get('username'))
    password = request.form.get('password') or (request.json and request.json.get('password'))
    if not username or not password:
        return jsonify({'error': 'username and password are required'}), 400

    conn = get_db_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT id, full_name, password_hash FROM users WHERE username=%s", (username,))
        row = cur.fetchone()
    conn.close()
    if not row or not check_password_hash(row['password_hash'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    session['username'] = username
    session['full_name'] = row['full_name']
    return jsonify({'ok': True, 'username': username, 'full_name': row['full_name']})


@app.route('/api/signout', methods=['POST'])
def api_signout():
    session.clear()
    return jsonify({'ok': True})

@app.route('/detect', methods=['POST'])
def detect_news():
    try:
        url = request.form.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
            
        # Web scraping
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            return jsonify({'error': f"URL fetch failed: {str(e)}"}), 400
            
        soup = BeautifulSoup(response.text, 'html.parser')
        headline = soup.find('h1').get_text().strip() if soup.find('h1') else ""
        
        if not headline:
            return jsonify({'error': 'No headline found'}), 400
            
        # Language handling
        try:
            lang = detect(headline)
            if lang != 'en':
                headline = GoogleTranslator(source='auto', target='en').translate(headline)
        except:
            lang = 'en'  # Fallback to English
        
        # Prediction
        try:
            prediction = model.predict([headline])[0]
            result = "REAL" if prediction == 0 else "FAKE"
            # If logged in, save entry
            if 'username' in session:
                try:
                    conn = get_db_conn()
                    with conn.cursor() as cur:
                        cur.execute(
                            "INSERT INTO url_entries (username, full_name, url) VALUES (%s, %s, %s)",
                            (session.get('username'), session.get('full_name'), url)
                        )
                    conn.close()
                except Exception as db_e:
                    print(f"⚠️ Failed to record URL entry: {db_e}")

            return jsonify({
                'headline': headline,
                'result': result,
                'language': lang,
                'saved': bool(session.get('username'))
            })
        except Exception as e:
            return jsonify({'error': f"Model prediction failed: {str(e)}"}), 500
            
    except Exception as e:
        return jsonify({'error': f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    # Development configuration (safe for local testing)
    init_db()
    app.run(
        debug=True,          # Auto-reload on code changes
        host='127.0.0.1',   # Localhost-only access
        port=4000,          # Explicit port
        use_reloader=True   # Restart server on file changes
    )