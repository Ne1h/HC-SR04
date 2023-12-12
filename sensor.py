import RPi.GPIO as GPIO
import time
import json
import os
import requests

TRIG = 20
ECHO = 26


def setup_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.output(TRIG, False)

def measure_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

def save_distance_to_json(distance):
    file_name = 'distance_data.json'
    distance_data = {
        'distance': distance,
        'time': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    if os.path.exists(file_name) and os.stat(file_name).st_size > 0:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
    else:
        data = {}

    if 'history' not in data:
        data['history'] = []

    data['history'].append(distance_data)

    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def send_to_server(distance):
    url = 'http://localhost:8000/upload'

    timestamp = int(time.time())

    data = {"distance": distance, "timestamp": timestamp}

    headers = {"Content-Type": "application/json"}

    response = requests.put(url, data=json.dumps(data), headers=headers)

    res = response.json()

    print(res)

def main():
    setup_GPIO()

    while True:
        print("--------|Calculating...|--------")
        time.sleep(0.2)
        distance = measure_distance()

        print("Distance:", distance, "cm")
        save_distance_to_json(distance)
        send_to_server(distance)
        time.sleep(10)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
