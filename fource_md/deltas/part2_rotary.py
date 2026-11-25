import math
from ..algebra import Phasor, coa_star
from ..ledger import DeltaFragment


def delta_07_shaft_key(
    Ma_Nm: float = 120.0, Tm_Nm: float = 180.0, Se_MPa: float = 280.0, Sut_MPa: float = 850.0,
    span_mm: float = 180.0, F_rad_N: float = 2500.0, misalignment_rad: float = 0.02,
) -> DeltaFragment:
    d_raw = (((16.0 * 2.0 / math.pi) * (
        (2.0 * 2.0 * Ma_Nm / (Se_MPa * 1e6)) + (math.sqrt(3.0) * 1.6 * Tm_Nm / (Sut_MPa * 1e6))
    )) ** (1.0 / 3.0)) * 1000.0
    d_mm = coa_star(d_raw, 0.0, lambda a, b: a + b, lambda x: max(x, 25.0))
    I = math.pi * ((d_mm / 1000.0) ** 4) / 64.0
    slope = (F_rad_N * ((span_mm / 1000.0) ** 2)) / (16.0 * 207e9 * I)
    ok = slope < 0.001
    carriers = [Phasor(1.0, 0.0), Phasor(1.0, misalignment_rad)]
    return DeltaFragment(
        "Δ07", "CH07-MD-007", {"Ma_Nm": Ma_Nm, "Tm_Nm": Tm_Nm, "span_mm": span_mm},
        {"d_shaft_mm": round(d_mm, 2), "slope_rad": round(slope, 6)},
        C_K=0.96 if ok else 0.30, C_T=0.96, carriers=carriers,
        violations=[] if ok else [f"Bearing slope {slope:.5f} rad >= 0.001 rad"],
    )


def delta_08_journal_bearing(
    D_mm: float = 50.0, L_mm: float = 50.0, c_mm: float = 0.04,
    W_N: float = 4000.0, N_rpm: float = 1500.0, mu_mPas: float = 25.0,
) -> DeltaFragment:
    R, L, c = (D_mm / 2000.0), (L_mm / 1000.0), (c_mm / 1000.0)
    P_Pa = W_N / (2.0 * R * L)
    S = ((R / c) ** 2) * ((mu_mPas * 1e-3) * (N_rpm / 60.0) / P_Pa)
    ok = S >= 0.05
    return DeltaFragment(
        "Δ08", "CH08-MD-008", {"D_mm": D_mm, "W_N": W_N, "N_rpm": N_rpm},
        {"Sommerfeld_S": round(S, 4), "P_proj_MPa": round(P_Pa / 1e6, 2)},
        C_K=0.95 if ok else 0.30, C_T=0.96,
        violations=[] if ok else [f"Sommerfeld S={S:.4f} < 0.05 boundary threshold"],
    )


def delta_09_rolling_bearing(
    C_kN: float = 35.0, Fr_kN: float = 2.2, Fa_kN: float = 0.8, N_rpm: float = 1450.0, target_h: float = 20000.0,
) -> DeltaFragment:
    P_kN = 0.56 * Fr_kN + 1.45 * Fa_kN
    L10h = (1e6 / (60.0 * N_rpm)) * ((C_kN / max(P_kN, 1e-4)) ** 3)
    ok = L10h >= target_h
    return DeltaFragment(
        "Δ09", "CH09-MD-009", {"C_kN": C_kN, "Fr_kN": Fr_kN, "Fa_kN": Fa_kN},
        {"P_eq_kN": round(P_kN, 2), "L10h_hours": round(L10h, 0)},
        C_K=0.95 if ok else 0.30, C_T=0.97,
        violations=[] if ok else [f"Bearing L10h {L10h:.0f}h < {target_h:.0f}h"],
    )


def delta_10_spur_gear(
    power_kW: float = 10.0, rpm: float = 1200.0, m_mm: float = 3.0, Zp: int = 20,
) -> DeltaFragment:
    dp_m = (m_mm * Zp) / 1000.0
    V = math.pi * dp_m * (rpm / 60.0)
    Wt = (power_kW * 1000.0) / V
    Wr = Wt * math.tan(math.radians(20.0))
    ok = Zp >= 18
    return DeltaFragment(
        "Δ10", "CH10-MD-010", {"power_kW": power_kW, "m_mm": m_mm, "Zp": Zp},
        {"Wt_N": round(Wt, 1), "Wr_N": round(Wr, 1), "V_ms": round(V, 2)},
        C_K=0.96 if ok else 0.25, C_T=0.97,
        violations=[] if ok else [f"Pinion teeth {Zp} < 18 undercutting limit"],
    )


def delta_11_helical_gear(
    power_kW: float = 15.0, rpm: float = 1450.0, mn_mm: float = 3.0, Zp: int = 20, psi_deg: float = 18.0,
) -> DeltaFragment:
    psi = math.radians(psi_deg)
    phi_t = math.atan(math.tan(math.radians(20.0)) / math.cos(psi))
    dp_m = ((mn_mm / math.cos(psi)) * Zp) / 1000.0
    V = math.pi * dp_m * (rpm / 60.0)
    Wt = (power_kW * 1000.0) / V
    Wr, Wa = Wt * math.tan(phi_t), Wt * math.tan(psi)
    Torque = Wt * (dp_m / 2.0)
    carriers = [Phasor(1.0, 0.0), Phasor(1.0, psi * 0.25)]
    return DeltaFragment(
        "Δ11", "CH11-MD-011", {"power_kW": power_kW, "rpm": rpm, "psi_deg": psi_deg},
        {"Wt_N": round(Wt, 1), "Wr_N": round(Wr, 1), "Wa_N": round(Wa, 1), "Torque_Nm": round(Torque, 2)},
        C_K=0.95, C_T=0.96, carriers=carriers,
    )


def delta_12_belt_chain(
    power_kW: float = 7.5, D_mm: float = 150.0, rpm: float = 1750.0, sprocket_teeth: int = 19,
) -> DeltaFragment:
    V = math.pi * (D_mm / 1000.0) * (rpm / 60.0)
    ripple_pct = (1.0 - math.cos(math.pi / sprocket_teeth)) * 100.0
    ok = V <= 30.0 and sprocket_teeth >= 17
    return DeltaFragment(
        "Δ12", "CH12-MD-012", {"power_kW": power_kW, "D_mm": D_mm, "sprocket_teeth": sprocket_teeth},
        {"V_ms": round(V, 2), "chordal_ripple_pct": round(ripple_pct, 2)},
        C_K=0.95 if ok else 0.30, C_T=0.95,
        violations=[] if ok else ["Belt speed or chain chordal ripple limit exceeded"],
    )
