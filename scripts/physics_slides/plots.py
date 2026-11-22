import json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(sys.argv[1]); FIG = OUT / "fig"; FIG.mkdir(exist_ok=True)
R = json.load(open(OUT / "fast.json"))
S = json.load(open(OUT / "slow.json")) if (OUT / "slow.json").exists() else {}
NAVY, AMBER, TEAL, RED, GRAY, INK, MUTE = "#0E1A2B", "#F2A541", "#2A9D8F", "#D1495B", "#8FA3BF", "#1B2A3F", "#5B6B80"
plt.rcParams.update({"font.family": "Arial", "font.size": 15, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTE, "axes.labelcolor": INK, "xtick.color": MUTE, "ytick.color": MUTE,
                     "axes.titlesize": 15, "axes.titlecolor": INK, "legend.frameon": False, "legend.fontsize": 12.5,
                     "savefig.dpi": 200, "savefig.bbox": "tight", "lines.linewidth": 2.2})
SIZES = ["2.0", "2.5", "3.0", "3.5"]; NB = np.array([2.0, 2.5, 3.0, 3.5]); T = 200.0
SIZE_COL = {"2.0": RED, "2.5": AMBER, "3.0": TEAL, "3.5": NAVY}
def save(fig, name): fig.savefig(FIG / name); plt.close(fig); print("saved", name)
pflip = lambda g: 0.5 * (1 - np.exp(-np.asarray(g) * T))

# ---------- WLS sealed-prediction (verbatim maths of notebook 4.3) ----------
hid = R["flip_hidden"]; N = np.array([hid[s]["n"] for s in SIZES]); K = np.array([hid[s]["k"] for s in SIZES])
p = K / N; sp = np.sqrt(p * (1 - p) / N); g = -np.log(1 - 2 * p) / T; sg = 2 / (T * (1 - 2 * p)) * sp
y = np.log(g); sy = sg / g; w = 1 / sy**2
def wls(deg):
    A = np.column_stack([NB**j for j in range(deg + 1)]); cov = np.linalg.inv(A.T @ (w[:, None] * A)); beta = cov @ (A.T @ (w * y))
    chi2 = float(np.sum(w * (y - A @ beta) ** 2)); return beta, cov, chi2, len(NB) - deg - 1
FITS = {d: wls(d) for d in (1, 2)}
def predict(nb, deg=1, inflate=True):
    beta, cov, chi2, dof = FITS[deg]; x = np.array([nb**j for j in range(deg + 1)])
    s = (max(1, np.sqrt(chi2 / dof)) if inflate else 1) * np.sqrt(x @ cov @ x); G = np.exp(x @ beta)
    return 0.5 * (1 - np.exp(-G * T)), 0.5 * T * np.exp(-G * T) * G * s
json.dump({d: {"beta": FITS[d][0].tolist(), "chi2": FITS[d][2], "dof": FITS[d][3]} for d in FITS}, open(OUT / "wls.json", "w"))

# ---------- f02 rates ----------
if "nominal" in S:
    nb = np.array(S["nominal"]["nbar"]); gz = np.array(S["nominal"]["gamma_z"]); gx = np.array(S["nominal"]["gamma_x"])
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    ax.semilogy(nb, gz, "o-", color=NAVY, label=r"bit flip $\Gamma_Z$")
    ax.semilogy(nb, gx, "s-", color=TEAL, label=r"phase flip $\Gamma_X$")
    nbf = np.linspace(1.5, 4.5, 50); ax.semilogy(nbf, 2 * 0.02 * ((1 + 0.2) * nbf + 0.1), ":", color=TEAL, lw=1.8, label=r"$2\kappa_1[(1+2n_{th})\bar n+n_{th}]$")
    c = -np.polyfit(nb, np.log(gz), 1)[0]
    ax.text(1.55, 2.5e-4, f"$\\Gamma_Z \\propto e^{{-{c:.2f}\\,\\bar n}}$", color=NAVY, fontsize=16)
    ax.set(xlabel=r"cat size $\bar n$", ylabel=r"rate (units of $\kappa_2$)", title="Nominal device, Liouvillian spectrum")
    ax.legend(loc="center right", bbox_to_anchor=(1.0, 0.45)); save(fig, "f02_rates.png")
    S["c_nominal"] = c

