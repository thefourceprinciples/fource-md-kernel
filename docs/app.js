document.getElementById("audit_date").value = new Date().toISOString().split("T");
let UNIT_MODE = "METRIC";

document.querySelectorAll(".metric").forEach(m => {
  const k = m.querySelector(".k"), v = m.querySelector(".v");
  if (k && k.textContent.includes(",")) {
    const [label, key] = k.textContent.split(",");
    k.textContent = label;
    v.id = v.id.split("_") + "_" + key;
  }
});

const METRIC_BOLTS = `<option value="6,20.1">M6 × 1.0 (At = 20.1 mm²)</option><option value="8,36.6">M8 × 1.25 (At = 36.6 mm²)</option><option value="10,58.0">M10 × 1.5 (At = 58.0 mm²)</option><option value="12,84.3" selected>M12 × 1.75 (At = 84.3 mm²)</option><option value="16,157.0">M16 × 2.0 (At = 157.0 mm²)</option>`;
const INCH_BOLTS = `<option value="6.35,20.5">1/4"-20 UNC (At = 0.0318 in²)</option><option value="9.525,50.0">3/8"-16 UNC (At = 0.0775 in²)</option><option value="12.7,91.5" selected>1/2"-13 UNC (At = 0.1419 in²)</option><option value="15.875,145.8">5/8"-11 UNC (At = 0.2260 in²)</option><option value="19.05,215.5">3/4"-10 UNC (At = 0.3340 in²)</option>`;
const METRIC_GRADES = `<option value="580">Class 8.8 (Sp = 580 MPa)</option><option value="830" selected>Class 10.9 (Sp = 830 MPa)</option><option value="970">Class 12.9 (Sp = 970 MPa)</option>`;
const INCH_GRADES = `<option value="586">SAE Grade 5 (Sp = 85 ksi)</option><option value="827" selected>SAE Grade 8 (Sp = 120 ksi)</option><option value="965">Socket Cap A574 (Sp = 140 ksi)</option>`;

const LABELS = {
  METRIC: {
    pf_d: ["Shaft Diameter d (mm)", 35, 0.5], pf_do: ["Hub Outer Dia D_o (mm)", 75, 1],
    pf_delta_d: ["Diametral Interference Δd (mm)", 0.044, 0.002], pf_len: ["Engaged Length L (mm)", 35, 1],
    pf_treq: ["Required Torque T_req (N·m)", 120, 5], pf_sy: ["Hub Yield S_y (MPa)", 450, 10],
    pf_e: ["Modulus E (GPa)", 207, 1], bt_pext: ["External Load / Bolt P (N)", 12000, 500],
    bt_kb: ["Bolt Stiffness k_b (kN/mm)", 420, 20], bt_km: ["Member Stiffness k_m (kN/mm)", 1900, 50],
    st_t1: ["Feature 1 ±t₁ (mm)", 0.05, 0.005], st_t2: ["Feature 2 ±t₂ (mm)", 0.08, 0.005],
    st_t3: ["Feature 3 ±t₃ (mm)", 0.04, 0.005], st_t4: ["Feature 4 ±t₄ (mm)", 0.05, 0.005],
    st_nom: ["Nominal Gap (mm)", 0.18, 0.01], st_min: ["Min Required Gap (mm)", 0.02, 0.005],
    sh_ma: ["Bending Moment M_a (N·m)", 140, 10], sh_tm: ["Steady Torque T_m (N·m)", 180, 10],
    sh_span: ["Bearing Span L (mm)", 180, 10], sh_frad: ["Radial Load F_rad (N)", 3100, 100],
    sh_se: ["Endurance S_e (MPa)", 280, 10], sh_sut: ["Ultimate S_ut (MPa)", 850, 10]
  },
  INCH: {
    pf_d: ["Shaft Diameter d (in)", 1.500, 0.025], pf_do: ["Hub Outer Dia D_o (in)", 3.000, 0.05],
    pf_delta_d: ["Diametral Interference Δd (in)", 0.0018, 0.0001], pf_len: ["Engaged Length L (in)", 1.500, 0.05],
    pf_treq: ["Required Torque T_req (lb·ft)", 90, 5], pf_sy: ["Hub Yield S_y (ksi)", 65, 2],
    pf_e: ["Modulus E (Mpsi)", 30.0, 0.5], bt_pext: ["External Load / Bolt P (lbf)", 2800, 100],
    bt_kb: ["Bolt Stiffness k_b (klbf/in)", 2400, 100], bt_km: ["Member Stiffness k_m (klbf/in)", 10800, 250],
    st_t1: ["Feature 1 ±t₁ (in)", 0.002, 0.0002], st_t2: ["Feature 2 ±t₂ (in)", 0.003, 0.0002],
    st_t3: ["Feature 3 ±t₃ (in)", 0.0015, 0.0002], st_t4: ["Feature 4 ±t₄ (in)", 0.002, 0.0002],
    st_nom: ["Nominal Gap (in)", 0.007, 0.0005], st_min: ["Min Required Gap (in)", 0.001, 0.0002],
    sh_ma: ["Bending Moment M_a (lb·ft)", 105, 5], sh_tm: ["Steady Torque T_m (lb·ft)", 135, 5],
    sh_span: ["Bearing Span L (in)", 7.0, 0.25], sh_frad: ["Radial Load F_rad (lbf)", 700, 25],
    sh_se: ["Endurance S_e (ksi)", 40, 2], sh_sut: ["Ultimate S_ut (ksi)", 125, 5]
  }
};

