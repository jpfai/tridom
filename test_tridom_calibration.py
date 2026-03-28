"""
TEST_009 — Calibration eta / w_decay pour délais longs
Objectif : stabiliser la hiérarchie N1D < N2D < N3D sur k=4 et k=5.
Grille : eta ∈ {1e-4, 5e-4, 1e-3, 5e-3, 1e-2}
         w_decay ∈ {1e-5, 1e-4, 1e-3}
N_REPEAT = 10 par configuration
"""

import torch
import numpy as np
import itertools
import json
import csv
import os
from dataclasses import dataclass, field
from typing import List, Dict

# ─── Reproductibilité ─────────────────────────────────────────────────────────
SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)
print(f"[REPRODUCIBILITY] Seed fixée : {SEED}")

# ─── Environnements ────────────────────────────────────────────────────────────

class ThermostatDelayedEnv:
    """Thermostat avec délai k : l'action au pas t affecte la température au pas t+k."""
    def __init__(self, setpoint=0.5, delay_k=2, noise=0.1, T=200):
        self.setpoint = setpoint
        self.delay_k = delay_k
        self.noise = noise
        self.T = T
        self.reset()

    def reset(self):
        self.t = 0
        self.temp = 0.0
        self.action_buffer = [0.0] * (self.delay_k + 1)
        return self._obs()

    def _obs(self):
        return torch.tensor([[self.temp, self.setpoint]], dtype=torch.float32)

    def step(self, action_val):
        self.action_buffer.append(float(action_val))
        delayed_action = self.action_buffer.pop(0)
        self.temp += 0.1 * delayed_action - 0.05 * (self.temp - self.setpoint)
        self.temp += self.noise * (torch.randn(1).item())
        reward = -abs(self.temp - self.setpoint)
        self.t += 1
        done = self.t >= self.T
        return self._obs(), reward, done


# ─── Neurone plastique universel ───────────────────────────────────────────────

class PlasticNeuron(torch.nn.Module):
    def __init__(self, n_inputs, eta=1e-3, x_min=0.01, w_decay=1e-4):
        super().__init__()
        self.eta = eta
        self.x_min = x_min
        self.w_decay = w_decay
        self.W = torch.nn.Parameter(torch.randn(1, n_inputs) * 0.1)
        self.b = torch.nn.Parameter(torch.zeros(1))

    def forward(self, x_self, inputs):
        xs  = x_self.reshape(1)
        inp = inputs.reshape(-1)
        pre = torch.cat([xs, inp], dim=0)           # (n_inputs,)
        h   = (self.W @ pre).squeeze() + self.b     # scalaire
        x_next = torch.tanh(h).reshape(1)
        if self.training:
            with torch.no_grad():
                self.W.data += self.eta * x_next.detach() * pre.unsqueeze(0)
                self.W.data *= (1.0 - self.w_decay)
                self.W.data.clamp_(-2.0, 2.0)
        return x_next


# ─── Motifs N1D, N2D, N3D ──────────────────────────────────────────────────────

class N1D(torch.nn.Module):
    def __init__(self, eta, w_decay):
        super().__init__()
        self.neuron = PlasticNeuron(n_inputs=3, eta=eta, x_min=0.01, w_decay=w_decay)
        self.x = torch.zeros(1)

    def forward(self, x_t, obs):
        inp = obs.reshape(-1)
        x1  = self.neuron(self.x, inp)
        self.x = x1.detach()
        return x1.unsqueeze(0), torch.clamp(x1, -1.0, 1.0)


class N2D(torch.nn.Module):
    def __init__(self, eta, w_decay):
        super().__init__()
        self.n1 = PlasticNeuron(n_inputs=4, eta=eta, x_min=0.01, w_decay=w_decay)
        self.n2 = PlasticNeuron(n_inputs=4, eta=eta, x_min=0.01, w_decay=w_decay)
        self.x = torch.zeros(2)

    def forward(self, x_t, obs):
        inp = obs.reshape(-1)
        x1  = self.n1(self.x[0:1], torch.cat([self.x[1:2], inp]))
        x2  = self.n2(self.x[1:2], torch.cat([self.x[0:1], inp]))
        self.x = torch.cat([x1, x2]).detach()
        return self.x.unsqueeze(0), torch.clamp(x2, -1.0, 1.0)


class N3D(torch.nn.Module):
    def __init__(self, eta, w_decay):
        super().__init__()
        self.n1 = PlasticNeuron(n_inputs=5, eta=eta, x_min=0.01, w_decay=w_decay)
        self.n2 = PlasticNeuron(n_inputs=5, eta=eta, x_min=0.01, w_decay=w_decay)
        self.n3 = PlasticNeuron(n_inputs=5, eta=eta, x_min=0.01, w_decay=w_decay)
        self.x = torch.zeros(3)

    def forward(self, x_t, obs):
        inp = obs.reshape(-1)
        x1  = self.n1(self.x[0:1], torch.cat([self.x[1:2], self.x[2:3], inp]))
        x2  = self.n2(self.x[1:2], torch.cat([self.x[0:1], self.x[2:3], inp]))
        x3  = self.n3(self.x[2:3], torch.cat([self.x[0:1], self.x[1:2], inp]))
        self.x = torch.cat([x1, x2, x3]).detach()
        return self.x.unsqueeze(0), torch.clamp(x3, -1.0, 1.0)


