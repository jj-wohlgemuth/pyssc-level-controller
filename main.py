import pyssc as ssc
import os
from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD
from pickle import TRUE
from RPi import GPIO
from VolumeControl import VolumeControl
import time

CLOCKPIN = 5
DATAPIN = 6
SWITCHPIN = 13
VOLUME_STEP_DB = 1
SEND_TIME_S = .5
LIGHT_TIME_S = 5


def safe_exit(signum, frame):
    exit(1)


signal(SIGTERM, safe_exit)
signal(SIGHUP, safe_exit)
lc = LCD()
GPIO.setmode(GPIO.BCM)
found = False
while not found:
    if os.path.exists('setup.json'):
        found_setup = ssc.Ssc_device_setup()
        found_setup.from_json('setup.json')
        found = TRUE
    else:
        lc.text('setup.json not found', 1)
network_ready = False
while not network_ready:
    try:
        found_setup.connect_all()
        network_ready = True
    except Exception as e:
        time.sleep(5)
        lc.text('Network error: ', 1)
        lc.text(str(e), 2)

vc = VolumeControl(CLOCKPIN, DATAPIN, SWITCHPIN,
                   found_setup, VOLUME_STEP_DB, SEND_TIME_S,
                   LIGHT_TIME_S, lc)
try:
    vc.start()
    pause()

except KeyboardInterrupt:
    pass

finally:
    lc.clear()
    GPIO.cleanup()
    found_setup.disconnect_all()
