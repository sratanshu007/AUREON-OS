import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from core.configuration.settings_schema import AureonSettings
from core.configuration.settings_manager import SettingsManager

class TestAureonSettings(unittest.TestCase):
    def test_default_values(self):
        settings = AureonSettings()
        self.assertEqual(settings.appearance.theme.value, 'light')
        self.assertEqual(settings.dock.position.value, 'bottom')
        self.assertTrue(settings.dock.magnification)

    def test_save_and_load(self):
        test_path = '/tmp/test_aureon_settings.json'
        mgr = SettingsManager(settings_file=test_path)
        s = mgr.load()
        self.assertIsNotNone(s)
        self.assertEqual(s.appearance.theme.value, 'light')

if __name__ == '__main__':
    unittest.main()
