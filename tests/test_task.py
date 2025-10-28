import unittest

class TestTask(unittest.TestCase):
    def test_task(self):
        from experiment.run import run
        run(task_directory='tests/test_task')