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
token = "hCya2h1PVTb6GNHLYtCfkQ92ZiOLaKiIQvMl0y-9Ws0SYSfPtooW8r9L_KC29RPkQD9QDSblDs8QDhPRx9DfYw=="
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
    print("🤖 LSTM Model Loaded")
except:
    print("⚠️ LSTM model not found → Rule-based mode only")

buffer = []

# =====================
# MQTT CALLBACK
# =====================
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())

        temp = float(data["temperature"])
        rpm = float(data["rpm"])
        vibration = float(data["vibration"])

        print("\n🤖 EDGE AI DETECTOR")
        print("------------------------")
        print("🌡 Temp:", temp)
        print("⚙️ RPM:", rpm)
        print("📳 Vibration:", vibration)

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

            print("🧠 AI Score:", round(score, 4))

        # =====================
        # RULE ENGINE
        # =====================
        if vibration > 8.5:
            status = "FAILURE RISK"
            anomaly = 1
            print("🚨 STATUS: FAILURE RISK")

        elif vibration > 7.5:
            status = "WARNING"
            anomaly = 1
            print("⚠️ STATUS: WARNING")

        else:
            status = "NORMAL"
            anomaly = 0
            print("✅ STATUS: NORMAL")

        # =====================
        # INFLUXDB WRITE (FIXED)
        # =====================
        point = (
            Point("cnc_machine")
            .field("temperature", float(temp))
            .field("rpm", float(rpm))
            .field("vibration", float(vibration))
            .field("anomaly", int(anomaly))
        )

        write_api.write(bucket=bucket, org=org, record=point)

    except Exception as e:
        print("❌ Error:", e)

# =====================
# MQTT SETUP
# =====================
client = mqtt.Client()
client.connect("localhost", 1883, 60)

client.subscribe("cnc/data")
client.on_message = on_message

print("🤖 Edge AI System Running...")
print("Waiting for CNC sensor data...\n")

client.loop_forever()