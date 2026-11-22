const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/Users/trinity/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/b17751b2-b157-416e-ab13-a2265283385d/e9aa77cc-011a-44af-b1a6-c7df1ae623cb/skills/pptx/scripts/apply_theme.js");

const OUTDIR = process.argv[2];
const OUT = process.argv[3];
const FIG = path.join(OUTDIR, "fig");
const R = JSON.parse(fs.readFileSync(path.join(OUTDIR, "fast.json")));
const S = JSON.parse(fs.readFileSync(path.join(OUTDIR, "slow.json")));
const D = JSON.parse(fs.readFileSync(path.join(OUTDIR, "derived.json")));
const W = JSON.parse(fs.readFileSync(path.join(OUTDIR, "wls.json")));

const HEX = { navy: "0E1A2B", ink: "1B2A3F", amber: "F2A541", teal: "2A9D8F", ice: "E8EEF5", mute: "5B6B80", red: "D1495B", white: "FFFFFF", grid: "D5DCE5", soft: "B8C4D6" };
const THEME = { name: "Catch the Flip Physics", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: HEX.ink, lt1: HEX.white, dk2: HEX.navy, lt2: HEX.ice, accent1: HEX.amber, accent2: HEX.teal, accent3: HEX.mute, accent4: HEX.red, accent5: "8FA3BF", accent6: "264653", hlink: HEX.teal, folHlink: HEX.mute } };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Catch the Flip: physics and detector";
const C = pres.SchemeColor;

pres.defineSlideMaster({ title: "DARK", background: { color: C.text2 }, objects: [], slideNumber: { x: 12.4, y: 6.95, w: 0.6, h: 0.3, color: "8FA3BF", fontSize: 10 } });
pres.defineSlideMaster({ title: "CONTENT", background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.85, fontSize: 30, bold: true, color: C.text2, valign: "middle", margin: 0, align: "left" }, text: "" } },
    { text: { text: "Catch the Flip  ·  PushQuantum Hackathon 2026", options: { x: 0.6, y: 6.98, w: 6, h: 0.3, fontSize: 10, color: C.accent3, margin: 0 } } },
  ],
  slideNumber: { x: 12.4, y: 6.98, w: 0.6, h: 0.3, color: C.accent3, fontSize: 10 } });

const plain = (t) => String(t).replace(/_\{([^}]*)\}/g, "$1").replace(/_/g, "");
const tb = (o) => Object.assign({ isTextBox: true, margin: 0, valign: "top" }, o);
const f2 = (x, d = 2) => Number(x).toFixed(d);
const pct = (x, d = 1) => (100 * x).toFixed(d) + " %";
function sub(str, opts) { // "κ_b" -> κ with subscript b
  return str.split(/_\{([^}]+)\}|_([A-Za-z0-9ξ])(?![A-Za-z])/).filter((t) => t !== undefined).map((t, i) => ({ text: t, options: Object.assign({}, opts, i % 2 ? { subscript: true } : {}) })).filter((r) => r.text !== "");
}
function lines(items, base) { // items: strings or [head, body]; returns runs with breaks
  const runs = [];
  items.forEach((it, i) => {
    const last = i === items.length - 1;
    if (Array.isArray(it)) {
      sub(it[0], Object.assign({ bold: true, color: base.head || C.accent2, fontSize: base.headSize || 17 }, {})).forEach((r) => runs.push(r));
      runs[runs.length - 1].options.breakLine = true;
      const b = sub(it[1], { fontSize: base.size || 14, color: base.color || C.text1, paraSpaceAfter: last ? 0 : 10 });
      b[b.length - 1].options.breakLine = !last; b.forEach((r) => runs.push(r));
    } else {
      const b = base.bullet ? [{ text: plain(it), options: { fontSize: base.size || 14, color: base.color || C.text1, bullet: { indent: 15 }, paraSpaceAfter: last ? 0 : 8 } }] : sub(it, { fontSize: base.size || 14, color: base.color || C.text1, paraSpaceAfter: last ? 0 : 8 });
      b[b.length - 1].options.breakLine = !last; b.forEach((r) => runs.push(r));
    }
  });
  return runs;
}
function pngSize(file) { const b = fs.readFileSync(file); return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) }; }
function fig(s, name, x, y, maxW, maxH, alt) {
  const f = path.join(FIG, name); const { w, h } = pngSize(f); const r = w / h;
  let W_ = maxW, H_ = maxW / r; if (H_ > maxH) { H_ = maxH; W_ = maxH * r; }
  s.addImage({ path: f, x: x + (maxW - W_) / 2, y, w: W_, h: H_, altText: alt, objectName: alt });
  return { x: x + (maxW - W_) / 2, y, w: W_, h: H_ };
}
function card(s, x, y, w, h, fill, name) { s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { color: fill }, objectName: name }); }
function side(s, items, x = 8.75, y = 1.45, w = 4.0, h = 5.3, opts = {}) {
  card(s, x, y, w, h, C.background2, "Takeaway card");
  s.addText(lines(items, opts), tb({ x: x + 0.3, y: y + 0.3, w: w - 0.6, h: h - 0.6 }));
}
function callout(s, big, small, x, y, w, h, name) {
  card(s, x, y, w, h, C.text2, name);
  s.addText([...sub(big, { fontSize: 26, bold: true, color: C.accent1, fontFace: "Cambria" }).map((r, i, a) => (i === a.length - 1 ? (r.options.breakLine = true, r) : r)),
    ...sub(small, { fontSize: 13, color: C.background1 })], tb({ x: x + 0.25, y: y + 0.12, w: w - 0.5, h: h - 0.24, valign: "middle" }));
}
function content(title, section) { const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section }); s.addText(title, { placeholder: "title" }); return s; }
function divider(kicker, title, sub_, section) {
  pres.addSection({ title: section });
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: section });
  s.addText(kicker, tb({ x: 0.8, y: 2.3, w: 11, h: 0.5, fontSize: 18, color: C.accent1, bold: true }));
  s.addText(title, tb({ x: 0.8, y: 2.85, w: 11.5, h: 1.2, fontSize: 40, bold: true, color: C.background1, fontFace: "Cambria" }));
  s.addText(plain(sub_), tb({ x: 0.8, y: 4.15, w: 11, h: 1.0, fontSize: 18, color: HEX.soft }));
  return s;
}
const TH = (t) => ({ text: plain(t), options: { bold: true, color: C.background1, fill: { color: C.text2 } } });
const TD = (t, i, o = {}) => ({ text: plain(t), options: Object.assign({ color: C.text1, fill: { color: i % 2 ? C.background1 : C.background2 } }, o) });
function table(s, rows, x, y, w, colW, fs = 14, rowH = 0.42) {
  s.addTable(rows, { x, y, w, colW, fontSize: fs, fontFace: "Calibri", rowH, border: { type: "solid", pt: 0.5, color: HEX.grid }, valign: "middle", margin: 0.08, objectName: "Data table" });
}

