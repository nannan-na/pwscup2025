#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import random

# -------------------------
# PyTorch MLP
# -------------------------
class SimpleMLP(nn.Module):
    def __init__(self, input_dim: int, hidden: int = 64, dropout: float = 0.2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, 1)
        )

    def forward(self, x):
        return self.net(x).squeeze(1)

# -------------------------
# Utilities
# -------------------------
def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def make_features(df: pd.DataFrame) -> pd.DataFrame:
    p = df["prob"].astype(float).clip(1e-12, 1 - 1e-12)
    true_vals = df["true_label"].astype(int)
    X = pd.DataFrame({
        "prob": p,
        "margin": np.abs(p - 0.5),
        "entropy": -(p * np.log(p) + (1 - p) * np.log(1 - p)),
        "logit": np.log(p / (1 - p)).clip(-50, 50),
        "correct": ((p >= 0.5).astype(int) == true_vals).astype(int)
    })
    return X

# -------------------------
# Train
# -------------------------
def train_attack_nn(train_df, epochs=30, batch_size=256, hidden=64, lr=1e-3, seed=42):
    set_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    X = make_features(train_df).values
    y = train_df["member"].astype(int).values

    X_tr, X_val, y_tr, y_val = train_test_split(
        X, y, test_size=0.1, random_state=seed, stratify=y
    )

    scaler = StandardScaler()
    X_tr = scaler.fit_transform(X_tr)
    X_val = scaler.transform(X_val)

    train_ds = TensorDataset(torch.from_numpy(X_tr).float(), torch.from_numpy(y_tr).float())
    val_ds = TensorDataset(torch.from_numpy(X_val).float(), torch.from_numpy(y_val).float())
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)

    model = SimpleMLP(X_tr.shape[1], hidden=hidden).to(device)
    opt = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.BCEWithLogitsLoss()

    best_loss = float("inf")
    best_state = None
    patience, no_improve = 6, 0

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            opt.step()
            total_loss += loss.item() * xb.size(0)
        train_loss = total_loss / len(train_loader.dataset)

        # validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for xb, yb in val_loader:
                xb, yb = xb.to(device), yb.to(device)
                loss = criterion(model(xb), yb)
                val_loss += loss.item() * xb.size(0)
        val_loss /= len(val_loader.dataset)

        print(f"[{epoch}] train={train_loss:.6f} val={val_loss:.6f}")

        if val_loss < best_loss:
            best_loss = val_loss
            best_state = {k: v.cpu() for k, v in model.state_dict().items()}
            no_improve = 0
        else:
            no_improve += 1
            if no_improve >= patience:
                print("Early stopping")
                break

    if best_state:
        model.load_state_dict(best_state)
    return model, scaler

# -------------------------
# Predict
# -------------------------
def predict_topk_nn(model, scaler, val_df, k=10000):
    X = make_features(val_df).values
    Xs = scaler.transform(X)

    device = next(model.parameters()).device
    with torch.no_grad():
        logits = model(torch.from_numpy(Xs).float().to(device)).cpu().numpy()
    probs = 1 / (1 + np.exp(-logits))

    n = len(probs)
    topk = np.argsort(-probs, kind="stable")[: min(k, n)]
    labels = np.zeros(n, dtype=int)
    labels[topk] = 1
    return labels

# -------------------------
# Main
# -------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("train_csv")
    parser.add_argument("val_csv")
    parser.add_argument("out_csv")
    parser.add_argument("--k", type=int, default=10000)
    args = parser.parse_args()

    # ヘッダーなしCSVを読み込む場合は自動で列名を付ける
    colnames = ["true_label", "prob", "member"]
    train_df = pd.read_csv(args.train_csv, header=None, names=colnames)
    val_df = pd.read_csv(args.val_csv, header=None, names=colnames)

    print("Training attack model...")
    model, scaler = train_attack_nn(train_df)

    print("Predicting on validation data...")
    labels = predict_topk_nn(model, scaler, val_df, k=args.k)

    pd.DataFrame(labels).to_csv(args.out_csv, index=False, header=False)
    print(f"Saved predictions to {args.out_csv} (1s={labels.sum()}, top-k={args.k})")

if __name__ == "__main__":
    main()
