from unittest import TestCase

from maing import SettingsManager

class TestMain(TestCase):
    
    main_class = SettingsManager('general_config.json')

    def test_open_config(self):
       self.assertEquals(self.main_class.extension, '')