// ---------- numbers ----------
const SZ = ["2.0", "2.5", "3.0", "3.5"];
const nomIdx = SZ.map((v) => S.nominal.nbar.indexOf(Number(v)));
const gz = nomIdx.map((i) => S.nominal.gamma_z[i]), gx = nomIdx.map((i) => S.nominal.gamma_x[i]);
const gxFormula = SZ.map((v) => 2 * 0.02 * ((1 + 0.2) * Number(v) + 0.1));
const hid = R.flip_hidden, nom = R.flip_nominal_tierB, cb = R.clicks.by_size, det = R.detector;
const tau = D.burst_tau;
const photons = SZ.map((v) => (cb[v].tot_flip - cb[v].tot_no) / 0.8);
const tm = S.twomode; const chi2 = tm.chi2; let best = [0, 0], cmin = 1e9;
chi2.forEach((row, i) => row.forEach((c, j) => { if (c < cmin) { cmin = c; best = [i, j]; } }));
const okSet = []; chi2.forEach((row, i) => row.forEach((c, j) => { if (c - cmin <= 2.3) okSet.push(`κ_b = ${tm.kappa_b[i]}, K = ${tm.kerr[j]}`); }));
const c1 = -W["1"].beta[1];
const or = D.oracle_summary;
const rc = R.repcode;
const pg = R.clicks.p_given_peak; const lastPg = pg[pg.length - 1];
const ratio = SZ.map((v) => hid[v].p / nom[v].p);

// ================= TITLE =================
pres.addSection({ title: "Opening" });
let s = pres.addSlide({ masterName: "DARK", sectionTitle: "Opening" });
s.addText("Catch the Flip", tb({ x: 0.8, y: 1.6, w: 11, h: 1.0, fontSize: 48, bold: true, color: C.background1, fontFace: "Cambria" }));
s.addText("The physics of a heralded bit flip, the hidden device, and a detector built from both", tb({ x: 0.8, y: 2.7, w: 11.5, h: 0.9, fontSize: 22, color: HEX.soft }));
[["0.561", "flip suppression at 70 % yield"], ["κ_b ≈ 8, K ≈ 0", "hidden device identified"], [`τ ≈ ${f2(tau)}/κ_2`, "measured burst duration"]].forEach(([a, b], i) => {
  const x = 0.8 + i * 4.0;
  s.addText([...sub(a, { fontSize: 30, bold: true, color: C.accent1, fontFace: "Cambria" }).map((r, k, arr) => (k === arr.length - 1 ? (r.options.breakLine = true, r) : r)), { text: b, options: { fontSize: 15, color: HEX.soft } }],
    tb({ x, y: 4.4, w: 3.7, h: 1.3 }));
});
s.addText("PushQuantum Hackathon 2026  ·  Alice & Bob track", tb({ x: 0.8, y: 6.5, w: 8, h: 0.4, fontSize: 13, color: "8FA3BF" }));
s.addNotes("Title. Three headline numbers: leaderboard-level suppression, the identified hidden device, and a measured physical quantity (burst duration) that ties the physics to the detector.");

// ================= A. PHYSICS =================
divider("Part 1", "The cat qubit and why a flip shines", "Noise bias, the buffer as a witness, and what a flip radiates", "Physics of the flip");
const PH = "Physics of the flip";

s = content("A cat qubit stores a bit in two coherent states", PH);
fig(s, "f01_wigner.png", 0.6, 1.4, 12.1, 3.9, "Wigner functions of cat states");
[["Code space", "|±α⟩ are dark states of κ_2 D[a² − α²]: the buffer emits nothing."], ["Parity = X_L", "Cat superpositions are parity eigenstates; loss and thermal photons flip parity (phase flips)."],
 ["Kicks leave the code space", "a† and a†a deform the lobe; stabilisation pulls it back in ~1/(κ_2 n̄)."]].forEach(([h, t], i) => {
  s.addText(lines([[h, t]], { size: 14 }), tb({ x: 0.6 + i * 4.1, y: 5.5, w: 3.8, h: 1.3 }));
});
s.addNotes("Wigner functions at nbar = 2.5. Left: logical |+alpha>, one lobe. Middle: the even cat, a parity eigenstate, with interference fringes. Right: after a thermal kick a-dagger|+alpha>: the lobe is deformed and has left the code space; this is what the buffer sees.");

