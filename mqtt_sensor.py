import paho.mqtt.client as mqtt
import time
import random

broker = "localhost"
port = 1883
topic = "cnc/vibration"

client = mqtt.Client()
client.connect(broker, port)

print("📡 Sensor started sending data...")

while True:

    vibration = round(random.uniform(2, 10), 2)

    client.publish(topic, vibration)

    print("Sent vibration:", vibration)

    time.sleep(2)