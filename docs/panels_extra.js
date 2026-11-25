  <div id="panel-bearings" class="panel">
    <div class="card"><h2>Δ08–Δ09 — Journal &amp; Rolling Bearings</h2><div class="sub">Sommerfeld Hydrodynamic Number (S) &amp; ISO 281 L₁₀h Rating Life</div><div class="grid-2">
      ${f("br_c","Dynamic Rating C (kN)",35.0,1.0,"calcBearings")}${f("br_fr","Radial Load F_r (kN)",2.2,0.2,"calcBearings")}
      ${f("br_fa","Axial Thrust F_a (kN)",0.8,0.1,"calcBearings")}${f("br_rpm","Shaft Speed (RPM)",1450,50,"calcBearings")}
      ${f("br_d","Journal Dia D (mm)",50,2,"calcBearings")}${f("br_mu","Oil Viscosity μ (mPa·s)",25,2,"calcBearings")}
    </div></div>
    ${outCard("br","Verification Output (CH08–09)","Limits: L₁₀h ≥ 20,000 hrs | Sommerfeld S ≥ 0.05",["Equivalent Load P","peq"],["Rolling Life L₁₀h","l10h"],["Journal Sommerfeld S","som"],["Projected Pressure","pproj"])}
  </div>

  <div id="panel-gears" class="panel">
    <div class="card"><h2>Δ10–Δ12 — Spur/Helical Gears, Belts &amp; Chains</h2><div class="sub">3D Gear Forces (W_t, W_r, W_a), Pitch Velocity &amp; Chordal Ripple</div><div class="grid-2">
      ${f("gr_kw","Transmitted Power (kW)",15.0,1.0,"calcGears")}${f("gr_rpm","Pinion Speed (RPM)",1450,50,"calcGears")}
      ${f("gr_mn","Normal Module m_n (mm)",3.0,0.25,"calcGears")}${f("gr_zp","Pinion Teeth Z_p (≥ 18)",20,1,"calcGears")}
      ${f("gr_psi","Helix Angle ψ (deg, 0=Spur)",18.0,1.0,"calcGears")}${f("gr_zs","Chain Sprocket Teeth",19,1,"calcGears")}
    </div></div>
    ${outCard("gr","Verification Output (CH10–12)","Limits: Pinion Z_p ≥ 18 | Pitch Velocity ≤ 30 m/s",["Tangential Force W_t","wt"],["Radial / Axial W_r, W_a","wra"],["Pitch Line Speed V","vel"],["Chain Chordal Ripple","rip"])}
  </div>

  <div id="panel-actuators" class="panel">
    <div class="card"><h2>Δ13–Δ15 — Brakes, Springs &amp; Power Screws</h2><div class="sub">Uniform-Wear Disc Torque, Wahl Spring Shear &amp; Acme Self-Locking</div><div class="grid-2">
      ${f("ac_ro","Brake Outer Radius R_o (mm)",140,5,"calcActuators")}${f("ac_ri","Brake Inner Radius R_i (mm)",85,5,"calcActuators")}
      ${f("ac_fa","Brake Clamp Force F_a (N)",3500,100,"calcActuators")}${f("ac_sd","Spring Wire Dia d (mm)",4.0,0.2,"calcActuators")}
      ${f("ac_sD","Spring Mean Dia D (mm)",32.0,1.0,"calcActuators")}${f("ac_sf","Spring Max Load F (N)",450,25,"calcActuators")}
      ${f("ac_scw","Screw Load F (N)",12000,500,"calcActuators")}${f("ac_lead","Acme Screw Lead l (mm)",6.0,0.5,"calcActuators")}
    </div></div>
    ${outCard("ac","Verification Output (CH13–15)","Limits: Spring Index 4 ≤ C ≤ 12 | Acme Self-Locking",["Disc Brake Torque","tbrk"],["Wahl Spring Shear τ","tau"],["Spring Index C (K_w)","idx"],["Acme Raise Torque","tscr"])}
  </div>
