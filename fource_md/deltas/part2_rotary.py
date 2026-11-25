import math
from ..ledger import DeltaFragment


def delta_07_shaft_key(
    Ma_Nm: float, Tm_Nm: float, Se_MPa: float, Sut_MPa: float,
    span_mm: float = 180.0, F_rad_N: float = 2500.0, N_sf: float = 2.0
) -> DeltaFragment:
    d_m = ((16.0 * N_sf / math.pi) * (
        (2.0 * 2.0 * Ma_Nm / (Se_MPa * 1e6)) + (math.sqrt(3.0) * 1.6 * Tm_Nm / (Sut_MPa * 1e6))
    )) ** (1.0 / 3.0)
    d_mm = max(d_m * 1000.0, 25.0)
    I = math.pi * ((d_mm / 1000.0) ** 4) / 64.0
    slope = (F_rad_N * ((span_mm / 1000.0) ** 2)) / (16.0 * 207e9 * I)
    v = [] if slope < 0.001 else [f"Bearing slope {slope:.5f} rad >= 0.001 rad"]
    return DeltaFragment(
        "Δ07", "CH07-MD-007", {"Ma_Nm": Ma_Nm, "Tm_Nm": Tm_Nm, "span_mm": span_mm},
        {"d_shaft_mm": round(d_mm, 2), "slope_rad": round(slope, 6)},
        {"O": 0.95, "E": 0.96 if not v else 0.55, "H": 0.94, "X": 0.96}, lambda_cost=0.20, violations=v
    )


def delta_08_journal_bearing(
    D_mm: float = 50.0, L_mm: float = 50.0, c_mm: float = 0.04,
    W_N: float = 4000.0, N_rpm: float = 1500.0, mu_mPas: float = 25.0
) -> DeltaFragment:
    R, L, c = (D_mm / 2000.0), (L_mm / 1000.0), (c_mm / 1000.0)
    P_Pa = W_N / (2.0 * R * L)
    S = ((R / c) ** 2) * ((mu_mPas * 1e-3) * (N_rpm / 60.0) / P_Pa)
    v = [] if S >= 0.05 else [f"Sommerfeld number S={S:.4f} risks boundary contact"]
    return DeltaFragment(
        "Δ08", "CH08-MD-008", {"D_mm": D_mm, "W_N": W_N, "N_rpm": N_rpm},
        {"Sommerfeld_S": round(S, 4), "P_proj_MPa": round(P_Pa / 1e6, 2)},
        {"O": 0.95, "E": 0.95, "H": 0.94 if not v else 0.50, "X": 0.95}, lambda_cost=0.21, violations=v
    )


def delta_09_rolling_bearing(
    C_kN: float, Fr_kN: float, Fa_kN: float, N_rpm: float, target_h: float = 20000.0
) -> DeltaFragment:
    P_kN = 0.56 * Fr_kN + 1.45 * Fa_kN
    L10h = (1e6 / (60.0 * N_rpm)) * ((C_kN / max(P_kN, 1e-4)) ** 3)
    v = [] if L10h >= target_h else [f"Bearing L10h {L10h:.0f}h < {target_h:.0f}h"]
    return DeltaFragment(
        "Δ09", "CH09-MD-009", {"C_kN": C_kN, "Fr_kN": Fr_kN, "Fa_kN": Fa_kN},
        {"P_eq_kN": round(P_kN, 2), "L10h_hours": round(L10h, 0)},
        {"O": 0.96, "E": 0.95, "H": 0.93 if not v else 0.50, "X": 0.96}, lambda_cost=0.21, violations=v
    )


def delta_10_spur_gear(
    power_kW: float = 10.0, rpm: float = 1200.0, m_mm: float = 3.0, Zp: int = 20, b_mm: float = 35.0
) -> DeltaFragment:
    dp_m = (m_mm * Zp) / 1000.0
    V = math.pi * dp_m * (rpm / 60.0)
    Wt = (power_kW * 1000.0) / V
    Wr = Wt * math.tan(math.radians(20.0))
    v = [] if Zp >= 18 else [f"Pinion teeth {Zp} < 18 undercutting limit"]
    return DeltaFragment(
        "Δ10", "CH10-MD-010", {"power_kW": power_kW, "m_mm": m_mm, "Zp": Zp},
        {"Wt_N": round(Wt, 1), "Wr_N": round(Wr, 1), "V_ms": round(V, 2)},
        {"O": 0.96 if not v else 0.50, "E": 0.95, "H": 0.94, "X": 0.95}, lambda_cost=0.20, violations=v
    )


def delta_11_helical_gear(
    power_kW: float = 15.0, rpm: float = 1450.0, mn_mm: float = 3.0, Zp: int = 20, psi_deg: float = 18.0
) -> DeltaFragment:
    psi = math.radians(psi_deg)
    phi_t = math.atan(math.tan(math.radians(20.0)) / math.cos(psi))
    dp_m = ((mn_mm / math.cos(psi)) * Zp) / 1000.0
    V = math.pi * dp_m * (rpm / 60.0)
    Wt = (power_kW * 1000.0) / V
    Wr, Wa = Wt * math.tan(phi_t), Wt * math.tan(psi)
    Torque = Wt * (dp_m / 2.0)
    return DeltaFragment(
        "Δ11", "CH11-MD-011", {"power_kW": power_kW, "rpm": rpm, "psi_deg": psi_deg},
        {"Wt_N": round(Wt, 1), "Wr_N": round(Wr, 1), "Wa_N": round(Wa, 1), "Torque_Nm": round(Torque, 2)},
        {"O": 0.95, "E": 0.94, "H": 0.92, "X": 0.95}, lambda_cost=0.22
    )


def delta_12_belt_chain(
    power_kW: float = 7.5, D_mm: float = 150.0, rpm: float = 1750.0, sprocket_teeth: int = 19
) -> DeltaFragment:
    V = math.pi * (D_mm / 1000.0) * (rpm / 60.0)
    ripple_pct = (1.0 - math.cos(math.pi / sprocket_teeth)) * 100.0
    v = [] if (V <= 30.0 and sprocket_teeth >= 17) else ["Belt speed or chain chordal ripple limit exceeded"]
    return DeltaFragment(
        "Δ12", "CH12-MD-012", {"power_kW": power_kW, "D_mm": D_mm, "sprocket_teeth": sprocket_teeth},
        {"V_ms": round(V, 2), "chordal_ripple_pct": round(ripple_pct, 2)},
        {"O": 0.95, "E": 0.94, "H": 0.93, "X": 0.95 if not v else 0.55}, lambda_cost=0.16, violations=v
    )
