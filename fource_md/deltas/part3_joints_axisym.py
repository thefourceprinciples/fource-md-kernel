import math
from ..ledger import DeltaFragment


def delta_13_brake_clutch(
    Ro_mm: float = 140.0, Ri_mm: float = 85.0, Fa_N: float = 3500.0, mu: float = 0.35, surfaces: int = 2
) -> DeltaFragment:
    T_wear = 0.5 * surfaces * mu * Fa_N * ((Ro_mm + Ri_mm) / 1000.0)
    return DeltaFragment(
        "Δ13", "CH13-MD-013", {"Ro_mm": Ro_mm, "Ri_mm": Ri_mm, "Fa_N": Fa_N},
        {"T_wear_Nm": round(T_wear, 2)},
        {"O": 0.95, "E": 0.95, "H": 0.93, "X": 0.95}, lambda_cost=0.18
    )


def delta_14_helical_spring(
    d_mm: float = 4.0, D_mm: float = 32.0, Na: float = 10.0, F_max_N: float = 450.0, L0_mm: float = 85.0
) -> DeltaFragment:
    C = D_mm / d_mm
    Kw = ((4.0 * C - 1.0) / (4.0 * C - 4.0)) + (0.615 / C)
    tau_MPa = Kw * (8.0 * F_max_N * D_mm) / (math.pi * (d_mm ** 3))
    buck_lim = 2.63 * (D_mm / 0.5)
    v = [] if (4.0 <= C <= 12.0 and L0_mm < buck_lim) else ["Spring index or buckling limit violated"]
    return DeltaFragment(
        "Δ14", "CH14-MD-014", {"d_mm": d_mm, "D_mm": D_mm, "F_max_N": F_max_N},
        {"Spring_C": round(C, 2), "Kw": round(Kw, 3), "tau_max_MPa": round(tau_MPa, 1)},
        {"O": 0.96, "E": 0.96, "H": 0.94, "X": 0.96 if not v else 0.50}, lambda_cost=0.15, violations=v
    )


def delta_15_power_screw(
    F_N: float = 12000.0, dm_mm: float = 28.0, lead_mm: float = 6.0, mu: float = 0.12
) -> DeltaFragment:
    sec_a = 1.0 / math.cos(math.radians(14.5))
    self_locking = (math.pi * mu * dm_mm * sec_a) > lead_mm
    T_raise = (F_N * (dm_mm / 2000.0)) * (
        (lead_mm + math.pi * mu * dm_mm * sec_a) / (math.pi * dm_mm - mu * lead_mm * sec_a)
    )
    return DeltaFragment(
        "Δ15", "CH15-MD-015", {"F_N": F_N, "dm_mm": dm_mm, "lead_mm": lead_mm},
        {"T_raise_Nm": round(T_raise, 2), "self_locking": self_locking},
        {"O": 0.96, "E": 0.95, "H": 0.94, "X": 0.96}, lambda_cost=0.17
    )


def delta_16_bolted_joint(
    At_mm2: float = 84.3, Sp_MPa: float = 830.0, kb: float = 4.2e5, km: float = 1.9e6, P_ext_N: float = 8000.0
) -> DeltaFragment:
    Fi = 0.75 * At_mm2 * Sp_MPa
    C = kb / (kb + km)
    N_sep = Fi / max((1.0 - C) * P_ext_N, 1e-4)
    v = [] if N_sep >= 1.5 else [f"Bolt separation SF {N_sep:.2f} < 1.5"]
    return DeltaFragment(
        "Δ16", "CH16-MD-016", {"At_mm2": At_mm2, "P_ext_N": P_ext_N},
        {"Fi_N": round(Fi, 1), "C_stiff": round(C, 3), "N_sep": round(N_sep, 2)},
        {"O": 0.97, "E": 0.96 if not v else 0.50, "H": 0.95, "X": 0.97}, lambda_cost=0.16, violations=v
    )


def delta_17_welds_adhesives(
    F_N: float = 25000.0, weld_len_mm: float = 200.0, leg_h_mm: float = 6.0, Sut_filler_MPa: float = 480.0
) -> DeltaFragment:
    tau_throat = F_N / (0.707 * leg_h_mm * weld_len_mm)
    tau_allow = 0.30 * Sut_filler_MPa
    sf = tau_allow / tau_throat
    v = [] if sf >= 1.5 else [f"Weld throat SF {sf:.2f} < 1.5"]
    return DeltaFragment(
        "Δ17", "CH17-MD-017", {"F_N": F_N, "weld_len_mm": weld_len_mm, "leg_h_mm": leg_h_mm},
        {"tau_throat_MPa": round(tau_throat, 2), "SF_weld": round(sf, 2)},
        {"O": 0.95, "E": 0.95, "H": 0.93 if not v else 0.50, "X": 0.96}, lambda_cost=0.18, violations=v
    )


def delta_18_axisymmetric(
    d_shaft_mm: float = 35.0, hub_od_mm: float = 75.0, delta_rad_mm: float = 0.022,
    hub_L_mm: float = 35.0, Torque_req_Nm: float = 100.0
) -> DeltaFragment:
    R, Ro, d = d_shaft_mm / 2000.0, hub_od_mm / 2000.0, delta_rad_mm / 1000.0
    p = (207e9 * d / (2.0 * R)) * (1.0 - (R / Ro) ** 2)
    T_slip = 2.0 * math.pi * (R ** 2) * (hub_L_mm / 1000.0) * 0.15 * p
    sf_slip = T_slip / max(Torque_req_Nm, 1e-4)
    v = [] if sf_slip >= 2.0 else [f"Shrink-fit slip SF {sf_slip:.2f} < 2.0"]
    return DeltaFragment(
        "Δ18", "CH18-MD-018", {"d_shaft_mm": d_shaft_mm, "delta_rad_mm": delta_rad_mm},
        {"p_fit_MPa": round(p / 1e6, 2), "T_slip_Nm": round(T_slip, 1), "SF_slip": round(sf_slip, 2)},
        {"O": 0.95, "E": 0.95 if not v else 0.55, "H": 0.94, "X": 0.97}, lambda_cost=0.19, violations=v
    )
