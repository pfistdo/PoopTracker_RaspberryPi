import time
import sys
import requests
from mq import *
from twilio.rest import Client

def tare():
    hx.reset()
    hx.tare()
    print("Tare done!")

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
            print("Poop Weight inserted successfully!")
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def sendLiveWeight(weight):
    url = "https://poop-tracker-48b06530794b.herokuapp.com/liveWeights/"
    payload = {"weight": int(weight)}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def sendAirQuality(smoke, co, lpg):
    url = "https://poop-tracker-48b06530794b.herokuapp.com/air_qualities/"
    payload = {"smoke": int(1000*smoke), "co": int(1000*co), "lpg": int(1000*lpg)}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Air Quality inserted successfully!")
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def sendLiveAirQuality(smoke, co, lpg):
    url = "https://poop-tracker-48b06530794b.herokuapp.com/liveair_qualities/"
    payload = {"smoke": int(1000*smoke), "co": int(1000*co), "lpg": int(1000*lpg)}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def getAllTelephoneNumber():
    url = "https://poop-tracker-48b06530794b.herokuapp.com/telephone_numbers/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Telephone Numbers retrieved successfully!")
            return response.json()
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
    perc = mq.MQPercentage()
    sys.stdout.write("\r")
    sys.stdout.write("\033[K")
    sys.stdout.write("LPG: %g ppm, CO: %g ppm, Smoke: %g ppm" % (perc["GAS_LPG"], perc["CO"], perc["SMOKE"]))
    sys.stdout.flush()
    sendAirQuality(perc["GAS_LPG"], perc["CO"], perc["SMOKE"])
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
    sys.stdout.write(f"Weight increase detected! Current Value: {val}, Cat Weight: {catWeight}\n" )
    sys.stdout.flush()
    time.sleep(0.1)

def sendPoopMessage(telephoneNumbers, poopWeight):
    for number in telephoneNumbers:
        message = client.messages.create(
            body='Your cat has pooped! The trophy weighs ' + str(int(poopWeight)) + ' grams.',
            from_='whatsapp:+14155238886',
            to='whatsapp:'+number['telnr']
        )

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
tare()
mq = MQ()

poopWeight = 0
catWeight = 0
totalWeight = 0
lastMeasurementTime = time.time()
account_sid = 'ACa1decc9dbef0c0e90bbd2db9a7e42931'
auth_token = '30fcc286a892254d0e30eed68a5f4166'
client = Client(account_sid, auth_token)
telephoneNumbers = getAllTelephoneNumber()


while True:
    try:
        poopInside = False
        poopWeight = 0
        catWeight = 0
        totalWeight = 0
        lastCatWeight = 0
        val = hx.get_weight(5)
        sendLiveWeight(val)
        hx.power_down()
        hx.power_up()
        time.sleep(0.1)

        if time.time() - lastMeasurementTime > 300:
             measureAirQuality()
             lastMeasurementTime = time.time()
             tare()


        updateMeasurementHistory(val)  # Update the measurement history
        runningAverage = calculateAverageHistory()  # Calculate the running average
        showSensorValues()
        perc = mq.MQPercentage()
        sendLiveAirQuality(perc["GAS_LPG"], perc["CO"], perc["SMOKE"])
        

        while val > 100:
            val = hx.get_weight(5)
            hx.power_down()
            hx.power_up()
            time.sleep(0.1)
            totalWeight = 0
            
            for _ in range(counter):
                val = hx.get_weight(5)
                totalWeight += val
                time.sleep(0.1)
            newCatWeight = totalWeight / counter
            if newCatWeight >= lastCatWeight * 0.9:
                catWeight = newCatWeight
            lastCatWeight = catWeight
            showValuesWhilePooping()
            poopInside = True

        if poopInside:
            sendCatWeight(catWeight)
            print(f"Cat Weight sent: {catWeight}")
            totalWeight = 0
            for _ in range(counter):
                weight = hx.get_weight(5)
                totalWeight += weight
                time.sleep(0.1)
            poopWeight = totalWeight / counter
            time.sleep(2)
            sendPoopWeight(poopWeight)
            sendPoopMessage(telephoneNumbers, poopWeight)
            print(f"Poop Weight sent: {poopWeight}")
            tare()
            poopInside = False


    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
