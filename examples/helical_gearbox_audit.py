import math
from fource_md.ledger import DeltaFragment
from fource_md.graph import CUCVerificationGraph

params = {
    "Sut_MPa": 850.0, "Sy_MPa": 680.0,
    "power_kW": 15.0, "rpm": 1450.0, "mn_mm": 3.0, "Zp": 20, "psi_deg": 18.0,
    "span_mm": 180.0, "delta_fit_mm": 0.022, "hub_od_mm": 75.0, "hub_L_mm": 35.0,
    "bearing_C_kN": 32.5, "bolt_At_mm2": 84.3, "bolt_d_mm": 12.0, "bolt_Sp_MPa": 830.0,
    "n_bolts": 6, "kb": 4.2e5, "km": 1.9e6
}

def run_delta_03(_):
    Se = 0.5 * params["Sut_MPa"] * 0.82 * 0.88 * 0.897
    return DeltaFragment(
        "Δ03", "CH03-MD-003", {"Sut_MPa": params["Sut_MPa"]},
        {"Se_MPa": round(Se, 2), "Sy_MPa": params["Sy_MPa"]},
        {"O": 0.96, "E": 0.95, "H": 0.94, "X": 0.97}, lambda_cost=0.18
    )

def run_delta_11(state):
    psi = math.radians(params["psi_deg"])
    phi_n = math.radians(20.0)
    phi_t = math.atan(math.tan(phi_n) / math.cos(psi))
    dp_m = (params["mn_mm"] / math.cos(psi) * params["Zp"]) / 1000.0
    V = math.pi * dp_m * (params["rpm"] / 60.0)
    Wt = (params["power_kW"] * 1000.0) / V
    Wr = Wt * math.tan(phi_t)
    Wa = Wt * math.tan(psi)
    Torque = Wt * (dp_m / 2.0)
    return DeltaFragment(
        "Δ11", "CH11-MD-011", {"psi_deg": params["psi_deg"], "power_kW": params["power_kW"]},
        {"Wt_N": round(Wt, 1), "Wr_N": round(Wr, 1), "Wa_N": round(Wa, 1), "Torque_Nm": round(Torque, 2)},
        {"O": 0.95, "E": 0.94, "H": 0.92, "X": 0.95}, lambda_cost=0.22
    )

def run_delta_07(state):
    g = state["Δ11"].outputs
    m = state["Δ03"].outputs
    L = params["span_mm"] / 1000.0
    F_rad = math.hypot(g["Wt_N"], g["Wr_N"])
    Ma = (F_rad * L) / 4.0
    Tm = g["Torque_Nm"]
    d_m = ((16.0 * 2.0 / math.pi) * ((2.0 * 2.0 * Ma / (m["Se_MPa"] * 1e6)) + (math.sqrt(3.0) * 1.6 * Tm / (m["Sut_MPa"] * 1e6)))) ** (1/3)
    d_mm = max(d_m * 1000.0, 30.0)
    I = math.pi * ((d_mm / 1000.0) ** 4) / 64.0
    slope = (F_rad * L**2) / (16.0 * 207e9 * I)
    v = [] if slope < 0.001 else [f"Bearing slope {slope:.5f} rad exceeds 0.001 rad limit"]
    return DeltaFragment(
        "Δ07", "CH07-MD-007", {"Ma_Nm": round(Ma, 2), "Tm_Nm": Tm},
        {"d_shaft_mm": round(d_mm, 2), "slope_rad": round(slope, 6), "Fr_bearing_N": round(F_rad / 2.0, 1)},
        {"O": 0.95, "E": 0.96 if not v else 0.60, "H": 0.94, "X": 0.96}, lambda_cost=0.20, violations=v
    )

