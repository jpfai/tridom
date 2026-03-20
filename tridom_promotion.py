"""
TRIDOM — Règle de promotion endogène + Architecture TridomGroupSystem (TGS)
N1D → N2D → N3D → TGS (Nona)

La promotion est déclenchée de l'intérieur du motif :
  - Pas d'oracle externe
  - Le motif "sait" qu'il ne s'en sort pas via sa vitalité et sa récompense cumulée
  - Il se remplace par le motif de niveau supérieur
"""

import torch
import torch.nn as nn
import numpy as np
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, List


# ─── Environnement Thermostat unifié ──────────────────────────────────────────

class ThermostatEnv:
    """Thermostat configurable : simple, bruit, délai, hystérésis."""
    def __init__(self, mode="simple", delay_k=0, noise=0.05, T=300,
                 setpoint=0.5, hyst_up=0.6, hyst_down=0.4):
        self.mode = mode
        self.delay_k = delay_k
        self.noise = noise
        self.T_steps = T
        self.setpoint = setpoint
        self.hyst_up = hyst_up
        self.hyst_down = hyst_down
        self.reset()

    def reset(self):
        self.t = 0
        self.temp = np.random.uniform(0.0, 1.0)
        self.action_buffer = deque([0.0] * (self.delay_k + 1), maxlen=self.delay_k + 1)
        self._heating = False  # état hystérésis
        return self._obs()

    def _obs(self):
        return torch.tensor([[self.temp, self.setpoint]], dtype=torch.float32)

    def step(self, action_val):
        a = float(action_val)
        self.action_buffer.append(a)
        effective_action = self.action_buffer[0]

        if self.mode == "hysteresis":
            # Logique hystérésis
            if self.temp < self.hyst_down:
                self._heating = True
            elif self.temp > self.hyst_up:
                self._heating = False
            heat = 0.1 if self._heating else 0.0
            self.temp += heat * effective_action - 0.03 * (self.temp - self.setpoint)
        else:
            self.temp += 0.1 * effective_action - 0.05 * (self.temp - self.setpoint)

        self.temp += self.noise * np.random.randn()
        reward = -abs(self.temp - self.setpoint)
        self.t += 1
        done = self.t >= self.T_steps
        return self._obs(), reward, done


# ─── Neurone plastique ─────────────────────────────────────────────────────────

class PlasticNeuron(nn.Module):
    def __init__(self, n_inputs, eta=1e-3, w_decay=1e-4):
        super().__init__()
        self.eta = eta
        self.w_decay = w_decay
        self.W = nn.Parameter(torch.randn(1, n_inputs) * 0.1)
        self.b = nn.Parameter(torch.zeros(1))

    def forward(self, x_self, inputs):
        # x_self : (1,) ou scalaire → (1,)
        # inputs : (n_inputs-1,)
        xs = x_self.reshape(1)
        inp = inputs.reshape(-1)
        pre = torch.cat([xs, inp], dim=0)          # (n_inputs,)
        h = (self.W @ pre).squeeze() + self.b      # scalaire
        x_next = torch.tanh(h).reshape(1)
        if self.training:
            with torch.no_grad():
                self.W.data += self.eta * x_next.detach() * pre.unsqueeze(0)
                self.W.data *= (1.0 - self.w_decay)
                self.W.data.clamp_(-2.0, 2.0)
        return x_next


# ─── Motifs hiérarchiques ──────────────────────────────────────────────────────

class N1D(nn.Module):
    LEVEL = 1
    def __init__(self, eta=1e-3, w_decay=1e-4):
        super().__init__()
        self.n = PlasticNeuron(3, eta, w_decay)  # x_self(1) + obs(2) = 3
        self.x = torch.zeros(1)
    def forward(self, obs):
        inp = obs.reshape(-1)           # (2,)
        x1 = self.n(self.x, inp)        # (1,)
        self.x = x1.detach()
        return torch.clamp(x1, -1, 1)
    def reset(self):
        self.x = torch.zeros(1)

class N2D(nn.Module):
    LEVEL = 2
    def __init__(self, eta=1e-3, w_decay=1e-4):
        super().__init__()
        # x_self(1) + x_other(1) + obs(2) = 4
        self.n1 = PlasticNeuron(4, eta, w_decay)
        self.n2 = PlasticNeuron(4, eta, w_decay)
        self.x = torch.zeros(2)
    def forward(self, obs):
        inp = obs.reshape(-1)                                   # (2,)
        x1 = self.n1(self.x[0:1], torch.cat([self.x[1:2], inp]))
        x2 = self.n2(self.x[1:2], torch.cat([self.x[0:1], inp]))
        self.x = torch.cat([x1, x2]).detach()
        return torch.clamp(x2, -1, 1)
    def reset(self):
        self.x = torch.zeros(2)

