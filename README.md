# 🛡️ SpamShield AI — Email Spam Detection & NLP Security System

An end-to-end Machine Learning and Natural Language Processing (NLP) web application that inspects emails, messages, and suspicious notifications in real-time to detect spam, phishing attempts, and fraudulent financial triggers with high precision.

---

## 👨‍💻 Author
**Kalp Shah**  
- B.Tech in Information Technology | Honours in Data Science & Analytics  
- Birla Vishvakarma Mahavidyalaya (BVM)  
- [GitHub Profile](https://github.com/K1905-cpu) • [LinkedIn](https://www.linkedin.com/in/kalp-shah-3024ab333/)

---

## 🌟 Key Features

- **⚡ High Diagnostic Accuracy (96%):** Trained and cross-validated across diverse spam, phishing, scam, and legitimate academic/work email datasets.
- **🔍 Explainable NLP Insights:** Highlights specific detected spam trigger keywords (e.g. `urgent`, `verify`, `password`, `bitcoin`, `funds`, `lottery`) and provides structured reasoning for the verdict.
- **📊 Real-time Risk Speedometer & Confidence Scoring:** Calculates an exact risk index from `0` to `100` alongside spam vs. ham probability distributions.
- **💡 1-Click Quick Samples:** Test instant pre-loaded examples including crypto scams, bank phishing alerts, work-from-home offers, university meeting schedules, and GitHub PR reviews.
- **🕒 Local Scan History:** Stores and displays recent scans in a clean dashboard table with timestamps and verdicts.
- **🚀 Dual-Mode Execution:**
  - **Standalone / Offline Mode:** Can run directly in browser without a server using built-in client heuristic rules.
  - **Full Flask / REST API Mode:** Real-time ML inference backed by Scikit-Learn pipelines.
  - **Serverless Vercel Ready:** Pre-configured with `api/index.py` and `vercel.json` for 1-click cloud deployment.

---

## 🏗️ Technical Architecture & ML Pipeline

```
Raw Email Input (Subject + Body)
               │
               ▼
   [NLP Text Preprocessing]
   • Lowercasing & whitespace normalization
   • URL, email & currency regex tokenization
   • Punctuation & numeric filtering
               │
               ▼
   [TF-IDF Feature Extraction]
   • Unigrams & Bigrams (1, 2)
   • Sublinear TF frequency scaling
   • 2,500+ Dimensional Vocabulary
               │
               ▼
   [Machine Learning Classifier]
   • Multinomial Naive Bayes / Logistic Regression / Linear SVM
   • Probability calibration & decision scoring
               │
               ▼
   [Security Output & Explainability Engine]
   • Classification (SPAM vs HAM)
   • Threat Level (Critical / Suspicious / Safe)
   • Trigger Keywords Extraction & Insights
```

---

## 📂 Project Structure

```
Email-spam/
│
├── train_model.py          # ML training pipeline, cross-validation & model serialization
├── app.py                  # Flask web server & multi-page REST API routes
├── spam_model.joblib       # Serialized trained classification model (Logistic Regression)
├── vectorizer.joblib       # Serialized TF-IDF vectorizer (2,500+ features)
├── model_metadata.json     # Benchmark metrics, vocabulary size & top spam predictors
├── test_api.py             # Automated unit tests for model & endpoints
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel deployment configuration
│
├── api/
│   └── index.py            # Vercel serverless function entrypoint
│
└── frontend/
    ├── index.html          # Page 1: Email Detection Workspace UI
    ├── history.html        # Page 2: Threat Registry & Scan History UI
    ├── impact.html         # Page 3: Accuracy Benchmarks & Impact Analytics UI
    ├── app.js              # Detection controller & gauge visualizer
    ├── history.js          # History data controller & JSON exporter
    ├── style.css           # Glassmorphism dark aesthetic stylesheet
    └── favicon.svg         # SpamShield AI tab icon
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure Python 3.9+ is installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Re-train the Model
```bash
python train_model.py
```

### 4. Run Automated Tests
```bash
python test_api.py
```

### 5. Launch the Web Application
```bash
python app.py
```
Open your browser and navigate to **`http://127.0.0.1:5000`** to use the interactive dashboard!

---

## 🌐 Deploy to Vercel

1. Push this `Email-spam` directory to a new GitHub repository: `https://github.com/K1905-cpu/Email-spam`.
2. Connect your repository to [Vercel](https://vercel.com).
3. Vercel will automatically read `vercel.json` and deploy both the serverless Python API and static frontend!

---

## 📜 License
MIT License © 2026 Kalp Shah
