# tests/test_review.py
import unittest
import os
import shutil
import tempfile
import datetime
from unittest.mock import patch, MagicMock
import mynah.memory.review as review

class TestMemoryReview(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_daily_dir = review.VAULT_DAILY_DIR
        self.original_me_dir = review.VAULT_ME_DIR
        
        review.VAULT_DAILY_DIR = os.path.join(self.temp_dir, "daily")
        review.VAULT_ME_DIR = os.path.join(self.temp_dir, "me")
        
        os.makedirs(review.VAULT_DAILY_DIR, exist_ok=True)
        os.makedirs(review.VAULT_ME_DIR, exist_ok=True)

    def tearDown(self):
        review.VAULT_DAILY_DIR = self.original_daily_dir
        review.VAULT_ME_DIR = self.original_me_dir
        shutil.rmtree(self.temp_dir)

    @patch("mynah.memory.review.get_local_client")
    def test_quiz_me_success(self, mock_get_client):
        # 1. Create a dummy note file
        note_file = os.path.join(review.VAULT_DAILY_DIR, "2026-08-27.md")
        with open(note_file, "w") as f:
            f.write("Completed security keychain integration using native macOS utilities.")
            
        # 2. Setup mock LLM completion
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="What did you complete on 2026-08-27?\nA) Keychain Integration\nB) Slack integration\nC) Safari testing"))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        
        # 3. Call quiz_me
        res = review.quiz_me()
        self.assertIn("Memory Quiz from '2026-08-27.md'", res)
        self.assertIn("Keychain Integration", res)

    @patch("mynah.memory.review.get_local_client")
    def test_summarize_month_success(self, mock_get_client):
        # 1. Create multiple daily logs from different days
        today = datetime.date.today()
        dates_to_write = [today, today - datetime.timedelta(days=2), today - datetime.timedelta(days=10)]
        for dt in dates_to_write:
            date_str = dt.strftime("%Y-%m-%d")
            log_file = os.path.join(review.VAULT_DAILY_DIR, f"{date_str}.md")
            with open(log_file, "w") as f:
                f.write(f"Log for {date_str}: Did coding.")
                
        # 2. Setup mock LLM response
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Summary: Coding completed over the past weeks."))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        
        # 3. Call summarize_month
        res = review.summarize_month()
        self.assertEqual(res, "Summary: Coding completed over the past weeks.")
        mock_client.chat.completions.create.assert_called_once()

if __name__ == "__main__":
    unittest.main()