s = content("Noise bias: phase flips grow linearly, bit flips fall exponentially", PH);
fig(s, "f02_rates.png", 0.5, 1.4, 7.9, 5.3, "Bit-flip and phase-flip rates vs cat size");
side(s, [["Bit flips: exponential", `Γ_Z ∝ e^(−${f2(D.c_nominal)} n̄) on the nominal device (Liouvillian spectrum, Fock cutoff converged).`],
  ["Phase flips: linear", `Γ_X = 2κ_1[(1+2n_{th})n̄ + n_{th}] matches the spectrum to 1 %: loss and thermal photons flip parity, dephasing does not.`],
  ["Bias at n̄ = 3.5", `T_Z / T_X ≈ ${Math.round(gx[3] / gz[3])}`]]);
s.addNotes(`Rates from the slowest Liouvillian eigenvalues (Fock cutoff converged at N = 20/24/28). Gamma_Z falls exponentially with c = ${f2(D.c_nominal)}; Gamma_X grows linearly. The primer's 2 kappa_1 nbar misses the thermal terms; with them the estimate matches the spectrum (${gxFormula.map((v) => f2(v, 3)).join(", ")} vs ${gx.map((v) => f2(v, 3)).join(", ")}).`);

s = content("Rates of the nominal device (results table, rows 1–3)", PH);
table(s, [[TH("n̄"), TH("Γ_Z (spectrum)"), TH("Γ_X (spectrum)"), TH("Γ_X formula"), TH("p_flip nominal"), TH("p_flip hidden"), TH("hidden / nominal")],
  ...SZ.map((v, i) => [TD(v, i), TD(gz[i].toExponential(2), i), TD(f2(gx[i], 3), i), TD(f2(gxFormula[i], 3), i), TD(`${pct(nom[v].p)} ± ${pct(nom[v].err)}`, i), TD(`${pct(hid[v].p)} ± ${pct(hid[v].err)}`, i), TD(f2(ratio[i]) + "×", i, { bold: true })])],
  0.6, 1.5, 12.1, [0.9, 1.9, 1.8, 1.7, 2.1, 2.1, 1.6], 15, 0.55);
s.addText(lines([["How obtained", "Γ from the slowest non-zero Liouvillian eigenvalues (Fock cutoff 24/28, converged). Flip probabilities per segment (T_{seg} = 200) are label fractions: train split (nominal) and validation split (hidden device), binomial 1σ errors. Labels include readout sampling."],
  ["What it says", "The hidden device flips 1.7–2.8× more often, and the excess grows with n̄: its exponential protection is weaker. Explaining this is Part 2."]], { size: 14 }),
  tb({ x: 0.6, y: 4.6, w: 12.1, h: 2.1 }));
s.addNotes("These are the first rows of the results table in submission_template/README.md. All numbers computed from the package spectrum and the labelled datasets.");

s = content("A flip must cross the origin, and there the buffer lights up", PH);
card(s, 0.6, 1.45, 6.0, 5.3, C.background2, "Mechanism card");
s.addText(lines([["Buffer output = distance from code space", "Adiabatic elimination gives b ≈ −(2ig_2/κ_b)(a² − α²): dark when a² = α²."],
  ["Kicks", "Thermal (a†) and dephasing (a†a) jumps knock the memory off its lobe; it relaxes back in ~1/(κ_2 n̄). Loss (a) does not kick."],
  ["Flip = excursion through the saddle", "Near the origin ⟨a²⟩ ≈ 0, so ⟨L + L†⟩ ≈ −√2 n̄: a negative step in I, in a known quadrature."],
  ["Photon budget", "N_{burst} ≈ n̄² κ_2 τ: big cats flip rarely but loudly."]], { size: 14 }), tb({ x: 0.9, y: 1.7, w: 5.4, h: 4.9 }));
fig(s, "f04_burst_photons.png", 6.9, 1.6, 5.9, 3.2, "Photons radiated per flip");
callout(s, `τ = ${f2(tau)} / κ_2`, `n̄² scaling fits the click records; photons per flip ${photons.map((p) => f2(p, 1)).join(" · ")} (n̄ = 2 → 3.5)`, 6.9, 5.1, 5.9, 1.55, "Tau callout");
s.addNotes(`Photons per flip defined as the excess buffer clicks of flip-labelled segments over flip-free ones (tier A, nominal device), divided by detector efficiency 0.8. A one-parameter fit N = nbar^2 tau gives tau = ${f2(tau)} in units of 1/kappa_2. Right: the peak click count in one time unit separates flips from kicks more strongly for larger cats.`);

