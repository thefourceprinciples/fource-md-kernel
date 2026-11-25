import cmath
import math
from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence, Tuple, TypeVar

T = TypeVar("T")


def wrap_phase(phi: float) -> float:
    """Wrap angle in radians into [-pi, pi]."""
    return (phi + math.pi) % (2.0 * math.pi) - math.pi


def distortion_energy(coherence: float, eps: float = 1e-6) -> float:
    """CS mapping: C in [0, 1] -> additive distortion energy E >= 0."""
    c_clamped = max(0.0, min(1.0, coherence))
    return -math.log(c_clamped + eps)


def coherence_from_distortion(energy: float, eps: float = 1e-6) -> float:
    """Inverse CS mapping: E -> C in [0, 1]."""
    return max(0.0, min(1.0, math.exp(-energy) - eps))


class Phasor:
    """PFA (Phase/Fource Algebra) carrier z = A * exp(i * phi) with running Kuramoto memory."""

    def __init__(self, amplitude: float, phase_rad: float, _m: int = 1, _mean_vec: complex | None = None):
        if amplitude < 0.0:
            raise ValueError("Amplitude A must be >= 0.")
        self.A = float(amplitude)
        self.phi = wrap_phase(float(phase_rad))
        self._m = _m
        self._mean_vec = _mean_vec if _mean_vec is not None else cmath.rect(1.0, self.phi)

    def streaming_couple(self, other: "Phasor", beta: float = 2.0) -> "Phasor":
        """Near-associative binary fusion using running Kuramoto order parameter."""
        m_new = self._m + other._m
        mean_new = (self._m * self._mean_vec + other._m * other._mean_vec) / m_new
        r_new = abs(mean_new)
        w_group = math.exp(-beta * (1.0 - r_new))
        return Phasor(self.A * other.A * w_group, self.phi + other.phi, _m=m_new, _mean_vec=mean_new)

    def __repr__(self) -> str:
        return f"Phasor(A={self.A:.4f}, phi={self.phi:.4f}, r={abs(self._mean_vec):.4f})"


def kuramoto_order(phases: Sequence[float]) -> Tuple[float, float]:
    """Compute Kuramoto order parameter r in [0, 1] and mean phase psi."""
    if not phases:
        return 1.0, 0.0
    r_complex = sum(cmath.rect(1.0, phi) for phi in phases) / len(phases)
    return abs(r_complex), cmath.phase(r_complex)


def fuse_group(carriers: Sequence[Phasor], beta: float = 2.0, quadratic: bool = False) -> Tuple[Phasor, float]:
    """Order-invariant n-ary PFA group fusion operator Fuse({z_1, ..., z_n})."""
    if not carriers:
        return Phasor(1.0, 0.0), 1.0
    r, _ = kuramoto_order([z.phi for z in carriers])
    penalty = (1.0 - r) ** 2 if quadratic else (1.0 - r)
    w_group = math.exp(-beta * penalty)
    amp_prod = math.prod(z.A for z in carriers) * w_group
    phi_sum = sum(z.phi for z in carriers)
    return Phasor(amp_prod, phi_sum), r


def branch_contradictions(
    items: Sequence[T],
    contradiction_fn: Callable[[T, T], float],
    theta_ctr: float = 0.6,
) -> List[List[T]]:
    """Partition evidence/requirements into non-contradictory hypothesis basins."""
    clusters: List[List[T]] = []
    for item in items:
        placed = False
        for cluster in clusters:
            if all(contradiction_fn(item, existing) <= theta_ctr for existing in cluster):
                cluster.append(item)
                placed = True
                break
        if not placed:
            clusters.append([item])
    return clusters


def coa_star(
    x: T,
    y: T,
    couple_fn: Callable[[T, T], T],
    project_fn: Callable[[T], T],
    stabilize_fn: Callable[[T], T] = lambda s: s,
) -> T:
    """Canonical COA operator: x ★_K y = R( Π_K( x ⊗ y ) )."""
    return stabilize_fn(project_fn(couple_fn(x, y)))


@dataclass
class UnifiedCoherenceScore:
    """Unified Coherence Metric tying C_K, C_T, Kuramoto r, and contradiction density."""
    C_K: float
    C_T: float
    C_phi_group: float
    ctr_density: float = 0.0
    gamma: float = 2.0
    exponents: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    eps: float = 1e-6

    @property
    def C_ctr(self) -> float:
        return math.exp(-self.gamma * max(0.0, min(1.0, self.ctr_density)))

    @property
    def C_total(self) -> float:
        a, b, c, d = self.exponents
        val = (
            (max(0.0, min(1.0, self.C_K)) ** a)
            * (max(0.0, min(1.0, self.C_T)) ** b)
            * (max(0.0, min(1.0, self.C_phi_group)) ** c)
            * (self.C_ctr ** d)
        )
        return round(val, 6)

    @property
    def E_total(self) -> float:
        return round(distortion_energy(self.C_total, eps=self.eps), 6)


def select_min_distortion_branch(
    branches: Dict[str, UnifiedCoherenceScore]
) -> Tuple[str, UnifiedCoherenceScore]:
    """CS min-plus selection: k* = argmin_k E_total(k)."""
    return min(branches.items(), key=lambda kv: kv[1].E_total)
