import paho.mqtt.client as mqtt
import json
import time
import random

client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.loop_start()

print("🚀 Anomaly Publisher Started!")
count = 0

while True:
    count += 1
    
    # Normal vibrations
    v1 = random.uniform(-0.8, 0.8)
    v2 = random.uniform(-0.8, 0.8)
    v3 = random.uniform(-0.8, 0.8)
    
    # Every 50 readings - HIGH vibrations (ANOMALY)
    if count % 50 == 0:
        v1 = random.uniform(-3, 3)
        v2 = random.uniform(-3, 3)
        v3 = random.uniform(-3, 3)
        print(f"💥 ANOMALY #{count//50} SENT!")
    
    data = {
        'v1': v1,
        'v2': v2,
        'v3': v3,
        'time': time.time()
    }
    
    client.publish("cnc/vibration", json.dumps(data))
    time.sleep(0.05)