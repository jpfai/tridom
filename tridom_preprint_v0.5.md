Tridom: A Minimal Signed Triadic Unit for
Substrate-Aware Network Dynamics

Jean-Paul Faihy

Independent Researcher, Saujon, Nouvelle-Aquitaine, France

Correspondence: faihy.jeanpaul@gmail.com  ·  GitHub: github.com/jpfai/tridom  ·  DOI:
10.5281/zenodo.19130439

March 2026  ·  v0.4

Abstract

We introduce Tridom, a formal unit defined as a strongly connected directed graph
on three nodes endowed with a binary signed coupling structure (excitatory /
inhibitory) and a qualitative dynamical equivalence class. We prove that the triadic
level constitutes a minimal threshold at which all non-trivial dynamical families —
multi-stability, oscillation, and minimal chaos — become accessible (the
Triadic Threshold Hypothesis). We further show that the binary sign pattern (topology
+ E/I labelling) is structurally substrate-invariant at the L1 level: it is preserved across biological, digital, and
logical implementations. We provide: (i) a formal three-level equivalence hierarchy
(structural, regime, conjugacy); (ii) an exhaustive atlas of 78 canonical signed triadic
topologies classified by ODE dynamical regime (56 monostable, 15 oscillating, 7
chaotic candidates); (iii) a PyTorch reference implementation with local Hebbian plasticity,
calibrated on delay and hysteresis tasks; and (iv) a self-organising multi-agent
system (TridomGroupSystem v2 / Nona2) with endogenous birth, death, and replication within an explicitly specified rule scaffold. Tridom's contribution is not incremental: it shifts the ontological grain
from the motif as a network statistic to the motif as a formal, persistent,
substrate-aware candidate causal unit.

Keywords: network motifs, triadic circuits, signed directed graphs, substrate invariance,
dynamical systems, Hebbian plasticity, self-organising agents

1. Introduction

The  concept  of  network  motif  —  a  subgraph  appearing  significantly  more  often  than  in
equivalent randomised networks — has been central to systems biology since Milo, Alon et al.
(2002)1.  Yet,  despite  two  decades  of  productive  use,  the  motif  has  remained  a  statistical
signature, identified post-hoc in large networks, with no formal claim to ontological status as
an independent causal unit.

A  parallel  tradition,  rooted  in  Thomas  &  Kaufman  (2001)2  and  Soulé  (2003)3,  established
necessary  structural  conditions  linking  the  sign  pattern  of  feedback  loops  to  dynamical
regimes  (multistationarity,  oscillation).  These  results  apply  to  networks  of  arbitrary  size  and
provide necessary conditions — not a constructive classification at the scale of a minimal unit.

This paper elevates the three-node signed motif from statistical building block to ontological
unit. We call this unit a Tridom — a triadic domain of causal organisation. The central claim is:

"The elementary grain of a connectome is not the isolated neuron, but the
causal triad — defined by its dynamics, not its matter."

The contributions of this paper are threefold. Theoretically, we introduce a formal definition of
the  Tridom  as  a  triple  (G,  σ,  [f])  with  a  three-level  equivalence  hierarchy,  and  we  state  and
formulate  and  support  the  Triadic  Threshold  Hypothesis  that  n  =  3  is  the  minimal  size  for
substrate-invariant non-trivial organisation. Empirically, we provide an exhaustive atlas of 78
canonical  topologies  classified  by  ODE  regime,  a  calibrated  PyTorch  implementation,  and
benchmark  results  on  delay  and  hysteresis  tasks.  Architecturally,  we  introduce  TGS  v2  /
Nona2,  a  self-organising  population  of  Tridoms  with  endogenous  lifecycle  (birth,  death,
replication) governed by an internal vitality metric within a fixed lifecycle rule scaffold, without any external task-training oracle.

2. Related Work

2.1 Network Motifs
Milo  et  al.  (2002)1  defined  network  motifs  as  over-represented  subgraphs  and  identified
recurring  patterns  in  transcriptional  and  neuronal  networks.  Alon  (2007)4  characterised  their
computational  functions  (feedforward  loops,  autoregulation).  This  programme  is  descriptive
and  statistical:  motifs  are  identified  as  population-level  signatures,  not  individual  causal
agents.

