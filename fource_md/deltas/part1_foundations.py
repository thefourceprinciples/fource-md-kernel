import math
from typing import List
from ..ledger import DeltaFragment


def delta_01_reliability(beta_target: float = 3.5, beta_actual: float = 3.8) -> DeltaFragment:
    pf = 0.5 * math.erfc(beta_actual / math.sqrt(2.0))
    ok = beta_actual >= beta_target
    return DeltaFragment(
        "Δ01", "CH01-MD-001", {"beta_target": beta_target, "beta_actual": beta_actual},
        {"beta": round(beta_actual, 3), "pf": round(pf, 7)},
        C_K=0.98 if ok else 0.35, C_T=0.98,
        violations=[] if ok else [f"Hasofer-Lind beta {beta_actual:.2f} < {beta_target:.2f}"],
    )


def delta_02_material_index(Sut_MPa: float = 850.0, E_GPa: float = 207.0, rho_kg_m3: float = 7850.0) -> DeltaFragment:
    m_stiff = (E_GPa ** 0.5) / (rho_kg_m3 / 1000.0)
    m_strength = (Sut_MPa ** (2.0 / 3.0)) / (rho_kg_m3 / 1000.0)
    return DeltaFragment(
        "Δ02", "CH02-MD-002", {"Sut_MPa": Sut_MPa, "E_GPa": E_GPa, "rho_kg_m3": rho_kg_m3},
        {"M_stiff": round(m_stiff, 3), "M_strength": round(m_strength, 3)},
        C_K=0.96, C_T=0.97,
    )


def delta_03_mechanical_props(
    Sut_MPa: float = 850.0, Sy_MPa: float = 680.0, d_mm: float = 35.0,
    ka: float = 0.82, kc: float = 1.0, kd: float = 1.0, ke: float = 0.897,
) -> DeltaFragment:
    Se_prime = 0.5 * Sut_MPa if Sut_MPa <= 1400.0 else 700.0
    kb = 1.24 * (d_mm ** -0.107) if d_mm <= 51.0 else 1.51 * (d_mm ** -0.157)
    Se = ka * kb * kc * kd * ke * Se_prime
    return DeltaFragment(
        "Δ03", "CH03-MD-003", {"Sut_MPa": Sut_MPa, "Sy_MPa": Sy_MPa, "d_mm": d_mm},
        {"Se_MPa": round(Se, 2), "Sy_MPa": Sy_MPa, "Sut_MPa": Sut_MPa},
        C_K=0.95, C_T=0.96,
    )


def delta_04_tolerances(tolerances_mm: List[float], max_stack_mm: float = 0.25) -> DeltaFragment:
    wc = sum(abs(t) for t in tolerances_mm)
    rss = math.sqrt(sum(t ** 2 for t in tolerances_mm))
    ok = rss <= max_stack_mm
    return DeltaFragment(
        "Δ04", "CH04-MD-004", {"tolerances_mm": tolerances_mm, "max_stack_mm": max_stack_mm},
        {"WC_mm": round(wc, 4), "RSS_mm": round(rss, 4)},
        C_K=0.96 if ok else 0.30, C_T=0.97,
        violations=[] if ok else [f"RSS stack {rss:.4f} mm > {max_stack_mm:.4f} mm"],
    )


def delta_05_stress_buckling(
    sx_MPa: float = 120.0, sy_MPa: float = -30.0, txy_MPa: float = 65.0,
    P_comp_N: float = 15000.0, E_GPa: float = 207.0, I_mm4: float = 12000.0, Le_mm: float = 500.0,
) -> DeltaFragment:
    avg = 0.5 * (sx_MPa + sy_MPa)
    rad = math.sqrt((0.5 * (sx_MPa - sy_MPa)) ** 2 + txy_MPa ** 2)
    P_cr = (math.pi ** 2 * (E_GPa * 1e9) * (I_mm4 * 1e-12)) / ((Le_mm / 1000.0) ** 2)
    sf_buck = P_cr / max(P_comp_N, 1e-6)
    ok = sf_buck >= 2.0
    return DeltaFragment(
        "Δ05", "CH05-MD-005", {"sx_MPa": sx_MPa, "sy_MPa": sy_MPa, "txy_MPa": txy_MPa, "P_comp_N": P_comp_N},
        {"s1_MPa": round(avg + rad, 2), "s2_MPa": round(avg - rad, 2), "SF_buckling": round(sf_buck, 2)},
        C_K=0.96 if ok else 0.25, C_T=0.96,
        violations=[] if ok else [f"Buckling SF {sf_buck:.2f} < 2.0"],
    )


def delta_06_failure_fatigue(
    sa_MPa: float = 110.0, sm_MPa: float = 140.0, Se_MPa: float = 275.0,
    Sy_MPa: float = 680.0, Sut_MPa: float = 850.0,
) -> DeltaFragment:
    nf = 1.0 / ((sa_MPa / Se_MPa) + (sm_MPa / Sut_MPa))
    ny = Sy_MPa / (sa_MPa + sm_MPa)
    ok = nf >= 1.5 and ny >= 1.5
    return DeltaFragment(
        "Δ06", "CH06-MD-006", {"sa_MPa": sa_MPa, "sm_MPa": sm_MPa},
        {"Nf_Goodman": round(nf, 2), "Ny_Langer": round(ny, 2)},
        C_K=0.96 if ok else 0.30, C_T=0.97,
        violations=[] if ok else [f"Margin low (Nf={nf:.2f}, Ny={ny:.2f})"],
    )
