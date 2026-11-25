# fource-md-kernel

**Deterministic Python 3 Verification DAG & Coherence-Under-Constraint (CUC) Kernel for Modern Machine Design (`CIF-MD-000`)**

`fource-md-kernel` transforms the 18-chapter *Modern Machine Design Reference* (reconstructing Deutschman, Michels, and Wilson's *Machine Design: Theory and Practice* under modern ASME, ISO, AGMA, VDI, and AWS codes) into an executable, zero-regression engineering verification suite powered by **Fource Algebra (PFA, CS, and COA)**.

Instead of evaluating mechanical components in isolation, every chapter acts as a deterministic **Delta Node (`Δ01`–`Δ18`)** inside a **Directed Acyclic Graph (DAG)**. Modifying any upstream parameter automatically hashes and invalidates coupled downstream subsystems so no design change ships without full boundary re-verification.

---

## Core Governing Laws (Fource Algebra Stack)

Every mechanical subsystem evaluated by the kernel is governed by three coupled algebraic layers:

1. **PFA (Phase / Fource Algebra — Order-Invariant Group Lock):**
   \[R_{\text{complex}} = \frac{1}{n} \sum_{k=1}^n e^{i\phi_k}, \qquad r = \vert{}R_{\text{complex}}\vert{} \in [0, 1]\]
   Multi-stage shafts, gear meshes, and rotary carriers fuse via the Kuramoto order parameter r, ensuring phase-alignment coherence is independent of evaluation order.

2. **CS (Coherence Semiring — Min-Plus Distortion Energy):**
   \[C_{\text{total}} = C_K^a \cdot C_T^b \cdot C_{\phi,\text{group}}^c \cdot C_{\text{ctr}}^d, \qquad E_{\text{total}} = -\ln(C_{\text{total}} + \epsilon)\]
   Coherence multiplies across coupled components while distortion energy \(E_{\text{total}}\) adds along dependency chains—allowing incompatible design requirements to branch into separate hypothesis basins (`branch_contradictions`) and select the minimum-distortion architecture (\(k^* = \arg\min_k E_{\text{total},k}\)).

3. **COA (CUC Operator Algebra — Compose → Project → Stabilize):**
   \[x \star_K y = R\bigl(\Pi_K(x \otimes y)\bigr)\]
   Every operation couples states, repairs violations onto feasible engineering constraints (\(\Pi_K\)), and settles into a verified equilibrium basin (R).

---

## Repository Structure

```text
fource-md-kernel/
├── pyproject.toml                   # Zero-dependency standard-library Python package config
├── README.md                        # Architecture overview, Fource Algebra laws & quickstart
├── LICENSE                          # Apache License 2.0
├── .gitignore                       # Python & local audit exclusions
├── .github/
│   └── workflows/
│       └── ci.yml                   # Automated Python 3.10–3.12 verification workflow
├── fource_md/
│   ├── __init__.py                  # Top-level exports (Phasor, DeltaFragment, CUCVerificationGraph)
│   ├── algebra.py                   # PFA Kuramoto fusion, CS distortion E_total, COA & branching
│   ├── ledger.py                    # Unified DeltaFragment with UnifiedCoherenceScore & SHA-256 hash
│   ├── graph.py                     # CIF-MD-000 DAG solver, invalidation & multi-branch evaluator
│   └── deltas/                      # All 18 Chapter Verification Nodes (Δ01–Δ18)
│       ├── __init__.py
│       ├── part1_foundations.py     # Δ01–Δ06: Reliability, Materials, Marin Se, Tolerances, Buckling, Fatigue
│       ├── part2_rotary.py          # Δ07–Δ12: Shafts, Journal/Rolling Bearings, Spur/Helical/Worm Gears, Belts
│       └── part3_joints_axisym.py   # Δ13–Δ18: Brakes/Clutches, Springs, Power Screws, Bolts, Welds, Axisymmetric
└── tests/
    └── test_fource_algebra.py       # Unit & DAG cascade verification tests across all 18 chapters
```

---

## Quickstart

### 1. Clone & Install Locally (Editable Mode)
```bash
git clone https://github.com
cd fource-md-kernel
pip install -e .
```
*(Note: `fource-md-kernel` uses only the Python 3.10+ standard library and requires zero third-party dependencies.)*

### 2. Run the Full Verification Suite
```bash
python -m unittest discover -s tests -v
```

---

## Canonical Registry (`CIF-MD-000`)

| Delta | Document ID | Module Domain | Primary Standards |
| :--- | :--- | :--- | :--- |
| `Δ01` | `CH01-MD-001` | Design Methodology & Reliability | ASME Y14.5, Hasofer–Lind $\beta$ |
| `Δ02` | `CH02-MD-002` | Materials & Process Anisotropy | Ashby Indices, ASTM / SAE |
| `Δ03` | `CH03-MD-003` | Mechanical Properties & Fatigue | ASTM E8 / E23 / E466, Marin $S_e$ |
| `Δ04` | `CH04-MD-004` | Manufacturing & Tolerance Stack-Ups | ASME Y14.5, ISO 286, RSS / $C_{pk}$ |
| `Δ05` | `CH05-MD-005` | Stress, Strain & Buckling Analysis | Castigliano, Pilkey $K_t$, Hertz |
| `Δ06` | `CH06-MD-006` | Failure Theories & Fracture Mechanics | von Mises, Goodman, Miner, ASTM E399 |
| `Δ07` | `CH07-MD-007` | Shafts, Keys, Couplings & U-Joints | DIN 743, Rayleigh–Ritz, ISO 1940-1 |
| `Δ08` | `CH08-MD-008` | Journal Bearings & Lubrication | Reynolds Wedge, Sommerfeld, ISO 7902 |
| `Δ09` | `CH09-MD-009` | Rolling Contact Bearings | ISO 281 ($L_{nm}$), ISO 4406 EHL |
| `Δ10` | `CH10-MD-010` | Spur Gears & Involute Kinematics | ANSI/AGMA 2001-D04, ISO 6336 |
| `Δ11` | `CH11-MD-011` | Helical, Bevel & Worm Gears | AGMA 2001 / 2003 / 6034 |
| `Δ12` | `CH12-MD-012` | Belt & Chain Drives | RMA IP-20, ISO 5296, ASME B29.1 |
| `Δ13` | `CH13-MD-013` | Brakes, Clutches & Friction | SAE J661, ISO 13849-1 (SAHR) |
| `Δ14` | `CH14-MD-014` | Mechanical Springs | EN 13906, Wahl $K_w$, Zimmerli |
| `Δ15` | `CH15-MD-015` | Power Screws & Linear Actuation | ASME B1.5, ISO 2901 / 3408 |
| `Δ16` | `CH16-MD-016` | Threaded Fasteners & Preload | VDI 2230-1, ISO 898-1, DIN 25201 |
| `Δ17` | `CH17-MD-017` | Welded & Adhesive Joints | AWS D1.1, IIW FAT, ASTM D1002 |
| `Δ18` | `CH18-MD-018` | Axisymmetric Cylinders & Rotors | ASME BPVC VIII Div 3, DIN 7190 |

---

## License

Licensed under the **Apache License, Version 2.0**. See `LICENSE` for details.
