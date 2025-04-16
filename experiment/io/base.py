import time

class IOInterface:
    def __init__(self):
        self.devices = {}
        self.reward_params = {}
    def add_device(self, name, device):
        self.devices[name] = device
    def good_monkey(self, duration, speed=None, channels=None):
        reward_device = self.devices.get('reward')
        if reward_device is None:
            raise ValueError("No reward device defined")

        if channels is None:
            channels = reward_device.channels
        
        if speed is not None:
            for channel in channels:
                reward_device.set_speed(channel, speed)
        
        for channel in channels:
            reward_device.start_pump(channel)
        
        time.sleep(duration)

        for channel in channels:
            reward_device.stop_pump(channel)