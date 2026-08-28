# tests/test_compaction.py
import unittest
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock

import mynah.memory.compaction as compaction

class TestDailyCompaction(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
        self.original_daily_dir = compaction.VAULT_DAILY_DIR
        self.original_me_dir = compaction.VAULT_ME_DIR
        
        compaction.VAULT_DAILY_DIR = os.path.join(self.temp_dir, "daily")
        compaction.VAULT_ME_DIR = os.path.join(self.temp_dir, "me")
        
        os.makedirs(compaction.VAULT_DAILY_DIR, exist_ok=True)
        os.makedirs(compaction.VAULT_ME_DIR, exist_ok=True)

    def tearDown(self):
        compaction.VAULT_DAILY_DIR = self.original_daily_dir
        compaction.VAULT_ME_DIR = self.original_me_dir
        shutil.rmtree(self.temp_dir)

    @patch("mynah.memory.compaction.get_local_client")
    def test_compact_daily_log_promotes_facts(self, mock_get_client):
        # 1. Create a dummy daily log file
        date_str = "2026-08-27"
        daily_file = os.path.join(compaction.VAULT_DAILY_DIR, f"{date_str}.md")
        with open(daily_file, "w") as f:
            f.write("Today I updated my phone number to +1-408-555-0199 and finished my voice assistant code.")
            
        # 2. Setup profile template files
        with open(os.path.join(compaction.VAULT_ME_DIR, "identity.md"), "w") as f:
            f.write("# Identity\n- Name: Vijay")
        with open(os.path.join(compaction.VAULT_ME_DIR, "work.md"), "w") as f:
            f.write("# Work History")
            
        # 3. Setup mock LLM response
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='''{
                "identity_updates": ["Updated phone to +1-408-555-0199"],
                "work_updates": ["Finished coding mynah voice assistant routing engine"],
                "preference_updates": []
            }'''))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        
        # 4. Run compaction
        res = compaction.compact_daily_log(date_str)
        self.assertIn("Successfully compacted daily log. Promoted 2 items", res)
        
        # 5. Verify updates
        with open(os.path.join(compaction.VAULT_ME_DIR, "identity.md"), "r") as f:
            identity_content = f.read()
            self.assertIn("Identity", identity_content)
            self.assertIn("Compacted Updates from 2026-08-27", identity_content)
            self.assertIn("- Updated phone to +1-408-555-0199", identity_content)
            
        with open(os.path.join(compaction.VAULT_ME_DIR, "work.md"), "r") as f:
            work_content = f.read()
            self.assertIn("Finished coding mynah voice assistant routing engine", work_content)

if __name__ == "__main__":
    unittest.main()
