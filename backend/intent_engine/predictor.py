import os
import pickle
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "model", "intent_model.pkl")

try:
    print("Initializing CodeBERT intent predictor...")
    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
    model = AutoModel.from_pretrained("microsoft/codebert-base")
    model.eval()
    
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            classifier = pickle.load(f)
    else:
        classifier = None
except Exception as e:
    print(f"Error loading CodeBERT predictor model: {e}")
    tokenizer = None
    model = None
    classifier = None


class IntentPredictor:

    def predict(self, code):
        if not model or not tokenizer or not classifier:
            return {
                "intent": "General Utility / Scripting",
                "confidence": 0.0,
                "top_predictions": []
            }

        # Tokenize and extract embedding
        inputs = tokenizer(code, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        cls_emb = outputs[0][:, 0, :].numpy()[0]

        # Use classifier to predict intent and class probabilities
        pred = classifier.predict([cls_emb])[0]
        probs = classifier.predict_proba([cls_emb])[0]
        classes = classifier.classes_

        top_prob = probs[list(classes).index(pred)]
        confidence = round(float(top_prob), 2)

        # Fallback to general scripting if prediction probability is too low
        prediction = pred
        if confidence < 0.35:
            prediction = "General Utility / Scripting"

        # Build top-3 predictions
        all_predictions = []
        for c, p in zip(classes, probs):
            all_predictions.append({
                "intent": str(c),
                "confidence": round(float(p), 2)
            })
        all_predictions.sort(key=lambda x: x["confidence"], reverse=True)
        top_predictions = all_predictions[:3]

        return {
            "intent": prediction,
            "confidence": confidence,
            "top_predictions": top_predictions
        }