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
poopWeight = 0
catWeight = 0
totalWeight = 0
print("Tare done!")
# mq = MQ()

def sendCatWeight(weight):
    url = "https://poop-tracker-48b06530794b.herokuapp.com/weights/"
    payload = {"weight": int(weight),"cat_ID": 4}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Cat Weight inserted successfully!")
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def sendPoopWeight(weight):
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

def updateMeasurementHistory(weight):
    if len(measurement_history) >= 5:
        measurement_history.pop(0)  # Remove the oldest measurement
    measurement_history.append(weight)  # Add the new measurement

def calculateAverageHistory():
    if measurement_history:
        return sum(measurement_history) / len(measurement_history)
    return 0

def measureAirQuality():
    #perc = mq.MQPercentage()
    sys.stdout.write("\r")
    sys.stdout.write("\033[K")
    sys.stdout.write("LPG: %g ppm, CO: %g ppm, Smoke: %g ppm" % (perc["GAS_LPG"], perc["CO"], perc["SMOKE"]))
    sys.stdout.flush()
    time.sleep(0.1)

def showSensorValues():
    sys.stdout.write("\r")
    sys.stdout.write("\033[K")
    sys.stdout.write(f"Current Value: {val}, Running Average: {runningAverage}")
    sys.stdout.flush()
    time.sleep(0.1)

def showValuesWhilePooping():
    sys.stdout.write("\r")
    sys.stdout.write("\033[K")
    sys.stdout.write(f"Weight increase detected! Current Value: {val}, Running Average: {runningAverage} Cat Weight: {catWeight}" )
    sys.stdout.flush()
    time.sleep(0.1)

while True:
    try:
        poopInside = False
        poopWeight = 0
        catWeight = 0
        totalWeight = 0
        val = hx.get_weight(5)
        hx.power_down()
        hx.power_up()
        time.sleep(0.1)

        # measureAirQuality()

        updateMeasurementHistory(val)  # Update the measurement history
        runningAverage = calculateAverageHistory()  # Calculate the running average
        showSensorValues()

        while val > 100:
            # print("Weight increase detected.")
            val = hx.get_weight(5)
            # print(val)
            hx.power_down()
            hx.power_up()
            time.sleep(0.1)
            totalWeight = 0
            
            for _ in range(counter):
                weight = hx.get_weight(5)
                totalWeight += weight
                time.sleep(0.1)
            catWeight = totalWeight / counter
            # print(f"Cat Weight: {catWeight}")
            showValuesWhilePooping()
            poopInside = True

        if poopInside:
            sendCatWeight(catWeight)
            totalWeight = 0
            for _ in range(counter):
                weight = hx.get_weight(5)
                totalWeight += weight
                time.sleep(0.1)
            poopWeight = totalWeight / counter
            #print(f"Poop Weight: {poopWeight}")
            time.sleep(2)
            sendPoopWeight(poopWeight)
            poopInside = False


    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
