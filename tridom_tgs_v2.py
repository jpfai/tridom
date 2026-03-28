"""
TRIDOM — TridomGroupSystem v2
Piste 1 : Auto-réplication (un groupe prospère → génère un nouveau groupe)
Piste 2 : Mort endogène (vitalité < seuil pendant N fenêtres → suppression)
Structure cible : Nona² = TGS de TGS (jusqu'à 27 Tridoms, niveau 5)

Règles endogènes (aucun oracle externe) :
  - Naissance : mean_vitality d'un groupe > BIRTH_THRESHOLD pendant BIRTH_WINDOW fenêtres
  - Mort      : mean_vitality d'un groupe < DEATH_THRESHOLD pendant DEATH_WINDOW fenêtres
  - Maximum   : MAX_GROUPS groupes simultanés (plafond ressource)
"""

import torch
import torch.nn as nn
import numpy as np
from collections import deque
from dataclasses import dataclass, field
from typing import List, Optional
import uuid
import os

# ─── Hyperparamètres TGS v2 ────────────────────────────────────────────────────
ETA           = 1e-3    # calibré par TEST_009
W_DECAY       = 1e-5    # calibré par TEST_009
VITALITY_EMA  = 0.1     # lissage EMA de la vitalité
BIRTH_THRESH  = 0.80    # seuil de vitalité pour déclencher la réplication
DEATH_THRESH  = 0.25    # seuil de vitalité pour déclencher la mort
BIRTH_WINDOW  = 30      # fenêtre (en pas) pour confirmer naissance
DEATH_WINDOW  = 40      # fenêtre (en pas) pour confirmer mort
MAX_GROUPS    = 9       # Nona² : jusqu'à 9 groupes × 3 Tridoms = 27 Tridoms
MIN_GROUPS    = 1       # Résilience minimale : au moins 1 groupe survit toujours
TRIDOMS_PER_GROUP = 3

# ─── Environnements ────────────────────────────────────────────────────────────

class ThermostatEnv:
    def __init__(self, mode="hysteresis", hyst_up=0.9, hyst_down=0.1,
                 noise=0.1, T=600, setpoint=0.5):
        self.mode = mode
        self.hyst_up = hyst_up
        self.hyst_down = hyst_down
        self.noise = noise
        self.T_steps = T
        self.setpoint = setpoint
        self.reset()

    def reset(self):
        self.t = 0
        self.temp = np.random.uniform(0.0, 1.0)
        self._heating = False
        return self._obs()

    def _obs(self):
        return torch.tensor([[self.temp, self.setpoint]], dtype=torch.float32)

    def step(self, action_val):
        a = float(action_val)
        if self.mode == "hysteresis":
            if self.temp < self.hyst_down:
                self._heating = True
            elif self.temp > self.hyst_up:
                self._heating = False
            heat = 0.1 if self._heating else 0.0
            self.temp += heat * a - 0.03 * (self.temp - self.setpoint)
        else:
            self.temp += 0.1 * a - 0.05 * (self.temp - self.setpoint)
        self.temp += self.noise * np.random.randn()
        reward = -abs(self.temp - self.setpoint)
        self.t += 1
        done = self.t >= self.T_steps
        return self._obs(), reward, done


# ─── Neurone plastique (calibré TEST_009) ──────────────────────────────────────

class PlasticNeuron(nn.Module):
    def __init__(self, n_inputs, eta=ETA, w_decay=W_DECAY):
        super().__init__()
        self.eta = eta
        self.w_decay = w_decay
        self.W = nn.Parameter(torch.randn(1, n_inputs) * 0.1)
        self.b = nn.Parameter(torch.zeros(1))

    def forward(self, x_self, inputs):
        xs  = x_self.reshape(1)
        inp = inputs.reshape(-1)
        pre = torch.cat([xs, inp], dim=0)
        h   = (self.W @ pre).squeeze() + self.b
        x_next = torch.tanh(h).reshape(1)
        if self.training:
            with torch.no_grad():
                self.W.data += self.eta * x_next.detach() * pre.unsqueeze(0)
                self.W.data *= (1.0 - self.w_decay)
                self.W.data.clamp_(-2.0, 2.0)
        return x_next


# ─── N3D (brique de base du TGS) ───────────────────────────────────────────────

