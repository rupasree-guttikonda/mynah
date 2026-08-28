# tests/test_scheduler.py
import unittest
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock

import mynah.scheduler.launchd as launchd

class TestLaunchdScheduler(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_plist = os.path.join(self.temp_dir, "com.mynah.compaction.plist")
        self.original_plist_path = launchd.PLIST_PATH
        launchd.PLIST_PATH = self.temp_plist

    def tearDown(self):
        launchd.PLIST_PATH = self.original_plist_path
        shutil.rmtree(self.temp_dir)

    @patch("subprocess.run")
    def test_register_compaction_job(self, mock_run):
        # Setup mock subprocess runs to avoid modifying launchd state in container
        mock_run.return_value = MagicMock(returncode=0, stdout="Success")
        
        res = launchd.register_compaction_job()
        
        self.assertIn("Successfully registered compaction launchd job", res)
        self.assertTrue(os.path.exists(self.temp_plist))
        
        with open(self.temp_plist, "r") as f:
            content = f.read()
            self.assertIn("<string>com.mynah.compaction</string>", content)
            self.assertIn("<string>--compact</string>", content)
            self.assertIn("<key>StartCalendarInterval</key>", content)

if __name__ == "__main__":
    unittest.main()
