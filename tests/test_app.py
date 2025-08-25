import unittest
from epsilon_editor.app import EpsilonApp


class TestApp(unittest.TestCase):
    def test_app_importable_and_instantiable(self):
        """
        Tests that the main application class can be imported and instantiated.
        """
        try:
            app = EpsilonApp()
            self.assertIsInstance(app, EpsilonApp)
        except Exception as e:
            self.fail(f"Failed to import or instantiate EpsilonApp: {e}")


if __name__ == "__main__":
    unittest.main()