class N3D(nn.Module):
    LEVEL = 3
    def __init__(self, eta=1e-3, w_decay=1e-4):
        super().__init__()
        # x_self(1) + x_other1(1) + x_other2(1) + obs(2) = 5
        self.n1 = PlasticNeuron(5, eta, w_decay)
        self.n2 = PlasticNeuron(5, eta, w_decay)
        self.n3 = PlasticNeuron(5, eta, w_decay)
        self.x = torch.zeros(3)
    def forward(self, obs):
        inp = obs.reshape(-1)                                              # (2,)
        x1 = self.n1(self.x[0:1], torch.cat([self.x[1:2], self.x[2:3], inp]))
        x2 = self.n2(self.x[1:2], torch.cat([self.x[0:1], self.x[2:3], inp]))
        x3 = self.n3(self.x[2:3], torch.cat([self.x[0:1], self.x[1:2], inp]))
        self.x = torch.cat([x1, x2, x3]).detach()
        return torch.clamp(x3, -1, 1)
    def reset(self):
        self.x = torch.zeros(3)

MOTIF_CLASSES = {1: N1D, 2: N2D, 3: N3D}


# ─── Agent adaptatif avec promotion endogène ──────────────────────────────────

class AdaptiveTridomAgent:
    """
    Agent qui commence au niveau N1D et se promeut automatiquement
    si sa vitalité (récompense moyenne récente) stagne sous un seuil.
    Promotion : N1D → N2D → N3D (niveau 3 = terminal)
    """
    def __init__(self,
                 eta=1e-3, w_decay=1e-4,
                 promotion_window=30,
                 promotion_threshold=-1.2,
                 start_level=1):
        self.eta = eta
        self.w_decay = w_decay
        self.promotion_window = promotion_window
        self.promotion_threshold = promotion_threshold
        self.level = start_level
        self.motif = MOTIF_CLASSES[self.level](eta, w_decay)
        self.motif.train()
        self.reward_buffer = deque(maxlen=promotion_window)
        self.promotion_log: List[dict] = []

    def act(self, obs):
        return self.motif(obs)

    def record_reward(self, r, t):
        self.reward_buffer.append(r)
        # Évaluation de promotion toutes les `promotion_window` étapes
        if len(self.reward_buffer) == self.promotion_window:
            mean_r = np.mean(self.reward_buffer)
            if mean_r < self.promotion_threshold and self.level < 3:
                old_level = self.level
                self.level += 1
                self.motif = MOTIF_CLASSES[self.level](self.eta, self.w_decay)
                self.motif.train()
                self.reward_buffer.clear()
                entry = {
                    "t": t,
                    "from": old_level,
                    "to": self.level,
                    "trigger_mean_r": round(mean_r, 4)
                }
                self.promotion_log.append(entry)
                print(f"  [t={t:4d}] PROMOTION N{old_level}D → N{self.level}D "
                      f"(mean_r={mean_r:.4f} < {self.promotion_threshold})")

    def reset(self):
        self.motif.reset()


# ─── TridomGroupSystem (TGS) — Nona ───────────────────────────────────────────

class TridomGroupSystem:
    """
    TGS — Niveau 4 : 9 Tridoms N3D organisés en 3 groupes de 3 (structure Nona).
    Chaque groupe agrège ses sorties en moyenne pondérée par vitalité.
    Le TGS agrège les 3 groupes de la même manière.
    """
    N_GROUPS = 3
    TRIDOMS_PER_GROUP = 3  # → 9 Tridoms au total

    def __init__(self, eta=1e-3, w_decay=1e-4):
        self.groups: List[List[N3D]] = [
            [N3D(eta, w_decay) for _ in range(self.TRIDOMS_PER_GROUP)]
            for _ in range(self.N_GROUPS)
        ]
        # Vitalité courante de chaque Tridom
        self.vitalities = [[1.0] * self.TRIDOMS_PER_GROUP for _ in range(self.N_GROUPS)]
        # Récompenses récentes par groupe
        self.group_rewards = [deque(maxlen=20) for _ in range(self.N_GROUPS)]
        # Mettre tous en mode entraînement
        for grp in self.groups:
            for m in grp:
                m.train()

    def _update_vitality(self, g, i, reward):
        """Vitalité = EMA de la récompense (normalisée 0–1)."""
        alpha = 0.1
        normalized = max(0.0, min(1.0, (reward + 2.0) / 2.0))
        self.vitalities[g][i] = (1 - alpha) * self.vitalities[g][i] + alpha * normalized

    def forward(self, obs):
        group_actions = []
        for g in range(self.N_GROUPS):
            actions = []
            weights = []
            for i, motif in enumerate(self.groups[g]):
                with torch.no_grad():
                    a = motif(obs)
                actions.append(a)
                weights.append(self.vitalities[g][i])
            # Agrégation pondérée par vitalité
            w_sum = sum(weights)
            if w_sum < 1e-6:
                w_sum = 1.0
            group_action = sum(w * a for w, a in zip(weights, actions)) / w_sum
            group_actions.append(group_action)
        # Agrégation des groupes (poids uniformes ici, extensible)
        final_action = sum(group_actions) / self.N_GROUPS
        return torch.clamp(final_action, -1.0, 1.0)

    def record_reward(self, r):
        for g in range(self.N_GROUPS):
            self.group_rewards[g].append(r)
            for i in range(self.TRIDOMS_PER_GROUP):
                self._update_vitality(g, i, r)

    def vitality_summary(self):
        all_v = [v for grp in self.vitalities for v in grp]
        return np.mean(all_v), np.min(all_v), np.max(all_v)


