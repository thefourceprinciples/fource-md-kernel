document.querySelectorAll(".metric").forEach(m => {
  const k = m.querySelector(".k"), v = m.querySelector(".v");
  if (k && k.textContent.includes(",")) {
    const [label, key] = k.textContent.split(",");
    k.textContent = label;
    v.id = v.id.split("_").shift() + "_" + key;
  }
});

function calcWelds() {
  const F = +document.getElementById("wl_f").value || 0;
  const L = +document.getElementById("wl_len").value || 1;
  const h = +document.getElementById("wl_leg").value || 1;
  const Sut = +document.getElementById("wl_sut").value || 480;

  const te = 0.707 * h;
  const tau = F / (te * L);
  const allow = 0.30 * Sut;
  const sf = allow / Math.max(tau, 0.01);

  document.getElementById("wl_te").textContent = `${te.toFixed(2)} mm (${(te / 25.4).toFixed(3)} in)`;
  document.getElementById("wl_tau").textContent = `${tau.toFixed(1)} MPa (${(tau * 0.145038).toFixed(2)} ksi)`;
  document.getElementById("wl_allow").textContent = `${allow.toFixed(1)} MPa (${(allow * 0.145038).toFixed(2)} ksi)`;
  document.getElementById("wl_sf").textContent = `${sf.toFixed(2)}×`;

  const v = sf < 1.5 ? [`AWS throat shear SF ${sf.toFixed(2)} < 1.5 minimum.`] : [];
  renderResult("wl", v.length === 0, "PASS — WELD THROAT SAFE", "FAIL — WELD OVERSTRESS", v.length === 0 ? 0.96 : 0.25, 0.97, v, `${F}:${L}:${h}:${Sut}`);
}

function calcFoundations() {
  const beta = +document.getElementById("fd_beta").value || 0;
  const Sut = +document.getElementById("fd_sut").value || 850;
  const d = +document.getElementById("fd_d").value || 35;
  const rho = +document.getElementById("fd_rho").value || 7850;
  const E = +document.getElementById("fd_e").value || 207;
  const ka = +document.getElementById("fd_ka").value || 0.82;

  const z = beta / Math.SQRT2;
  const t = 1 / (1 + 0.3275911 * Math.abs(z));
  const erf = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-z * z);
  const pf = 0.5 * (1 - (z >= 0 ? erf : -erf));

  const SePrime = Sut <= 1400 ? 0.5 * Sut : 700;
  const kb = d <= 51 ? 1.24 * Math.pow(d, -0.107) : 1.51 * Math.pow(d, -0.157);
  const Se = ka * kb * 0.897 * SePrime;
  const m1 = Math.sqrt(E) / (rho / 1000);
  const m2 = Math.pow(Sut, 2 / 3) / (rho / 1000);

  document.getElementById("fd_pf").textContent = pf.toExponential(2);
  document.getElementById("fd_se").textContent = `${Se.toFixed(1)} MPa (${(Se * 0.145038).toFixed(1)} ksi)`;
  document.getElementById("fd_m1").textContent = m1.toFixed(3);
  document.getElementById("fd_m2").textContent = m2.toFixed(2);

  const v = beta < 3.5 ? [`Reliability index β = ${beta.toFixed(2)} < 3.5 target.`] : [];
  renderResult("fd", v.length === 0, "PASS — RELIABILITY LOCKED", "FAIL — LOW RELIABILITY β", v.length === 0 ? 0.97 : 0.30, 0.98, v, `${beta}:${Sut}:${d}`);
}

function calcStress() {
  const sx = +document.getElementById("sr_sx").value || 0;
  const sy = +document.getElementById("sr_sy").value || 0;
  const txy = +document.getElementById("sr_txy").value || 0;
  const P = +document.getElementById("sr_pcomp").value || 0;
  const I = (+document.getElementById("sr_i").value || 1000) * 1e-12;
  const Le = (+document.getElementById("sr_le").value || 500) / 1000;

  const avg = 0.5 * (sx + sy), rad = Math.sqrt(Math.pow(0.5 * (sx - sy), 2) + txy * txy);
  const s1 = avg + rad, s2 = avg - rad;
  const vm = Math.sqrt(s1 * s1 - s1 * s2 + s2 * s2);
  const pCr = (Math.PI * Math.PI * 207e9 * I) / (Le * Le);
  const sfb = pCr / Math.max(P, 0.01);

  document.getElementById("sr_s1").textContent = `${s1.toFixed(1)} MPa`;
  document.getElementById("sr_vm").textContent = `${vm.toFixed(1)} MPa`;
  document.getElementById("sr_pcr").textContent = `${(pCr / 1000).toFixed(1)} kN`;
  document.getElementById("sr_sfb").textContent = `${sfb.toFixed(2)}×`;

  const v = sfb < 2.0 ? [`Euler buckling SF ${sfb.toFixed(2)} < 2.0 critical limit.`] : [];
  renderResult("sr", v.length === 0, "PASS — BUCKLING SAFE", "FAIL — BUCKLING INSTABILITY", v.length === 0 ? 0.96 : 0.25, 0.96, v, `${sx}:${sy}:${P}:${Le}`);
}
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
