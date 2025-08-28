from experiment.components import BaseComponent

import time

class IOInterface(BaseComponent):
    COMPONENT_TYPE = "io_interface"
    def __init__(self):
        super().__init__()
        self.devices = {}
        self.reward_params = {}
    def add_device(self, name, device):
        self.devices[name] = device
    def good_monkey(self, duration, n_pulses=1, interpulse_interval=None, speed=None, channels=None):
        reward_device = self.devices.get('reward')
        if interpulse_interval is None:
            interpulse_interval = duration
        if reward_device is None:
            raise ValueError("No reward device defined")

        if channels is None:
            channels = reward_device.channels
        
        if speed is not None:
            for channel in channels:
                reward_device.set_speed(channel, speed)
        
        for pulse in range(n_pulses):
            for channel in channels:
                reward_device.start_pump(channel)
            
            time.sleep(duration)

            for channel in channels:
                reward_device.stop_pump(channel)
            
            if (pulse-1) == n_pulses:
                time.sleep(interpulse_interval)
        