s = content("A burst is evidence, not proof: label noise caps every detector", PH);
fig(s, "f05_p_given_peak.png", 0.5, 1.45, 6.4, 4.4, "Flip probability given burst size");
fig(s, "f16_oracle.png", 6.9, 1.45, 6.0, 4.4, "Oracle pneg histogram");
s.addText(lines([`Even the largest bursts (≥ ${R.clicks.cap} clicks in one time unit) give P(flip) = ${pct(lastPg.k / lastPg.N, 0)}: the memory can return, sit at the origin, or flip twice.`,
  `Oracle that saw every jump (300 simulated segments, n̄ = 2.5): best correction S = ${f2(or.S_opt)}. Only ${pct(or.frac_gt_half, 0)} of segments have pneg > 0.5: a flagged memory usually sits near the saddle, not on the other lobe.`], { size: 14, bullet: true }), tb({ x: 0.7, y: 6.0, w: 12, h: 0.9 }));
s.addNotes(`Left: P(flip label | peak clicks) from tier A at nbar 2.5 with Wilson 95% intervals. Right: the oracle's readout probabilities pneg from photon-counting simulations; the optimal rule "flip if pneg > 0.5" leaves a residual flip probability of ${f2(or.opt, 4)} vs ${f2(or.p0, 4)} without herald, S = ${f2(or.S_opt)}. Labels are Bernoulli draws of pneg: this sets a ceiling no detector can beat.`);

s = content("In heterodyne the burst lasts about one time unit and stays in I", PH);
fig(s, "f06_waveform.png", 0.5, 1.4, 8.1, 3.5, "Aligned burst waveforms");
side(s, [["Short", "The aligned excess is 1–2 bins wide (≈ 0.5–1 /κ_2), consistent with τ from the click records."],
  ["Grows with n̄", "Clear at n̄ = 3.5; buried in noise at n̄ = 2, as the d′ estimate predicts."],
  ["Q stays flat", "No burst in Q on either device: no Kerr rotation of the burst. Independent evidence for K ≈ 0."]], 8.75, 1.4, 4.0, 5.35);
s.addText(lines(["Method: centre each record, align on its deepest 3-bin dip, average the strongest half of flips, subtract the same alignment on flip-free records (removes the bias of aligning on noise)."], { size: 12, color: C.accent3 }), tb({ x: 0.6, y: 5.15, w: 7.9, h: 0.8 }));
s.addNotes("This is the open route 'the burst as a waveform'. Subtracting the flip-free control is essential: aligning pure noise on its minimum also creates a dip. Hidden and nominal bursts have the same width: with kappa_b ~ 8 the buffer response time 2/kappa_b ~ 0.25 is shorter than one 0.5 bin, so the finite bandwidth does not visibly reshape the burst. The finite bandwidth matters for the flip rate (Part 2), not for the burst shape.");

s = content("Detectability: why averaging fails and matched filters work", PH);
const dprime = SZ.map((v) => Number(v) * Math.sqrt(2 * tau));
const dilute = Math.sqrt(200 / tau);
table(s, [[TH("n̄"), TH("hidden p_flip"), TH("burst height √2 n̄"), TH("d′ matched filter"), TH("d′ segment mean")],
  ...SZ.map((v, i) => [TD(v, i), TD(pct(hid[v].p), i), TD(f2(Math.SQRT2 * Number(v)), i), TD(f2(dprime[i]), i, { bold: true }), TD(f2(dprime[i] / dilute), i)])],
  0.6, 1.5, 7.6, [1.0, 1.6, 1.8, 1.7, 1.5], 15, 0.55);
s.addText(lines([["Optimal SNR", `d′² = ∫s²dt / S_ξ = 2 n̄² τ = 2 N_{burst} (unit-spectral-density white noise, τ = ${f2(tau)} measured).`],
  ["Averaging dilutes", `The whole-segment mean loses √(T_{seg}/τ) ≈ ${f2(dilute, 0)}×: d′ ≈ 0.2. That is why the mean of I scores ${f2(R.baselines["mean of I"].suppression)}.`],
  ["Look-elsewhere", "Scanning ~130 windows pushes the noise maximum to ≈ 2.7σ: at n̄ = 2 the burst sits at the noise floor, and the prior (26 %) carries the decision."]], { size: 14 }),
  tb({ x: 0.6, y: 4.5, w: 7.6, h: 2.3 }));
callout(s, "√(2 N_{burst})", "the matched-filter SNR is set by the number of photons a flip radiates", 8.75, 1.5, 4.0, 1.6, "SNR callout");
s.addText(lines([["Design consequence", "Boxcar filters of 1–2 time units on I, scanned over onset: the generalised likelihood-ratio test for a rectangular burst of unknown start and length."]], { size: 14 }), tb({ x: 8.75, y: 3.4, w: 4.0, h: 2.5 }));
s.addNotes("d-prime uses the measured burst duration from the click records, so the detector design rests on a measured physical quantity, not on the slide's tau ~ 1 assumption.");

// ================= B. HIDDEN DEVICE =================
divider("Part 2", "Identifying the hidden device", "Finite buffer bandwidth κ_b and Kerr K: which one weakens the cat?", "Hidden device");
const HD = "Hidden device";

s = content("The hidden device flips more, and the gap grows with cat size", HD);
fig(s, "f03_flipprob.png", 0.5, 1.4, 7.4, 5.3, "Flip probability nominal vs hidden");
side(s, [["Nominal", `Labels follow the spectrum: p = ½(1 − e^(−Γ_Z T)), c = ${f2(D.c_nominal)}.`],
  ["Hidden", `Ratio ${ratio.map((r) => f2(r, 1)).join(" → ")} from n̄ = 2 to 3.5. Fitted slope c = ${f2(c1)}: the exponential protection is weaker.`],
  ["Two suspects", "The device sheet announces the type of change: the buffer is a real mode with finite κ_b, and a Kerr term −(K/2)a†²a² is added. Values are private."]], 8.4, 1.4, 4.35, 5.3);
