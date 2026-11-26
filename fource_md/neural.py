import math
from typing import Dict, List, Tuple
from .algebra import (
    Phasor,
    UnifiedCoherenceScore,
    coa_star,
    fuse_group,
    select_min_distortion_branch,
    wrap_phase,
)


class CUCPhaseLayer:
    """Single CUC Neural Layer executing Compose -> Project -> Stabilize per class basin."""

    def __init__(self, n_inputs: int, node_names: List[str], seed_offset: float = 0.0):
        self.n_inputs = n_inputs
        self.node_names = node_names
        self.weights: Dict[str, List[Phasor]] = {
            name: [
                Phasor(0.85, wrap_phase(seed_offset + (idx + 1) * 1.15 + i * 0.65))
                for i in range(n_inputs)
            ]
            for idx, name in enumerate(node_names)
        }

    def forward_node(self, inputs: List[Phasor], name: str) -> Tuple[Phasor, UnifiedCoherenceScore]:
        coupled: List[Phasor] = []
        for z_in, w in zip(inputs, self.weights[name]):
            d_phi = abs(wrap_phase(z_in.phi - w.phi))
            align_weight = math.exp(-1.5 * d_phi)
            proj_amp = coa_star(
                z_in.A * w.A * align_weight,
                0.0,
                lambda a, b: a + b,
                lambda x: max(0.05, min(1.0, x)),
            )
            coupled.append(Phasor(proj_amp, wrap_phase(z_in.phi - w.phi)))

        fused, r_lock = fuse_group(coupled, beta=2.0)
        mean_amp = sum(z.A for z in coupled) / max(len(coupled), 1)
        score = UnifiedCoherenceScore(
            C_K=round(mean_amp, 4),
            C_T=0.98,
            C_phi_group=r_lock,
            ctr_density=max(0.0, 1.0 - r_lock),
        )
        # Emit a complex Phasor carrier for the next downstream layer
        out_carrier = Phasor(score.C_total, fused.phi / max(len(coupled), 1))
        return out_carrier, score

    def forward(self, inputs: List[Phasor]) -> Tuple[List[Phasor], Dict[str, UnifiedCoherenceScore]]:
        out_carriers: List[Phasor] = []
        scores: Dict[str, UnifiedCoherenceScore] = {}
        for name in self.node_names:
            carrier, sc = self.forward_node(inputs, name)
            out_carriers.append(carrier)
            scores[name] = sc
        return out_carriers, scores

    def train_node(self, inputs: List[Phasor], target_name: str, lr: float = 0.25):
        for name in self.node_names:
            sign = 1.0 if name == target_name else -0.35
            updated: List[Phasor] = []
            for z_in, w in zip(inputs, self.weights[name]):
                err = wrap_phase(z_in.phi - w.phi)
                new_phi = wrap_phase(w.phi + lr * sign * math.sin(err))
                new_amp = coa_star(
                    w.A + 0.05 * sign * math.cos(err),
                    0.0,
                    lambda a, b: a + b,
                    lambda x: max(0.2, min(1.0, x)),
                )
                updated.append(Phasor(new_amp, new_phi))
            self.weights[name] = updated


class CUCDeepNetwork:
    """
    Multi-Layer CUC Neural Network:
      - Stacks hidden CUCPhaseLayers into an output CUCPhaseLayer.
      - Tracks additive CS chain distortion E_chain = sum(E_layer) across depth.
    """

    def __init__(self, layer_specs: List[Tuple[int, List[str]]]):
        self.layers = [
            CUCPhaseLayer(n_in, names, seed_offset=idx * 0.9)
            for idx, (n_in, names) in enumerate(layer_specs)
        ]

    def forward(self, inputs: List[Phasor]) -> Tuple[str, float, Dict[str, UnifiedCoherenceScore]]:
        cur_carriers = inputs
        chain_energy = 0.0
        final_scores: Dict[str, UnifiedCoherenceScore] = {}

        for idx, layer in enumerate(self.layers):
            cur_carriers, scores = layer.forward(cur_carriers)
            _, best_layer_sc = select_min_distortion_branch(scores)
            chain_energy += best_layer_sc.E_total
            if idx == len(self.layers) - 1:
                final_scores = scores

        winner, _ = select_min_distortion_branch(final_scores)
        return winner, round(chain_energy, 6), final_scores

    def train_step(self, inputs: List[Phasor], hidden_targets: List[str], output_target: str, lr: float = 0.25):
        cur_carriers = inputs
        for idx, layer in enumerate(self.layers):
            target = hidden_targets[idx] if idx < len(hidden_targets) else output_target
            layer.train_node(cur_carriers, target, lr=lr)
            cur_carriers, _ = layer.forward(cur_carriers)