function toggleUnits() {
  UNIT_MODE = UNIT_MODE === "METRIC" ? "INCH" : "METRIC";
  document.getElementById("unit_btn").textContent = UNIT_MODE === "METRIC" ? "Units: METRIC (mm / N)" : "Units: INCH (in / lbf)";
  for (const [id, [lbl, val, step]] of Object.entries(LABELS[UNIT_MODE])) {
    const inp = document.getElementById(id);
    if (inp) { inp.previousElementSibling.textContent = lbl; inp.value = val; inp.step = step; }
  }
  document.getElementById("bt_size").innerHTML = UNIT_MODE === "METRIC" ? METRIC_BOLTS : INCH_BOLTS;
  document.getElementById("bt_grade").innerHTML = UNIT_MODE === "METRIC" ? METRIC_GRADES : INCH_GRADES;
  applyBoltPreset(); calcPressFit(); calcStackup(); calcShaft();
}

function switchTab(id, el) {
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
  el.classList.add("active");
  document.getElementById("panel-" + id).classList.add("active");
}

function quickHash(str) {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
  return "Δ-" + (h >>> 0).toString(16).padStart(8, "0");
}

function renderResult(prefix, passed, passMsg, failMsg, cK, cT, violations, raw) {
  const cTotal = +(cK * cT).toFixed(4), eTotal = +(-Math.log(cTotal + 1e-6)).toFixed(4);
  const banner = document.getElementById(prefix + "_banner");
  banner.className = "status-banner " + (passed ? "status-pass" : "status-fail");
  document.getElementById(prefix + "_status_text").textContent = passed ? passMsg : failMsg;
  document.getElementById(prefix + "_hash").textContent = quickHash(raw);
  document.getElementById(prefix + "_cuc").innerHTML = `<strong>CUC Telemetry:</strong> C_K = ${cK.toFixed(2)} &bull; C_T = ${cT.toFixed(2)} &bull; <strong>C_total = ${cTotal}</strong> &bull; <strong>Distortion E_total = ${eTotal}</strong>`;
  document.getElementById(prefix + "_violations").innerHTML = violations.map(v => `<li>${v}</li>`).join("");
}
function calcPressFit() {
  const inMode = UNIT_MODE === "INCH";
  const d = (+document.getElementById("pf_d").value || 1) * (inMode ? 25.4 : 1);
  const Do = (+document.getElementById("pf_do").value || 2) * (inMode ? 25.4 : 1);
  const deltaD = (+document.getElementById("pf_delta_d").value || 0) * (inMode ? 25.4 : 1);
  const L = (+document.getElementById("pf_len").value || 1) * (inMode ? 25.4 : 1);
  const tReq = (+document.getElementById("pf_treq").value || 0.1) * (inMode ? 1.35582 : 1);
  const Sy = (+document.getElementById("pf_sy").value || 1) * (inMode ? 6.89476 : 1);
  const mu = +document.getElementById("pf_mu").value || 0;
  const E = (+document.getElementById("pf_e").value || 207) * (inMode ? 6.89476 : 1) * 1e9;

  const R = (d / 2) / 1000, Ro = (Do / 2) / 1000, deltaR = (deltaD / 2) / 1000;
  const pPa = (E * deltaR / (2 * R)) * (1 - Math.pow(R / Ro, 2));
  const pMPa = pPa / 1e6;
  const tSlip = 2 * Math.PI * R * R * (L / 1000) * mu * pPa;
  const sfSlip = tSlip / Math.max(tReq, 0.01);
  const hoopMPa = pMPa * ((Ro * Ro + R * R) / Math.max(Ro * Ro - R * R, 1e-9));
  const sfYield = Sy / Math.max(hoopMPa, 0.01);

  document.getElementById("pf_p").textContent = inMode ? `${(pMPa * 0.145038).toFixed(2)} ksi (${pMPa.toFixed(1)} MPa)` : `${pMPa.toFixed(1)} MPa (${(pMPa * 145.038).toFixed(0)} psi)`;
  document.getElementById("pf_tslip").textContent = inMode ? `${(tSlip * 0.73756).toFixed(1)} lb·ft (${tSlip.toFixed(1)} N·m)` : `${tSlip.toFixed(1)} N·m (${(tSlip * 0.73756).toFixed(1)} lb·ft)`;
  document.getElementById("pf_sf_slip").textContent = `${sfSlip.toFixed(2)}×`;
  document.getElementById("pf_hoop").textContent = inMode ? `${(hoopMPa * 0.145038).toFixed(2)} ksi (${sfYield.toFixed(2)}×)` : `${hoopMPa.toFixed(1)} MPa (${sfYield.toFixed(2)}×)`;

  const v = [];
  if (sfSlip < 2.0) v.push(`Torque slip SF ${sfSlip.toFixed(2)} < 2.0 Tier-1 threshold.`);
  if (sfYield < 1.5) v.push(`Hub bore hoop stress yields hub (SF ${sfYield.toFixed(2)} < 1.5).`);
  const ok = v.length === 0;
  renderResult("pf", ok, "PASS — COHERENT FIT", "FAIL — CONSTRAINT BREACH", ok ? 0.96 : 0.28, 0.97, v, `${d}:${Do}:${deltaD}:${L}:${tReq}`);
}

