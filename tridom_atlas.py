"""
TRIDOM ATLAS — Énumération des 13 classes de topologies triadiques signées
Énumère tous les graphes orientés fortement connexes à 3 nœuds,
avec labelling binaire E/I sur chaque arête.
Classe chaque Tridom par régime dynamique (L2) via simulation ODE.
"""

import itertools
import json
import numpy as np
from scipy.integrate import solve_ivp
from dataclasses import dataclass, asdict
from typing import List, Optional

# ─── Représentation d'un Tridom binaire ────────────────────────────────────────

@dataclass
class TridomBinaire:
    """
    Un Tridom binaire est défini par :
    - edges : liste des arêtes (i→j) présentes
    - signs : dictionnaire (i,j) → +1 (E) ou -1 (I)
    - id    : identifiant canonique (str)
    """
    edges: List[tuple]
    signs: dict
    n_edges: int = 0
    n_excit: int = 0
    n_inhib: int = 0
    id: str = ""
    regime_l2: str = ""           # mono-stable | bi-stable | oscillant | chaos
    description: str = ""
    example_use: str = ""

    def __post_init__(self):
        self.n_edges = len(self.edges)
        self.n_excit = sum(1 for s in self.signs.values() if s == 1)
        self.n_inhib = sum(1 for s in self.signs.values() if s == -1)
        # ID canonique : arêtes triées + signes
        edge_str = ".".join(
            f"{i}{j}{'E' if self.signs[(i,j)]==1 else 'I'}"
            for (i,j) in sorted(self.edges)
        )
        self.id = edge_str


# ─── Génération de tous les graphes fortement connexes à 3 nœuds ──────────────

def is_strongly_connected(edges, n=3):
    """Vérifie la forte connexité par BFS depuis chaque nœud."""
    adj = {i: set() for i in range(n)}
    for (i, j) in edges:
        adj[i].add(j)
    for src in range(n):
        visited = {src}
        queue = [src]
        while queue:
            node = queue.pop()
            for nb in adj[node]:
                if nb not in visited:
                    visited.add(nb)
                    queue.append(nb)
        if len(visited) < n:
            return False
    return True

def has_feedback_cycle(edges):
    """Vérifie la présence d'au moins un cycle (y compris auto-boucles exclues)."""
    adj = {i: set() for i in range(3)}
    for (i, j) in edges:
        if i != j:
            adj[i].add(j)
    # DFS pour détecter un cycle
    color = {i: 0 for i in range(3)}
    def dfs(u):
        color[u] = 1
        for v in adj[u]:
            if color[v] == 1:
                return True
            if color[v] == 0 and dfs(v):
                return True
        color[u] = 2
        return False
    for u in range(3):
        if color[u] == 0 and dfs(u):
            return True
    return False


def enumerate_tridoms_binaires():
    """
    Énumère les graphes fortement connexes à 3 nœuds sans auto-boucles,
    avec labelling E/I sur chaque arête.
    Retourne les classes canoniques (jusqu'à permutation des nœuds).
    """
    nodes = [0, 1, 2]
    possible_edges = [(i, j) for i in nodes for j in nodes if i != j]  # 6 arêtes possibles

    seen_canonical = set()
    tridoms = []

    # Énumère tous les sous-ensembles d'arêtes (2^6 = 64)
    for r in range(1, 7):
        for edge_subset in itertools.combinations(possible_edges, r):
            if not is_strongly_connected(edge_subset):
                continue
            if not has_feedback_cycle(edge_subset):
                continue

            # Pour chaque labelling E/I sur les arêtes
            for signs_tuple in itertools.product([1, -1], repeat=len(edge_subset)):
                signs = {e: s for e, s in zip(edge_subset, signs_tuple)}

                # Forme canonique via permutations des nœuds
                canonical = None
                for perm in itertools.permutations(nodes):
                    perm_edges = tuple(sorted(
                        (perm[i], perm[j]) for (i, j) in edge_subset
                    ))
                    perm_signs = tuple(
                        signs[(i, j)] for (i, j) in
                        sorted(edge_subset, key=lambda e: (perm[e[0]], perm[e[1]]))
                    )
                    candidate = (perm_edges, perm_signs)
                    if canonical is None or candidate < canonical:
                        canonical = candidate

                key = str(canonical)
                if key not in seen_canonical:
                    seen_canonical.add(key)
                    tb = TridomBinaire(
                        edges=list(edge_subset),
                        signs=signs
                    )
                    tridoms.append(tb)

    return tridoms


# ─── Classification dynamique L2 via ODE ──────────────────────────────────────

