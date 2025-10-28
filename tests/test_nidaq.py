
import unittest
from unittest.mock import MagicMock
import sys
# sys.modules['nidaqmx'] = MagicMock()

import time
import tempfile
from pathlib import Path
import numpy as np

class TestNIDAQ(unittest.TestCase):
    def setUp(self):
        from experiment.io.nidaq import AnalogReader
        self.root = tempfile.TemporaryDirectory()
        path = Path(self.root.name, 'test_data.bin')
        self.reader = AnalogReader(data_path=path.as_posix(), channels='Dev1/ai0:1', sampling_rate=1000, chunk_size=10)
        self.reader.start()
    def test_reading(self):
        time.sleep(0.1)  # Allow some time for data to be read
        self.reader.stop()
        data = self.reader.get_data(timeout=1.0)
        self.assertIsNotNone(data)
    def test_saving(self):
        time.sleep(0.1)  # Allow some time for data to be read
        self.reader.stop()
        data_path = Path(self.reader.data_path)
        timestamps_path = Path(self.reader.timestamps_path)
        self.assertTrue(data_path.exists())
        self.assertTrue(timestamps_path.exists())
        data = np.fromfile(data_path, dtype=np.float64)
        timestamps = np.fromfile(timestamps_path, dtype=np.float64)
        self.assertGreater(len(data), 0)
        self.assertGreater(len(timestamps), 0)
    def tearDown(self):
        self.root.cleanup()