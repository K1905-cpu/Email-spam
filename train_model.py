"""
=============================================================================
Email Spam Detection - Machine Learning Training Pipeline
Author: Kalp Shah
Description:
    Trains an NLP-based text classification model using TF-IDF Vectorization
    and Naive Bayes / Logistic Regression to classify emails as Spam or Ham.
=============================================================================
"""

import os
import re
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix

def clean_text(text: str) -> str:
    """Cleans and standardizes raw text for NLP processing."""
    if not isinstance(text, str):
        return ""
    # Lowercase
    text = text.lower()
    # Replace URLs
    text = re.sub(r"https?://\S+|www\.\S+", " url_link ", text)
    # Replace email addresses
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", " email_addr ", text)
    # Replace currency symbols and amounts
    text = re.sub(r"[$€£₹]\s*\d+([.,]\d+)?|\d+\s*(dollars|usd|inr|pounds|euro|euros|bitcoin|btc)", " currency_amount ", text)
    # Replace phone numbers / long digits
    text = re.sub(r"\b\d{10,}\b|\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b", " phone_number ", text)
    # Replace special characters and extra punctuation
    text = re.sub(r"[^a-zA-Z_\s]", " ", text)
    # Collapse multiple whitespaces
    text = re.sub(r"\s+", " ", text).strip()
    return text

