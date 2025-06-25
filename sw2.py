import RPi.GPIO as GPIO
import time

SW2 = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(SW2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    while True:
        print("SW2:", GPIO.input(SW2))
        time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()