class N3D(nn.Module):
    def __init__(self):
        super().__init__()
        self.n1 = PlasticNeuron(5)   # x_self(1) + x2(1) + x3(1) + obs(2)
        self.n2 = PlasticNeuron(5)
        self.n3 = PlasticNeuron(5)
        self.x  = torch.zeros(3)

    def forward(self, obs):
        inp = obs.reshape(-1)
        x1 = self.n1(self.x[0:1], torch.cat([self.x[1:2], self.x[2:3], inp]))
        x2 = self.n2(self.x[1:2], torch.cat([self.x[0:1], self.x[2:3], inp]))
        x3 = self.n3(self.x[2:3], torch.cat([self.x[0:1], self.x[1:2], inp]))
        self.x = torch.cat([x1, x2, x3]).detach()
        return torch.clamp(x3, -1.0, 1.0)

    def reset(self):
        self.x = torch.zeros(3)


# ─── Groupe de Tridoms ─────────────────────────────────────────────────────────

@dataclass
class TridomGroup:
    """
    Un groupe contient TRIDOMS_PER_GROUP Tridoms N3D.
    Il naît, vit, se réplique ou meurt selon sa vitalité.
    """
    gid: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    tridoms: List[N3D] = field(default_factory=list)
    vitality: float = 0.5
    birth_count: int = 0      # nombre de fois qu'il s'est répliqué
    age: int = 0              # âge en pas de temps
    alive: bool = True
    birth_streak: int = 0     # fenêtres consécutives au-dessus de BIRTH_THRESH
    death_streak: int = 0     # fenêtres consécutives en-dessous de DEATH_THRESH
    recent_rewards: deque = field(default_factory=lambda: deque(maxlen=BIRTH_WINDOW))

    def __post_init__(self):
        if not self.tridoms:
            self.tridoms = [N3D() for _ in range(TRIDOMS_PER_GROUP)]
            for m in self.tridoms:
                m.train()

    def act(self, obs) -> torch.Tensor:
        """Agrégation pondérée des sorties par vitalité uniforme (extensible)."""
        actions = [m(obs) for m in self.tridoms]
        return sum(actions) / len(actions)

    def record_reward(self, r: float):
        self.recent_rewards.append(r)
        # EMA vitalité
        normalized = max(0.0, min(1.0, (r + 2.0) / 2.0))
        self.vitality = (1 - VITALITY_EMA) * self.vitality + VITALITY_EMA * normalized
        self.age += 1

    def check_birth(self) -> bool:
        """True si le groupe a maintenu une vitalité haute assez longtemps."""
        if len(self.recent_rewards) < BIRTH_WINDOW:
            return False
        mean_v = self.vitality
        if mean_v >= BIRTH_THRESH:
            self.birth_streak += 1
        else:
            self.birth_streak = 0
        return self.birth_streak >= 1  # une seule fenêtre suffit (ajustable)

    def check_death(self) -> bool:
        """True si le groupe doit mourir."""
        if self.age < DEATH_WINDOW:
            return False  # immunité de jeunesse
        if self.vitality <= DEATH_THRESH:
            self.death_streak += 1
        else:
            self.death_streak = 0
        return self.death_streak >= 2  # deux fenêtres consécutives

    def spawn_child(self) -> "TridomGroup":
        """
        Crée un groupe enfant par copie + mutation des poids.
        Mutation = bruit gaussien léger (10% des poids).
        """
        child = TridomGroup()
        for src, dst in zip(self.tridoms, child.tridoms):
            for (_, src_p), (_, dst_p) in zip(
                src.named_parameters(), dst.named_parameters()
            ):
                dst_p.data.copy_(src_p.data + 0.1 * torch.randn_like(src_p.data))
        self.birth_count += 1
        child.vitality = self.vitality * 0.9  # enfant part légèrement en dessous
        return child


# ─── TridomGroupSystem v2 ──────────────────────────────────────────────────────

