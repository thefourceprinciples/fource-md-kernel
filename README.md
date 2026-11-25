# fource-md-kernel

**Deterministic Python 3 Verification DAG & Coherence-Under-Constraint (CUC) Kernel for Modern Machine Design (`CIF-MD-000`)**

`fource-md-kernel` transforms the 18-chapter *Modern Machine Design Reference* (reconstructing Deutschman, Michels, and Wilson's *Machine Design: Theory and Practice* under modern ASME, ISO, AGMA, VDI, and AWS codes) into an executable, zero-regression engineering verification suite.

Instead of evaluating mechanical components in isolation, every chapter acts as a deterministic **Delta Node (`Δ01`–`Δ18`)** inside a **Directed Acyclic Graph (DAG)**. Modifying any upstream parameter automatically hashes and invalidates coupled downstream subsystems so no design change ships without full boundary re-verification.

---

## Core Governing Laws

Every mechanical subsystem evaluated by the kernel must satisfy two foundational invariants before design release:

1. **Multiplicative Coherence Law:**
   \[C = O \times E \times H \times X\]
   * **Origin Integrity (O):** Manufacturing cleanliness, material batch fidelity, and absence of initial flaws.
   * **Expression Fidelity (E):** Kinematic alignment, stiffness bounds, and geometric fit under operating load.
   * **Historical Continuity (H):** Resistance to cumulative fatigue, wear, creep, and preload relaxation.
   * **Resonance Stability (X):** Separation from critical speeds, buckling bifurcations, surge, and peel instabilities.

2. **Persistence Margin Invariant:**
   \[\text{Persistence Margin} = (C \cdot K_{\text{compat}}) - \lambda > 0\]
   System coherence scaled by physical/code compliance (\(K_{\text{compat}}\)) must strictly exceed normalized complexity and manufacturing constraint cost (λ).

---

## Repository Structure

```text
fource-md-kernel/
├── pyproject.toml                # Zero-dependency standard-library Python package config
├── README.md                     # Architecture overview & quickstart
├── LICENSE                       # Apache License 2.0
├── .gitignore                    # Python & local audit exclusions
├── fource_md/
│   ├── __init__.py
│   ├── ledger.py                 # DeltaFragment dataclass, C = O*E*H*X scorer & SHA-256 hasher
│   ├── graph.py                  # CIF-MD-000 DAG dependency & stale-invalidation engine
│   └── deltas/                   # Chapter verification nodes (Δ01–Δ18)
│       ├── __init__.py
│       ├── delta_03_materials.py # Marin endurance limit & yield envelope
│       ├── delta_07_shafts.py    # Goodman–von Mises shaft diameter & bearing slope
│       ├── delta_09_bearings.py  # ISO 281 modified bearing rating life (L_nm)
│       ├── delta_11_gears.py     # Helical 3D gear forces (Wt, Wr, Wa)
│       ├── delta_16_bolts.py     # VDI 2230 housing bolt separation & fatigue
│       └── delta_18_axisym.py    # Shrink-fit hub contact pressure & slip torque
└── examples/
    └── helical_gearbox_audit.py  # Coupled multi-chapter audit & perturbation cascade
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

### 2. Run the Coupled Gearbox Audit
```bash
python examples/helical_gearbox_audit.py
```

This runs an initial verification across `Δ03 → Δ11 → Δ07 → Δ18 → Δ09 → Δ16`, perturbs the helical gear angle $\psi$, invalidates all downstream coupled fragments via SHA-256 state hashes, and flags any Tier-1 constraint violations.

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
