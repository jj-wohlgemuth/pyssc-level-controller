from RPi import GPIO
import json
from threading import Timer


class VolumeControl:
    CLOCKWISE = 0
    COUNTERCLOCKWISE = 1
    DEBOUNCE = 1

    def __init__(self,
                 clockPin,
                 dataPin,
                 switchPin,
                 setup,
                 volume_step,
                 send_time_s,
                 light_time_s,
                 display):
        self.clockPin = clockPin
        self.dataPin = dataPin
        self.switchPin = switchPin
        self.setup = setup
        self.volume_step = volume_step
        self.display = display
        self.set_volume_db = None
        self.want_volume_db = None
        self.send_time_s = send_time_s
        self.light_time_s = light_time_s
        self.send_timer = None
        self.light_timer = None
        self.block = False
        self.mute_state = False

        GPIO.setup(clockPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(dataPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(switchPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def start(self):
        GPIO.add_event_detect(self.clockPin,
                              GPIO.FALLING,
                              callback=self._clockCallback)
        GPIO.add_event_detect(self.switchPin,
                              GPIO.FALLING,
                              callback=self._switchCallback,
                              bouncetime=self.DEBOUNCE)
        self.display.clear()
        self.write_volume()

    def stop(self):
        GPIO.remove_event_detect(self.clockPin)
        GPIO.remove_event_detect(self.switchPin)

    def reset_send_timer(self):
        if self.send_timer is not None:
            self.send_timer.cancel()
        self.send_timer = Timer(self.send_time_s, self.write_volume)
        self.send_timer.start()

    def turn_off_light(self):
        self.display.backlight(turn_on=False)

    def reset_light_timer(self):
        self.block = True
        if self.light_timer is not None:
            self.light_timer.cancel()
        if not self.display.backlight_status:
            self.display.backlight(turn_on=True)
        self.light_timer = Timer(self.light_time_s,
                                 self.turn_off_light)
        self.light_timer.start()
        self.block = False

    def buffer_value(self, value):
        self.block = True
        self.want_volume_db = value
        self.display.text(str(self.want_volume_db) + ' dB ⚫', 1)
        print(str(self.want_volume_db) + ' dB ⚫')
        self.reset_send_timer()
        self.reset_light_timer()
        self.block = False

    def write_volume(self):
        self.block = True
        if self.want_volume_db is None:
            command = '{"audio":{"out":{"level":null}}}'
            event = self.setup.ssc_devices[0].send_ssc(command)
            rx_value = json.loads(event['RX'])
            self.want_volume_db = rx_value['audio']['out']['level']
        for ssc_device in self.setup.ssc_devices:
            command = '{"audio":{"out":{"level":' +\
                        str(self.want_volume_db) + 'null}}}'
            event = ssc_device.send_ssc(command)
        rx_value = json.loads(event['RX'])
        self.want_volume_db = rx_value['audio']['out']['level']
        self.display.text(str(self.want_volume_db) + ' dB √', 1)
        print(str(self.want_volume_db) + ' dB √')
        self.block = False

    def _clockCallback(self, pin):
        if GPIO.input(self.clockPin) == 0 and not self.block:
            data = GPIO.input(self.dataPin)
            if data == 1:
                self.buffer_value(self.want_volume_db + self.volume_step)
            else:
                self.buffer_value(self.want_volume_db - self.volume_step)

    def _switchCallback(self, pin):
        if GPIO.input(self.switchPin) == 0 and not self.block:
            self.block = True
            event = self.setup.ssc_devices[0].\
                send_ssc('{"audio":{"out":{"mute":null}}}')
            rx_value = json.loads(event['RX'])
            rx_mute_state = rx_value['audio']['out']['mute']
            self.setup.send_all('{"audio":{"out":{"mute":'
                                + str(not rx_mute_state).lower() + '}}}',
                                interface='%eth0')
            self.mute_state = not rx_mute_state
            if self.mute_state:
                self.display.text('Mute!', 2)
                print('Mute!')
            else:
                self.display.text('', 2)
            self.reset_light_timer()
            self.block = False