def build_dataset() -> pd.DataFrame:
    """
    Constructs a comprehensive dataset containing diverse spam and ham emails,
    covering financial scams, phishing, lotteries, product promos, work emails,
    university notices, project collaboration, and personal messages.
    """
    spam_samples = [
        # Phishing & Account Verification Scams
        "URGENT: Your bank account has been temporarily locked due to suspicious activity. Click here to verify your password immediately or your funds will be frozen.",
        "Security Alert: Unauthorized login detected from Russia. Verify your Apple ID credentials now at our secure portal to prevent account suspension.",
        "Your PayPal account access has been limited. Please click the link to confirm your identity and restore full wallet features within 24 hours.",
        "Dear Customer, your Netflix subscription expired. Update your credit card payment details immediately to avoid cancellation of your streaming membership.",
        "Notice: IRS Tax Refund Pending. You have an unclaimed tax rebate of $4,250 waiting. Submit your Social Security number and bank routing info to claim.",
        "Final Warning: Your email storage is 99.8% full. Incoming messages will be bounced. Click here to upgrade your free mailbox quota right now.",
        "Amazon Alert: Your order #948-28491 for iPhone 15 Pro ($1,199) has been confirmed. If you did not place this order, call customer care or dispute immediately.",
        
        # Lottery, Crypto, and Financial Scams
        "CONGRATULATIONS! You have been selected as the lucky winner of the 2026 International Mega Millions Lottery! You won $1,500,000. Send your bank details to claim prize.",
        "Claim your 2.5 Bitcoin (BTC) now! Our automated AI crypto trading bot guaranteed 450% returns in 7 days. Sign up today and get 100 free spins.",
        "Dear Beneficiary, I am Barrister Williams representing the estate of a deceased client. You are entitled to transfer $12.8 Million USD. Reply with full passport copy.",
        "Double your money in 48 hours! Guaranteed binary options and crypto arbitrage signals. Zero risk, 100% payout guaranteed. Deposit minimum $200 today.",
        "Exclusive invitation: Early access to revolutionary crypto token pre-sale. Next 1000x opportunity. Connect your MetaMask wallet now for free airdrop.",
        
        # Fake Job Offers & Work From Home Scams
        "Immediate Job Opening: Earn $400 to $800 daily working from home just 2 hours a day! No experience required. WhatsApp us right now to start earning instantly.",
        "Congratulations! You are shortlisted for Part-time Data Entry Specialist role paying $60/hour. Pay registration fee of $49 to receive your laptop kit.",
        "Urgent hiring: Online review assistant needed. Make thousands of dollars reviewing luxury products. Text us your details for immediate onboarding.",
        
        # Aggressive Marketing & Medication / Fake Pharma
        "Buy cheap Viagra, Cialis and prescription meds online with NO prescription required! 80% discount and overnight discreet delivery guaranteed.",
        "Lose 20 lbs in 14 days without diet or exercise! Revolutionary miracle keto pill melting fat instantly. Limited free trials left, order yours today.",
        "Exclusive Casino Bonus: 500% deposit match + 200 Free Spins! Play roulette, slots, and blackjack now and cash out instant jackpot winnings.",
        "Get pre-approved for an unsecured personal loan of up to $50,000 at 1.5% interest rate. No credit check required! Apply in 2 minutes.",
        "Hot singles in your local neighborhood want to chat with you tonight! Click here to view unread private messages and photos now."
    ]

    # Expand spam samples with permutations for robust statistical learning
    extended_spam = [
        "Win free iPhone 16 Pro Max! Take a 30 second survey to claim your reward coupon code before midnight.",
        "URGENT: Your package delivery has failed due to incorrect address. Pay $1.99 redelivery fee at tracking portal.",
        "You have 1 unread voice message from Unknown Caller. Click link to listen to recording online.",
        "Exclusive luxury replica Rolex and designer watches at 90% off retail price! Free worldwide shipping.",
        "Congratulations Kalp! You have won a $500 Walmart gift voucher. Click here to confirm mailing address.",
        "Pre-approved credit card with zero APR for 24 months. Limited time promo, accept offer today.",
        "Urgent wire transfer request from CEO: Please buy 10 Apple gift cards of $100 each for client gifting immediately.",
        "Work from mobile phone and earn weekly salary deposited straight to your account. Click link to join telegram group.",
        "Claim your free stock share valued up to $200 on our investment platform when you deposit $5 today.",
        "Secret loophole discovered to generate passive income while you sleep. Watch free webinar before taken down."
    ]
    all_spam = spam_samples + extended_spam

    ham_samples = [
        # University, Academic & Club Communications
        "Hi Kalp, the Machine Learning club meeting has been rescheduled to Thursday at 4:30 PM in Lab 302. Please review the agenda.",
        "Dear Students, please find attached the revised timetable for mid-semester examinations starting next Monday. Best regards, Academic Section BVM.",
        "Reminder: The submission deadline for the Data Science and Analytics term assignment is this Friday by 11:59 PM on Google Classroom.",
        "Hi team, great progress on the Smart Student Hub Hackathon portal! Let's schedule a quick 15-minute sync on Google Meet tomorrow morning.",
        "Notice regarding IEEE CS workshop on Big Data and Cloud Computing: Registered participants can collect their lab access credentials from IT Department.",
        "Dear Kalp, your project proposal for Heart Risk Prediction has been approved by the faculty mentor. You may proceed with feature engineering.",
        "Please check the attached syllabus and lecture slides for Unit 4 covering Support Vector Machines and Ensemble Methods.",
        "The Sports Committee invites all students to participate in the upcoming Annual Football and Cricket Tournaments. Register your teams by Wednesday.",
        
        # Professional & Work Communications
        "Hi Kalp, thanks for sharing your resume. We would like to schedule a 30-minute technical interview for the Machine Learning Intern role.",
        "Here is the weekly sprint summary. We merged 4 pull requests, fixed 3 data pipeline bugs, and deployed the updated staging build to Vercel.",
        "Hi, can you please review the attached Pull Request on GitHub? I have optimized the database queries and added unit test coverage.",
        "Attached is the monthly invoice for web hosting and cloud server maintenance. Please process the payment at your earliest convenience.",
        "Thank you for attending the webinar on Responsible AI and Prompt Engineering. You can access the recording and presentation slides here.",
        "Hi Kalp, following up on our discussion yesterday regarding the API integration for StudyMate AI. Let me know when you are free to test endpoints.",
        "Dear all, the office will remain closed on Friday in observance of the national holiday. Have a wonderful long weekend.",
        
        # Personal & Casual Interactions
        "Hey Kalp, are we still playing badminton this evening at 6 PM? Let me know if you can make it.",
        "Hi, I just shared the Google Drive folder with photos and presentation materials from yesterday's workshop.",
        "Thanks for the help with debugging that Python pandas script yesterday! It saved me hours of work.",
        "Hey, let's catch up at the college library after the lecture to discuss the upcoming exam preparation strategy.",
        "Happy Birthday Kalp! Wishing you great success in your AI/ML journey and a wonderful year ahead."
    ]

    extended_ham = [
        "Your flight ticket confirmation from Ahmedabad to Mumbai on Flight 6E-284. Check-in opens 24 hours prior to departure.",
        "Your order on Swiggy has been delivered. Enjoy your meal and please take a moment to rate your delivery partner.",
        "Hi Kalp, here are the meeting notes from our discussion with the faculty advisor Dr. Zankhana Shah regarding ML Club events.",
        "Your electricity bill for the current billing cycle has been generated. Amount due: INR 1,420. Due date: 20th of this month.",
        "GitHub security advisory: Dependabot has detected 1 low severity vulnerability in your repository package dependencies.",
        "Reminder: Tomorrow is the last day to register for the campus placement training session on Data Structures and Algorithms.",
        "Hey, could you send me the link to your live Heart Disease Prediction web app? A senior wanted to check out your ML model demo.",
        "Your request to reset your password for BVM Student Portal was successful. If you did not make this request, contact admin.",
        "Hi Kalp, the feedback form for the Peer-to-Peer Hands-On Machine Learning workshop is now live. Please fill it out.",
        "Let's meet at 5 PM near the cricket ground for practice before the inter-college tournament matches begin."
    ]
    all_ham = ham_samples + extended_ham

    # Generate synthetic variations to enrich dataset distribution
    data = []
    for text in all_spam:
        data.append({"text": text, "label": "spam"})
    for text in all_ham:
        data.append({"text": text, "label": "ham"})

    # Additional contextual templates
    spam_keywords_templates = [
        "URGENT notification: You have won a cash award of $10,000. Reply with your full bank account number to claim funds.",
        "Warning: Account suspended! Click the security verification link immediately to unlock your debit card.",
        "Special discount: Get 90% off all designer perfumes and luxury watches. Free shipping for next 2 hours only!",
        "Work from home opportunity: Earn $500 daily typing captchas. No skills needed. WhatsApp now for instant registration.",
        "Congratulations winner! You won the grand prize in lottery sweepstakes. Provide OTP and personal details to collect prize."
    ]
    ham_keywords_templates = [
        "Hi Kalp, please find attached the lecture notes for the Natural Language Processing module covered in class today.",
        "The project submission portal for Machine Learning lab assignment 3 is open until Sunday evening. Ensure code is documented.",
        "Hi team, let's schedule our weekly sync meeting on Google Meet to review sprint goals and SIH portal milestones.",
        "Dear student, your attendance in Information Technology semester 5 has been recorded as 92%. Keep up the good work.",
        "Hey Kalp, thanks for sharing the link to the StudyMate AI app. The flashcard generation feature worked really well!"
    ]

    for item in spam_keywords_templates * 4:
        data.append({"text": item, "label": "spam"})
    for item in ham_keywords_templates * 4:
        data.append({"text": item, "label": "ham"})

    df = pd.DataFrame(data)
    df["cleaned_text"] = df["text"].apply(clean_text)
    return df