def run_delta_18(state):
    d_mm = state["Δ07"].outputs["d_shaft_mm"]
    Tm = state["Δ11"].outputs["Torque_Nm"]
    R = (d_mm / 2.0) / 1000.0
    Ro = (params["hub_od_mm"] / 2.0) / 1000.0
    delta = params["delta_fit_mm"] / 1000.0
    p = (207e9 * delta / (2.0 * R)) * (1.0 - (R / Ro) ** 2)
    T_slip = 2.0 * math.pi * (R ** 2) * (params["hub_L_mm"] / 1000.0) * 0.15 * p
    sf_slip = T_slip / Tm
    v = [] if sf_slip >= 2.0 else [f"Press-fit slip SF {sf_slip:.2f} < 2.0"]
    return DeltaFragment(
        "Δ18", "CH18-MD-018", {"d_shaft_mm": d_mm, "delta_mm": params["delta_fit_mm"]},
        {"p_fit_MPa": round(p / 1e6, 2), "T_slip_Nm": round(T_slip, 1), "SF_slip": round(sf_slip, 2)},
        {"O": 0.95, "E": 0.95 if not v else 0.55, "H": 0.94, "X": 0.97}, lambda_cost=0.19, violations=v
    )

def run_delta_09(state):
    Fr_kN = state["Δ07"].outputs["Fr_bearing_N"] / 1000.0
    Fa_kN = state["Δ11"].outputs["Wa_N"] / 1000.0
    P_kN = 0.56 * Fr_kN + 1.45 * Fa_kN
    L10h = (1e6 / (60.0 * params["rpm"])) * ((params["bearing_C_kN"] / P_kN) ** 3)
    v = [] if L10h >= 20000.0 else [f"Bearing L10h {L10h:.0f}h < 20,000h target"]
    return DeltaFragment(
        "Δ09", "CH09-MD-009", {"Fr_kN": round(Fr_kN, 2), "Fa_kN": round(Fa_kN, 2)},
        {"P_eq_kN": round(P_kN, 2), "L10h_hours": round(L10h, 0)},
        {"O": 0.96, "E": 0.95, "H": 0.93 if not v else 0.50, "X": 0.96}, lambda_cost=0.21, violations=v
    )

def run_delta_16(state):
    Wa_N = state["Δ11"].outputs["Wa_N"]
    P_bolt = Wa_N / params["n_bolts"]
    Fi = 0.75 * params["bolt_At_mm2"] * params["bolt_Sp_MPa"]
    C = params["kb"] / (params["kb"] + params["km"])
    N_sep = Fi / ((1.0 - C) * P_bolt)
    v = [] if N_sep >= 1.5 else [f"Housing bolt separation SF {N_sep:.2f} < 1.5"]
    return DeltaFragment(
        "Δ16", "CH16-MD-016", {"Wa_N": Wa_N, "n_bolts": params["n_bolts"]},
        {"Fi_N": round(Fi, 1), "C_stiff": round(C, 3), "N_sep": round(N_sep, 2)},
        {"O": 0.97, "E": 0.96 if not v else 0.50, "H": 0.95, "X": 0.97}, lambda_cost=0.16, violations=v
    )

if __name__ == "__main__":
    dag = CUCVerificationGraph()
    dag.register("Δ03", [], run_delta_03)
    dag.register("Δ11", ["Δ03"], run_delta_11)
    dag.register("Δ07", ["Δ03", "Δ11"], run_delta_07)
    dag.register("Δ18", ["Δ03", "Δ07", "Δ11"], run_delta_18)
    dag.register("Δ09", ["Δ07", "Δ11"], run_delta_09)
    dag.register("Δ16", ["Δ03", "Δ11"], run_delta_16)

    print("=== INITIAL RUN (psi = 18 deg) ===")
    for k, frag in dag.run().items():
        print(f"{k} [{frag.state_hash}] | C={frag.coherence} | Margin={frag.persistence_margin} | PASS={frag.passed} | {frag.outputs}")

    print("\n=== PERTURBATION: INCREASE HELIX ANGLE TO 32 DEG ===")
    params["psi_deg"] = 32.0
    dag.invalidate("Δ11")
    for k, frag in dag.run().items():
        status = "PASS" if frag.passed else f"FAIL -> {frag.violations}"
        print(f"{k} [{frag.state_hash}] | Margin={frag.persistence_margin} | {status}")
