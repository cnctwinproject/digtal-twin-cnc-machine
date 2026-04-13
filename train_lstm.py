import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

# =====================
# SAMPLE DATA (DEMO)
# =====================
normal = np.random.normal(7, 0.5, (100, 5))
abnormal = np.random.normal(9, 0.5, (100, 5))

X = np.concatenate((normal, abnormal))
y = np.concatenate((np.zeros(100), np.ones(100)))

X = torch.tensor(X).float().view(-1, 5, 1)
y = torch.tensor(y).float().view(-1, 1)

# =====================
# MODEL
# =====================
class LSTMModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(1, 32, batch_first=True)
        self.fc = nn.Linear(32, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return torch.sigmoid(out)

model = LSTMModel()

# =====================
# TRAINING
# =====================
loss_fn = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

for epoch in range(50):

    output = model(X)
    loss = loss_fn(output, y)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    print(f"Epoch {epoch}, Loss: {loss.item():.4f}")

# =====================
# SAVE MODEL
# =====================
torch.save(model.state_dict(), "lstm_model.pth")

print("✅ Model Trained & Saved")