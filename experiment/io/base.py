import time
from typing import Mapping, Callable

class IOInterface:
    def __init__(self):
        self.devices = {}
        self.reward_params = {}

    def add_device(self, name, device):
        self.devices[name] = device

    def good_monkey(self, duration, n_pulses=1, interpulse_interval=None, speed=None, channels=None, return_callbacks=False):
        if interpulse_interval is None:
            interpulse_interval = duration
        callbacks = self.get_reward_callbacks(speed=speed, channels=channels)
        if return_callbacks:
            return callbacks

        callbacks['reward_setup_callback']()
        for pulse in range(n_pulses):
            callbacks['reward_on_callback']()
            time.sleep(duration)
            callbacks['reward_off_callback']()
            if pulse < n_pulses - 1:
                time.sleep(interpulse_interval)

    def get_reward_callbacks(self, speed=None, channels=None) -> Mapping[str, Callable[[], None]]:
        reward_device = self.devices.get('reward')
        if reward_device is None:
            raise ValueError("No reward device defined")
        if channels is None:
            active_channels = reward_device.channels
        else:
            active_channels = channels

        def reward_setup():
            if speed is not None:
                for channel in active_channels:
                    reward_device.set_speed(channel, speed)

        def reward_on():
            for channel in active_channels:
                reward_device.start_pump(channel)

        def reward_off():
            for channel in active_channels:
                reward_device.stop_pump(channel)

        return {'reward_setup_callback': reward_setup,
                'reward_on_callback': reward_on,
                'reward_off_callback': reward_off}