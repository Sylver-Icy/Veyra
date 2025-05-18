import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
model = joblib.load(BASE_DIR / "nsfw_classifier_v1.pkl")
vectorizer = joblib.load(BASE_DIR / "vectorizer.pkl")

def classify(text):
    """Function to classify whether the input text is Nsfw or Sfw along with confidence"""
    vec = vectorizer.transform([text])
    prediction = model.predict(vec)[0]
    confidence = model.predict_proba(vec)[0]

    return prediction, confidence