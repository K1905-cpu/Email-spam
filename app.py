"""
=============================================================================
Email Spam Detection - Web Application Server
Author: Kalp Shah
=============================================================================
"""

import os
import re
import json
import joblib
import numpy as np
from flask import Flask, request, jsonify, render_template, send_from_directory

app = Flask(__name__, static_folder="frontend", static_url_path="", template_folder="frontend")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "spam_model.joblib")
VEC_PATH = os.path.join(BASE_DIR, "vectorizer.joblib")
META_PATH = os.path.join(BASE_DIR, "model_metadata.json")

# Load model and vectorizer
model = None
vectorizer = None
metadata = {}

try:
    if os.path.exists(MODEL_PATH) and os.path.exists(VEC_PATH):
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VEC_PATH)
    if os.path.exists(META_PATH):
        with open(META_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)
except Exception as e:
    print(f"Error loading model: {e}")

def clean_text(text: str) -> str:
    """Preprocesses input text."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", " url_link ", text)
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", " email_addr ", text)
    text = re.sub(r"[$€£₹]\s*\d+([.,]\d+)?|\d+\s*(dollars|usd|inr|pounds|euro|euros|bitcoin|btc)", " currency_amount ", text)
    text = re.sub(r"\b\d{10,}\b|\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b", " phone_number ", text)
    text = re.sub(r"[^a-zA-Z_\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

SPAM_KEYWORDS = [
    "urgent", "winner", "won", "prize", "lottery", "congratulations", "claim",
    "password", "suspended", "unauthorized", "locked", "funds", "frozen", "verify",
    "bitcoin", "crypto", "free", "cash", "loan", "earn", "money", "offer", "discount",
    "viagra", "keto", "pharmacy", "replica", "airdrop", "deposit", "payout", "risk",
    "guaranteed", "wire", "transfer", "dispute", "redelivery", "wallet", "credit", "irs"
]

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route("/history")
@app.route("/history.html")
def history_page():
    return send_from_directory("frontend", "history.html")

@app.route("/impact")
@app.route("/impact.html")
@app.route("/accuracy")
def impact_page():
    return send_from_directory("frontend", "impact.html")

@app.route("/api/stats", methods=["GET"])
def get_stats():
    return jsonify({
        "status": "success",
        "metadata": metadata,
        "model_loaded": model is not None
    })

@app.route("/api/samples", methods=["GET"])
def get_samples():
    samples = [
        {
            "id": 1,
            "title": "Crypto Lottery Win (Phishing)",
            "type": "spam",
            "subject": "CONGRATULATIONS! Claim your 2.5 Bitcoin Reward",
            "body": "Congratulations! You have been selected as the grand winner of the 2026 Crypto Sweepstakes. You won 2.5 Bitcoin (BTC) valued at $165,000. Connect your wallet or reply with your bank details immediately to claim your funds before deadline!"
        },
        {
            "id": 2,
            "title": "Urgent Bank Security Alert",
            "type": "spam",
            "subject": "URGENT: Your account has been temporarily locked",
            "body": "Security Alert: Unauthorized login attempt detected on your bank account. Your access has been restricted. Click here to verify your password and identity immediately to avoid permanent account suspension."
        },
        {
            "id": 3,
            "title": "Work From Home Easy Money",
            "type": "spam",
            "subject": "Earn $500 to $800 Daily Working Online",
            "body": "Immediate hiring for online product review assistants. Work from home just 2 hours a day and make thousands of dollars. No experience needed. WhatsApp us right now to start earning cash instantly!"
        },
        {
            "id": 4,
            "title": "Flight Booking Confirmation",
            "type": "ham",
            "subject": "E-Ticket Confirmation: Indigo Flight 6E-284 from AMD to BOM",
            "body": "Dear Kalp, your flight booking reference PNR #X8K92P has been confirmed. Departure is scheduled for Friday at 07:15 AM from Terminal 1, Ahmedabad (AMD) arriving at Mumbai (BOM) at 08:30 AM. Web check-in opens 24 hours prior to departure. Have a pleasant journey."
        },
        {
            "id": 5,
            "title": "Cloud Services Invoice Receipt",
            "type": "ham",
            "subject": "Monthly Payment Receipt: Invoice #INV-2026-089",
            "body": "Hello Kalp, thank you for your payment. Your cloud hosting and database cluster subscription for the period of August 2026 has been successfully processed. Total Amount: $49.00 charged to your card ending in 4128. Download your full PDF tax invoice from your account billing portal."
        },
        {
            "id": 6,
            "title": "Weekly Team Project Sync",
            "type": "ham",
            "subject": "Engineering Team: Weekly Sprint Review & Architecture Notes",
            "body": "Hi team, here is the summary from our weekly technical sync. We completed the core model inference pipeline, optimized database queries, and updated the frontend dashboard. Next sprint will focus on caching and latency benchmarks. Please review the updated documentation."
        }
    ]
    return jsonify({"samples": samples})

@app.route("/api/predict", methods=["POST"])
def predict():
    if not model or not vectorizer:
        return jsonify({"status": "error", "message": "Model not loaded"}), 500

    data = request.get_json() or {}
    text = data.get("text", "").strip()
    subject = data.get("subject", "").strip()

    full_text = f"{subject} {text}".strip()
    if not full_text:
        return jsonify({"status": "error", "message": "Please enter email text to analyze."}), 400

    cleaned = clean_text(full_text)
    vec = vectorizer.transform([cleaned])

    pred = model.predict(vec)[0]
    
    # Probability calculation
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(vec)[0]
        spam_prob = float(proba[1])
        ham_prob = float(proba[0])
    elif hasattr(model, "decision_function"):
        df = model.decision_function(vec)[0]
        spam_prob = float(1 / (1 + np.exp(-df)))
        ham_prob = 1.0 - spam_prob
    else:
        spam_prob = 1.0 if pred == 1 else 0.0
        ham_prob = 1.0 - spam_prob

    # Risk score (0 to 100)
    risk_score = round(spam_prob * 100, 1)

    # Detect trigger keywords present in input
    detected_triggers = []
    words_in_text = re.findall(r"\b[a-z]+\b", cleaned)
    for w in set(words_in_text):
        if w in SPAM_KEYWORDS or w in metadata.get("top_spam_indicators", []):
            detected_triggers.append(w)

    is_spam = bool(pred == 1 or spam_prob >= 0.5)

    if risk_score >= 80:
        threat_level = "Critical Threat"
        badge_color = "#ef4444"
    elif risk_score >= 50:
        threat_level = "Suspicious / Spam"
        badge_color = "#f97316"
    elif risk_score >= 20:
        threat_level = "Low Risk"
        badge_color = "#eab308"
    else:
        threat_level = "Safe / Legitimate"
        badge_color = "#10b981"

    # Insights / Explainability breakdown
    reasons = []
    if is_spam:
        if any(w in detected_triggers for w in ["urgent", "suspended", "locked", "verify", "password"]):
            reasons.append("High urgency language & credential verification alert detected.")
        if any(w in detected_triggers for w in ["winner", "won", "prize", "lottery", "congratulations"]):
            reasons.append("Lottery / reward claim indicators found.")
        if any(w in detected_triggers for w in ["bitcoin", "crypto", "cash", "money", "earn", "loan", "deposit"]):
            reasons.append("Unsolicited financial / crypto transaction terminology.")
        if "url_link" in cleaned:
            reasons.append("External hyperlink redirects detected.")
        if not reasons:
            reasons.append("Statistical word distribution strongly correlates with spam datasets.")
    else:
        reasons.append("Email contains natural conversational / academic / professional vocabulary.")
        reasons.append("No critical phishing or fraudulent financial triggers identified.")

    return jsonify({
        "status": "success",
        "is_spam": is_spam,
        "label": "SPAM" if is_spam else "HAM (Legitimate)",
        "risk_score": risk_score,
        "confidence": round(max(spam_prob, ham_prob) * 100, 1),
        "threat_level": threat_level,
        "badge_color": badge_color,
        "spam_probability": round(spam_prob * 100, 2),
        "ham_probability": round(ham_prob * 100, 2),
        "detected_triggers": detected_triggers[:10],
        "reasons": reasons,
        "processed_tokens_count": len(words_in_text),
        "model_used": metadata.get("best_model", "Logistic Regression / Naive Bayes")
    })

if __name__ == "__main__":
    print("\n" + "="*50)
    print(" Email Spam Detector running at http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
