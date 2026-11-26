import math
from typing import List, Tuple
from fource_md.algebra import (
    Phasor,
    UnifiedCoherenceScore,
    coa_star,
    fuse_group,
    kuramoto_order,
    wrap_phase,
)


def kuramoto_coa_step(
    carriers: List[Phasor],
    kappa: float = 0.35,
    amp_bounds: Tuple[float, float] = (0.1, 1.0),
) -> Tuple[List[Phasor], UnifiedCoherenceScore]:
    """
    One step of a CUC Phase-Locked Layer:
      1. Compose: compute group Kuramoto order parameter (r, psi)
      2. Constrain: project amplitudes onto feasible box K = [amp_min, amp_max]
      3. Stabilize: step phases toward mean attractor psi via dphi = -kappa * sin(phi_i - psi)
    """
    r, psi = kuramoto_order([z.phi for z in carriers])
    lo, hi = amp_bounds

    updated: List[Phasor] = []
    for z in carriers:
        # COA projection on amplitude + Kuramoto phase-lock update
        a_proj = coa_star(z.A, 0.0, lambda a, b: a + b, lambda x: max(lo, min(hi, x)))
        phi_next = wrap_phase(z.phi - kappa * math.sin(z.phi - psi))
        updated.append(Phasor(a_proj, phi_next))

    _, r_after = fuse_group(updated, beta=2.0)
    score = UnifiedCoherenceScore(
        C_K=1.0,
        C_T=0.98,
        C_phi_group=r_after,
        ctr_density=max(0.0, 1.0 - r_after),
    )
    return updated, score


def run_phase_lock_simulation(steps: int = 12) -> UnifiedCoherenceScore:
    # Start with 5 scattered oscillators / feature channels (exceeding upper amp bound 1.0)
    carriers = [
        Phasor(1.4, -1.8),
        Phasor(0.9, -0.5),
        Phasor(1.2, 0.4),
        Phasor(0.8, 1.6),
        Phasor(1.5, 2.3),
    ]

    r0, _ = kuramoto_order([z.phi for z in carriers])
    print(f"Initial Scattered State | Kuramoto r = {r0:.4f}")

    score = None
    for step in range(1, steps + 1):
        carriers, score = kuramoto_coa_step(carriers, kappa=0.45)
        print(
            f"Step {step:02d} | r_lock = {score.C_phi_group:.4f} | "
            f"C_total = {score.C_total:.4f} | Distortion E_total = {score.E_total:.4f}"
        )

    return score


if __name__ == "__main__":
    final_score = run_phase_lock_simulation(steps=12)
    assert final_score is not None and final_score.C_phi_group > 0.99, "Failed to reach phase-lock basin"
    print("\nSUCCESS: Layer settled into phase-locked low-distortion basin.")
