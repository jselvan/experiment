import nidaqmx
import numpy as np

import threading
import queue
import time
from pathlib import Path

class AnalogReader:
    def __init__(self, data_path: str, channels="Dev1/ai0:3", sampling_rate: float=1000, chunk_size: int=100):
        """
        Parameters
        ----------
        data_path: path to save recorded data
        channels: e.g., "Dev1/ai0:3"
        sampling_rate: sample sampling_rate in Hz
        chunk_size: number of samples per channel per read
        """
        self.data_path = Path(data_path)
        self.timestamps_path = self.data_path.with_suffix('.ts.bin')

        self.channels = channels
        self.sampling_rate = sampling_rate
        self.chunk_size = chunk_size
        self.task = nidaqmx.Task()
        self.queue = queue.Queue(maxsize=100)
        self._stop = threading.Event()

        # Configure the task
        self.task.ai_channels.add_ai_voltage_chan(
            channels, min_val=-10.0, max_val=10.0
        )
        self.task.timing.cfg_samp_clk_timing(
            sampling_rate, 
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
            samps_per_chan=chunk_size
        )

    def start(self):
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.task.start()
        self.thread.start()

    def stop(self):
        self._stop.set()
        self.thread.join()
        self.task.stop()
        self.task.close()

    def _read_loop(self):
        """Continuously read from DAQ and push into queue."""
        reader = nidaqmx.stream_readers.AnalogMultiChannelReader(self.task.in_stream)
        buffer = np.zeros((self.task.number_of_channels, self.chunk_size))
        while not self._stop.is_set():
            reader.read_many_sample(
                buffer, 
                number_of_samples_per_channel=self.chunk_size, 
                timeout=10.0
            )
            ts = time.time()
            try:
                self.queue.put((ts, buffer.copy()), timeout=1.0)
            except queue.Full:
                print("Warning: queue full, dropping data")
            # write data to disk
            self._write_to_disk(ts, buffer.copy())

    def _write_to_disk(self, timestamp, data):
        with open(self.timestamps_path, 'ab') as ts_file:
            t = np.arange(self.chunk_size) / self.sampling_rate + timestamp
            t.tofile(ts_file)
        with open(self.data_path, 'ab') as data_file:
            data.tofile(data_file)

    def get_data(self, timeout=None):
        """Retrieve latest data chunk."""
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None