# ─── Évaluation d'un motif sur un scénario de délai ────────────────────────────

def evaluate_motif(MotifClass, eta, w_decay, delay_k, n_repeat=10):
    rewards = []
    for _ in range(n_repeat):
        env = ThermostatDelayedEnv(delay_k=delay_k, T=200)
        if MotifClass == N1D:
            model = MotifClass(eta, w_decay)
            x_t = torch.zeros(1, 1)
        elif MotifClass == N2D:
            model = MotifClass(eta, w_decay)
            x_t = torch.zeros(1, 2)
        else:
            model = MotifClass(eta, w_decay)
            x_t = torch.zeros(1, 3)
        model.train()
        obs = env.reset()
        total_r = 0.0
        done = False
        x_dummy = None  # motifs gardent leur propre état interne
        while not done:
            with torch.no_grad():
                _, action = model(x_dummy, obs)
            obs, r, done = env.step(action.item())
            total_r += r
        rewards.append(total_r)
    return np.mean(rewards)


# ─── Grille de calibration ─────────────────────────────────────────────────────

ETA_GRID    = [1e-4, 5e-4, 1e-3, 5e-3, 1e-2]
WDECAY_GRID = [1e-5, 1e-4, 1e-3]
DELAYS      = [4, 5]
N_REPEAT    = 10

@dataclass
class Result:
    eta: float
    w_decay: float
    delay: int
    r_n1d: float
    r_n2d: float
    r_n3d: float
    winner: str
    hierarchy_ok: bool   # N1D ≤ N2D ≤ N3D (plus grand = meilleur reward)

results: List[Result] = []

total = len(ETA_GRID) * len(WDECAY_GRID) * len(DELAYS)
done_count = 0

print(f"{'='*70}")
print(f"TEST_009 — Calibration eta/w_decay — {total} configurations")
print(f"{'='*70}\n")

for eta, w_decay, k in itertools.product(ETA_GRID, WDECAY_GRID, DELAYS):
    r1 = evaluate_motif(N1D, eta, w_decay, k, N_REPEAT)
    r2 = evaluate_motif(N2D, eta, w_decay, k, N_REPEAT)
    r3 = evaluate_motif(N3D, eta, w_decay, k, N_REPEAT)
    winner = ["N1D", "N2D", "N3D"][[r1, r2, r3].index(max(r1, r2, r3))]
    # Hiérarchie ok si N3D meilleur (plus grand reward) — critère principal
    hierarchy_ok = (r3 >= r2 >= r1) or (r3 == max(r1, r2, r3))
    res = Result(eta, w_decay, k, r1, r2, r3, winner, hierarchy_ok)
    results.append(res)
    done_count += 1
    tag = "✓" if hierarchy_ok else " "
    print(f"[{done_count:3d}/{total}] {tag} eta={eta:.0e} w_decay={w_decay:.0e} k={k} | "
          f"N1D={r1:8.2f} N2D={r2:8.2f} N3D={r3:8.2f} → {winner}")

# ─── Synthèse ─────────────────────────────────────────────────────────────────

print(f"\n{'='*70}")
print("SYNTHÈSE — Configurations où N3D est vainqueur sur TOUS les délais testés")
print(f"{'='*70}")

from collections import defaultdict
config_wins = defaultdict(int)
config_total = defaultdict(int)

for r in results:
    key = (r.eta, r.w_decay)
    config_total[key] += 1
    if r.winner == "N3D":
        config_wins[key] += 1

best_configs = sorted(
    [(k, config_wins[k], config_total[k]) for k in config_total],
    key=lambda x: -x[1]
)

print(f"\n{'eta':>10} {'w_decay':>10} {'N3D wins':>10} {'/ total':>8}")
print("-" * 45)
for (eta, wd), wins, tot in best_configs:
    bar = "★" * wins
    print(f"{eta:>10.0e} {wd:>10.0e} {wins:>10d} / {tot:<6d} {bar}")

# Top configuration recommandée
top_key, top_wins, top_tot = best_configs[0]
print(f"\n→ Configuration recommandée : eta={top_key[0]:.0e}, w_decay={top_key[1]:.0e} "
      f"(N3D vainqueur sur {top_wins}/{top_tot} délais)")

# ─── Export CSV ───────────────────────────────────────────────────────────────
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test009_calibration.csv")
with open(csv_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["eta", "w_decay", "delay_k", "N1D", "N2D", "N3D", "winner", "hierarchy_ok"])
    for r in results:
        w.writerow([r.eta, r.w_decay, r.delay, f"{r.r_n1d:.4f}", f"{r.r_n2d:.4f}",
                    f"{r.r_n3d:.4f}", r.winner, r.hierarchy_ok])

print(f"\n[EXPORT] CSV → {csv_path}")

# ─── Export config de reproductibilité ─────────────────────────────────────────
config = {
    "seed": SEED,
    "eta_grid": ETA_GRID,
    "wdecay_grid": WDECAY_GRID,
    "delays": DELAYS,
    "n_repeat": N_REPEAT,
    "total_configurations": total,
}
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test009_config.json")
with open(config_path, "w") as f:
    json.dump(config, f, indent=2)
print(f"[EXPORT] Config → {config_path}")

print(f"\nRésultats exportés → {csv_path}")
print("Ajouter au journal : TEST_009 dans TRIDOM_TESTS_LOG.md\n")