# ---------- f03 flip probability nominal vs hidden ----------
nomB = R["flip_nominal_tierB"]; rat = [hid[s]["p"] / nomB[s]["p"] for s in SIZES]
fig, ax = plt.subplots(figsize=(6.6, 4.4))
ax.errorbar(NB, [hid[s]["p"] * 100 for s in SIZES], [hid[s]["err"] * 100 for s in SIZES], fmt="o", color=AMBER, ms=9, capsize=4, label="hidden device (val labels)")
ax.errorbar(NB, [nomB[s]["p"] * 100 for s in SIZES], [nomB[s]["err"] * 100 for s in SIZES], fmt="s", color=GRAY, ms=8, capsize=4, label="nominal device (train labels)")
if "nominal" in S:
    ax.plot(nb, pflip(gz) * 100, "-", color=INK, lw=1.5, label="nominal, spectrum (no readout error)")
ax.set_yscale("log"); ax.set_xlim(1.8, 3.7); ax.set_ylim(0.5, 40)
ax.set(xlabel=r"cat size $\bar n$", ylabel="flip probability per segment (%)", title=f"Hidden device flips {min(rat):.1f}–{max(rat):.1f}× more than nominal")
ax.legend(loc="lower left", fontsize=11.5); save(fig, "f03_flipprob.png")

# ---------- f04 burst photons (tier A) ----------
cb = R["clicks"]["by_size"]; eta = 0.8
extra = np.array([(cb[s]["tot_flip"] - cb[s]["tot_no"]) / eta for s in SIZES]); extra_e = np.array([cb[s]["tot_flip_se"] / eta for s in SIZES])
fig, ax = plt.subplots(1, 2, figsize=(12, 4.3))
ax[0].errorbar(NB, extra, extra_e, fmt="o", color=AMBER, ms=9, capsize=4, label="data: extra photons in flip segments")
tau = np.sum(extra * NB**2) / np.sum(NB**4); nbf = np.linspace(1.8, 3.7, 50)
ax[0].plot(nbf, tau * nbf**2, "--", color=INK, label=f"$\\bar n^2\\kappa_2\\tau$, fit $\\tau$ = {tau:.2f}")
ax[0].set(xlabel=r"cat size $\bar n$", ylabel="buffer photons per flip", title="Photons radiated by a flip (η = 0.8 corrected)"); ax[0].legend(loc="upper left", fontsize=11.5)
ax[1].plot(NB, [cb[s]["peak_flip"] for s in SIZES], "o-", color=RED, label="flip label")
ax[1].plot(NB, [cb[s]["peak_no"] for s in SIZES], "s-", color=GRAY, label="no flip")
ax[1].set(xlabel=r"cat size $\bar n$", ylabel="max clicks in 1 time unit", title="Burst stands out more for big cats"); ax[1].legend()
save(fig, "f04_burst_photons.png"); R["burst_tau"] = tau

# ---------- f05 P(flip | peak) ----------
pg = R["clicks"]["p_given_peak"]; xs = np.array([r["n"] for r in pg]); Nn = np.array([r["N"] for r in pg]); Kk = np.array([r["k"] for r in pg])
pp_ = Kk / Nn; z = 1.96; den = 1 + z * z / Nn; cen = (pp_ + z * z / (2 * Nn)) / den; dl = z / den * np.sqrt(pp_ * (1 - pp_) / Nn + z * z / (4 * Nn * Nn))
fig, ax = plt.subplots(figsize=(6.6, 4.4))
ax.errorbar(xs, pp_, [pp_ - np.maximum(0, cen - dl), np.minimum(1, cen + dl) - pp_], fmt="o-", color=NAVY, capsize=4, ms=8)
ax.axhline(0.5, ls=":", color=GRAY); ax.text(xs[0], 0.53, "50 %: where correcting would start to pay", color=MUTE, fontsize=12)
ax.set_ylim(0, 1); ax.set(xlabel=f"peak clicks in 1 time unit (last bin ≥ {R['clicks']['cap']})", ylabel="P(flip label | burst)", title=r"Nominal click records, $\bar n = 2.5$")
save(fig, "f05_p_given_peak.png")

