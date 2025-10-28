import unittest

class TestComponentInitialization(unittest.TestCase):
    def setUp(self) -> None:
        import tomllib
        with open('minimal_config.toml', 'rb') as f:
            self.config = tomllib.load(f)

    def test_initialize_manager(self):
        from experiment.manager import Manager
        manager = Manager.from_config(self.config)
        self.assertIsInstance(manager, Manager)