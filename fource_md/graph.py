from typing import Callable, Dict, List, Tuple
from .algebra import UnifiedCoherenceScore, select_min_distortion_branch
from .ledger import DeltaFragment


class CUCVerificationGraph:
    """Directed Acyclic Graph executing Compose -> Constrain -> Stabilize with CS distortion."""

    def __init__(self):
        self.nodes: Dict[str, Callable[[Dict[str, DeltaFragment]], DeltaFragment]] = {}
        self.deps: Dict[str, List[str]] = {}
        self.cache: Dict[str, DeltaFragment] = {}
        self.stale: set[str] = set()

    def register(self, delta_id: str, upstream: List[str], fn: Callable[[Dict[str, DeltaFragment]], DeltaFragment]):
        self.nodes[delta_id] = fn
        self.deps[delta_id] = upstream
        self.stale.add(delta_id)

    def invalidate(self, delta_id: str):
        self.stale.add(delta_id)
        for node_id, upstreams in self.deps.items():
            if delta_id in upstreams:
                self.invalidate(node_id)

    def _topo_order(self) -> List[str]:
        visited, order = set(), []
        def visit(n: str):
            if n not in visited:
                visited.add(n)
                for u in self.deps.get(n, []):
                    visit(u)
                order.append(n)
        for node in self.nodes:
            visit(node)
        return order

    def run(self) -> Dict[str, DeltaFragment]:
        for node_id in self._topo_order():
            upstreams = self.deps.get(node_id, [])
            cached = self.cache.get(node_id)
            upstream_changed = cached is None or any(
                u in self.stale or self.cache[u].state_hash not in cached.upstream_hashes
                for u in upstreams
            )
            if node_id in self.stale or upstream_changed:
                frag = self.nodes[node_id](self.cache)
                frag.upstream_hashes = [self.cache[u].state_hash for u in upstreams]
                self.cache[node_id] = frag
                self.stale.discard(node_id)
        return self.cache

    def chain_distortion(self) -> float:
        """CS semiring chain cost: E_chain = sum(E_total) across all executed nodes."""
        results = self.run()
        return round(sum(frag.E_total for frag in results.values()), 6)


def evaluate_hypothesis_branches(
    branch_graphs: Dict[str, CUCVerificationGraph]
) -> Tuple[str, float, Dict[str, Dict[str, DeltaFragment]]]:
    """Run multiple non-contradictory hypothesis DAGs and select min-distortion winner k*."""
    executed: Dict[str, Dict[str, DeltaFragment]] = {}
    branch_scores: Dict[str, UnifiedCoherenceScore] = {}

    for name, graph in branch_graphs.items():
        res = graph.run()
        executed[name] = res
        # Aggregate branch coherence via CS distortion sum -> equivalent C_K
        total_e = sum(f.E_total for f in res.values())
        avg_e = total_e / max(len(res), 1)
        branch_scores[name] = UnifiedCoherenceScore(
            C_K=pow(2.718281828, -avg_e),
            C_T=1.0,
            C_phi_group=1.0,
            ctr_density=0.0,
        )

    winner, win_score = select_min_distortion_branch(branch_scores)
    return winner, win_score.E_total, executed