function applyBoltPreset() {
  const [d, at] = document.getElementById("bt_size").value.split(",").map(Number);
  window._boltD = d; window._boltAt = at;
  calcBolts();
}

function calcBolts() {
  const inMode = UNIT_MODE === "INCH";
  const d = window._boltD || 12, At = window._boltAt || 84.3;
  const Sp = +document.getElementById("bt_grade").value;
  const Pext = (+document.getElementById("bt_pext").value || 0) * (inMode ? 4.44822 : 1);
  const ratio = (+document.getElementById("bt_ratio").value || 75) / 100;
  const kb = (+document.getElementById("bt_kb").value || 1) * (inMode ? 0.175127 : 1);
  const km = (+document.getElementById("bt_km").value || 1) * (inMode ? 0.175127 : 1);
  const K = +document.getElementById("bt_k").value || 0.18;

  const Fi = ratio * At * Sp;
  const C = kb / (kb + km);
  const stressPct = ((Fi + C * Pext) / (At * Sp)) * 100;
  const nSep = Fi / Math.max((1 - C) * Pext, 0.01);
  const torqueNm = K * Fi * (d / 1000);

  document.getElementById("bt_fi").textContent = inMode ? `${(Fi * 0.224809).toFixed(0)} lbf (${(Fi / 1000).toFixed(2)} kN)` : `${(Fi / 1000).toFixed(2)} kN (${(Fi * 0.224809).toFixed(0)} lbf)`;
  document.getElementById("bt_torque").textContent = inMode ? `${(torqueNm * 0.73756).toFixed(1)} lb·ft (${torqueNm.toFixed(1)} N·m)` : `${torqueNm.toFixed(1)} N·m (${(torqueNm * 0.73756).toFixed(1)} lb·ft)`;
  document.getElementById("bt_nsep").textContent = `${nSep.toFixed(2)}×`;
  document.getElementById("bt_c").textContent = `${C.toFixed(3)} (${stressPct.toFixed(0)}% Sp)`;

  const v = [];
  if (nSep < 1.5) v.push(`Flange separation margin N_sep = ${nSep.toFixed(2)} < 1.5 minimum.`);
  if (stressPct > 92) v.push(`Peak bolt tension reaches ${stressPct.toFixed(1)}% of proof load (> 92%).`);
  const ok = v.length === 0;
  renderResult("bt", ok, "PASS — CLAMP LOCKED", "FAIL — JOINT SEPARATION RISK", ok ? 0.97 : 0.25, 0.97, v, `${d}:${Sp}:${Pext}:${kb}:${km}`);
}