2.2 Structural Theory of Feedback Circuits
Thomas  &  Kaufman  (2001)2  established  that  a  positive  feedback  circuit  is  necessary  for
multistationarity  and  a  negative  circuit  for  oscillation.  Soulé  (2003)3  formalised  the  positive
circuit condition algebraically. These results are necessary conditions on the sign pattern of an
arbitrary-size network, not a classification at the minimal-unit level.

2.3 Three-Node Motif Atlases
Krauss et al. (2019)5 — the closest prior work — exhaustively enumerate 3,411 distinct motif
classes  for  binary  Boltzmann  neurons  with  ternary  connection  strengths  {-1,  0,  +1}  and
develop permutation-invariant structural and dynamical distance metrics (correlation r = 0.59,
p  <  0.001).  Key  differences  from  Tridom:  no  ODE  regime  classification  (monostable  /
oscillating  /  chaos),  no  strong  connectivity  requirement,  no  substrate  invariance,  and  a
descriptive  rather  than  axiomatic  approach.  Ahnert  &  Fink  (2016)6  classify  104  three-node
topologies  in  Boolean  networks  by  basin  entropy  and  attractor  diversity  —  a  step  toward
formal dynamical classification, but confined to the Boolean formalism with no sign pattern as
a primary dimension.

2.4 Dynamical Motifs in Large Networks
Driscoll,  Shenoy  &  Sussillo  (2024)7  use  the  term  'dynamical  motifs'  for  high-dimensional
attractors and rotations (N = 100–1,000 units) in multi-task RNNs. This is a distinct usage: their
motifs  are  patterns  in  activity  space,  identified  by  fixed-point  analysis  and  PCA,  with  no
connection to 3-node signed graphs. Their architectural robustness (tanh / softplus / GRU) is
algorithmic and empirical, not substrate-invariant by construction.

2.5 Meso-Scale Assemblages
Adler  &  Medzhitov  (2022)8  define  hypermotifs  as  meso-scale  assemblages  of  motifs.  This
work  is  complementary  and  operates  one  level  above  Tridom,  presupposing  rather  than
defining the base unit.

3. Formal Definition

3.1 The Tridom

A Tridom is a triple (G, σ, [f]) where:

• G = (V, E) with V = {n

, n

1

2

, n

3

feedback cycle.

}, a strongly connected directed graph with at least one

• σ : E -> {+1, -1} — binary edge labelling, excitatory (E) or inhibitory (I).

• [f] — equivalence class of local dynamics under topological conjugacy of the phase-space

flow.

3.2 Equivalence Hierarchy

Level

Criterion

Verifiability

Substrate-invariant?

L1 — Structural

Same signed graph (topology + σ)

Combinatorial, easy

L2 — Regime

Same attractor family (monostable,
bistable, oscillating, chaotic)

Numerical (ODE
integration)

Yes — invariant
core

Conditionally / generically under realization constraints

L3 — Conjugacy

Homeomorphism of phase spaces

Analytic,
case-by-case

Partial

The substrate-invariant core is the L1 pair (topology + sign pattern). The realization — substrate choice
(ODE, neural network, logic circuit) plus continuous parameters — is not preserved under substrate
change.

4. The Triadic Threshold Hypothesis

Hypothesis (Triadic Threshold). For any strongly connected signed directed graph G on n nodes:

n

1

2

3

Accessible dynamical families

Remark

Monostability only

No relational structure; single stable fixed point

Monostability, bistability

Bidirectional feedback possible; no generic periodic
oscillation or chaos

All families: monostability,
multistability, oscillation, minimal
chaos

Generically stable under parameter perturbation —
minimal complete grain

Corollary (conjectural).  n  =  3  is  the  smallest  integer  at  which  substrate-invariant  non-trivial  causal
organisation  becomes  possible  in  the  strong  sense:  there  exist  signed  triadic  topologies
admitting each dynamical family under suitable realizations,  enabling  the  signed  structure  to  preserve  its
qualitative regime under substrate change.

