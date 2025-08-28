import serial

class IsmatecPumpSerial:
    def __init__(self, address):
        self.address = address
        self.baudrate = 9600
        self.serial = serial.Serial(
            self.address, self.baudrate, 
            parity=serial.PARITY_NONE,
            bytesize=8,
            stopbits=1,
            timeout=None,
            xonxoff=False,
            rtscts=False
        )
        self.channels = []
    def init(self, channel_info):
        self.sendmsg('1~1') # set channel addressing mode on startup
        for channel in channel_info:
            channel_number = channel['channel']
            self.channels.append(channel_number)
            clockwise = channel.get('clockwise', True)
            speed = channel.get('speed', 100)
            self.set_rpm_mode(channel_number)
            self.set_direction(channel_number, clockwise)
            self.set_speed(channel_number, speed)
    def sendmsg(self, msg):
        msg = msg + '\r\n'
        self.serial.write(msg.encode('utf-8'))
    def start_pump(self, channel):
        self.sendmsg(channel + 'H')
    def stop_pump(self, channel):
        self.sendmsg(channel + 'I')
    def set_speed(self, channel, speed):
        msg = f"{channel}S0{speed:3.1f}".replace('.','')
        self.sendmsg(msg)
    def set_direction(self, channel, clockwise=True):
        direction = 'L'
        if not clockwise:
            raise NotImplementedError(":( look it up idk")
        msg = f"{channel}{direction}"
        self.sendmsg(msg)
    def set_rpm_mode(self, channel):
        self.sendmsg(f"{channel}xRJ")

if __name__ == '__main__':
    import sys
    import time
    addr = sys.argv[1]
    pump = IsmatecPumpSerial(addr)
    pump.init([{'channel': '1', 'clockwise': True, 'speed': 100}])
    pump.start_pump('1')
    time.sleep(1)
    pump.stop_pump('1')
