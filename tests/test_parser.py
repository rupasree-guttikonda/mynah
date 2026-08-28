# tests/test_parser.py
import unittest
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock

import mynah.memory.parser as parser

class TestMeetingParser(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_meetings_dir = parser.VAULT_MEETINGS_DIR
        parser.VAULT_MEETINGS_DIR = self.temp_dir

    def tearDown(self):
        parser.VAULT_MEETINGS_DIR = self.original_meetings_dir
        shutil.rmtree(self.temp_dir)

    @patch("mynah.memory.parser.get_local_client")
    def test_parse_meeting_transcript_success(self, mock_get_client):
        # Setup mock client and choices response
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='''{
                "title": "Weekly Standup",
                "participants": ["Alice", "Bob"],
                "decisions": ["Deploy version 1.1 to staging"],
                "action_items": [
                    {"owner": "Alice", "task": "Run system benchmark"},
                    {"owner": "Bob", "task": "Check SQLite logger logs"}
                ]
            }'''))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        raw_transcript = "Alice says we should deploy v1.1. Bob agrees. Bob will check sqlite logs. Alice will benchmark."
        parsed = parser.parse_meeting_transcript(raw_transcript)
        
        self.assertEqual(parsed["title"], "Weekly Standup")
        self.assertEqual(parsed["participants"], ["Alice", "Bob"])
        self.assertEqual(parsed["decisions"], ["Deploy version 1.1 to staging"])
        self.assertEqual(len(parsed["action_items"]), 2)
        self.assertEqual(parsed["action_items"][0]["owner"], "Alice")
        self.assertEqual(parsed["action_items"][1]["task"], "Check SQLite logger logs")

    def test_save_meeting_log_creates_file(self):
        parsed_data = {
            "title": "Project Kickoff",
            "participants": ["John", "Sarah"],
            "decisions": ["Build voice assistant"],
            "action_items": [
                {"owner": "John", "task": "Setup git repo"},
                {"owner": "Sarah", "task": "Write test scripts"}
            ]
        }
        
        log_file = parser.save_meeting_log(parsed_data)
        self.assertTrue(os.path.exists(log_file))
        
        with open(log_file, "r") as f:
            content = f.read()
            self.assertIn("Project Kickoff", content)
            self.assertIn("- John", content)
            self.assertIn("- Sarah", content)
            self.assertIn("Build voice assistant", content)
            self.assertIn("- **[John]**: Setup git repo", content)
            self.assertIn("- **[Sarah]**: Write test scripts", content)

if __name__ == "__main__":
    unittest.main()
