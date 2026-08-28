# tests/test_clipboard.py
import unittest
from unittest.mock import patch, MagicMock
import mynah.tools.clipboard as clipboard

class TestClipboardTools(unittest.TestCase):
    @patch("mynah.tools.clipboard.read_clipboard")
    @patch("mynah.tools.clipboard.get_local_client")
    def test_explain_code(self, mock_get_client, mock_read):
        # 1. Setup clipboard content
        mock_read.return_value = "def add(a, b): return a + b"
        
        # 2. Setup mock local client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="This function adds two numbers and returns the sum."))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        
        # 3. Call explain_code
        res = clipboard.explain_code()
        self.assertEqual(res, "This function adds two numbers and returns the sum.")
        mock_client.chat.completions.create.assert_called_once()

    @patch("mynah.tools.clipboard.read_clipboard")
    @patch("mynah.tools.clipboard.get_local_client")
    def test_summarize_text(self, mock_get_client, mock_read):
        mock_read.return_value = "Mynah is an advanced local voice assistant running on macOS."
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Mynah is a macOS voice assistant."))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        
        res = clipboard.summarize_text()
        self.assertEqual(res, "Mynah is a macOS voice assistant.")

    @patch("mynah.tools.clipboard.read_clipboard")
    @patch("mynah.tools.clipboard.get_local_client")
    def test_translate_selection(self, mock_get_client, mock_read):
        mock_read.return_value = "Hello"
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Hola"))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        
        res = clipboard.translate_selection("Spanish")
        self.assertEqual(res, "Hola")

if __name__ == "__main__":
    unittest.main()