# ---------- f06 burst waveform ----------
fig, ax = plt.subplots(1, 2, figsize=(12, 4.3), sharey=True)
for a, nbs in zip(ax, ["2.0", "3.5"]):
    for nm, col in [("hidden", AMBER), ("nominal", GRAY)]:
        wv = R["waveform"][nm][nbs]; t = np.array(wv["t"])
        a.plot(t, np.array(wv["I"]) - np.array(wv["I_noflip"]), "-", color=col, label=f"I, {nm} (flip − no-flip)")
        a.plot(t, np.array(wv["Q"]), ":", color=col, lw=1.6, label=f"Q, {nm}")
    a.axhline(0, color=GRAY, lw=0.8); a.set(xlabel="time from deepest dip (1/$\kappa_2$)", title=f"$\\bar n$ = {nbs}: strongest half of flips, aligned", xlim=(-8, 8))
ax[0].set_ylabel("mean quadrature"); ax[1].legend(fontsize=11, loc="lower right")
save(fig, "f06_waveform.png")

# ---------- f07 features ----------
ex = R["example"]; t = np.arange(400) * 0.5
fig, ax = plt.subplots(2, 1, figsize=(12, 5.2), sharex=True)
for a, key, title in [(ax[0], "flip", "flip label"), (ax[1], "noflip", "no flip")]:
    a.plot(t, ex[key]["I"], color=GRAY, lw=0.8, label="I (centred)")
    a.plot(t, ex[key]["s3"], color=NAVY if key == "flip" else MUTE, lw=1.8, label="3-bin boxcar")
    for th, ls in [(2.0, ":"), (2.5, "--"), (3.0, "-")]:
        a.axhline(-th, color=RED, ls=ls, lw=1.2)
    s3 = np.array(ex[key]["s3"]); a.fill_between(t, s3, -2.0, where=s3 < -2.0, color=AMBER, alpha=0.8)
    a.set_ylim(-6, 6); a.set_ylabel("I quadrature"); a.text(1, 3.6, f"{title}, n̄ = 3.5  ·  model P(flip) = {ex[key]['score']:.2f}", fontsize=13, color=INK)
ax[1].set_xlabel("time (1/$\kappa_2$)"); ax[1].legend(loc="upper right", ncol=2, fontsize=11)
save(fig, "f07_features.png")

# ---------- f09 post-selection curve ----------
fig, ax = plt.subplots(figsize=(6.6, 4.4))
for nm, col, lab in [("ours", AMBER, "our detector"), ("cat size alone", GRAY, "cat size alone"), ("mean of I", RED, "mean of I")]:
    c = R["ps_curve"][nm]; ax.plot(c["Y"], c["rho"], color=col, label=lab)
ax.axvline(0.7, ls=":", color=INK, lw=1); ax.plot([0.7], [R["detector"]["rho"]], "o", color=AMBER, ms=9)
ax.text(0.72, R["detector"]["rho"] - 0.08, f"$\\rho_{{70}}$ = {R['detector']['rho']:.3f}", color=INK)
ax.set(xlabel="yield (fraction kept)", ylabel="residual flip fraction ρ", title="Post-selection curve, validation (out-of-fold)", xlim=(0.3, 1), ylim=(0, 1.05))
ax.legend(loc="upper left"); save(fig, "f09_ps_curve.png")

# ---------- f11 reliability ----------
fig, ax = plt.subplots(figsize=(6.6, 4.4))
for s in SIZES:
    r = R["reliability"][s]; ax.plot(r["pred"], r["obs"], "o-", color=SIZE_COL[s], label=f"n̄ = {s}", ms=7)
ax.plot([0, 0.7], [0, 0.7], "--", color=GRAY, lw=1.2)
ax.set(xlabel="predicted P(flip)", ylabel="observed flip fraction", title="Calibration per cat size (6 bins each)", xlim=(0, 0.7), ylim=(0, 0.7))
ax.legend(); save(fig, "f11_reliability.png")

