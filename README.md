# FakeNews_Detection

Fake News Detection App: Built a Flask web app that identifies fake news from URLs using NLP and machine learning. Used TF-IDF with Logistic Regression, integrated web scraping, multilingual support, and created a responsive frontend with HTML, CSS, and JS.


Project-Overview:
________________

Fake News Detection Web Application

The Fake News Detection project is a machine learning-based web application designed to classify online news as either real or fake. Built using Python, Flask, and scikit-learn, this system leverages Natural Language Processing (NLP) techniques and a logistic regression model to detect misinformation from news article headlines.

The application starts with a user submitting a URL of a news article through a simple and intuitive frontend built with HTML, CSS, and JavaScript. The backend uses BeautifulSoup and requests to scrape the webpage and extract the main headline. To ensure global usability, the system incorporates language detection (using langdetect) and automatic translation to English (using deep-translator) if the headline is in another language.

Once translated (if needed), the headline text is vectorized using the TF-IDF (Term Frequency-Inverse Document Frequency) method, which transforms the textual data into numerical features. These features are then passed to a logistic regression model trained on a labeled dataset of real and fake news headlines. The model outputs a binary classification result indicating whether the input news is real (0) or fake (1).

The final prediction is sent back to the frontend and displayed to the user, along with the detected language and the translated headline if applicable. Error handling is included to manage issues like invalid URLs, missing headlines, and server errors.

This project demonstrates full-stack development skills, including web scraping, NLP, machine learning, Flask API development, and frontend integration. It also showcases the ability to handle real-world challenges like multilingual input and unreliable web sources. The result is a lightweight but effective tool to combat the spread of fake news.

**Requirements:**
_________________

🔧 System Requirements
 ----------------------
  1.Python 3.7 or above

  2.Modern web browser (e.g., Chrome, Firefox)

 Functional Requirements
 -----------------------
   1.Accept a URL from the user.

   2.Scrape the headline from the URL.

   3.Detect and translate non-English headlines.

   4.Predict whether the news is fake or real using a trained ML model.

   5.Display results (headline, prediction, language) to the user.


  

