import paho.mqtt.client as mqtt
import torch
import torch.nn as nn
import numpy as np
import json
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# =====================
# INFLUXDB CONFIG
# =====================
url = "http://localhost:8086"
token = "YfRVMDNRL349HKwJPNSh-0PmzBjTqIqWgCskDLXaJWXhyIv8KPbUEzuPtBtb9wBXkZbpGJst7RFbkO7EDEsIvg=="
org = "cnc-org"
bucket = "cnc_data"

db_client = InfluxDBClient(url=url, token=token, org=org)
write_api = db_client.write_api(write_options=SYNCHRONOUS)

# =====================
# LSTM MODEL
# =====================
class LSTMModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(1, 32, batch_first=True)
        self.fc = nn.Linear(32, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

model = LSTMModel()

try:
    model.load_state_dict(torch.load("lstm_model.pth", map_location="cpu"))
    model.eval()
    print(" LSTM Model Loaded")
except:
    print(" LSTM model not found → Rule-based mode only")

buffer = []

# =====================
# MQTT CALLBACK
# =====================
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())

        #  CLEAN INPUT (FROM MQTT)
        temp = float(data["temperature"])
        rpm = float(data["rpm"])
        vibration = float(data["vibration"])

        anomaly = int(data.get("anomaly", 0))           
        master_alert = int(data.get("master_alert", 0)) 

        print("\n🤖EDGE AI DETECTOR")
        print("------------------------")
        print(" Temp:", temp)
        print(" RPM:", rpm)
        print(" Vibration:", vibration)
        print(" ANOMALY:", anomaly)
        print(" MASTER ALERT:", master_alert)

        buffer.append(vibration)

        if len(buffer) > 5:
            buffer[:] = buffer[-5:]

        # =====================
        # LSTM PREDICTION
        # =====================
        if len(buffer) == 5:
            seq = np.array(buffer)
            seq = torch.tensor(seq).float().view(1, 5, 1)

            output = model(seq)
            score = abs(output.item())

            print(" AI Score:", round(score, 4))

        # =====================
        # STATUS DISPLAY (NO OVERRIDE)
        # =====================
        if anomaly == 1:
            print(" STATUS: ANOMALY DETECTED")
        else:
            print(" STATUS: NORMAL")

        # =====================
        # INFLUXDB WRITE
        # =====================
        point = (
            Point("cnc_machine")
            .field("temperature", temp)
            .field("rpm", rpm)
            .field("vibration", vibration)
            .field("anomaly", anomaly)
            .field("master_alert", master_alert)
        )

        write_api.write(bucket=bucket, org=org, record=point)

    except Exception as e:
        print(" Error:", e)

# =====================
# MQTT SETUP
# =====================
client = mqtt.Client()
client.connect("localhost", 1883, 60)

client.subscribe("cnc/data")
client.on_message = on_message

print(" Edge AI System Running...")
print("Waiting for CNC sensor data...\n")

client.loop_forever()