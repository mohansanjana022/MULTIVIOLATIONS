
import torch
import torch.nn as nn
from transformers import DistilBertTokenizer, DistilBertModel


class AccidentClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.bert = DistilBertModel.from_pretrained("distilbert-base-uncased")
        self.dropout = nn.Dropout(0.3)
        self.out = nn.Linear(768, 6)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled = outputs.last_hidden_state[:, 0]
        return self.out(self.dropout(pooled))


tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")


def load_model(path):
    model = AccidentClassifier()
    model.load_state_dict(torch.load(path, map_location="cpu"))
    model.eval()
    return model


def predict(model, text):

    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.sigmoid(outputs).numpy()[0]

    # ==============================
    # 🔥 HYBRID KEYWORD BOOST LOGIC
    # ==============================
    text_lower = text.lower()

    if "speed" in text_lower:
        probs[0] = max(probs[0], 0.80)

    if "red light" in text_lower or "signal" in text_lower:
        probs[1] = max(probs[1], 0.80)

    if "drunk" in text_lower or "alcohol" in text_lower:
        probs[5] = max(probs[5], 0.85)

    if "wrong lane" in text_lower:
        probs[4] = max(probs[4], 0.75)

    if "careless" in text_lower:
        probs[2] = max(probs[2], 0.70)

    if "mobile" in text_lower or "phone" in text_lower:
        probs[3] = max(probs[3], 0.75)

    # ==============================
    # Violation Labels
    # ==============================

    labels = [
        "Speeding",
        "Signal Violation",
        "Careless Driving",
        "Distraction",
        "Wrong Lane",
        "Drunk Driving"
    ]

    # Multi-violation threshold
    STRONG_THRESHOLD = 0.30

    results = [labels[i] for i, p in enumerate(probs) if p >= STRONG_THRESHOLD]

    if not results:
        return ["No Strong Violation Detected"]

    return results