# ---------- f12 herald ----------
hs = R["herald_sweep"]; f = np.array([r["f"] for r in hs["rows"]])
fig, ax = plt.subplots(figsize=(6.6, 4.4))
ax.plot(f * 100, [r["p_kept"] * 100 for r in hs["rows"]], "o-", color=TEAL, label="post-selection: flips among kept")
ax.plot(f * 100, [r["x_resid"] * 100 for r in hs["rows"]], "s-", color=RED, label="apply X to flagged: residual flips")
ax.axhline(hs["p0"] * 100, ls="--", color=GRAY, label="no herald")
ax.axvline(30, ls=":", color=INK, lw=1)
ax.set(xlabel="segments flagged (%)", ylabel="flip probability (%)", title="Same flags, opposite outcomes"); ax.legend(loc="upper left", fontsize=11.5)
save(fig, "f12_herald.png")

# ---------- slow-dependent ----------
if "twomode" in S:
    tm = S["twomode"]; chi2 = np.array(tm["chi2"]); kbs = np.array(tm["kappa_b"]); kerrs = np.array(tm["kerr"])
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    dchi = chi2 - chi2.min()
    im = ax.imshow(np.log10(dchi + 1), origin="lower", cmap="cividis_r", aspect="auto")
    ax.set_xticks(range(len(kerrs)), [f"{k:g}" for k in kerrs]); ax.set_yticks(range(len(kbs)), [f"{k:g}" for k in kbs])
    for i in range(len(kbs)):
        for j in range(len(kerrs)):
            ax.text(j, i, f"{dchi[i, j]:.0f}" if dchi[i, j] >= 10 else f"{dchi[i, j]:.1f}", ha="center", va="center", fontsize=12,
                    color="white" if np.log10(dchi[i, j] + 1) > 1.2 else INK, fontweight="bold" if dchi[i, j] <= 2.3 else "normal")
    ax.set(xlabel="Kerr $K$ (units of $\\kappa_2$)", ylabel="buffer bandwidth $\\kappa_b$ (units of $\\kappa_2$)", title="Δχ² of hidden-device flip rates (bold: Δχ² ≤ 2.3)")
    ax.spines[:].set_visible(False); cb_ = fig.colorbar(im, ax=ax); cb_.set_label("$\log_{10}(\Delta\chi^2+1)$")
    save(fig, "f13_chi2map.png")
    # ratio hidden/nominal vs nbar: data and model lines
    Praw = np.array(tm["Praw"]); pnom = np.array(tm["p_nom_spec"]); calib = np.array(tm["calib"])
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.3), sharey=True)
    ratio = p / np.array(tm["p_train"]); rerr = ratio * np.sqrt((sp / p) ** 2 + (np.array([nomB[s]["err"] for s in SIZES]) / np.array(tm["p_train"])) ** 2)
    for a in ax: a.errorbar(NB, ratio, rerr, fmt="o", color=AMBER, ms=9, capsize=4, label="data: hidden / nominal", zorder=5)
    cols = [RED, AMBER, TEAL, NAVY, GRAY]
    for i, kb in enumerate(kbs):
        ax[0].plot(NB, Praw[i, 0] / pnom, "-", color=plt.cm.cividis(i / (len(kbs) - 1)), label=f"$\\kappa_b$ = {kb:g}")
    for j, Kk_ in enumerate(kerrs):
        ax[1].plot(NB, Praw[list(kbs).index(8.0), j] / pnom, "-", color=plt.cm.viridis(j / (len(kerrs) - 1)), label=f"K = {Kk_:g}")
    ax[0].set(title="K = 0, vary buffer bandwidth", xlabel=r"cat size $\bar n$", ylabel="flip-rate ratio  hidden / nominal")
    ax[1].set(title=r"$\kappa_b$ = 8, vary Kerr", xlabel=r"cat size $\bar n$")
    ax[0].legend(fontsize=10.5, ncol=2, loc="upper left"); ax[1].legend(fontsize=10.5, loc="upper left")
    save(fig, "f14_twomode_ratio.png")
