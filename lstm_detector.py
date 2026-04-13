import numpy as np
import torch
import torch.nn as nn
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# =========================
# CONFIG
# =========================
url = "http://localhost:8086"
token = "hCya2h1PVTb6GNHLYtCfkQ92ZiOLaKiIQvMl0y-9Ws0SYSfPtooW8r9L_KC29RPkQD9QDSblDs8QDhPRx9DfYw=="
org = "cnc-org"
bucket = "cnc_data"

client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()
write_api = client.write_api(write_options=SYNCHRONOUS)

# =========================
# LSTM MODEL
# =========================
class LSTMModel(nn.Module):
    def __init__(self):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=32, batch_first=True)
        self.fc = nn.Linear(32, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return torch.sigmoid(out)   # IMPORTANT

# =========================
# LOAD TRAINED MODEL
# =========================
model = LSTMModel()
model.load_state_dict(torch.load("lstm_model.pth", map_location=torch.device('cpu')))
model.eval()

print("🤖 Trained LSTM Model Loaded")

# =========================
# MAIN LOOP
# =========================
while True:

    query = f'''
    from(bucket: "{bucket}")
      |> range(start: -2m)
      |> filter(fn: (r) => r._measurement == "cnc_machine")
      |> filter(fn: (r) => r._field == "vibration")
    '''

    tables = query_api.query(query)

    values = []

    for table in tables:
        for record in table.records:
            values.append(record.get_value())

    # =========================
    # PROCESS DATA
    # =========================
    if len(values) >= 5:

        data = np.array(values[-5:])
        data = torch.tensor(data).float().view(1, 5, 1)

        with torch.no_grad():
            output = model(data)

        score = output.item()
        print("score:", round(score, 4))

        # =========================
        # ANOMALY DETECTION
        # =========================
        if score > 0.5:
            anomaly = 1
            print("🚨 Machine Abnormal")
        else:
            anomaly = 0
            print("✅ Machine Normal")

        # =========================
        # SEND TO INFLUXDB
        # =========================
        point = Point("cnc_machine") \
            .field("vibration", float(values[-1])) \
            .field("anomaly", int(anomaly))

        write_api.write(bucket=bucket, org=org, record=point)

    time.sleep(2)