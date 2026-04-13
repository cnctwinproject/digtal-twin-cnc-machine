import paho.mqtt.client as mqtt
import random
import time
import json

# MQTT SETUP
client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.loop_start()

print("📡 CNC Simulator (MQTT Mode) Started...\n")

while True:

    mode = random.choice(["normal", "abnormal"])

    temperature = random.uniform(40, 90)
    rpm = random.randint(1000, 5000)

    if mode == "normal":
        vibration = random.uniform(6, 8.4)
        anomaly = 0
    else:
        vibration = random.uniform(8.6, 10)
        anomaly = 1

    data = {
        "temperature": round(temperature, 2),
        "rpm": rpm,
        "vibration": round(vibration, 2),
        "anomaly": anomaly
    }

    payload = json.dumps(data)

    # SEND TO MQTT (IMPORTANT)
    client.publish("cnc/data", payload)

    print("Sent MQTT:", payload)

    time.sleep(2)