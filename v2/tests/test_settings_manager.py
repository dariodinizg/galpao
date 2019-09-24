import sys
sys.path.append('v2')

from unittest import TestCase
from settings_manager import SettingsManager


class TestMain(TestCase):

    config_file = SettingsManager('/home/dariodg/Desktop/free/Galpao/ComissionApp/code/galpao/v2/general_config.json').settings

    def test_open_config(self):
        self.assertEquals(type(self.config_file), dict)
