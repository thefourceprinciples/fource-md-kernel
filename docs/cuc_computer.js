const wrap = p => ((p + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;
const distEnergy = c => -Math.log(Math.max(0, Math.min(1, c)) + 1e-6);

function kuramoto(phases) {
  if (!phases.length) return;
  let sx = 0, sy = 0;
  phases.forEach(p => { sx += Math.cos(p); sy += Math.sin(p); });
  sx /= phases.length; sy /= phases.length;
  return [Math.hypot(sx, sy), Math.atan2(sy, sx)];
}

let vmStepIdx = 0;
let vmBasins = {};
let vmWinner = null;

function drawPhasors() {
  const cvs = document.getElementById("phaseCanvas");
  const ctx = cvs.getContext("2d");
  const cx = cvs.width / 2, cy = cvs.height / 2, R = 92;
  ctx.clearRect(0, 0, cvs.width, cvs.height);

  // Unit circle & crosshairs
  ctx.strokeStyle = "#334155"; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.arc(cx, cy, R, 0, 2 * Math.PI); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(cx - R - 10, cy); ctx.lineTo(cx + R + 10, cy);
  ctx.moveTo(cx, cy - R - 10); ctx.lineTo(cx, cy + R + 10); ctx.stroke();

  const colors = { H0: "#38bdf8", H1: "#22c55e", H2: "#f59e0b" };
  Object.entries(vmBasins).forEach(([bname, list]) => {
    const col = colors[bname] || "#a855f7";
    list.forEach(z => {
      const x = cx + z.A * R * Math.cos(z.phi);
      const y = cy - z.A * R * Math.sin(z.phi);
      ctx.strokeStyle = col; ctx.lineWidth = vmWinner === bname ? 3 : 2;
      ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(x, y); ctx.stroke();
      ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y, 4.5, 0, 2 * Math.PI); ctx.fill();
    });
  });
}

function vmReset() {
  vmStepIdx = 0; vmBasins = {}; vmWinner = null;
  document.getElementById("vm_trace").textContent = "";
  document.getElementById("vm_status").innerHTML = "Ready. Click <strong>Step Next Opcode</strong> to load scattered Phasor stream.";
  drawPhasors();
}

function vmStep() {
  const trace = document.getElementById("vm_trace");
  const status = document.getElementById("vm_status");
  if (vmStepIdx === 0) {
    vmBasins = { H0: [{ A: 1.15, phi: 0.12 }, { A: 1.08, phi: 0.35 }, { A: 1.12, phi: -0.18 }, { A: 0.72, phi: -2.45 }, { A: 0.68, phi: -2.05 }] };
    trace.textContent += "01: LOAD -> 5 carriers loaded into H0\n";
    status.innerHTML = "<strong>LOAD:</strong> 5 raw carriers loaded into primary register <code>H0</code>.";
  } else if (vmStepIdx === 1) {
    vmBasins.H0 = vmBasins.H0.map(z => ({ A: Math.min(1.0, Math.max(0.1, z.A)), phi: wrap(z.phi + 0.05) }));
    trace.textContent += "02: COMPOSE + PROJECT -> clamped amplitudes into [0.1, 1.0]\n";
    status.innerHTML = "<strong>PROJECT (Π_K):</strong> Clamped amplitudes onto feasible energy box <code>[0.1, 1.0]</code>.";
  } else if (vmStepIdx === 2) {
    const h1 = vmBasins.H0.filter(z => Math.abs(z.phi) < 1.2);
    const h2 = vmBasins.H0.filter(z => Math.abs(z.phi) >= 1.2);
    vmBasins = { H1: h1, H2: h2 };
    trace.textContent += `03: BRANCH (theta=0.35) -> Split into H1 (n=${h1.length}) & H2 (n=${h2.length})\n`;
    status.innerHTML = "<strong>BRANCH:</strong> Contradictory phases split into isolated basins <span style='color:#22c55e'>H1</span> &amp; <span style='color:#f59e0b'>H2</span>.";
  } else if (vmStepIdx === 3) {
    Object.keys(vmBasins).forEach(k => {
      for (let s = 0; s < 14; s++) {
        const [, psi] = kuramoto(vmBasins[k].map(z => z.phi));
        vmBasins[k] = vmBasins[k].map(z => ({ A: z.A, phi: wrap(z.phi - 0.45 * Math.sin(z.phi - psi)) }));
      }
    });
    trace.textContent += "04: STABILIZE -> Kuramoto phase-lock converged (14 steps)\n";
    status.innerHTML = "<strong>STABILIZE (R):</strong> Both basins phase-locked onto their respective attractors.";
  } else if (vmStepIdx === 4) {
    const [r1] = kuramoto(vmBasins.H1.map(z => z.phi));
    const [r2] = kuramoto(vmBasins.H2.map(z => z.phi));
    const c1 = +(0.96 * 0.98 * r1).toFixed(4), c2 = +(0.70 * 0.98 * r2).toFixed(4);
    const e1 = distEnergy(c1).toFixed(4), e2 = distEnergy(c2).toFixed(4);
    vmWinner = +e1 <= +e2 ? "H1" : "H2";
    trace.textContent += `05: SELECT -> H1(E=${e1}) vs H2(E=${e2}) => Winner: ${vmWinner}\n06: HALT\n`;
    status.innerHTML = `<strong>SELECT (CS):</strong> Optimal basin <strong>${vmWinner}</strong> selected (Min Distortion <code>E* = ${e1}</code>).`;
  }
  vmStepIdx = Math.min(vmStepIdx + 1, 5);
  drawPhasors();
}

function vmRunAll() { vmReset(); while (vmStepIdx < 5) vmStep(); }
let nnEpoch = 0;
let nnWeights = {};

function netReset() {
  nnEpoch = 0;
  nnWeights = {
    Alpha: [1.4, 1.6, 1.2, 1.5],
    Beta:  [-0.8, -0.5, -0.9, -0.6]
  };
  netEval();
}

function forwardDeep(x) {
  const scores = {};
  Object.entries(nnWeights).forEach(([cname, wList]) => {
    const coupled = x.map((phi, i) => {
      const d = Math.abs(wrap(phi - wList[i]));
      return { A: Math.max(0.05, Math.min(1.0, 0.9 * Math.exp(-1.5 * d))), phi: wrap(phi - wList[i]) };
    });
    const [rLock] = kuramoto(coupled.map(z => z.phi));
    const meanA = coupled.reduce((s, z) => s + z.A, 0) / coupled.length;
    const cTotal = meanA * 0.98 * rLock * Math.exp(-2 * (1 - rLock));
    // 2-layer additive CS chain distortion (hidden + output)
    const eChain = distEnergy(cTotal) + distEnergy(0.95 * rLock);
    scores[cname] = { cTotal, eChain };
  });
  const pred = scores.Alpha.eChain <= scores.Beta.eChain ? "Alpha" : "Beta";
  return { pred, scores };
}

function netEval() {
  const xAlpha = [0.10, 0.18, 0.12, 0.08];
  const xBeta  = [2.20, 2.35, 2.10, 2.25];
  const rA = forwardDeep(xAlpha);
  const rB = forwardDeep(xBeta);
  const acc = ((rA.pred === "Alpha" ? 1 : 0) + (rB.pred === "Beta" ? 1 : 0)) * 50;
  const meanE = ((rA.scores.Alpha.eChain + rB.scores.Beta.eChain) / 2).toFixed(4);

  document.getElementById("nn_epoch").textContent = nnEpoch;
  document.getElementById("nn_echain").textContent = meanE;
  document.getElementById("nn_p1").textContent = `${rA.pred} (E=${rA.scores.Alpha.eChain.toFixed(2)})`;
  document.getElementById("nn_p2").textContent = `${rB.pred} (E=${rB.scores.Beta.eChain.toFixed(2)})`;
  document.getElementById("nn_acc").textContent = `ACCURACY: ${acc.toFixed(1)}%`;

  const banner = document.getElementById("nn_banner");
  banner.className = "status-banner " + (acc === 100 ? "status-pass" : "status-fail");
  document.getElementById("nn_log").innerHTML = acc === 100
    ? `<strong>Converged:</strong> Both hidden &amp; output basins phase-locked onto target regimes (<code>E_chain = ${meanE}</code>).`
    : `<strong>Training Needed:</strong> Basins not yet phase-locked. Click <strong>Train +15 Epochs</strong>.`;
}

function netTrain(epochs) {
  const data = [
    ["Alpha", [0.10, 0.18, 0.12, 0.08]],
    ["Beta",  [2.20, 2.35, 2.10, 2.25]]
  ];
  for (let e = 0; e < epochs; e++) {
    data.forEach(([target, x]) => {
      Object.keys(nnWeights).forEach(cname => {
        const sign = cname === target ? 1.0 : -0.35;
        nnWeights[cname] = nnWeights[cname].map((w, i) => wrap(w + 0.28 * sign * Math.sin(wrap(x[i] - w))));
      });
    });
    nnEpoch++;
  }
  netEval();
}

vmReset();
netReset();