# ─── Test de démonstration ─────────────────────────────────────────────────────

def run_adaptive_demo():
    """
    Scénario progressif :
    Phase 1 (t=0..149)    : régulation simple          → N1D devrait suffire
    Phase 2 (t=150..299)  : bruit fort                 → promotion possible → N2D
    Phase 3 (t=300..449)  : hystérésis forte           → promotion possible → N3D
    """
    print("\n" + "=" * 70)
    print("DÉMO — Agent adaptatif avec promotion endogène")
    print("=" * 70)

    # Environnement avec changement de mode en cours de route
    agent = AdaptiveTridomAgent(
        eta=5e-3, w_decay=1e-4,
        promotion_window=50,
        promotion_threshold=-1.0,
        start_level=1
    )

    total_reward = 0.0
    phase_rewards = {1: [], 2: [], 3: []}

    env_simple = ThermostatEnv(mode="simple",      noise=0.05, T=150)
    env_noisy  = ThermostatEnv(mode="simple",      noise=0.5,  T=150)
    env_hyst   = ThermostatEnv(mode="hysteresis",  hyst_up=0.9, hyst_down=0.1, T=150)

    for phase, env in enumerate([(1, env_simple), (2, env_noisy), (3, env_hyst)], start=1):
        phase_num, env_obj = phase, env if isinstance(env, ThermostatEnv) else env[1]
        # Correction : env est un tuple (phase_num, env_obj)

    envs = [(1, env_simple), (2, env_noisy), (3, env_hyst)]
    t_global = 0

    for phase_num, env_obj in envs:
        obs = env_obj.reset()
        done = False
        phase_r = 0.0
        mode_label = ["simple", "bruit fort", "hystérésis forte"][phase_num - 1]
        print(f"\n  Phase {phase_num} ({mode_label}) — Niveau actuel : N{agent.level}D")
        while not done:
            action = agent.act(obs)
            obs, r, done = env_obj.step(action.item())
            agent.record_reward(r, t_global)
            phase_r += r
            t_global += 1
        phase_rewards[phase_num] = phase_r
        print(f"  → Récompense phase {phase_num} : {phase_r:.2f} | Niveau final : N{agent.level}D")

    print(f"\n  Log de promotions : {agent.promotion_log if agent.promotion_log else 'aucune'}")
    print(f"  Récompense totale : {sum(phase_rewards.values()):.2f}")
    return agent


def run_tgs_demo():
    """Test rapide du TridomGroupSystem (Nona)."""
    print("\n" + "=" * 70)
    print("DÉMO — TridomGroupSystem (Nona : 9 Tridoms N3D)")
    print("=" * 70)

    tgs = TridomGroupSystem(eta=5e-3, w_decay=1e-4)
    env = ThermostatEnv(mode="hysteresis", hyst_up=0.9, hyst_down=0.1, T=300, noise=0.1)

    obs = env.reset()
    done = False
    total_r = 0.0
    t = 0

    while not done:
        action = tgs.forward(obs)
        obs, r, done = env.step(action.item())
        tgs.record_reward(r)
        total_r += r
        t += 1
        if t % 50 == 0:
            v_mean, v_min, v_max = tgs.vitality_summary()
            print(f"  t={t:4d} | r_cumul={total_r:8.2f} | vitalité moy={v_mean:.3f} "
                  f"min={v_min:.3f} max={v_max:.3f}")

    print(f"\n  Récompense finale TGS (Nona) : {total_r:.2f}")
    v_mean, v_min, v_max = tgs.vitality_summary()
    print(f"  Vitalité finale — moy={v_mean:.3f} | min={v_min:.3f} | max={v_max:.3f}")
    return tgs


if __name__ == "__main__":
    agent = run_adaptive_demo()
    tgs   = run_tgs_demo()

    print("\n" + "=" * 70)
    print("ARCHITECTURE TGS — RÉSUMÉ")
    print("=" * 70)
    print("""
Hiérarchie :
  N1D (lvl 1) : 1 neurone  → régulation simple
  N2D (lvl 2) : 2 neurones → filtrage bruit, mémoire courte
  N3D (lvl 3) : 3 neurones → hystérésis, délais, oscillations
  TGS / Nona  : 9 × N3D   → comportements émergents, robustesse collective

Promotion endogène (AdaptiveTridomAgent) :
  Si mean(reward sur fenêtre) < seuil → niveau += 1
  Pas d'oracle externe. Décision purement interne.

Structure Nona (TridomGroupSystem) :
  3 groupes × 3 Tridoms N3D
  Agrégation pondérée par vitalité (EMA des récompenses)
  Extensible : critère de mort/naissance par groupe

Prochaine étape :
  - Auto-réplication : un groupe qui prospère génère un 4e groupe
  - Mort d'un groupe : vitalité < seuil pendant N fenêtres → suppression
  - Nona² : TGS de TGS (27 Tridoms, niveau 5)
""")
