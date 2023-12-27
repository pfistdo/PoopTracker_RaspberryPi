import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)

try:
    while True:
        if GPIO.input(4):
            print("Im reading TRUE on GPIO 4")
        else:
            print("Im reading FALSE on GPIO 4")
        sleep(1)
finally:
    print("Cleaning up...")
    GPIO.cleanup()