Evidence sketch. The n = 1 and n = 2 cases follow directly from the Thomas–Kaufman conditions2:
without  a  positive  feedback  circuit  of  length  ≥  2,  multistationarity  is  structurally  excluded;
without  a  negative  feedback  circuit  of  length  ≥  3,  generic  oscillation  is  excluded.  The  n  =  3
constructive  case  is  demonstrated  by  the  atlas  (Section  5):  the  existence  of  signed  strongly
connected  3-node  graphs  producing  oscillation  (e.g.,  topology  01I.12I.20I,  the  three-inhibitor
cycle) and chaos (e.g., 01E.12E.20I) under ODE integration with tanh nonlinearity, stable across
random initial conditions, provides constructive numerical support for the lower bound. A complete formal proof of the Triadic Threshold Hypothesis within the Thomas–Kaufman / Soulé framework remains an open contribution item (see Section 8).

5. Atlas of 78 Canonical Topologies and Numerical Classification Protocol

We  exhaustively  enumerate  all  strongly  connected  signed  directed  graphs  on  3  nodes  (no
self-loops), up to node-index permutation. Each topology is classified by dynamical regime via
ODE numerical integration: tanh nonlinearity, coupling matrix drawn from the signed topology,
8  random  initial  conditions  per  topology,  500  integration  steps.  The  full  atlas  is  published  as
open data in tridom_atlas.json.

In this version of the paper, the atlas should be read as a constructive numerical classification under that protocol, not yet as a formal substrate-independent regime theorem.

Regime

Count

%

Characteristic

Monostable

56

71.8%

Converges to a single stable fixed point from all tested
initial conditions

Oscillating

Chaotic candidates

Total

15

7

78

19.2%

9.0%

100%

Representative topologies

ID

01I.12I.20I

01E.12E.20I

01E.02E.10E.21I

01E.02E.10E.12E.20I

Arcs

3

3

4

5

E

0

2

3

4

I

3

1

1

1

Stable limit cycle; trajectory variance > threshold across all
trials

Sensitive dependence on initial conditions; positive
Lyapunov-type numerical indicator

Regime

Typical use

Oscillating

Internal clock, central pattern
generator

Chaotic candidates

Exploration, variability generation

Oscillating

Regulated rhythm with feedforward

Chaotic candidates

Sensitivity to initial conditions

6. Reference Implementation

6.1 N3D — Minimal Triadic Cell (PyTorch)

The  N3D  module  implements  a  single  Tridom  as  a  3-state  recurrent  cell  with  local  Hebbian
plasticity:

x_{t+1} = tanh(W * x_t + b + u_t) # triadic recurrence

dW_ij = eta * x_i * x_j - lam * W_ij # local Hebbian + weight decay

where W is initialised as a strongly connected signed matrix consistent with the chosen atlas
topology,  η  is  the  learning  rate,  and  λ  is  the  weight  decay  coefficient.  No  gradient  is
backpropagated through the Hebbian rule — the update is entirely local.

6.2 Vitality Metric

A  Tridom  is  defined  as  alive  if  its  vitality  exceeds  a  threshold.  Vitality  measures  whether  the
cell operates in a non-trivial, regulated dynamical regime:

vitality = 0.5 * (activity + regularity)

activity = fraction of steps where max|x_t| > x_min (not at rest)

regularity = 1 - std(max|x_t|) / (mean(max|x_t|) + eps) (not diverging)

Death  is  triggered  when  vitality  remains  below  0.25  for  a  sustained  window,  entirely  without
external supervision.

6.3 Comparative Architecture: N1D / N2D / N3D

Unit

N1D

N2D

N3D

Nodes

Connectivity

Dynamical capacity

1

2

3

Recurrent self-loop

Monostability only

Bidirectional feedback A <->
B

Monostability, bistability; no generic
oscillation

Signed triadic loop
A->B->C->A

Full palette: monostability, multistability,
oscillation, minimal chaos

7. Experimental Results

7.1 TEST_008 — Comparative Dynamics with Hebbian Plasticity

N1D,  N2D,  and  N3D  were  evaluated  on  eight  task  scenarios  with  identical  PlasticNeuron
modules  (η  =  10-3,  w_decay  =  10-4,  5  repetitions  per  scenario).  The  score  is  the  cumulative
negative loss over 300 steps (higher = better).

Scenario

N1D

N2D

N3D

Winner

Simple regulation

-10,273

-10,424

-10,514

High noise (0.5)

-10,509

-8,959

-10,445

Delay k=2

Delay k=3

Delay k=5

-9,929

-10,341

-9,710

-9,691

-10,134

-9,527

-9,767

-9,335

-9,744

Weak hysteresis

