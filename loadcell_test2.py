import RPi.GPIO as gpio
from hx711 import HX711

gpio.setmode(gpio.BCM)

hx = HX711(dout_pin=6, pd_sck_pin=5)
hx.set_debug_mode(flag=True)

print("Starting...")

while True:
    print("Reading data...")
    reading = hx.get_raw_data()
    print(f"{reading}g")