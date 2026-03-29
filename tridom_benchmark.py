"""
TRIDOM BENCHMARK v0.1 — Comparaison Tridom vs GRU vs LSTM

Tâche : classification de séries temporelles avec hystérésis.

Le signal d'entrée est un sinusoid bruité dont la classe dépend
de l'hystérésis (signal lent sous-jacent). C'est une tâche qui
teste la capacité de mémoire à court terme — exactement le type
de dynamique que les Tridom bistables ou oscillants peuvent encoder.

Comparaison :
- TridomCell (3 nœuds, topologie fixe sélectionnée)
- GRU (3 unités)
- LSTM (3 unités)

Métriques : accuracy, nombre de paramètres, temps d'entraînement.

Hyperparamètres :
- seed=42 pour reproductibilité
- lr=0.001, epochs=50, batch_size=64
- hidden_size=3 (même dimension pour comparaison équitable)
- train/test split 80/20
- 2000 séries de longueur 50, 2 classes

Choix de la topologie Tridom :
  On utilise 01E.12E.20I (EEI cycle) — classée oscillante, connue pour
  sa capacité de mémoire temporelle. C'est la topologie Tridom la plus
  adaptée à la classification de séries.
"""

import json
import os
import time
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# ─── Reproductibilité ──────────────────────────────────────────────────────────

SEED = 42
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ─── Génération de données : classification avec hystérésis ────────────────────

def generate_hysteresis_dataset(n_samples=2000, seq_len=50, noise_std=0.15):
    """
    Génère des séries temporelles avec hystérésis pour classification binaire.

    Signal : x(t) = sin(2π * f * t) + h(t) + bruit
    où h(t) est un signal d'hystérésis (marche lente) :
      - classe 0 : h(t) oscille autour de -0.5
      - classe 1 : h(t) oscille autour de +0.5
      - la transition est lente (hystérésis)

    Le modèle doit distinguer les deux classes à partir de la séquence.
    """
    X = np.zeros((n_samples, seq_len), dtype=np.float32)
    y = np.zeros(n_samples, dtype=np.int64)

    for i in range(n_samples):
        cls = i % 2
        # Fréquence légèrement variable
        f = 0.1 + np.random.uniform(-0.02, 0.02)
        t = np.arange(seq_len, dtype=np.float32)

        # Signal sinusoïdal
        signal = np.sin(2 * np.pi * f * t / seq_len)

        # Hystérésis : offset selon la classe, avec transition lente
        if cls == 0:
            hysteresis = -0.5 * np.tanh((t - seq_len / 2) / (seq_len / 4))
        else:
            hysteresis = 0.5 * np.tanh((t - seq_len / 2) / (seq_len / 4))

        # Bruit
        noise = noise_std * np.random.randn(seq_len)

        X[i] = signal + hysteresis + noise
        y[i] = cls

    return X, y


# ─── Modèle Tridom Cell ────────────────────────────────────────────────────────

class TridomCell(nn.Module):
    """
    Cellule récurrente Tridom : dynamique triadique discrétisée.

    Topologie : 01E.12E.20I (EEI cycle, 3 nœuds, 3 arêtes).
    Équation : x_{t+1} = tanh(1.5 * W @ x_t) - 0.5 * x_t + B * u_t
    où W est la matrice de poids définie par la topologie signée.
    """

    def __init__(self, input_size, hidden_size=3):
        super().__init__()
        self.hidden_size = hidden_size

        # Matrice de topologie signée : 01E.12E.20I
        # Arêtes : 0→1 (+1), 1→2 (+1), 2→0 (-1)
        W = torch.zeros(hidden_size, hidden_size)
        W[0, 1] = 1.0   # 0→1 excitatory
        W[1, 2] = 1.0   # 1→2 excitatory
        W[2, 0] = -1.0  # 2→0 inhibitory
        self.register_buffer('W', W)

        # Couche d'entrée
        self.input_proj = nn.Linear(input_size, hidden_size, bias=True)

    def forward(self, x, h=None):
        """
        x : (batch, seq_len, input_size)
        retourne : (batch, seq_len, hidden_size), (batch, hidden_size)
        """
        batch_size, seq_len, _ = x.shape
        if h is None:
            h = torch.zeros(batch_size, self.hidden_size, device=x.device)

        outputs = []
        for t in range(seq_len):
            u_t = self.input_proj(x[:, t, :])
            # Dynamique Tridom : tanh(1.5 * W @ h) - 0.5 * h + input
            dx = h @ self.W.T  # (batch, hidden)
            h = torch.tanh(1.5 * dx) - 0.5 * h + u_t
            outputs.append(h)

        outputs = torch.stack(outputs, dim=1)  # (batch, seq_len, hidden)
        return outputs, h


class TridomClassifier(nn.Module):
    def __init__(self, input_size=1, hidden_size=3, n_classes=2):
        super().__init__()
        self.cell = TridomCell(input_size, hidden_size)
        self.fc = nn.Linear(hidden_size, n_classes)

    def forward(self, x):
        # x: (batch, seq_len, 1)
        outputs, h = self.cell(x)
        # Utiliser le dernier état caché
        return self.fc(outputs[:, -1, :])


# ─── Modèles de référence ──────────────────────────────────────────────────────

class GRUClassifier(nn.Module):
    def __init__(self, input_size=1, hidden_size=3, n_classes=2):
        super().__init__()
        self.gru = nn.GRU(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, n_classes)

    def forward(self, x):
        out, _ = self.gru(x)
        return self.fc(out[:, -1, :])


class LSTMClassifier(nn.Module):
    def __init__(self, input_size=1, hidden_size=3, n_classes=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, n_classes)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


# ─── Entraînement et évaluation ───────────────────────────────────────────────

