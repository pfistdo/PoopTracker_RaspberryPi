import time
import sys
import requests
from mq import *

EMULATE_HX711 = False

referenceUnit = 113
counter = 5
measurement_history = []  # List to store the last five measurements


if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    print('Emulated not possible')

def cleanAndExit():
    print("Cleaning...")
    if not EMULATE_HX711:
        GPIO.cleanup()
    print("Bye!")
    sys.exit()

hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()
print("Tare done!")
# mq = MQ()

def send_cat_weight(weight):
    url = "https://poop-tracker-48b06530794b.herokuapp.com/cats/"
    payload = {"weight": float(weight)}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Cat weight inserted successfully!")
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def send_poop_weight(weight):
    url = "https://poop-tracker-48b06530794b.herokuapp.com/poops/"
    payload = {"weight": int(weight)}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Poop weight inserted successfully!")
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")        

def update_measurement_history(weight):
    if len(measurement_history) >= 5:
        measurement_history.pop(0)  # Remove the oldest measurement
    measurement_history.append(weight)  # Add the new measurement

def calculate_average_history():
    if measurement_history:
        return sum(measurement_history) / len(measurement_history)
    return 0

def measure_air_quality():
    perc = mq.MQPercentage()
    sys.stdout.write("\r")
    sys.stdout.write("\033[K")
    sys.stdout.write("LPG: %g ppm, CO: %g ppm, Smoke: %g ppm" % (perc["GAS_LPG"], perc["CO"], perc["SMOKE"]))
    sys.stdout.flush()
    time.sleep(0.1)

while True:
    try:
        poopInside = False
        poop_weight = 0
        cat_weight = 0
        total_weight = 0
        val = hx.get_weight(5)
        print(val)
        hx.power_down()
        hx.power_up()
        time.sleep(0.1)

        # measure_air_quality()

        update_measurement_history(val)  # Update the measurement history
        running_average = calculate_average_history()  # Calculate the running average
        print(f"Running Average: {running_average}")

        while val > 100:
            print("Weight increase detected.")
            val = hx.get_weight(5)
            print(val)
            hx.power_down()
            hx.power_up()
            time.sleep(0.1)
            total_weight = 0
            
            for _ in range(counter):
                weight = hx.get_weight(5)
                total_weight += weight
                time.sleep(0.1)
            cat_weight = total_weight / counter
            print(f"Cat Weight: {cat_weight}")
            poopInside = True

        if poopInside:
            send_cat_weight(cat_weight)
            total_weight = 0
            for _ in range(counter):
                weight = hx.get_weight(5)
                total_weight += weight
                time.sleep(0.1)
            poop_weight = total_weight / counter
            print(f"Poop Weight: {poop_weight}")
            send_poop_weight(poop_weight)
            poopInside = False


    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