s.addNotes("The growth of the ratio with nbar is the fingerprint: a constant multiplicative change (e.g. readout) would give a constant ratio. A constant-ratio model fits poorly (chi2 ~ 24 for 3 dof).");

s = content("Two candidate mechanisms predict different fingerprints", HD);
card(s, 0.6, 1.45, 5.95, 5.3, C.background2, "Bandwidth card");
s.addText(lines([["Finite buffer bandwidth κ_b", "H = g_2(a²b† + a†²b) − ε_d(b + b†), κ_2 = 4g_2²/κ_b held fixed."],
  ["Adiabatic elimination breaks", "It needs κ_b ≫ g_2√n̄. At κ_b = 8, g_2 = 1.41: g_2√n̄ = 2.6 at n̄ = 3.5, only 3× smaller than κ_b."],
  ["Prediction", "Confinement saturates at large n̄ → flip rate rises faster than nominal → hidden/nominal ratio grows with n̄. Burst shape: response time 2/κ_b ≈ 0.25 < one bin, barely filtered."]], { size: 14, head: C.accent2 }),
  tb({ x: 0.9, y: 1.7, w: 5.35, h: 4.9 }));
card(s, 6.8, 1.45, 5.95, 5.3, C.background2, "Kerr card");
s.addText(lines([["Kerr nonlinearity K", "H_K = −(K/2) a†² a²: the memory frequency depends on photon number."],
  ["Rotates and shears the lobes", "Photon-number-dependent frequency pulls the field off the real axis, away from the stabilised manifold."],
  ["Prediction", "Raises the flip rate, more for big cats and narrow buffers, but by ≤ 10 % for K ≤ 0.1 at κ_b ≥ 8. Would rotate the burst from I into Q."]], { size: 14, head: C.accent4 }),
  tb({ x: 7.1, y: 1.7, w: 5.35, h: 4.9 }));
s.addNotes("Two-mode model from docs/THEORY.md section 2. g2 = sqrt(kappa2 kappa_b)/2, so lowering kappa_b at fixed kappa2 lowers g2 more slowly than kappa_b: the ratio kappa_b/(g2 alpha) = 2 sqrt(kappa_b)/alpha shrinks. Data test both predictions: the rate ratio vs nbar, and the Q quadrature.");

s = content("Fitting the two-mode model to the hidden flip rates", HD);
fig(s, "f14_twomode_ratio.png", 0.5, 1.4, 12.3, 4.3, "Two-mode model predictions vs data");
s.addText(lines([`Each curve: two-mode Liouvillian spectrum (Fock 24/28 × 4) at the four cat sizes, divided by the nominal spectrum. Calibration c(n̄) = p(train) / p(spectrum) absorbs readout error (${tm.calib.map((v) => f2(v)).join(", ")}).`,
  "κ_b moves the ratio by a factor ~2 across the grid and reproduces its rise with n̄; Kerr up to 0.1 changes it by only a few % at κ_b = 8. The rates pin κ_b and only bound K."], { size: 14, bullet: true }),
  tb({ x: 0.7, y: 5.85, w: 12, h: 1.0 }));
s.addNotes("This is notebook section 4.4. 5 x 4 grid, 80 spectra. The binomial chi-square is computed against validation counts.");

s = content("Δχ² map: bandwidth-limited, not Kerr-detuned", HD);
fig(s, "f13_chi2map.png", 0.5, 1.4, 7.6, 5.4, "Delta chi-square map");
side(s, [["Best fit", `κ_b = ${tm.kappa_b[best[0]]}, K = ${tm.kerr[best[1]]}, χ² = ${f2(cmin, 1)} (4 points, 2 parameters).`],
  ["Allowed region (Δχ² ≤ 2.3)", okSet.join("; ") + "."],
  ["Three independent arguments", "1. Rate ratio rises with n̄ (κ_b shape). 2. No burst in Q (no rotation). 3. Q features add nothing to the detector."],
  ["Caveat", "Coarse grid: K ≲ 0.02 cannot be excluded; κ_b between 4 and 16 deserves a finer scan."]], 8.4, 1.4, 4.35, 5.4, { size: 13.5 });
s.addNotes("Answer to the open route 'Identify the hidden device: which of the two matters?' - finite buffer bandwidth. Note the grid resolution: the conclusion is kappa_b of order 8 and K small, not exact values.");

s = content("Sealed prediction: empirical fit and physics model agree", HD);
fig(s, "f15_sealed.png", 0.5, 1.35, 12.3, 3.7, "Sealed prediction models");
const pt = D.pred_table.filter((r) => [2.75, 3.25, 4.0, 4.5].includes(r.nbar));
table(s, [[TH("n̄★"), TH("WLS degree 1"), TH("WLS degree 2"), TH("physics (κ_b, K)")],
  ...pt.map((r, i) => [TD(f2(r.nbar), i), TD(`${f2(100 * r.w1[0])} ± ${f2(100 * r.w1[1])} %`, i), TD(`${f2(100 * r.w2[0])} ± ${f2(100 * r.w2[1])} %`, i), TD(`${f2(r.phys[0])} [${f2(r.phys[1])}, ${f2(r.phys[2])}] %`, i)])],
  0.6, 5.15, 7.6, [1.0, 2.2, 2.2, 2.2], 12.5, 0.33);
