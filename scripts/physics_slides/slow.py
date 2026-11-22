"""Expensive physics computations (spectra, two-mode fit, oracle). Mirrors notebook 11 sections 1.2, 4.2b, 4.4."""
import json, sys, time
from pathlib import Path
import numpy as np
import dynamiqs as dq
from catchtheflip import models, rates, protocol, records, simulate

dq.set_precision("double")
OUT = Path(sys.argv[1]); OUT.mkdir(exist_ok=True)
DATA = Path("/Users/trinity/catch-the-flip/data")
t0 = time.time()
log = lambda *a: print(f"[{time.time()-t0:6.0f}s]", *a, flush=True)
res = {}

# 1. nominal device rates vs nbar
nb_grid = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
gz, gx = [], []
for v in nb_grid:
    s = rates.spectrum(models.nominal_model(nbar=v))
    gz.append(float(s["gamma_z"])); gx.append(float(s["gamma_x"]))
    log("nominal", v, gz[-1], gx[-1])
res["nominal"] = {"nbar": nb_grid, "gamma_z": gz, "gamma_x": gx}
json.dump(res, open(OUT / "slow.json", "w"))

# 2. two-mode (kappa_b, K) fit, exactly as notebook 4.4
val = records.load_dataset(DATA / "tierB_val.npz"); tr = records.load_dataset(DATA / "tierB_train.npz")
sizes = np.array(protocol.CAT_SIZES)
n_val = np.array([np.sum(val["nbar"] == v) for v in sizes]); k_val = np.array([np.sum(val["labels"][val["nbar"] == v]) for v in sizes])
p_tr = np.array([tr["labels"][tr["nbar"] == v].mean() for v in sizes])

def p_two(nb, kb, K, Nb=4):
    pp = models.TwoModeParams(nbar=nb, kappa_b=kb, kerr=K, Na=protocol.fock_cutoff(nb), Nb=Nb)
    return float(rates.flip_probability(rates.spectrum(models.two_mode(pp))["gamma_z"], protocol.T_SEG))

p_nom = np.array([rates.flip_probability(rates.spectrum(models.nominal_model(nbar=v))["gamma_z"], protocol.T_SEG) for v in sizes])
calib = p_tr / p_nom
kbs = [2.0, 4.0, 8.0, 16.0, 32.0]; kerrs = [0.0, 0.02, 0.05, 0.1]
P = np.zeros((len(kbs), len(kerrs), len(sizes))); Praw = np.zeros_like(P)
for i, kb in enumerate(kbs):
    for j, K in enumerate(kerrs):
        Praw[i, j] = [p_two(v, kb, K) for v in sizes]
        P[i, j] = calib * Praw[i, j]
        log("grid", kb, K, np.round(P[i, j], 4))
chi2 = np.sum((k_val - n_val * P) ** 2 / (n_val * P * (1 - P)), axis=-1)
res["twomode"] = {"kappa_b": kbs, "kerr": kerrs, "sizes": sizes.tolist(), "calib": calib.tolist(), "p_nom_spec": p_nom.tolist(),
                  "p_train": p_tr.tolist(), "n_val": n_val.tolist(), "k_val": k_val.tolist(), "P": P.tolist(), "Praw": Praw.tolist(), "chi2": chi2.tolist()}
json.dump(res, open(OUT / "slow.json", "w"))

# 3. physics prediction curve over nbar (all grid points in Delta chi2 <= 2.3)
ok = np.argwhere(chi2 - chi2.min() <= 2.3)
log("ok set", [(kbs[a], kerrs[b]) for a, b in ok])
curve_nb = [1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0, 4.25, 4.5]
curves = []
for a, b in ok:
    c = []
    for v in curve_nb:
        cc = np.exp(np.interp(v, sizes, np.log(calib)))
        c.append(float(cc * p_two(v, kbs[a], kerrs[b])))
    curves.append({"kappa_b": kbs[a], "kerr": kerrs[b], "p": c}); log("curve", kbs[a], kerrs[b])
res["physics_curve"] = {"nbar": curve_nb, "curves": curves}
json.dump(res, open(OUT / "slow.json", "w"))

# 4. Wigner functions: code-space cat and a kicked state
dev = models.nominal_model(nbar=2.5)
xv = np.linspace(-3, 3, 121)
def wig(psi):
    _, _, w = dq.wigner(psi, xmax=3, ymax=3, npixels=121)
    return np.asarray(w).tolist()
plus = dev.psi0
mid = dq.coherent(dev.a.shape[-1], 0.0)
res["wigner"] = {"x": xv.tolist(), "plus": wig(plus), "cat_even": wig((plus + dq.coherent(dev.a.shape[-1], -np.sqrt(2.5))).unit()),
                 "kicked": wig((dev.a.dag() @ plus).unit())}
json.dump(res, open(OUT / "slow.json", "w"))
log("wigner done")

# 5. oracle from counting simulations (nominal, nbar=2.5), as notebook 1.4 / 4.2b
seg = simulate.counting_segments(models.nominal_model(nbar=2.5), n_segments=300, T_seg=protocol.T_SEG, seed=2)
pneg = np.asarray(seg["pneg"], float)
res["oracle"] = {"pneg": pneg.tolist()}
json.dump(res, open(OUT / "slow.json", "w"))
log("done")
