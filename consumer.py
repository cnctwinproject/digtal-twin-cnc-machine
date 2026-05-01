import paho.mqtt.client as mqtt
import json
import csv

file = open("data.csv", "a", newline="")
writer = csv.writer(file)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())

    v1 = data["v1"]
    v2 = data["v2"]
    v3 = data["v3"]
    t = data["time"]

    writer.writerow([t, v1, v2, v3])
    print("Saved:", v1, v2, v3)

client = mqtt.Client()
client.connect("localhost", 1883, 60)

client.subscribe("cnc/vibration")
client.on_message = on_message

client.loop_forever()