callout(s, "n̄★ = [  ] → [  ] ± [  ] %", `WLS degree 1 (χ²/dof = ${f2(W["1"].chi2, 1)}/${W["1"].dof}, error × √(χ²/dof)); outside [2, 3.5] add the model spread in quadrature`, 8.5, 5.15, 4.25, 1.6, "Sealed callout");
s.addNotes(`WLS: ln Gamma_Z linear (or quadratic) in nbar, weights from binomial errors propagated by the delta method; error inflated by the Birge factor sqrt(chi2/dof) = ${f2(Math.sqrt(W["1"].chi2 / W["1"].dof))}. Physics: two-mode spectrum over the Delta chi2 <= 2.3 region; its band covers parameter-grid spread only, so it is a cross-check rather than the error bar. Inside the data range all three agree within errors; beyond 3.5 the gap measures model uncertainty.`);

// ================= C. DETECTOR =================
divider("Part 3", "From physics to a detector", "Matched filters, calibrated posteriors, and where the budget goes", "Detector");
const DT = "Detector";

s = content("Score = posterior probability of a flip: the optimal ranking", DT);
s.addChart(pres.charts.BAR, [
  { name: "Our detector", labels: SZ.map((v) => "n̄ = " + v), values: SZ.map((v) => det.by_size[v].discarded) },
  { name: "Cat size alone", labels: SZ.map((v) => "n̄ = " + v), values: SZ.map((v) => R.baselines["cat size alone"].by_size[v]) },
  { name: "Mean of I", labels: SZ.map((v) => "n̄ = " + v), values: SZ.map((v) => R.baselines["mean of I"].by_size[v]) },
], { x: 0.5, y: 1.4, w: 7.8, h: 5.3, barDir: "col", chartColors: [HEX.amber, "8FA3BF", HEX.red], barGapWidthPct: 60,
  showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0%", dataLabelColor: HEX.ink, dataLabelFontSize: 11, dataLabelFontFace: "+mn-lt",
  valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 1.15, valGridLine: { style: "none" }, catGridLine: { style: "none" },
  catAxisLabelColor: HEX.ink, catAxisLabelFontSize: 14, catAxisLabelFontFace: "+mn-lt", showLegend: true, legendPos: "b", legendFontSize: 13, legendFontFace: "+mn-lt", legendColor: HEX.ink,
  showTitle: true, title: "Share of each cat size discarded (30 % budget overall)", titleFontSize: 13, titleColor: HEX.mute, titleFontFace: "+mn-lt", objectName: "Budget allocation chart" });
side(s, [["Fractional knapsack", "Each discard costs one segment and removes P(flip | record, n̄) flips in expectation: discard the top 30 % of the posterior, pooled over sizes."],
  ["Consequences", "No class weights (they distort the posterior). One logistic model per cat size, so each keeps its own prior."],
  ["Where it spends", "All of n̄ = 2, two thirds of 2.5, and only the loudest 12 % of 3.5."]], 8.75, 1.4, 4.0, 5.3);
s.addNotes("Results-table row: fraction of each cat size discarded on the validation split. Our detector spends the budget where flips are likely (small cats) but still reaches into large cats when a loud burst is seen: 88 of 174 flips at nbar 3.5 removed with only 12% of those segments.");

s = content("Seven physics features: dip depth, excess area, time below", DT);
fig(s, "f07_features.png", 0.5, 1.35, 8.2, 4.2, "Feature illustration");
side(s, [["d_2, d_3, d_4", "Deepest dip of 1, 1.5, 2 time-unit boxcars: the matched-filter scan."],
  ["a_{2.0}, a_{2.5}, a_{3.0}", "Area below thresholds at 2.4σ, 3.1σ, 3.7σ of the 3-bin noise: sustained flip vs brief kick."],
  ["n_{below}", "Bins below −2.5: duration of the excursion."],
  ["Classifier", "Standardised, L2 logistic (C = 5) per n̄, 5-fold out-of-fold, 5-model ensemble on test."]], 8.9, 1.35, 3.85, 5.4, { size: 13 });
s.addText(lines(["Shaded: excess area below −2.0 that feeds a_{2.0}. Red lines: the three thresholds."], { size: 12, color: C.accent3 }), tb({ x: 0.6, y: 5.75, w: 8, h: 0.5 }));
s.addNotes("Every feature has a physical reason. Centering removes slow offsets; the burst shifts the mean by only h tau / T ~ 0.02. The model was trained on the hidden-device validation split, which captures the higher flip rate directly.");

s = content(`Result: 1 − ρ₇₀ = ${f2(det.suppression, 3)}, full leaderboard points`, DT);
fig(s, "f09_ps_curve.png", 0.5, 1.4, 6.3, 4.3, "Post-selection curve");
fig(s, "f11_reliability.png", 6.8, 1.4, 6.0, 4.3, "Calibration per cat size");
table(s, [[TH("AUC"), TH("1 − ρ₇₀"), TH("yield"), TH("TPR"), TH("FPR"), TH("S"), TH("points")],
  [TD(f2(det.auc, 3), 0), TD(f2(det.suppression, 3), 0, { bold: true }), TD(f2(det.yield), 0), TD(f2(det.tpr), 0), TD(f2(det.fpr), 0), TD(f2(det.S), 0), TD(`${f2(det.points, 0)} / 10`, 0)]],
  0.6, 5.95, 12.1, [1.7, 1.8, 1.6, 1.6, 1.6, 1.6, 2.2], 14, 0.4);
