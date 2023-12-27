import requests
from sense_hat import SenseHat

sense = SenseHat()
sense.clear()

temp = sense.get_temperature()

url = "https://pfistdo.pythonanywhere.com/poop/"
payload = {
    "weight": temp
}

try:
    response = requests.post(url, json=payload)
    if response.status_code == 201:
        print("Data inserted successfully!")
    else:
        print(f"Failed to send data. Status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
