from typing import Callable, Dict, List
from .ledger import DeltaFragment

class CUCVerificationGraph:
    def __init__(self):
        self.nodes: Dict[str, Callable[[Dict[str, DeltaFragment]], DeltaFragment]] = {}
        self.deps: Dict[str, List[str]] = {}
        self.cache: Dict[str, DeltaFragment] = {}
        self.stale: set[str] = set()

    def register(self, delta_id: str, upstream: List[str], fn: Callable):
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
            upstream_changed = any(
                u in self.stale or
                self.cache[u].state_hash not in self.cache.get(node_id, DeltaFragment("", "", {}, {}, {"O":1,"E":1,"H":1,"X":1}, 0)).upstream_hashes
                for u in upstreams
            )
            if node_id in self.stale or upstream_changed or node_id not in self.cache:
                frag = self.nodes[node_id](self.cache)
                frag.upstream_hashes = [self.cache[u].state_hash for u in upstreams]
                self.cache[node_id] = frag
                self.stale.discard(node_id)
        return self.cache
