const f = (id, lbl, val, step, fn) => `<div class="field"><label>${lbl}</label><input type="number" id="${id}" value="${val}" step="${step}" oninput="${fn}()" /></div>`;
const outCard = (p, title, sub, m1, m2, m3, m4) => `<div class="card"><h2>${title}</h2><div class="sub">${sub}</div><div id="${p}_banner" class="status-banner status-pass"><span id="${p}_status_text">PASS</span><span id="${p}_hash"></span></div><div class="metrics"><div class="metric"><div class="k">${m1[0]}</div><div class="v" id="${p}_${m1[1]}">—</div></div><div class="metric"><div class="k">${m2[0]}</div><div class="v" id="${p}_${m2[1]}">—</div></div><div class="metric"><div class="k">${m3[0]}</div><div class="v" id="${p}_${m3[1]}">—</div></div><div class="metric"><div class="k">${m4[0]}</div><div class="v" id="${p}_${m4[1]}">—</div></div></div><div class="cuc-bar" id="${p}_cuc"></div><ul class="violation-list" id="${p}_violations"></ul></div>`;

document.getElementById("panels-root").innerHTML = `
  <div id="panel-pressfit" class="panel active">
    <div class="card"><h2>Δ18 — Press &amp; Shrink-Fit Interface</h2><div class="sub">Lamé Contact Pressure, Slip Torque &amp; Hub Hoop Stress</div><div class="grid-2">
      ${f("pf_d","Shaft Diameter d (mm)",35,0.5,"calcPressFit")}${f("pf_do","Hub Outer Dia D_o (mm)",75,1,"calcPressFit")}
      ${f("pf_delta_d","Diametral Interference Δd (mm)",0.044,0.002,"calcPressFit")}${f("pf_len","Engaged Length L (mm)",35,1,"calcPressFit")}
      ${f("pf_treq","Required Torque T_req (N·m)",120,5,"calcPressFit")}${f("pf_sy","Hub Yield S_y (MPa)",450,10,"calcPressFit")}
      ${f("pf_mu","Friction μ",0.15,0.01,"calcPressFit")}${f("pf_e","Modulus E (GPa)",207,1,"calcPressFit")}
    </div></div>
    ${outCard("pf","Verification Output (CH18-MD-018)","Limits: Slip SF ≥ 2.0 | Hub Yield SF ≥ 1.5",["Contact Pressure","p"],["Max Slip Torque","tslip"],["Torque Slip SF","sf_slip"],["Hub Hoop Stress (SF)","hoop"])}
  </div>
  <div id="panel-bolts" class="panel">
    <div class="card"><h2>Δ16 — Bolted Fixture &amp; Preload</h2><div class="sub">VDI 2230 Stiffness Sharing &amp; Flange Separation Check</div><div class="grid-2">
      <div class="field"><label>Metric Bolt Size</label><select id="bt_size" onchange="applyBoltPreset()"><option value="6,20.1">M6 × 1.0 (20.1 mm²)</option><option value="8,36.6">M8 × 1.25 (36.6 mm²)</option><option value="10,58.0">M10 × 1.5 (58.0 mm²)</option><option value="12,84.3" selected>M12 × 1.75 (84.3 mm²)</option><option value="16,157.0">M16 × 2.0 (157.0 mm²)</option></select></div>
      <div class="field"><label>ISO Class (Proof S_p)</label><select id="bt_grade" onchange="calcBolts()"><option value="580">Class 8.8 (580 MPa)</option><option value="830" selected>Class 10.9 (830 MPa)</option><option value="970">Class 12.9 (970 MPa)</option></select></div>
      ${f("bt_pext","External Load / Bolt P (N)",12000,500,"calcBolts")}${f("bt_ratio","Preload (% Proof)",75,5,"calcBolts")}
      ${f("bt_kb","Bolt Stiffness k_b (kN/mm)",420,20,"calcBolts")}${f("bt_km","Member Stiffness k_m (kN/mm)",1900,50,"calcBolts")}
      ${f("bt_k","Nut Factor K",0.18,0.01,"calcBolts")}
    </div></div>
    ${outCard("bt","Verification Output (CH16-MD-016)","Limits: Separation SF ≥ 1.5 | Bolt Stress ≤ 92% Proof",["Initial Preload F_i","fi"],["Tightening Torque","torque"],["Separation SF","nsep"],["Stiffness C","c"])}
  </div>
  <div id="panel-stackup" class="panel">
    <div class="card"><h2>Δ04 — Assembly Tolerance Stack-Up</h2><div class="sub">Worst-Case vs. Statistical RSS Print Audit (ASME Y14.5)</div><div class="grid-2">
      ${f("st_t1","Feature 1 ±t₁ (mm)",0.05,0.005,"calcStackup")}${f("st_t2","Feature 2 ±t₂ (mm)",0.08,0.005,"calcStackup")}
      ${f("st_t3","Feature 3 ±t₃ (mm)",0.04,0.005,"calcStackup")}${f("st_t4","Feature 4 ±t₄ (mm)",0.05,0.005,"calcStackup")}
      ${f("st_nom","Nominal Gap (mm)",0.18,0.01,"calcStackup")}${f("st_min","Min Required Gap (mm)",0.02,0.005,"calcStackup")}
    </div></div>
    ${outCard("st","Verification Output (CH04-MD-004)","Limit: RSS 3σ Min Gap ≥ Required Clearance",["Worst-Case Stack","wc"],["RSS Stack","rss"],["Worst-Case Min Gap","wc_gap"],["RSS 3σ Min Gap","rss_gap"])}
  </div>
  <div id="panel-shaft" class="panel">
    <div class="card"><h2>Δ07 — Shaft Fatigue &amp; Bearing Slope</h2><div class="sub">Goodman–von Mises Diameter &amp; Slope Limit (DIN 743)</div><div class="grid-2">
      ${f("sh_ma","Bending Moment M_a (N·m)",140,10,"calcShaft")}${f("sh_tm","Steady Torque T_m (N·m)",180,10,"calcShaft")}
      ${f("sh_span","Bearing Span L (mm)",180,10,"calcShaft")}${f("sh_frad","Radial Load F_rad (N)",3100,100,"calcShaft")}
      ${f("sh_se","Endurance S_e (MPa)",280,10,"calcShaft")}${f("sh_sut","Ultimate S_ut (MPa)",850,10,"calcShaft")}
      ${f("sh_nsf","Fatigue Safety Factor N",2.0,0.1,"calcShaft")}${f("sh_slim","Max Bearing Slope (rad)",0.001,0.0002,"calcShaft")}
    </div></div>
    ${outCard("sh","Verification Output (CH07-MD-007)","Limit: Bearing Slope θ < Max Slope Limit",["Min Fatigue Dia d","dmin"],["Bearing Slope θ","slope"],["Mid-Span Deflection","defl"],["Stiffness Min d","dstiff"])}
  </div>
`;