if "physics_curve" in S:
    pc = S["physics_curve"]; nbc = np.array(pc["nbar"]); allc = np.array([c["p"] for c in pc["curves"]]) * 100
    fig, ax = plt.subplots(figsize=(12, 4.6))
    nbf = np.linspace(1.75, 4.5, 120)
    for deg, col in [(1, NAVY), (2, TEAL)]:
        m = np.array([predict(v, deg)[0] for v in nbf]) * 100; e = np.array([predict(v, deg)[1] for v in nbf]) * 100
        ax.plot(nbf, m, color=col, label=f"WLS degree {deg} (±1σ, χ²-inflated)"); ax.fill_between(nbf, np.maximum(m - e, 1e-2), m + e, color=col, alpha=0.15)
    ax.fill_between(nbc, allc.min(0), allc.max(0), color=AMBER, alpha=0.35, lw=0)
    ax.plot(nbc, np.median(allc, 0), "--", color=AMBER, lw=2.4, label="two-mode physics fit (Δχ² ≤ 2.3)")
    ax.errorbar(NB, p * 100, sp * 100, fmt="o", color=RED, ms=9, capsize=4, label="hidden device, validation labels", zorder=5)
    ax.axvspan(2.0, 3.5, color=GRAY, alpha=0.08); ax.text(2.05, 1.0, "data range", color=MUTE, fontsize=12)
    ax.set_yscale("log"); ax.set_ylim(0.3, 40); ax.set(xlabel=r"cat size $\bar n$", ylabel="flip probability per segment (%)", title="Sealed prediction: three models, one curve")
    ax.legend(loc="upper right", fontsize=12); save(fig, "f15_sealed.png")
    S["pred_table"] = [{"nbar": v, "w1": predict(v, 1), "w2": predict(v, 2),
                        "phys": [float(np.median(allc[:, i])), float(allc[:, i].min()), float(allc[:, i].max())]} for i, v in enumerate(nbc)]
if "wigner" in S:
    W = S["wigner"]; x = np.array(W["x"])
    fig, ax = plt.subplots(1, 3, figsize=(12, 4.0))
    for a, key, title in zip(ax, ["plus", "cat_even", "kicked"], [r"$|{+}\alpha\rangle$: logical 0", r"$(|{+}\alpha\rangle+|{-}\alpha\rangle)/\sqrt{2}$: parity +1", r"$a^\dagger|{+}\alpha\rangle$: after a thermal kick"]):
        Wm = np.array(W[key]); v = np.abs(Wm).max()
        a.imshow(Wm.T, origin="lower", extent=[x[0], x[-1], x[0], x[-1]], cmap="RdBu_r", vmin=-v, vmax=v)
        a.set_title(title, fontsize=13.5); a.set_xticks([-2, 0, 2]); a.set_yticks([-2, 0, 2]); a.set_xlabel("x"); a.spines[:].set_visible(False)
    ax[0].set_ylabel("p"); save(fig, "f01_wigner.png")
if "oracle" in S:
    pn = np.array(S["oracle"]["pneg"]); fig, ax = plt.subplots(figsize=(6.6, 4.4))
    ax.hist(pn, bins=np.linspace(0, 1, 26), color=NAVY); ax.set_yscale("log")
    ax.set(xlabel="pneg of a segment (state at readout)", ylabel="segments", title=r"Oracle view, nominal $\bar n=2.5$, 300 simulated segments")
    save(fig, "f16_oracle.png")
    order = np.argsort(pn); fl = np.zeros(len(pn), bool); fl[order[int(round(.7 * len(pn))):]] = True
    S["oracle_summary"] = {"p0": float(pn.mean()), "post30": float(pn[~fl].mean()), "x30": float(np.mean(np.where(fl, 1 - pn, pn))),
                           "opt": float(np.mean(np.minimum(pn, 1 - pn))), "frac_gt_half": float(np.mean(pn > 0.5)),
                           "S_opt": float(np.mean(np.minimum(pn, 1 - pn)) / pn.mean())}
json.dump({k: S[k] for k in S if k in ("pred_table", "oracle_summary", "c_nominal")} | {"burst_tau": R["burst_tau"]}, open(OUT / "derived.json", "w"), default=float)
print(json.dumps({k: S[k] for k in S if k in ("pred_table", "oracle_summary", "c_nominal")}, default=float, indent=0)[:3000])