def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def train_and_evaluate(model, train_loader, test_loader, epochs=50, lr=0.001):
    """Entraîne le modèle et retourne (accuracy, n_params, train_time)."""
    model = model.to(DEVICE)
    n_params = count_parameters(model)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    t0 = time.time()
    for epoch in range(epochs):
        model.train()
        for batch_x, batch_y in train_loader:
            batch_x = batch_x.to(DEVICE)
            batch_y = batch_y.to(DEVICE)
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()

    train_time = time.time() - t0

    # Évaluation
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            batch_x = batch_x.to(DEVICE)
            batch_y = batch_y.to(DEVICE)
            logits = model(batch_x)
            preds = logits.argmax(dim=1)
            correct += (preds == batch_y).sum().item()
            total += batch_y.size(0)

    accuracy = correct / total
    return accuracy, n_params, train_time


# ─── Programme principal ───────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("TRIDOM BENCHMARK — Tridom vs GRU vs LSTM")
    print("=" * 70)
    print(f"Device: {DEVICE}")
    print(f"Seed: {SEED}")
    print()

    # Hyperparamètres
    N_SAMPLES = 2000
    SEQ_LEN = 50
    NOISE_STD = 0.15
    HIDDEN_SIZE = 3
    EPOCHS = 50
    LR = 0.001
    BATCH_SIZE = 64

    print(f"Hyperparamètres :")
    print(f"  N_SAMPLES={N_SAMPLES}, SEQ_LEN={SEQ_LEN}, NOISE={NOISE_STD}")
    print(f"  HIDDEN_SIZE={HIDDEN_SIZE}, EPOCHS={EPOCHS}, LR={LR}")
    print(f"  BATCH_SIZE={BATCH_SIZE}")
    print()

    # Génération des données
    print("Génération du dataset hystérésis...")
    X, y = generate_hysteresis_dataset(N_SAMPLES, SEQ_LEN, NOISE_STD)

    # Train/test split (80/20)
    n_train = int(0.8 * N_SAMPLES)
    indices = np.random.permutation(N_SAMPLES)
    train_idx, test_idx = indices[:n_train], indices[n_train:]

    X_train = torch.FloatTensor(X[train_idx]).unsqueeze(-1)  # (n, seq, 1)
    y_train = torch.LongTensor(y[train_idx])
    X_test = torch.FloatTensor(X[test_idx]).unsqueeze(-1)
    y_test = torch.LongTensor(y[test_idx])

    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

    print(f"  Train: {len(train_idx)}, Test: {len(test_idx)}")
    print()

    # ── Benchmark ──────────────────────────────────────────────────────────
    models = {
        "Tridom (EEI, 3 nodes)": TridomClassifier(1, HIDDEN_SIZE),
        "GRU (3 units)": GRUClassifier(1, HIDDEN_SIZE),
        "LSTM (3 units)": LSTMClassifier(1, HIDDEN_SIZE),
    }

    results = {}

    print(f"{'Modèle':<30s} {'Accuracy':>10s} {'Params':>10s} {'Time (s)':>10s}")
    print("-" * 65)

    for name, model in models.items():
        # Reset seed avant chaque modèle pour équité
        torch.manual_seed(SEED)
        np.random.seed(SEED)

        acc, n_params, train_time = train_and_evaluate(
            model, train_loader, test_loader, epochs=EPOCHS, lr=LR
        )
        results[name] = {
            "accuracy": round(acc, 4),
            "n_params": n_params,
            "train_time_s": round(train_time, 2),
        }
        print(f"{name:<30s} {acc:>10.4f} {n_params:>10d} {train_time:>10.2f}")

    print()

    # ── Analyse ────────────────────────────────────────────────────────────
    print("=" * 70)
    print("ANALYSE")
    print("=" * 70)

    tridom_acc = results["Tridom (EEI, 3 nodes)"]["accuracy"]
    gru_acc = results["GRU (3 units)"]["accuracy"]
    lstm_acc = results["LSTM (3 units)"]["accuracy"]
    tridom_params = results["Tridom (EEI, 3 nodes)"]["n_params"]
    gru_params = results["GRU (3 units)"]["n_params"]
    lstm_params = results["LSTM (3 units)"]["n_params"]

    print(f"\nTridom : acc={tridom_acc:.4f}, params={tridom_params}")
    print(f"GRU    : acc={gru_acc:.4f}, params={gru_params}")
    print(f"LSTM   : acc={lstm_acc:.4f}, params={lstm_params}")
    print(f"\nRatio paramètres Tridom/GRU : {tridom_params/gru_params:.2f}x")
    print(f"Ratio paramètres Tridom/LSTM : {tridom_params/lstm_params:.2f}x")

    if tridom_acc >= max(gru_acc, lstm_acc) - 0.05:
        print("\n→ Tridom est compétitif avec les baselines RNN classiques.")
    else:
        print(f"\n→ Tridom a un écart de {max(gru_acc, lstm_acc) - tridom_acc:.2%} "
              f"vs le meilleur. Écart attendu vu la topologie fixe.")

    # ── Export JSON ────────────────────────────────────────────────────────
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "tridom_benchmark_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "task": "hysteresis_classification",
            "seed": SEED,
            "device": str(DEVICE),
            "hyperparams": {
                "n_samples": N_SAMPLES,
                "seq_len": SEQ_LEN,
                "noise_std": NOISE_STD,
                "hidden_size": HIDDEN_SIZE,
                "epochs": EPOCHS,
                "lr": LR,
                "batch_size": BATCH_SIZE,
                "train_split": 0.8,
            },
            "results": results,
            "tridom_topology": "01E.12E.20I (EEI cycle)",
        }, f, indent=2, ensure_ascii=False)

    print(f"\nRésultats exportés → {out_path}")
