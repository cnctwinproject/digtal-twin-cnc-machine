"""
Live LSTM Anomaly Detector
Subscribes to MQTT → runs LSTM → prints anomaly result
Run: python live_detector.py
"""
import paho.mqtt.client as mqtt
import json, os
from lstm_model import AnomalyDetector

BROKER = "localhost"
TOPIC  = "cnc/vibration"          # <-- same topic as your publisher.py

# ── Load model ───────────────────────────────────────────
detector = AnomalyDetector(seq_len=20)
if os.path.exists("lstm_weights.pt"):
    detector.load("lstm_weights.pt")
else:
    print("⚠️  lstm_weights.pt not found!")
    print("   Run: python train.py  first!")
    exit()

icons = {"NORMAL": "🟢", "WARNING": "🟡", "CRITICAL": "🔴", "SEVERE": "💀"}
count = 0

def on_connect(client, userdata, flags, rc):
    print(f"✅ MQTT Connected | Listening: {TOPIC}\n")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    global count
    try:
        data = json.loads(msg.payload.decode())
        v1   = float(data.get("v1", 0))
        v2   = float(data.get("v2", 0))
        v3   = float(data.get("v3", 0))

        detector.add(v1, v2, v3)
        result = detector.predict()
        count += 1

        if result:
            icon = icons.get(result["severity"], "⚪")
            print(f"{icon} [{count:04d}] {result['severity']:8s} | "
                  f"X:{v1:+.3f} Y:{v2:+.3f} Z:{v3:+.3f} | "
                  f"Error:{result['error']:.5f} Thr:{result['threshold']:.5f}"
                  + (" ⚠️  ANOMALY!" if result["anomaly"] else ""))
        else:
            print(f"⏳ [{count:04d}] Buffering... ({len(detector.buffer)}/20)")

    except Exception as e:
        print(f"Error: {e}")

client = mqtt.Client(client_id="lstm_detector")
client.on_connect = on_connect
client.on_message = on_message

print("🤖 CNC Digital Twin - Live LSTM Detector")
print("=" * 55)
client.connect(BROKER, 1883, 60)
client.loop_forever()