s.addNotes(`All numbers out-of-fold on the validation split. The submitted tierB.csv matches this model's ensemble to ${R.submission_check.max_abs_diff.toExponential(1)} (float precision), 30% flagged. Calibration: the posteriors track observed rates per size, which the knapsack argument requires.`);

s = content("Negative results we can defend", DT);
const neg = [["Q quadrature", "IQ rotation ±10°: 0.53 / 0.52; I² + Q²: 0.38; Q veto: 0.54", "Consistent with K ≈ 0: no burst in Q"],
  ["21 features", "0.52", "Overfits 586 flips"], ["Gradient boosting", "0.50 (AUC 0.75)", "Hard splits, few positives"],
  ["Train on nominal, transfer", "0.54", "Device shift: rates and prior differ"], ["Gaussian matched filter", "0.551", "Close; boxcar bank slightly better"],
  ["Histogram likelihood ratio", "0.549", "Good baseline, combines features poorly"]];
table(s, [[TH("Tried"), TH("1 − ρ₇₀ (5-fold)"), TH("Physics / statistics reason")], ...neg.map((r, i) => r.map((t) => TD(t, i)))], 0.6, 1.5, 12.1, [3.0, 4.6, 4.5], 14, 0.55);
s.addNotes("Reference model for the Q tests was the 3-slice model at 0.556. The Q result doubles as physics evidence for the hidden-device identification.");

// ================= D. CAPSTONE =================
divider("Part 4", "What the herald is worth", "Post-selection, Pauli-frame correction, and the repetition code", "Capstone");
const CP = "Capstone";

s = content("Same flags, opposite outcomes: discard, never correct", CP);
fig(s, "f12_herald.png", 0.5, 1.4, 6.8, 4.6, "Post-selection vs correction");
side(s, [["Correction condition", "Applying X helps only if TPR·p > FPR·(1 − p): flag precision above 50 %."],
  ["Our flags", `Precision ${pct(R.herald_sweep.rows[0].precision, 0)} at the top 1 %, ${pct(R.herald_sweep.rows[5].precision, 0)} at 30 %. S = ${f2(R.herald_sweep.rows[0].S)} → ${f2(det.S)}: always worse.`],
  ["Even the oracle", `S = ${f2(or.S_opt)} at best: label noise from pneg limits any correction.`],
  ["Post-selection", `Flips among kept: ${pct(R.herald_sweep.p0)} → ${pct(R.herald_sweep.rows[5].p_kept)} at 70 % yield.`]], 7.6, 1.4, 5.15, 5.35, { size: 13.5 });
s.addNotes("Step 4.2 with our actual out-of-fold scores. Post-selection needs only ranking (AUC); correction needs precision > 50%, which the physics (label noise, d' of 2-4 and flip rates of 4-26%) does not allow.");

s = content("In a repetition code a herald is worth more as d grows", CP);
table(s, [[TH("distance d"), TH("no herald"), TH("post-selected"), TH("cycle yield"), TH("Pauli-frame corrected")],
  ...["3", "5", "7"].map((d, i) => [TD(d, i), TD(f2(rc.d[d].none, 3), i), TD(f2(rc.d[d].post, 3), i, { bold: true, color: C.accent2 }), TD(pct(rc.d[d].post_yield, 0), i), TD(f2(rc.d[d].corr, 3), i, { color: C.accent4 })])],
  0.6, 1.5, 7.6, [1.3, 1.5, 1.7, 1.5, 1.6], 15, 0.55);
s.addText(lines([["Why bit flips grow with d", "The repetition code corrects phase flips; a bit flip commutes with every X_{i}X_{i+1} stabiliser, so any odd number of flips is a logical flip: P ≈ ½[1 − (1 − 2p)^d]."],
  ["Measured inputs", `n̄ = 3.5, p = ${pct(rc.p, 2)}; our flags on that size: ρ = ${f2(rc.rho)}, yield ${f2(rc.yield)}, TPR ${f2(rc.tpr)}, FPR ${f2(rc.fpr)}.`]], { size: 14 }),
  tb({ x: 0.6, y: 4.0, w: 7.6, h: 2.8 }));
callout(s, `${f2(rc.d["5"].none, 3)} → ${f2(rc.d["5"].post, 3)}`, `d = 5 logical bit flips per cycle with post-selection (yield ${pct(rc.d["5"].post_yield, 0)}); correction makes it ${f2(rc.d["5"].corr, 3)}`, 8.6, 1.5, 4.15, 1.9, "Repcode callout");
s.addNotes("Results-table row 'logical bit-flip probability per cycle, d = 5'. Numbers from catchtheflip.repcode with our measured detector performance at nbar 3.5, not the notebook's illustrative rho = 0.4.");

// ================= E. CLOSE =================
divider("Wrap-up", "Results, AI errors, and what is next", "", "Wrap-up");
const WU = "Wrap-up";

