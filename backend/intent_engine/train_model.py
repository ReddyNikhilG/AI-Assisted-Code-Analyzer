import os
import pickle
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.linear_model import LogisticRegression
from intent_engine.dataset import dataset

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(CURRENT_DIR, "model")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "intent_model.pkl")

print("Loading Microsoft CodeBERT model and tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModel.from_pretrained("microsoft/codebert-base")
model.eval()

print("Generating semantic embeddings for the training dataset...")
X = []
y = []

with torch.no_grad():
    for i, item in enumerate(dataset):
        code = item["code"]
        intent = item["intent"]
        
        inputs = tokenizer(code, return_tensors="pt", truncation=True, max_length=512)
        outputs = model(**inputs)
        
        # Extract the CLS token embedding representing sequence summary
        cls_emb = outputs[0][:, 0, :].numpy()[0]
        
        X.append(cls_emb)
        y.append(intent)
        
        if (i + 1) % 10 == 0 or (i + 1) == len(dataset):
            print(f"Processed {i + 1}/{len(dataset)} items...")

X = np.array(X)
y = np.array(y)

print("Training Logistic Regression classifier on top of CodeBERT embeddings...")
clf = LogisticRegression(max_iter=1000, C=1.0)
clf.fit(X, y)

with open(MODEL_PATH, "wb") as f:
    pickle.dump(clf, f)

print(f"Logistic classifier model saved to {MODEL_PATH} successfully!")