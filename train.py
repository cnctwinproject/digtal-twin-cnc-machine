"""
Train LSTM using your existing data.csv
Run: python train.py
"""
from lstm_model import AnomalyDetector

print("=" * 45)
print("  CNC LSTM Training - data.csv use பண்றோம்")
print("=" * 45)

detector = AnomalyDetector(seq_len=20)
detector.train("data.csv", epochs=30)
detector.save("lstm_weights.pt")

print("\n✅ Training done!")
print("   Now run: python live_detector.py")
