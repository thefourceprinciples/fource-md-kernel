import math
from typing import Dict, List, Tuple
from fource_md.algebra import (
    Phasor,
    UnifiedCoherenceScore,
    coa_star,
    fuse_group,
    select_min_distortion_branch,
    wrap_phase,
)


class CUCPhaseLayer:
    """
    A multi-basin CUC Neural Layer:
      - Each output class c holds a vector of learned phase-coupling weights W[c][i].
      - Forward pass executes: Compose (z_i * W_ci) -> Constrain (PI_K) -> Stabilize (Kuramoto lock).
      - Prediction uses CS min-plus selection: c* = argmin_c E_total(c).
    """

    def __init__(self, n_inputs: int, class_names: List[str]):
        self.n_inputs = n_inputs
        self.class_names = class_names
        # Initialize deterministic offset phases per class so basins start separated
        self.weights: Dict[str, List[Phasor]] = {
            cname: [
                Phasor(0.85, wrap_phase((idx + 1) * 1.1 + i * 0.7))
                for i in range(n_inputs)
            ]
            for idx, cname in enumerate(class_names)
        }

    def forward_class(self, inputs: List[Phasor], cname: str) -> UnifiedCoherenceScore:
        coupled: List[Phasor] = []
        for z_in, w in zip(inputs, self.weights[cname]):
            # Compose: phase alignment difference determines coupling strength
            d_phi = abs(wrap_phase(z_in.phi - w.phi))
            align_weight = math.exp(-1.5 * d_phi)
            raw_amp = z_in.A * w.A * align_weight
            # Constrain (PI_K): clamp amplitude into feasible energy envelope
            proj_amp = coa_star(raw_amp, 0.0, lambda a, b: a + b, lambda x: max(0.05, min(1.0, x)))
            coupled.append(Phasor(proj_amp, wrap_phase(z_in.phi - w.phi)))

        # Stabilize: evaluate group phase lock r across all coupled channels
        _, r_lock = fuse_group(coupled, beta=2.0)
        mean_amp = sum(z.A for z in coupled) / len(coupled)
        return UnifiedCoherenceScore(
            C_K=round(mean_amp, 4),
            C_T=0.98,
            C_phi_group=r_lock,
            ctr_density=max(0.0, 1.0 - r_lock),
        )

    def predict(self, inputs: List[Phasor]) -> Tuple[str, Dict[str, UnifiedCoherenceScore]]:
        scores = {cname: self.forward_class(inputs, cname) for cname in self.class_names}
        winner, _ = select_min_distortion_branch(scores)
        return winner, scores

    def train_step(self, inputs: List[Phasor], target_class: str, lr: float = 0.25):
        """Phase-locking Hebbian update: pull target basin into phase lock, repel non-targets."""
        for cname in self.class_names:
            sign = 1.0 if cname == target_class else -0.35
            updated_w: List[Phasor] = []
            for z_in, w in zip(inputs, self.weights[cname]):
                err = wrap_phase(z_in.phi - w.phi)
                new_phi = wrap_phase(w.phi + lr * sign * math.sin(err))
                new_amp = coa_star(
                    w.A + 0.05 * sign * math.cos(err),
                    0.0,
                    lambda a, b: a + b,
                    lambda x: max(0.2, min(1.0, x)),
                )
                updated_w.append(Phasor(new_amp, new_phi))
            self.weights[cname] = updated_w


def run_cuc_neural_training() -> float:
    # 3 distinct signal regimes encoded as 4-channel Phasor patterns
    dataset = [
        ("Regime_Alpha", [Phasor(0.9, 0.10), Phasor(0.9, 0.20), Phasor(0.8, 0.15), Phasor(0.9, 0.05)]),
        ("Regime_Beta",  [Phasor(0.9, 2.10), Phasor(0.8, 2.30), Phasor(0.9, 1.95), Phasor(0.8, 2.20)]),
        ("Regime_Gamma", [Phasor(0.9, -1.80), Phasor(0.9, -1.60), Phasor(0.8, -1.90), Phasor(0.9, -1.70)]),
    ]

    net = CUCPhaseLayer(n_inputs=4, class_names=["Regime_Alpha", "Regime_Beta", "Regime_Gamma"])

    for epoch in range(1, 16):
        total_target_energy = 0.0
        for label, sample in dataset:
            net.train_step(sample, label, lr=0.30)
            _, scores = net.predict(sample)
            total_target_energy += scores[label].E_total
        if epoch in (1, 5, 10, 15):
            print(f"Epoch {epoch:02d} | Mean Target Distortion Energy E* = {total_target_energy / len(dataset):.4f}")

    # Evaluate final classification accuracy & distortion separation
    correct = 0
    print("\nFinal Basin Classification:")
    for label, sample in dataset:
        pred, scores = net.predict(sample)
        if pred == label:
            correct += 1
        print(f"  True: {label:12s} -> Pred: {pred:12s} | Target E={scores[label].E_total:.4f}")

    acc = correct / len(dataset)
    print(f"\nAccuracy: {acc * 100:.1f}%")
    return acc


if __name__ == "__main__":
    accuracy = run_cuc_neural_training()
    assert accuracy == 1.0, f"Expected 100% classification accuracy, got {accuracy * 100:.1f}%"
    print("SUCCESS: CUC Neural Network trained via distortion-energy minimization.")