def classify_regime_ode(tb: TridomBinaire, n_trials=8, T=50.0, dt=0.05) -> str:
    """
    Intègre le système ODE triadique pour plusieurs conditions initiales.
    Classifie le régime dynamique L2.
    """
    def ode(t, x):
        dx = np.zeros(3)
        for (i, j) in tb.edges:
            dx[i] += tb.signs[(i, j)] * x[j]
        # Gain + tanh (non-linéarité standard)
        return np.tanh(1.5 * dx) - 0.5 * x

    regimes = []
    for _ in range(n_trials):
        x0 = np.random.uniform(-1, 1, 3)
        try:
            sol = solve_ivp(ode, [0, T], x0, max_step=dt, dense_output=False)
            x_end = sol.y[:, -100:]  # derniers 100 points
            amplitude = np.max(x_end) - np.min(x_end)
            std_mean = np.mean(np.std(x_end, axis=1))

            if std_mean < 0.02:
                regime = "mono-stable"
            elif amplitude < 0.15:
                # Faible amplitude → point fixe, peut-être bistable
                regime = "mono-stable"
            else:
                # Teste si plusieurs attracteurs (bistabilité)
                # Approximation : variance inter-essais
                regime = "oscillant" if std_mean > 0.1 else "bi-stable"
        except Exception:
            regime = "indéterminé"
        regimes.append(regime)

    # Vote majoritaire
    from collections import Counter
    counts = Counter(regimes)
    dominant = counts.most_common(1)[0][0]

    # Détection chaos : Lyapunov approché
    chaos_score = _lyapunov_approx(ode)
    if chaos_score > 0.05:
        dominant = "chaos"

    return dominant


def _lyapunov_approx(ode_fn, T=30.0, eps=1e-6):
    """Exposant de Lyapunov approximé par perturbation."""
    x0 = np.array([0.3, -0.5, 0.7])
    x0p = x0 + eps * np.random.randn(3)
    try:
        sol  = solve_ivp(ode_fn, [0, T], x0,  max_step=0.05, dense_output=False)
        solp = solve_ivp(ode_fn, [0, T], x0p, max_step=0.05, dense_output=False)
        d_final = np.linalg.norm(sol.y[:, -1] - solp.y[:, -1])
        lyap = np.log(d_final / eps) / T
        return lyap
    except Exception:
        return 0.0


# ─── Descriptions sémantiques ──────────────────────────────────────────────────

REGIME_DESCRIPTIONS = {
    "mono-stable": "Converge vers un unique point fixe. Adapté à la régulation simple.",
    "bi-stable":   "Deux attracteurs stables. Utile pour la mémoire binaire et les décisions.",
    "oscillant":   "Cycle limite stable. Idéal pour les rythmes internes et le timing.",
    "chaos":       "Sensibilité aux conditions initiales. Potentiel pour l'exploration.",
    "indéterminé": "Régime non classifié avec les paramètres standards.",
}

REGIME_USECASE = {
    "mono-stable": "Contrôle, régulation, filtre passe-bas.",
    "bi-stable":   "Mémoire 1 bit, décision binaire, hystérésis.",
    "oscillant":   "Horloge interne, CPG (Central Pattern Generator), rythmes.",
    "chaos":       "Exploration stochastique, diversification, générateur de variabilité.",
    "indéterminé": "À étudier plus finement.",
}


# ─── Programme principal ───────────────────────────────────────────────────────

if __name__ == "__main__":
    np.random.seed(42)

    print("=" * 70)
    print("TRIDOM ATLAS v0.1 — Énumération et classification")
    print("=" * 70)
    print("Génération des topologies fortement connexes à 3 nœuds...")

    tridoms = enumerate_tridoms_binaires()
    print(f"→ {len(tridoms)} classes canoniques trouvées\n")

    # Classification
    print("Classification des régimes dynamiques (ODE + tanh)...")
    classified = []
    for i, tb in enumerate(tridoms):
        regime = classify_regime_ode(tb)
        tb.regime_l2 = regime
        tb.description = REGIME_DESCRIPTIONS.get(regime, "")
        tb.example_use = REGIME_USECASE.get(regime, "")
        classified.append(tb)
        sign_str = "+" * tb.n_excit + "-" * tb.n_inhib
        print(f"  [{i+1:3d}] arcs={tb.n_edges} ({sign_str:6s}) id={tb.id[:30]:30s} → {regime}")

    # Résumé par régime
    from collections import Counter
    regime_counts = Counter(tb.regime_l2 for tb in classified)
    print(f"\n{'='*70}")
    print("RÉSUMÉ PAR RÉGIME")
    print(f"{'='*70}")
    for regime, count in sorted(regime_counts.items(), key=lambda x: -x[1]):
        print(f"  {regime:15s} : {count:4d} topologies")

    # Export JSON (atlas complet)
    atlas = []
    for tb in classified:
        atlas.append({
            "id": tb.id,
            "n_edges": tb.n_edges,
            "n_excit": tb.n_excit,
            "n_inhib": tb.n_inhib,
            "edges": [[i, j] for (i, j) in tb.edges],
            "signs": {f"{i},{j}": s for (i, j), s in tb.signs.items()},
            "regime_l2": tb.regime_l2,
            "description": tb.description,
            "example_use": tb.example_use,
        })

    import os
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tridom_atlas.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"version": "0.1", "n_tridoms": len(atlas), "atlas": atlas}, f,
                  indent=2, ensure_ascii=False)
    print(f"\nAtlas exporté → {out_path}")
    print(f"Total : {len(atlas)} Tridoms binaires classifiés")
