import paho.mqtt.client as mqtt
import time
import random
import math
import json

client = mqtt.Client()
client.connect("localhost", 1883, 60)

t = 0

while True:
    v1 = math.sin(t) + random.uniform(-0.1, 0.1)
    v2 = math.sin(t + 1) + random.uniform(-0.1, 0.1)
    v3 = math.sin(t + 2) + random.uniform(-0.1, 0.1)

    data = {
        "v1": v1,
        "v2": v2,
        "v3": v3,
        "time": t
    }

    client.publish("cnc/vibration", json.dumps(data))
    print("Sent:", data)

    t += 0.1
    time.sleep(1)