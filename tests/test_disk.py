"""Unit tests for disk module"""

import unittest
from unittest.mock import patch, MagicMock
from arch_installer.disk import DiskManager

class TestDiskManager(unittest.TestCase):
    
    @patch('subprocess.check_output')
    def test_list_disks(self, mock_check_output):
        """Test disk listing"""
        mock_check_output.return_value = "sda 100G disk\nsdb 200G disk\n"
        
        disks = DiskManager.list_disks()
        expected = ["/dev/sda (100G)", "/dev/sdb (200G)"]
        self.assertEqual(disks, expected)
    
    @patch('subprocess.run')
    def test_is_disk_mounted(self, mock_run):
        """Test disk mount detection"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        self.assertTrue(DiskManager.is_disk_mounted("/dev/sda"))
        
        mock_result.returncode = 1
        self.assertFalse(DiskManager.is_disk_mounted("/dev/sda"))

if __name__ == '__main__':
    unittest.main()