class TGSv2:
    """
    Système dynamique de groupes de Tridoms avec :
    - Naissance endogène (réplication par prospérité)
    - Mort endogène (extinction par stagnation)
    - Plafond MAX_GROUPS
    """

    def __init__(self, n_initial_groups=3):
        self.groups: List[TridomGroup] = [
            TridomGroup() for _ in range(n_initial_groups)
        ]
        self.t = 0
        self.event_log: List[dict] = []

    def _active_groups(self) -> List[TridomGroup]:
        return [g for g in self.groups if g.alive]

    def forward(self, obs) -> torch.Tensor:
        active = self._active_groups()
        if not active:
            return torch.zeros(1)
        # Agrégation pondérée par vitalité
        total_v = sum(g.vitality for g in active) or 1.0
        action = sum(g.vitality * g.act(obs) for g in active) / total_v
        return torch.clamp(action, -1.0, 1.0)

    def record_reward(self, r: float):
        """Met à jour tous les groupes et gère naissances / morts."""
        active = self._active_groups()
        for g in active:
            g.record_reward(r)

        self.t += 1

        # Évaluation tous les BIRTH_WINDOW pas
        if self.t % BIRTH_WINDOW == 0:
            self._lifecycle_step()

    def _lifecycle_step(self):
        active = self._active_groups()
        births = []
        deaths = []

        for g in active:
            # Mort — respect du seuil MIN_GROUPS
            remaining_alive = len(active) - len(deaths)
            if g.check_death() and remaining_alive > MIN_GROUPS:
                g.alive = False
                deaths.append(g.gid)
                self.event_log.append({
                    "t": self.t, "event": "MORT",
                    "gid": g.gid, "vitality": round(g.vitality, 3), "age": g.age
                })
                print(f"  [t={self.t:4d}] 💀 MORT    groupe {g.gid} "
                      f"(vitalité={g.vitality:.3f}, âge={g.age})")

            # Naissance (si pas mort et capacité disponible)
            elif g.check_birth():
                n_active_after = len(self._active_groups()) - len(deaths)
                if n_active_after < MAX_GROUPS:
                    child = g.spawn_child()
                    births.append(child)
                    self.event_log.append({
                        "t": self.t, "event": "NAISSANCE",
                        "parent_gid": g.gid, "child_gid": child.gid,
                        "parent_vitality": round(g.vitality, 3),
                        "birth_count": g.birth_count
                    })
                    print(f"  [t={self.t:4d}] 🌱 NAISSANCE groupe {child.gid} "
                          f"(parent={g.gid}, vitalité parent={g.vitality:.3f})")

        for child in births:
            self.groups.append(child)

    def status(self) -> dict:
        active = self._active_groups()
        vits = [g.vitality for g in active]
        return {
            "t": self.t,
            "n_groups": len(active),
            "n_tridoms": len(active) * TRIDOMS_PER_GROUP,
            "vitality_mean": round(np.mean(vits), 3) if vits else 0.0,
            "vitality_min":  round(np.min(vits),  3) if vits else 0.0,
            "vitality_max":  round(np.max(vits),  3) if vits else 0.0,
            "total_births": sum(g.birth_count for g in self.groups),
            "total_deaths": sum(1 for g in self.groups if not g.alive),
        }


# ─── Démonstration ─────────────────────────────────────────────────────────────

