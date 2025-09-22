"""Unit tests for utils module"""

import unittest
from unittest.mock import patch, MagicMock
from arch_installer.utils import run, safe_run, check_efi

class TestUtils(unittest.TestCase):
    
    @patch('subprocess.run')
    def test_run_success(self, mock_run):
        """Test successful command execution"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "success"
        mock_run.return_value = mock_result
        
        result = run("echo test")
        self.assertEqual(result, "success")
    
    @patch('subprocess.run')
    def test_run_failure(self, mock_run):
        """Test command execution failure"""
        mock_run.side_effect = Exception("Command failed")
        
        with self.assertRaises(Exception):
            run("invalid command")
    
    @patch('arch_installer.utils.run')
    def test_safe_run(self, mock_run):
        """Test safe_run doesn't raise exceptions"""
        mock_run.side_effect = Exception("Error")
        
        result = safe_run("failing command")
        self.assertIsNone(result)
    
    @patch('os.path.exists')
    def test_check_efi(self, mock_exists):
        """Test EFI detection"""
        mock_exists.return_value = True
        self.assertTrue(check_efi())
        
        mock_exists.return_value = False
        self.assertFalse(check_efi())

if __name__ == '__main__':
    unittest.main()