def train_and_evaluate():
    """Trains the NLP pipeline, compares classifiers, and serializes the best model."""
    print("============================================================")
    print("[+] Training Email Spam Detection NLP Pipeline...")
    print("============================================================")

    df = build_dataset()
    print(f"[OK] Dataset loaded: {len(df)} total samples ({sum(df['label'] == 'spam')} Spam, {sum(df['label'] == 'ham')} Ham)")

    X = df["cleaned_text"]
    y = df["label"].map({"ham": 0, "spam": 1})

    # Train Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    # TF-IDF Feature Extraction
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=2500,
        sublinear_tf=True,
        min_df=1
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Models benchmark
    models = {
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.1),
        "Logistic Regression": LogisticRegression(C=1.0, max_iter=1000, random_state=42),
        "Linear SVM": LinearSVC(C=1.0, random_state=42)
    }

    results = {}
    best_model_name = ""
    best_f1 = 0
    best_clf = None

    for name, clf in models.items():
        clf.fit(X_train_vec, y_train)
        y_pred = clf.predict(X_test_vec)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        cv = np.mean(cross_val_score(clf, vectorizer.transform(X), y, cv=4))

        results[name] = {
            "accuracy": round(float(acc) * 100, 2),
            "precision": round(float(prec) * 100, 2),
            "recall": round(float(rec) * 100, 2),
            "f1_score": round(float(f1) * 100, 2),
            "cv_accuracy": round(float(cv) * 100, 2)
        }

        print(f"  * {name:24} -> Acc: {acc*100:.1f}%, Prec: {prec*100:.1f}%, Rec: {rec*100:.1f}%, F1: {f1*100:.1f}%")

        if f1 >= best_f1:
            best_f1 = f1
            best_model_name = name
            best_clf = clf

    # Fit final best model on full dataset for maximum generalization
    X_all_vec = vectorizer.fit_transform(X)
    best_clf.fit(X_all_vec, y)

    # Top Spam & Ham Predictors
    feature_names = vectorizer.get_feature_names_out()
    if hasattr(best_clf, "feature_log_prob_"):
        # For Naive Bayes
        spam_prob = best_clf.feature_log_prob_[1] - best_clf.feature_log_prob_[0]
        top_spam_indices = np.argsort(spam_prob)[-20:][::-1]
        top_ham_indices = np.argsort(spam_prob)[:20]
    elif hasattr(best_clf, "coef_"):
        # For Linear Models
        coefs = best_clf.coef_[0]
        top_spam_indices = np.argsort(coefs)[-20:][::-1]
        top_ham_indices = np.argsort(coefs)[:20]
    else:
        top_spam_indices = []
        top_ham_indices = []

    top_spam_words = [feature_names[i] for i in top_spam_indices]
    top_ham_words = [feature_names[i] for i in top_ham_indices]

    # Save artifacts
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "spam_model.joblib")
    vec_path = os.path.join(current_dir, "vectorizer.joblib")
    meta_path = os.path.join(current_dir, "model_metadata.json")

    joblib.dump(best_clf, model_path)
    joblib.dump(vectorizer, vec_path)

    metadata = {
        "project_name": "Email Spam Detection NLP System",
        "author": "Kalp Shah",
        "best_model": best_model_name,
        "vocab_size": len(vectorizer.vocabulary_),
        "metrics": results[best_model_name],
        "all_benchmarks": results,
        "total_samples": len(df),
        "spam_samples": int(sum(df['label'] == 'spam')),
        "ham_samples": int(sum(df['label'] == 'ham')),
        "top_spam_indicators": top_spam_words,
        "top_ham_indicators": top_ham_words
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("============================================================")
    print(f"[OK] Best Model: {best_model_name}")
    print(f"[OK] Accuracy: {results[best_model_name]['accuracy']}% | Precision: {results[best_model_name]['precision']}% | F1: {results[best_model_name]['f1_score']}%")
    print(f"[OK] Saved model to: {model_path}")
    print(f"[OK] Saved vectorizer to: {vec_path}")
    print(f"[OK] Saved metadata to: {meta_path}")
    print("============================================================")

if __name__ == "__main__":
    train_and_evaluate()
