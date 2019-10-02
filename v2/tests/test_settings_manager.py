import os
import sys
sys.path.append(os.getcwd())

from unittest import TestCase, skip
from config_manager import ConfigManager


class TestMain(TestCase):

    FILE_MANAGER = ConfigManager('general_config.json')
    CONFIG_FILE = FILE_MANAGER.settings

    def test_open_config(self):
        self.assertTrue(len(self.CONFIG_FILE.keys())>0)

    @skip('created just to check the cwd')
    def test_cwd(self):
        self.assertEqual(self.FILE_MANAGER.workdir,'')
