import unittest
from unittest.mock import patch, MagicMock
from arch_installer.utils import run, copy_configs

class TestUtils(unittest.TestCase):
    @patch('arch_installer.utils.subprocess.Popen')
    def test_run_dry_run(self, mock_popen):
        result = run("echo test", dry_run=True)
        mock_popen.assert_not_called()
        
    @patch('arch_installer.utils.shutil.copytree')
    @patch('arch_installer.utils.shutil.copy')
    def test_copy_configs_dry_run(self, mock_copy, mock_copytree):
        result = copy_configs("/src", "/dest", dry_run=True)
        mock_copytree.assert_not_called()
        mock_copy.assert_not_called()

if __name__ == '__main__':
    unittest.main()
