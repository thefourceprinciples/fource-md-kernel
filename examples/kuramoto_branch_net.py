import math
from typing import Dict, List, Tuple
from fource_md.algebra import (
    Phasor,
    UnifiedCoherenceScore,
    branch_contradictions,
    coa_star,
    fuse_group,
    kuramoto_order,
    select_min_distortion_branch,
    wrap_phase,
)


def phase_contradiction(z1: Phasor, z2: Phasor) -> float:
    """Normalized phase disagreement in [0, 1] based on wrapped phase delta."""
    return abs(wrap_phase(z1.phi - z2.phi)) / math.pi


def stabilize_basin(
    carriers: List[Phasor], steps: int = 10, kappa: float = 0.45
) -> Tuple[List[Phasor], UnifiedCoherenceScore]:
    """Run COA projection + Kuramoto phase-locking inside an isolated hypothesis basin."""
    state = list(carriers)
    for _ in range(steps):
        _, psi = kuramoto_order([z.phi for z in state])
        state = [
            Phasor(
                coa_star(z.A, 0.0, lambda a, b: a + b, lambda x: max(0.1, min(1.0, x))),
                wrap_phase(z.phi - kappa * math.sin(z.phi - psi)),
            )
            for z in state
        ]

    _, r_final = fuse_group(state, beta=2.0)
    mean_amp = sum(z.A for z in state) / len(state)
    score = UnifiedCoherenceScore(
        C_K=round(mean_amp, 4),
        C_T=0.98,
        C_phi_group=r_final,
        ctr_density=max(0.0, 1.0 - r_final),
    )
    return state, score


def run_multi_basin_demo() -> str:
    # Mixed input stream containing two contradictory signal basins
    mixed_stream = [
        Phasor(0.95, 0.10),
        Phasor(0.92, 0.25),
        Phasor(0.96, 0.18),
        Phasor(0.65, -2.50),
        Phasor(0.60, -2.15),
    ]

    # 1. Branch contradictions instead of averaging into mush
    basins = branch_contradictions(mixed_stream, phase_contradiction, theta_ctr=0.35)
    print(f"Split {len(mixed_stream)} carriers into {len(basins)} non-contradictory basins:\n")

    # 2. Stabilize each basin independently & score with UnifiedCoherenceScore
    basin_scores: Dict[str, UnifiedCoherenceScore] = {}
    for idx, cluster in enumerate(basins, start=1):
        name = f"Basin_H{idx}"
        _, score = stabilize_basin(cluster, steps=10)
        basin_scores[name] = score
        print(
            f"  {name} (n={len(cluster)}) | r_lock={score.C_phi_group:.4f} | "
            f"C_total={score.C_total:.4f} | E_total={score.E_total:.4f}"
        )

    # 3. CS Min-Plus Selection picks the lowest-distortion basin
    winner, best_score = select_min_distortion_branch(basin_scores)
    print(f"\nCS Selected Winner: {winner} (Min Distortion E* = {best_score.E_total:.4f})")
    return winner


if __name__ == "__main__":
    selected = run_multi_basin_demo()
    assert selected == "Basin_H1", f"Expected Basin_H1 to win, got {selected}"
    print("SUCCESS: Contradictory basins isolated and optimal attractor selected.")