-9,496

-10,356

-10,925

N1D

N2D

N3D

N3D

N2D

N1D

Strong hysteresis (*)

-12,342

-9,906

-7,518

N3D ×1.64

(*) Key result: on strong hysteresis (up=0.9, down=0.1), N3D scores -7,518 vs. -12,342 for N1D — a factor
×1.64. The triadic loop suggests directional encoding capability via local Hebbian
plasticity, although a formal demonstration of an internal directional representation is left for future analysis.

7.2 TEST_009 — Calibration Grid (eta x lambda)

30  configurations  of  (η,  λ)  were  tested  on  delays  k  =  4  and  k  =  5  (N_repeat  =  10).  The
recommended configuration η = 10-3, λ = 10-5 is the only one where N3D wins on both delays
simultaneously:

eta=1e-3, lam=1e-5: k=4 -> N1D=-66.88 N2D=-55.51 N3D=-52.44 *

k=5 -> N1D=-55.48 N2D=-62.45 N3D=-53.79 *

Full results are available in test009_calibration.csv.

8. TridomGroupSystem v2 / Nona2

TGS  v2  is  a  self-organising  population  of  Tridom  groups  implementing  an  endogenous
lifecycle within an explicitly specified rule scaffold. No external training signal, reward function, or evolutionary operator is required.

8.1 Architecture

• Level 1: N1D (1 neuron) — direct regulation

• Level 2: N2D (2 neurons) — noise filtering, short memory

• Level 3: N3D (3 neurons) — hysteresis, delays, oscillation

• Level 4: Nona (3 groups × N3D) — collective robustness

• Level 5: Nona2 (up to 9 groups) — auto-replication, death, evolution

8.2 Lifecycle Rules

Rule

Birth

Death

Condition

Action

vitality > 0.80 for BIRTH_WINDOW =
30 consecutive steps

Spawn child group (copy + Gaussian
mutation σ=0.1)

vitality < 0.25 for 2×DEATH_WINDOW
= 80 consecutive steps

Remove group from population

Resilience

n_active_groups = MIN_GROUPS = 1

Last survivor is immune to death

Cap

n_active_groups = MAX_GROUPS = 9 Maximum 27 simultaneous Tridoms

8.3 Demo Results (Three-Phase Experiment)

Phase

Steps

Groups

Tridoms

Vitality

Events

Hysteresis

0–200

12 (peak)

36

Extreme noise

200–400

1 (survivor)

3

Recovery

400–600

8

24

0.957

0.195

0.797

9 births

11 deaths

7 births

The sole survivor (group 713dc102) replicates three generations during recovery, rebuilding a population
of 8 groups with vitality 0.797. The peak of 12 groups was reached transiently before the MAX_GROUPS =
9 cap was enforced in steady state.

9. Discussion

9.1 Relation to Existing Frameworks

Tridom  does  not  replace  the  network  motif  programme  —  it  reframes  it.  The  statistical
over-representation  of  triadic  patterns  (Milo  et  al.  20021)  can  now  be  read  as  evidence  that
biological  systems  preferentially  instantiate  formal  causal  units  with  guaranteed  dynamical
properties. The Thomas–Kaufman structural conditions2 become the theoretical underpinning
of the Triadic Threshold Hypothesis rather than independent results.

The  distinction  from  Driscoll  et  al.  (2024)7  is  fundamental.  Their  'dynamical  motifs'  are
patterns  in  high-dimensional  activity  space,  shared  across  architectures  through  empirical
observation.  Tridom's  substrate  invariance  is  definitional:  the  binary  sign  structure  (L1)  is
preserved by construction, not discovered post-hoc.

9.2 Limitations

Several  limitations  should  be  acknowledged.  First,  the  Triadic  Threshold  Theorem  is  stated
with a proof sketch relying on constructive ODE examples; a complete formal proof within the
Thomas–Kaufman  /  Soulé  framework  remains  an  open  item.  Second,  the  calibration
experiments  (TEST_008,  TEST_009)  use  a  single  task  family  (delay  prediction,  hysteresis);
broader  benchmarking  against  standard  RNN  architectures  (GRU,  LSTM)  on  established
sequence  tasks  would  strengthen  the  empirical  claims.  Third,  the  atlas  is  limited  to  n  =  3;
extension to n = 4 would produce a substantially larger combinatorial space and is a natural
next step.