`);
function calcBearings() {
  const C = +document.getElementById("br_c").value || 1;
  const Fr = +document.getElementById("br_fr").value || 0;
  const Fa = +document.getElementById("br_fa").value || 0;
  const rpm = +document.getElementById("br_rpm").value || 1;
  const D = +document.getElementById("br_d").value || 50;
  const mu = +document.getElementById("br_mu").value || 25;

  const Peq = 0.56 * Fr + 1.45 * Fa;
  const L10h = (1e6 / (60 * rpm)) * Math.pow(C / Math.max(Peq, 0.001), 3);

  const R = (D / 2) / 1000, L = D / 1000, c = 0.00004;
  const W = Math.max(Fr * 1000, 1);
  const Pproj = W / (2 * R * L);
  const S = Math.pow(R / c, 2) * ((mu * 1e-3) * (rpm / 60) / Pproj);

  document.getElementById("br_peq").textContent = `${Peq.toFixed(2)} kN`;
  document.getElementById("br_l10h").textContent = `${Math.round(L10h).toLocaleString()} hrs`;
  document.getElementById("br_som").textContent = S.toFixed(4);
  document.getElementById("br_pproj").textContent = `${(Pproj / 1e6).toFixed(2)} MPa`;

  const v = [];
  if (L10h < 20000) v.push(`Rolling bearing L10h (${Math.round(L10h).toLocaleString()} hrs) < 20,000 hr target.`);
  if (S < 0.05) v.push(`Journal Sommerfeld S (${S.toFixed(4)}) < 0.05 hydrodynamic film limit.`);
  renderResult("br", v.length === 0, "PASS — FILM & LIFE COHERENT", "FAIL — BEARING WEAR RISK", v.length === 0 ? 0.95 : 0.30, 0.97, v, `${C}:${Fr}:${Fa}:${rpm}`);
}

function calcGears() {
  const kW = +document.getElementById("gr_kw").value || 0;
  const rpm = +document.getElementById("gr_rpm").value || 1;
  const mn = +document.getElementById("gr_mn").value || 3;
  const Zp = +document.getElementById("gr_zp").value || 20;
  const psi = (+document.getElementById("gr_psi").value || 0) * (Math.PI / 180);
  const Zs = +document.getElementById("gr_zs").value || 19;

  const phiT = Math.atan(Math.tan(20 * Math.PI / 180) / Math.cos(psi));
  const dp = ((mn / Math.cos(psi)) * Zp) / 1000;
  const V = Math.PI * dp * (rpm / 60);
  const Wt = (kW * 1000) / Math.max(V, 0.01);
  const Wr = Wt * Math.tan(phiT), Wa = Wt * Math.tan(psi);
  const ripple = (1 - Math.cos(Math.PI / Math.max(Zs, 3))) * 100;

  document.getElementById("wt") ? null : null;
  document.getElementById("gr_wt").textContent = `${Wt.toFixed(0)} N (${(Wt * 0.2248).toFixed(0)} lbf)`;
  document.getElementById("gr_wra").textContent = `${Wr.toFixed(0)} N / ${Wa.toFixed(0)} N`;
  document.getElementById("gr_vel").textContent = `${V.toFixed(2)} m/s (${(V * 196.85).toFixed(0)} fpm)`;
  document.getElementById("gr_rip").textContent = `${ripple.toFixed(2)}%`;

  const v = [];
  if (Zp < 18) v.push(`Pinion teeth Z_p = ${Zp} < 18 involute undercutting limit.`);
  if (V > 30) v.push(`Pitch velocity ${V.toFixed(1)} m/s exceeds 30 m/s standard drive ceiling.`);
  renderResult("gr", v.length === 0, "PASS — MESH COHERENT", "FAIL — MESH / SPEED VIOLATION", v.length === 0 ? 0.95 : 0.30, 0.96, v, `${kW}:${rpm}:${Zp}:${psi}`);
}

function calcActuators() {
  const Ro = (+document.getElementById("ac_ro").value || 140) / 1000;
  const Ri = (+document.getElementById("ac_ri").value || 85) / 1000;
  const Fa = +document.getElementById("ac_fa").value || 0;
  const d = +document.getElementById("ac_sd").value || 4;
  const D = +document.getElementById("ac_sD").value || 32;
  const Fspr = +document.getElementById("ac_sf").value || 0;
  const Fscr = +document.getElementById("ac_scw").value || 0;
  const lead = +document.getElementById("ac_lead").value || 6;

  const tBrk = 0.5 * 2 * 0.35 * Fa * (Ro + Ri);
  const C = D / Math.max(d, 0.1);
  const Kw = ((4 * C - 1) / Math.max(4 * C - 4, 0.1)) + (0.615 / C);
  const tauSpr = Kw * (8 * Fspr * D) / (Math.PI * Math.pow(d, 3));

  const dm = 28, mu = 0.12, secA = 1 / Math.cos(14.5 * Math.PI / 180);
  const lock = (Math.PI * mu * dm * secA) > lead;
  const tScr = (Fscr * (dm / 2000)) * ((lead + Math.PI * mu * dm * secA) / (Math.PI * dm - mu * lead * secA));

  document.getElementById("ac_tbrk").textContent = `${tBrk.toFixed(1)} N·m`;
  document.getElementById("ac_tau").textContent = `${tauSpr.toFixed(0)} MPa`;
  document.getElementById("ac_idx").textContent = `${C.toFixed(1)} (Kw=${Kw.toFixed(2)})`;
  document.getElementById("ac_tscr").textContent = `${tScr.toFixed(1)} N·m (${lock ? "LOCKED" : "BACK-DRIVE"})`;

  const v = [];
  if (C < 4 || C > 12) v.push(`Spring index C = ${C.toFixed(1)} outside 4 ≤ C ≤ 12 standard bounds.`);
  if (!lock) v.push(`Acme screw lead ${lead} mm is not self-locking (requires brake).`);
  renderResult("ac", v.length === 0, "PASS — ACTUATOR COHERENT", "FAIL — SPRING/SCREW BOUND", v.length === 0 ? 0.95 : 0.30, 0.96, v, `${Fa}:${d}:${D}:${lead}`);
}

calcWelds(); calcFoundations(); calcStress(); calcBearings(); calcGears(); calcActuators();