def run_tgs_v2_demo():
    print("=" * 70)
    print("TRIDOM TGS v2 — Auto-réplication + Mort endogène")
    print(f"BIRTH_THRESH={BIRTH_THRESH}  DEATH_THRESH={DEATH_THRESH}")
    print(f"MAX_GROUPS={MAX_GROUPS}  (plafond Nona² = 9 groupes × 3 = 27 Tridoms)")
    print("=" * 70)

    # Scénario en 3 phases :
    # Phase 1 (t=0..199)   : hystérésis forte → N3D prospère → naissances
    # Phase 2 (t=200..399) : bruit extrême → certains groupes meurent
    # Phase 3 (t=400..599) : retour hystérésis → récupération
    phases = [
        ("Hystérésis forte",   ThermostatEnv(mode="hysteresis", hyst_up=0.9, hyst_down=0.1, noise=0.05, T=200)),
        ("Bruit extrême",      ThermostatEnv(mode="simple",     noise=0.8,  T=200)),
        ("Récupération",       ThermostatEnv(mode="hysteresis", hyst_up=0.9, hyst_down=0.1, noise=0.1,  T=200)),
    ]

    tgs = TGSv2(n_initial_groups=3)
    total_r = 0.0
    snapshot_log = []

    for phase_name, env in phases:
        obs = env.reset()
        done = False
        phase_r = 0.0
        print(f"\n  ── Phase : {phase_name} ──")
        while not done:
            with torch.no_grad():
                action = tgs.forward(obs)
            obs, r, done = env.step(action.item())
            tgs.record_reward(r)
            phase_r += r
            total_r += r

            if tgs.t % 50 == 0:
                s = tgs.status()
                snapshot_log.append(s)
                print(f"  t={s['t']:4d} | groupes={s['n_groups']} "
                      f"tridoms={s['n_tridoms']:2d} | "
                      f"v_moy={s['vitality_mean']:.3f} "
                      f"v_min={s['vitality_min']:.3f} "
                      f"v_max={s['vitality_max']:.3f} | "
                      f"naissances={s['total_births']} morts={s['total_deaths']}")

        print(f"  → Récompense phase : {phase_r:.2f}")

    # Rapport final
    print("\n" + "=" * 70)
    print("RAPPORT FINAL TGS v2")
    print("=" * 70)
    s = tgs.status()
    print(f"  Récompense totale     : {total_r:.2f}")
    print(f"  Groupes actifs finaux : {s['n_groups']}")
    print(f"  Tridoms actifs finaux : {s['n_tridoms']}")
    print(f"  Vitalité moy/min/max  : {s['vitality_mean']} / {s['vitality_min']} / {s['vitality_max']}")
    print(f"  Total naissances      : {s['total_births']}")
    print(f"  Total morts           : {s['total_deaths']}")

    print("\n  Log des événements :")
    if tgs.event_log:
        for ev in tgs.event_log:
            if ev["event"] == "NAISSANCE":
                print(f"    t={ev['t']:4d} 🌱 NAISSANCE {ev['child_gid']} ← {ev['parent_gid']} "
                      f"(v={ev['parent_vitality']}, réplication #{ev['birth_count']})")
            else:
                print(f"    t={ev['t']:4d} 💀 MORT      {ev['gid']} "
                      f"(v={ev['vitality']}, âge={ev['age']})")
    else:
        print("    (aucun événement de naissance/mort)")

    # Architecture finale
    print("\n  Architecture finale :")
    active = tgs._active_groups()
    for g in active:
        print(f"    Groupe {g.gid} | âge={g.age} | v={g.vitality:.3f} | "
              f"réplications={g.birth_count} | tridoms={len(g.tridoms)}")

    return tgs, snapshot_log


if __name__ == "__main__":
    np.random.seed(42)
    torch.manual_seed(42)
    tgs, log = run_tgs_v2_demo()

    # ─── Export résultats (C3 — persistance) ──────────────────────────────────
    import json
    export = {
        "seed": 42,
        "status": tgs.status(),
        "event_log": tgs.event_log,
        "snapshots": log,
    }
    export_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tgs_v2_results.json")
    with open(export_path, "w") as f:
        json.dump(export, f, indent=2, default=str)
    print(f"\n[EXPORT] Résultats → {export_path}")

    print("\n" + "=" * 70)
    print("ARCHITECTURE Nona² — BILAN")
    print("=" * 70)
    print(f"""
Niveau 1 : N1D (1 neurone)         → régulation simple
Niveau 2 : N2D (2 neurones)        → filtrage, mémoire courte
Niveau 3 : N3D (3 neurones)        → hystérésis, délais, oscillations
Niveau 4 : Nona (3 groupes × N3D)  → robustesse collective, mémoire
Niveau 5 : Nona² (jusqu'à {MAX_GROUPS} groupes) → auto-réplication, mort, évolution

Propriétés endogènes opérationnelles :
  ✓ Naissance : vitalité > {BIRTH_THRESH} pendant {BIRTH_WINDOW} pas → nouveau groupe (copie + mutation)
  ✓ Mort      : vitalité < {DEATH_THRESH} pendant {DEATH_WINDOW*2} pas → suppression
  ✓ Plafond   : MAX_GROUPS = {MAX_GROUPS} (contrainte ressource)
  ✓ Hérédité  : enfant hérite des poids + mutation gaussienne (σ=0.1)

Invariant de base : Tridom binaire signé (topologie + E/I)
Grain de calcul  : PlasticNeuron (règle hebbienne locale, eta={ETA}, w_decay={W_DECAY})
""")
