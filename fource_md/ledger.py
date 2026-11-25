from dataclasses import dataclass, field
from typing import Any, Dict, List
import hashlib
import json
from .algebra import Phasor, UnifiedCoherenceScore, fuse_group


@dataclass
class DeltaFragment:
    delta_id: str
    doc_id: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    C_K: float                                       # Constraint feasibility coherence [0, 1]
    C_T: float                                       # Code/provenance trust coherence [0, 1]
    carriers: List[Phasor] = field(default_factory=list)
    ctr_density: float = 0.0
    tau_threshold: float = 0.50                      # Compatibility threshold tau in (0, 1]
    violations: List[str] = field(default_factory=list)
    upstream_hashes: List[str] = field(default_factory=list)

    @property
    def group_lock_r(self) -> float:
        if not self.carriers:
            return 1.0
        _, r = fuse_group(self.carriers)
        return round(r, 6)

    @property
    def score(self) -> UnifiedCoherenceScore:
        return UnifiedCoherenceScore(
            C_K=self.C_K,
            C_T=self.C_T,
            C_phi_group=self.group_lock_r,
            ctr_density=self.ctr_density,
        )

    @property
    def C_total(self) -> float:
        return self.score.C_total

    @property
    def E_total(self) -> float:
        return self.score.E_total

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0 and self.C_total >= self.tau_threshold

    @property
    def state_hash(self) -> str:
        raw = json.dumps({
            "delta_id": self.delta_id,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "upstream_hashes": self.upstream_hashes,
        }, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