function calcStackup() {
  const unit = UNIT_MODE === "INCH" ? "in" : "mm";
  const t = ["st_t1", "st_t2", "st_t3", "st_t4"].map(id => Math.abs(+document.getElementById(id).value || 0));
  const nom = +document.getElementById("st_nom").value || 0;
  const minReq = +document.getElementById("st_min").value || 0;
  const wc = t.reduce((a, b) => a + b, 0);
  const rss = Math.sqrt(t.reduce((a, b) => a + b * b, 0));
  const wcGap = nom - wc, rssGap = nom - rss;

  document.getElementById("st_wc").textContent = `±${wc.toFixed(4)} ${unit}`;
  document.getElementById("st_rss").textContent = `±${rss.toFixed(4)} ${unit}`;
  document.getElementById("st_wc_gap").textContent = `${wcGap.toFixed(4)} ${unit}`;
  document.getElementById("st_rss_gap").textContent = `${rssGap.toFixed(4)} ${unit}`;

  const v = [];
  if (rssGap < minReq) v.push(`Statistical 3σ min gap (${rssGap.toFixed(4)} ${unit}) violates required ${minReq.toFixed(4)} ${unit}.`);
  if (wcGap < 0) v.push(`Worst-case stack predicts ${Math.abs(wcGap).toFixed(4)} ${unit} interference at extreme limits.`);
  const ok = rssGap >= minReq;
  renderResult("st", ok, "PASS — STACK FEASIBLE", "FAIL — INTERFERENCE RISK", ok ? 0.96 : 0.30, 0.97, v, `${t.join(",")}:${nom}:${minReq}`);
}

function calcShaft() {
  const inMode = UNIT_MODE === "INCH";
  const Ma = (+document.getElementById("sh_ma").value || 0) * (inMode ? 1.35582 : 1);
  const Tm = (+document.getElementById("sh_tm").value || 0) * (inMode ? 1.35582 : 1);
  const span = ((+document.getElementById("sh_span").value || 100) * (inMode ? 25.4 : 1)) / 1000;
  const Frad = (+document.getElementById("sh_frad").value || 0) * (inMode ? 4.44822 : 1);
  const Se = (+document.getElementById("sh_se").value || 250) * (inMode ? 6.89476 : 1) * 1e6;
  const Sut = (+document.getElementById("sh_sut").value || 800) * (inMode ? 6.89476 : 1) * 1e6;
  const N = +document.getElementById("sh_nsf").value || 2.0;
  const sLim = +document.getElementById("sh_slim").value || 0.001;

  const dMinM = Math.cbrt((16 * N / Math.PI) * (((4.0 * Ma) / Se) + ((Math.sqrt(3) * 1.6 * Tm) / Sut)));
  const dMinMm = dMinM * 1000;
  const E = 207e9, I = Math.PI * Math.pow(dMinM, 4) / 64;
  const slope = (Frad * span * span) / (16 * E * I);
  const deflMm = ((Frad * Math.pow(span, 3)) / (48 * E * I)) * 1000;
  const dStiffMm = Math.pow((64 * ((Frad * span * span) / (16 * E * sLim))) / Math.PI, 0.25) * 1000;
  const dBestMm = Math.max(dMinMm, dStiffMm);

  document.getElementById("sh_dmin").textContent = inMode ? `${(dMinMm / 25.4).toFixed(3)} in (${dMinMm.toFixed(2)} mm)` : `${dMinMm.toFixed(2)} mm (${(dMinMm / 25.4).toFixed(3)} in)`;
  document.getElementById("sh_slope").textContent = `${slope.toFixed(5)} rad`;
  document.getElementById("sh_defl").textContent = inMode ? `${(deflMm / 25.4).toFixed(5)} in (${deflMm.toFixed(4)} mm)` : `${deflMm.toFixed(4)} mm (${(deflMm / 25.4).toFixed(5)} in)`;
  document.getElementById("sh_dstiff").textContent = inMode ? `${(dBestMm / 25.4).toFixed(3)} in (${dBestMm.toFixed(2)} mm)` : `${dBestMm.toFixed(2)} mm (${(dBestMm / 25.4).toFixed(3)} in)`;

  const v = [];
  if (slope >= sLim) v.push(`Bearing slope ${slope.toFixed(5)} rad exceeds ${sLim} rad limit.`);
  const ok = v.length === 0;
  renderResult("sh", ok, "PASS — WAVEGUIDE RIGID", "FAIL — EXCESSIVE BEARING SLOPE", ok ? 0.96 : 0.30, 0.96, v, `${Ma}:${Tm}:${span}:${Frad}:${sLim}`);
}

applyBoltPreset();
calcPressFit();
calcStackup();
calcShaft();
