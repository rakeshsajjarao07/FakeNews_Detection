from flask import Flask, render_template, request, jsonify
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

# Initialize Flask app
app = Flask(__name__)

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

@app.route('/')
def home():
    return render_template('index.html')

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
            return jsonify({
                'headline': headline,
                'result': result,
                'language': lang
            })
        except Exception as e:
            return jsonify({'error': f"Model prediction failed: {str(e)}"}), 500
            
    except Exception as e:
        return jsonify({'error': f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    # Development configuration (safe for local testing)
    app.run(
        debug=True,          # Auto-reload on code changes
        host='127.0.0.1',   # Localhost-only access
        port=5000,          # Explicit port
        use_reloader=True   # Restart server on file changes
    )
