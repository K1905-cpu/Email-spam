"""
=============================================================================
Email Spam Detection - Automated Verification Tests
Author: Kalp Shah
=============================================================================
"""

import json
import unittest
from app import app, clean_text

class TestEmailSpamDetection(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_stats_endpoint(self):
        """Tests /api/stats endpoint."""
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["model_loaded"])

    def test_samples_endpoint(self):
        """Tests /api/samples endpoint."""
        res = self.client.get("/api/samples")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("samples", data)
        self.assertGreater(len(data["samples"]), 0)

    def test_spam_prediction(self):
        """Tests spam detection with clear phishing/lottery input."""
        payload = {
            "subject": "URGENT: Account Locked",
            "text": "Your bank account has been suspended due to suspicious activity. Click here to verify your password immediately to avoid permanent funds freeze."
        }
        res = self.client.post("/api/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["is_spam"])
        self.assertGreaterEqual(data["risk_score"], 50)
        print(f"\n[Test] Spam Email -> Label: {data['label']}, Risk Score: {data['risk_score']}/100, Triggers: {data['detected_triggers']}")

    def test_ham_prediction(self):
        """Tests legitimate ham detection with college meeting schedule."""
        payload = {
            "subject": "BVM ML Club Weekly Meeting",
            "text": "Hi Kalp, the Machine Learning club meeting is scheduled for Thursday at 4:30 PM in Lab 302. Please review the agenda."
        }
        res = self.client.post("/api/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertFalse(data["is_spam"])
        self.assertLess(data["risk_score"], 50)
        print(f"\n[Test] Ham Email  -> Label: {data['label']}, Risk Score: {data['risk_score']}/100")

    def test_clean_text_utility(self):
        """Tests text sanitization."""
        raw = "Visit https://google.com and win $5,000 DOLLARS today! Email: test@example.com"
        cleaned = clean_text(raw)
        self.assertIn("url_link", cleaned)
        self.assertIn("currency_amount", cleaned)
        self.assertIn("email_addr", cleaned)

if __name__ == "__main__":
    unittest.main()
