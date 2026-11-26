import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple
from .algebra import (
    Phasor,
    UnifiedCoherenceScore,
    branch_contradictions,
    coa_star,
    fuse_group,
    kuramoto_order,
    select_min_distortion_branch,
    wrap_phase,
)


@dataclass
class CUCInstruction:
    opcode: str                    # LOAD, COMPOSE, PROJECT, BRANCH, STABILIZE, SELECT, HALT
    args: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CUCMachineState:
    basins: Dict[str, List[Phasor]] = field(default_factory=dict)
    scores: Dict[str, UnifiedCoherenceScore] = field(default_factory=dict)
    selected_basin: str | None = None
    halted: bool = False
    trace: List[str] = field(default_factory=list)


class CUCVirtualMachine:
    """
    Native Fource/CUC Computer Runtime.
    Executes Compose -> Project -> Branch -> Stabilize -> Select over Phasor registers.
    """

    def __init__(self):
        self.state = CUCMachineState()

    def step(self, instr: CUCInstruction):
        if self.state.halted:
            return
        op = instr.opcode.upper()
        args = instr.args

        if op == "LOAD":
            # Load initial carrier stream into primary basin H0
            carriers: List[Phasor] = args["carriers"]
            self.state.basins = {"H0": list(carriers)}
            self.state.trace.append(f"LOAD: {len(carriers)} carriers -> H0")

        elif op == "COMPOSE":
            # Couple incoming operator phasor across every active basin
            op_phasor: Phasor = args["phasor"]
            beta: float = args.get("beta", 1.5)
            for bname, plist in self.state.basins.items():
                self.state.basins[bname] = [
                    p.streaming_couple(op_phasor, beta=beta) for p in plist
                ]
            self.state.trace.append(f"COMPOSE: coupled {op_phasor} across {list(self.state.basins.keys())}")

        elif op == "PROJECT":
            # COA constraint projection PI_K onto amplitude bounds [lo, hi]
            lo, hi = args.get("bounds", (0.1, 1.0))
            for bname, plist in self.state.basins.items():
                self.state.basins[bname] = [
                    Phasor(
                        coa_star(p.A, 0.0, lambda a, b: a + b, lambda x: max(lo, min(hi, x))),
                        p.phi,
                    )
                    for p in plist
                ]
            self.state.trace.append(f"PROJECT: clamped amplitudes into [{lo}, {hi}]")

        elif op == "BRANCH":
            # Partition contradictory carriers into isolated hypothesis basins
            theta_ctr: float = args.get("theta_ctr", 0.35)
            new_basins: Dict[str, List[Phasor]] = {}
            idx = 1
            for plist in self.state.basins.values():
                clusters = branch_contradictions(
                    plist,
                    lambda a, b: abs(wrap_phase(a.phi - b.phi)) / math.pi,
                    theta_ctr=theta_ctr,
                )
                for c in clusters:
                    new_basins[f"H{idx}"] = c
                    idx += 1
            self.state.basins = new_basins
            self.state.trace.append(f"BRANCH: split into {len(new_basins)} basins {list(new_basins.keys())}")

        elif op == "STABILIZE":
            # Settle each basin via Kuramoto phase-locking & evaluate UnifiedCoherenceScore
            steps: int = args.get("steps", 10)
            kappa: float = args.get("kappa", 0.45)
            self.state.scores.clear()
            for bname, plist in self.state.basins.items():
                cur = list(plist)
                for _ in range(steps):
                    _, psi = kuramoto_order([p.phi for p in cur])
                    cur = [
                        Phasor(p.A, wrap_phase(p.phi - kappa * math.sin(p.phi - psi)))
                        for p in cur
                    ]
                self.state.basins[bname] = cur
                _, r_lock = fuse_group(cur, beta=2.0)
                mean_amp = sum(p.A for p in cur) / max(len(cur), 1)
                self.state.scores[bname] = UnifiedCoherenceScore(
                    C_K=round(mean_amp, 4),
                    C_T=0.98,
                    C_phi_group=r_lock,
                    ctr_density=max(0.0, 1.0 - r_lock),
                )
            self.state.trace.append(f"STABILIZE: settled {len(self.state.basins)} basins over {steps} steps")

        elif op == "SELECT":
            # CS min-plus selection: k* = argmin E_total
            winner, best = select_min_distortion_branch(self.state.scores)
            self.state.selected_basin = winner
            self.state.trace.append(f"SELECT: winner={winner} (E*={best.E_total:.4f}, C*={best.C_total:.4f})")

        elif op == "HALT":
            self.state.halted = True
            self.state.trace.append("HALT: execution complete")

        else:
            raise ValueError(f"Unknown CUC opcode: {op}")

    def run(self, program: List[CUCInstruction]) -> CUCMachineState:
        for instr in program:
            self.step(instr)
            if self.state.halted:
                break
        return self.state