s = content("Results table (submission README)", WU);
const rows = [
  ["Γ_Z nominal, n̄ = 2 / 2.5 / 3 / 3.5", gz.map((v) => v.toExponential(1)).join(" · "), "Liouvillian spectrum"],
  ["Γ_X nominal", gx.map((v) => f2(v, 3)).join(" · "), "spectrum; matches 2κ_1[(1+2n_th)n̄+n_th]"],
  ["p_flip nominal / hidden", SZ.map((v) => `${f2(100 * nom[v].p, 1)}/${f2(100 * hid[v].p, 1)}`).join(" · ") + " %", "label fractions, train / val"],
  ["Photons per flip (nominal)", photons.map((p) => f2(p, 1)).join(" · "), `excess clicks / η; fits n̄²τ, τ = ${f2(tau)}`],
  ["Detector (val, OOF)", `AUC ${f2(det.auc, 3)}, 1−ρ₇₀ ${f2(det.suppression, 3)}, TPR ${f2(det.tpr)}, FPR ${f2(det.fpr)}, S ${f2(det.S)}`, "5-fold out-of-fold"],
  ["Discarded share per n̄", SZ.map((v) => pct(det.by_size[v].discarded, 0)).join(" · "), "validation"],
  ["Leaderboard (test)", "[  ]", "fill in from leaderboard"],
  ["P(flip | large burst)", `${pct(lastPg.k / lastPg.N, 0)} (≥ ${R.clicks.cap} clicks / unit, n̄ = 2.5)`, "tier A; label noise caps it"],
  ["Oracle best S", f2(or.S_opt), "300 counting segments, n̄ = 2.5"],
  ["d = 5: none / post / corrected", `${f2(rc.d["5"].none, 3)} / ${f2(rc.d["5"].post, 3)} (yield ${pct(rc.d["5"].post_yield, 0)}) / ${f2(rc.d["5"].corr, 3)}`, "n̄ = 3.5, measured flags"],
];
table(s, [[TH("quantity"), TH("value"), TH("how obtained")], ...rows.map((r, i) => r.map((t) => TD(t, i)))], 0.6, 1.35, 12.1, [3.6, 4.9, 3.6], 12, 0.47);
s.addNotes("Paste into RESULTS.md. The leaderboard test score must be copied from the leaderboard page.");

s = content("Two things AI got wrong and how we caught them", WU);
const ai = [["Fed the sealed fit its own flags", "The AI-written cell measured flip rates from our 30 % discard decisions. That measures budget, not Γ_Z, and exceeds 50 % at n̄ = 2, where ln(1 − 2p) is undefined.", "Caught: required p = k/N to reproduce the published 26.2 / 11.3 / 8.4 / 4.3 %."],
  ["Sold an in-sample score", "It reported 0.571, fitted and scored on the same records, and called plain L2 logistic regression \"Bayesian\".", "Caught: re-ran 5-fold out-of-fold. We report the honest 0.561."]];
ai.forEach(([h, what, caught], i) => {
  const x = 0.6 + i * 6.2; card(s, x, 1.45, 5.9, 4.6, C.background2, `AI error ${i + 1}`);
  s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: 1.75, w: 0.65, h: 0.65, fill: { color: C.accent4 }, line: { color: C.accent4 }, objectName: `AI marker ${i + 1}` });
  s.addText(String(i + 1), tb({ x: x + 0.3, y: 1.75, w: 0.65, h: 0.65, align: "center", valign: "middle", fontSize: 20, bold: true, color: C.background1 }));
  s.addText(h, tb({ x: x + 1.15, y: 1.75, w: 4.5, h: 0.65, valign: "middle", fontSize: 20, bold: true, color: C.text2, fontFace: "Cambria" }));
  s.addText(sub(what, { fontSize: 15, color: C.text1 }), tb({ x: x + 0.3, y: 2.75, w: 5.3, h: 1.8 }));
  s.addText(caught, tb({ x: x + 0.3, y: 4.65, w: 5.3, h: 1.2, fontSize: 15, bold: true, color: C.accent2 }));
});
s.addNotes("Required slide. Also: an AI review got the sign of the nbar = 2.5 residual wrong (it lies below the line), and the completion notebook dropped the physics-fit section 4.4.");

s = pres.addSlide({ masterName: "DARK", sectionTitle: WU });
s.addText("What we bring", tb({ x: 0.8, y: 0.6, w: 11, h: 0.9, fontSize: 40, bold: true, color: C.background1, fontFace: "Cambria" }));
[[`τ = ${f2(tau)} / κ_2`, "burst duration measured, n̄² photon law confirmed"], ["κ_b, not K", "hidden device identified three independent ways"],
  [f2(det.suppression, 3), "flip suppression from physics-derived features"], ["Discard, don't correct", "precision < 50 % even for the oracle"]].forEach(([a, b], i) => {
  const x = 0.8 + (i % 2) * 6.1, y = 1.9 + Math.floor(i / 2) * 2.1;
  s.addText([...sub(a, { fontSize: 32, bold: true, color: C.accent1, fontFace: "Cambria" }).map((r, k, arr) => (k === arr.length - 1 ? (r.options.breakLine = true, r) : r)), { text: b, options: { fontSize: 17, color: HEX.soft } }],
    tb({ x, y, w: 5.7, h: 1.7 }));
});
s.addText("Next: quantum-filter detector (the optimal posterior), finer κb scan, importance sampling for n̄ > 4", tb({ x: 0.8, y: 6.2, w: 11.5, h: 0.5, fontSize: 16, color: C.background1 }));
s.addNotes("Close. Physics first: every number on this slide is measured or fitted from the data.");

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