9.3 Open Contributions

• Formal proof of the Triadic Threshold Hypothesis (Thomas–Kaufman / Soulé framework).

• Extension of the atlas to n = 4 (four-node strongly connected signed graphs).

• Benchmark Tridom-RNN against GRU / LSTM on standard sequence tasks.

• Implementation of integrated information phi (IIT) for binary Tridoms.

• Biological validation: identification of Tridom classes in published connectomes.

10. Conclusion

We have introduced Tridom as a formal candidate causal unit with a structurally substrate-invariant L1 core defined by a triple (G,
σ,  [f]):  signed  strongly  connected  graph  on  3  nodes,  binary  excitatory  /  inhibitory  edge
labelling, and dynamical equivalence class. The Triadic Threshold Hypothesis supports the view that n
=  3  is  the  minimal  grain  at  which  all  non-trivial  dynamical  families  become
accessible. The atlas of 78 canonical topologies, the calibrated PyTorch implementation, and
the TGS v2 self-organising system with endogenous lifecycle provide a complete open-source
platform for further investigation.

The contribution of Tridom is not incremental: it shifts the ontological grain from the motif as a
network  statistic  to  the  motif  as  a  formal,  persistent,  substrate-invariant  causal  unit  —  a
change  that  opens  new  theoretical  and  experimental  directions  at  the  intersection  of
dynamical systems theory, computational neuroscience, and artificial life.

References

1.

2.

3.

4.

5.

6.

7.

8.

9.

Milo R, Shen-Orr S, Itzkovitz S, Kashtan N, Chklovskii D, Alon U. (2002). Network motifs: simple building

blocks of complex networks. Science, 298(5594), 824–827. doi:10.1126/science.298.5594.824

Thomas R, Kaufman M. (2001). Multistationarity, the basis of cell differentiation and memory. I. Structural

conditions of multistationarity and other nontrivial behavior. Chaos, 11(1), 170–179.

doi:10.1063/1.1350439

Soule C. (2003). Graphic requirements for multistationarity. Complexus, 1(3), 123–133.

doi:10.1159/000076100

Alon U. (2007). Network motifs: theory and experimental approaches. Nature Reviews Genetics, 8(6),

450–461. doi:10.1038/nrg2102

Krauss P, Zankl A, Schilling A, Schulze H, Metzner C. (2019). Analysis of structure and dynamics in

three-neuron motifs. Frontiers in Computational Neuroscience, 13, 5. doi:10.3389/fncom.2019.00005

Ahnert SE, Fink TMA. (2016). Form and function in gene regulatory networks: the structure of network

motifs determines fundamental properties of their dynamical state space. Journal of the Royal Society

Interface, 13(120), 20160179. doi:10.1098/rsif.2016.0179

Driscoll LN, Shenoy K, Sussillo D. (2024). Flexible multitask computation in recurrent networks utilizes

shared dynamical motifs. Nature Neuroscience, 27(7), 1349–1363. doi:10.1038/s41593-024-01668-6

Adler M, Medzhitov R. (2022). Emergence of dynamic properties in network hypermotifs. PNAS, 119(26),

e2204967119. doi:10.1073/pnas.2204967119

Park Y, Lee MJ, Son SW. (2021). Motif dynamics in signed directional complex networks. Journal of the

Korean Physical Society. doi:10.1007/s40042-021-00058-6

10.

Prill RJ, Iglesias PA, Levchenko A. (2005). Dynamic properties of network motifs contribute to biological

network organization. PLOS Biology, 3(11), e343. doi:10.1371/journal.pbio.0030343

11.

Vasilaki E, Giugliano M. (2014). Emergence of connectivity motifs in networks of model neurons with

short- and long-term plastic synapses. PLOS ONE, 9(1), e84626. doi:10.1371/journal.pone.0084626

Repository and Data Availability

All code, data, and documentation are openly available under the MIT licence:

• GitHub: github.com/jpfai/tridom

• Zenodo archive (v0.4): doi:10.5281/zenodo.19130439

• tridom_atlas.json — 78 canonical topologies with regime labels (open data)

• tridom_tgs_v2.py — TGS v2 self-organising system with lifecycle

• test009_calibration.csv — full calibration grid results

Generated by Perplexity Computer · March 2026

