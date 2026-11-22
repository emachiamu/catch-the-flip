"""Data analyses from notebook 11 (FIXED): detector (exact code), Step 2/4 statistics, burst waveforms."""
import json, sys
from pathlib import Path
import numpy as np
import scipy.ndimage
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from catchtheflip import records, scoring, protocol, repcode

OUT = Path(sys.argv[1]); OUT.mkdir(exist_ok=True)
DATA = Path("/Users/trinity/catch-the-flip/data")
val = records.load_dataset(DATA / "tierB_val.npz"); test = records.load_dataset(DATA / "tierB_test.npz")
train = records.load_dataset(DATA / "tierB_train.npz"); clicks = records.load_dataset(DATA / "tierA_train.npz")
SIZES = list(protocol.CAT_SIZES)
R = {}

# ---------- flip fractions ----------
def frac(d):
    out = {}
    for v in SIZES:
        m = d["nbar"] == v; k = int(d["labels"][m].sum()); n = int(m.sum())
        out[str(v)] = {"k": k, "n": n, "p": k / n, "err": float(np.sqrt(k / n * (1 - k / n) / n))}
    return out
R["flip_hidden"] = frac(val); R["flip_nominal_tierB"] = frac(train); R["flip_nominal_tierA"] = frac(clicks)

# ---------- detector, verbatim from notebook ----------
def extract_features(I_data):
    I = I_data.astype(np.float32); I_c = I - I.mean(axis=-1, keepdims=True)
    s2, s3, s4 = (scipy.ndimage.uniform_filter1d(I_c, size=w, axis=-1) for w in (2, 3, 4))
    d2, d3, d4 = -s2.min(-1), -s3.min(-1), -s4.min(-1)
    a20, a25, a30 = (np.sum(np.maximum(0.0, -s3 - t), axis=-1) for t in (2.0, 2.5, 3.0))
    nbel = np.sum(s3 < -2.5, axis=-1).astype(np.float32)
    return np.column_stack([d2, d3, d4, a20, a25, a30, nbel])

X_val, y_val, nb_val = extract_features(val["I"]), val["labels"], val["nbar"]
X_test, nb_test = extract_features(test["I"]), test["nbar"]
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
oof = np.zeros(len(y_val)); test_scores = np.zeros(len(nb_test)); coefs = {v: [] for v in SIZES}
for tr_idx, va_idx in skf.split(X_val, y_val):
    for nb in SIZES:
        m_tr, m_va, m_te = nb_val[tr_idx] == nb, nb_val[va_idx] == nb, nb_test == nb
        sc = StandardScaler(); Xtr = sc.fit_transform(X_val[tr_idx][m_tr])
        clf = LogisticRegression(C=5.0, max_iter=1000, random_state=42).fit(Xtr, y_val[tr_idx][m_tr])
        oof[va_idx[m_va]] = clf.predict_proba(sc.transform(X_val[va_idx][m_va]))[:, 1]
        test_scores[m_te] += clf.predict_proba(sc.transform(X_test[m_te]))[:, 1] / 5
        coefs[nb].append(clf.coef_[0].tolist())
dec = oof > np.quantile(oof, protocol.YIELD)
ev = scoring.evaluate(oof, dec, y_val)
R["detector"] = {"auc": float(ev["auc"]), "suppression": float(ev["leaderboard"]["suppression"]),
                 "points": float(scoring.leaderboard_points(ev["leaderboard"]["suppression"]))}
sc_ = scoring.score(dec, y_val); ps_ = scoring.postselection(dec, y_val)
R["detector"].update({"tpr": float(sc_["tpr"]), "fpr": float(sc_["fpr"]), "S": float(sc_["S"]), "yield": float(ps_["yield"]), "rho": float(ps_["rho"])})
R["detector"]["by_size"] = {str(k): {kk: float(vv) for kk, vv in b.items()} for k, b in scoring.by_cat_size(oof, y_val, nb_val).items()}
R["detector"]["coef_mean"] = {str(k): np.mean(v, 0).tolist() for k, v in coefs.items()}
R["roc"] = {}
fpr_, tpr_ = scoring.roc_curve(oof, y_val)[:2]
idx = np.linspace(0, len(fpr_) - 1, 200).astype(int); R["roc"] = {"fpr": np.asarray(fpr_)[idx].tolist(), "tpr": np.asarray(tpr_)[idx].tolist()}
# check the submitted CSV matches this model
sub = scoring.read_submission("/Users/trinity/catch-the-flip/submission_template/tierB.csv")
R["submission_check"] = {"max_abs_diff": float(np.max(np.abs(np.asarray(sub["score"]) - test_scores))), "n": int(len(test_scores)),
                         "discard_frac": float(np.mean(sub["decision"]))}

# baselines (notebook step 3)
R["baselines"] = {}
for name, s in [("mean of I", -val["I"].mean(1, dtype=np.float64)), ("cat size alone", -val["nbar"].astype(float))]:
    R["baselines"][name] = {"suppression": float(scoring.rho_at_yield(s, y_val)["suppression"]),
                            "by_size": {str(k): float(b["discarded"]) for k, b in scoring.by_cat_size(s, y_val, nb_val).items()}}

# post-selection curves (yield sweep) for ours and baselines
R["ps_curve"] = {}
for name, s in [("ours", oof), ("mean of I", -val["I"].mean(1, dtype=np.float64)), ("cat size alone", -val["nbar"].astype(float) + 1e-9 * np.random.default_rng(0).random(len(oof)))]:
    Y, rho = scoring.postselection_curve(s, y_val)
    R["ps_curve"][name] = {"Y": np.asarray(Y).tolist(), "rho": np.asarray(rho).tolist()}

# reliability per size
R["reliability"] = {}
for v in SIZES:
    m = nb_val == v; s = oof[m]; y = y_val[m]; o = np.argsort(s); g = np.array_split(o, 6)
    R["reliability"][str(v)] = {"pred": [float(s[i].mean()) for i in g], "obs": [float(y[i].mean()) for i in g], "n": [len(i) for i in g]}

# step 4.2: post-selection vs X, flagged fraction sweep
lab = y_val.astype(bool); order = np.argsort(oof, kind="stable")
def flag_top(f):
    fl = np.ones(len(oof), bool); fl[order[:int(round((1 - f) * len(oof)))]] = False; return fl
rows = []
for f in [.01, .02, .05, .10, .20, .30, .40, .50]:
    fl = flag_top(f); p = scoring.postselection(fl, lab); s = scoring.score(fl, lab); c = scoring.confusion(fl, lab)
    rows.append({"f": f, "p_kept": float(p["p_kept"]), "x_resid": float(lab.mean() * s["S"]), "S": float(s["S"]), "precision": c["tp"] / max(c["tp"] + c["fp"], 1)})
R["herald_sweep"] = {"p0": float(lab.mean()), "rows": rows}
# repetition code at nbar = 3.5 with measured numbers
fl30 = flag_top(0.3); one = nb_val == 3.5; y1 = lab[one]; f1 = fl30[one]; p1 = float(y1.mean())
pp = scoring.postselection(f1, y1); cc = scoring.score(f1, y1)
R["repcode"] = {"nbar": 3.5, "p": p1, "rho": float(pp["rho"]), "yield": float(pp["yield"]), "tpr": float(cc["tpr"]), "fpr": float(cc["fpr"]), "d": {}}
for d in (3, 5, 7):
    m_ = repcode.postselected_memory(d, p1, rho=pp["rho"], yield_per_qubit=pp["yield"])
    R["repcode"]["d"][str(d)] = {"none": float(repcode.logical_bitflip_probability(d, p1)), "post": float(m_["p_logical_bitflip_kept"]),
                                 "post_yield": float(m_["yield"]), "corr": float(repcode.logical_bitflip_probability(d, p1, tpr=cc["tpr"], fpr=cc["fpr"]))}

# ---------- burst waveform: align flip segments on their deepest 3-bin dip ----------
def aligned(d, nb, flip, half=24, top=None):
    m = (d["nbar"] == nb) & (d["labels"] == flip)
    I = d["I"][m].astype(np.float64); Q = d["Q"][m].astype(np.float64)
    I -= I.mean(1, keepdims=True); Q -= Q.mean(1, keepdims=True)
    s3 = scipy.ndimage.uniform_filter1d(I, 3, axis=-1); k = s3.argmin(1); depth = -s3.min(1)
    keep = (k >= half) & (k < I.shape[1] - half)
    if top is not None: keep &= depth >= np.quantile(depth, top)
    win = np.arange(-half, half + 1)
    Iw = np.stack([I[i, k[i] + win] for i in np.where(keep)[0]]); Qw = np.stack([Q[i, k[i] + win] for i in np.where(keep)[0]])
    return (win * 0.5).tolist(), Iw.mean(0).tolist(), Qw.mean(0).tolist(), int(keep.sum())
R["waveform"] = {}
for nm, d in [("hidden", val), ("nominal", train)]:
    R["waveform"][nm] = {}
    for v in SIZES:
        t, mi, mq, n = aligned(d, v, 1, top=0.5); _, ci, cq, cn = aligned(d, v, 0, top=0.5)
        R["waveform"][nm][str(v)] = {"t": t, "I": mi, "Q": mq, "n": n, "I_noflip": ci, "Q_noflip": cq}

# example traces (one clear flip, one no-flip) at nbar 3.5 for the feature illustration
m = (val["nbar"] == 3.5)
I = val["I"].astype(np.float64); Ic = I - I.mean(1, keepdims=True); s3 = scipy.ndimage.uniform_filter1d(Ic, 3, axis=-1)
fl = np.where(m & (val["labels"] == 1))[0]; nf = np.where(m & (val["labels"] == 0))[0]
i_f = fl[np.argsort(s3[fl].min(1))[len(fl) // 6]]; i_n = nf[len(nf) // 2]
R["example"] = {"flip": {"I": Ic[i_f].tolist(), "s3": s3[i_f].tolist(), "score": float(oof[i_f])},
                "noflip": {"I": Ic[i_n].tolist(), "s3": s3[i_n].tolist(), "score": float(oof[i_n])}}

# ---------- tier A click statistics (Step 2 / 4.1) ----------
def peak(row, w=1.0):
    t = np.sort(row[np.isfinite(row)])
    return 0 if len(t) == 0 else int((np.searchsorted(t, t + w, side="left") - np.arange(len(t))).max())
ct = np.asarray(clicks["clicktimes"]); cl = np.asarray(clicks["labels"]).astype(bool); cn = np.asarray(clicks["nbar"])
pk = np.array([peak(r) for r in ct]); tot = np.isfinite(ct).sum(1)
R["clicks"] = {"meta": {k: (v if isinstance(v, (int, float, str, list)) else str(v)) for k, v in dict(clicks.get("meta", {})).items()}, "by_size": {}}
for v in SIZES:
    mm = cn == v
    R["clicks"]["by_size"][str(v)] = {"peak_flip": float(pk[mm & cl].mean()), "peak_no": float(pk[mm & ~cl].mean()),
                                      "tot_flip": float(tot[mm & cl].mean()), "tot_no": float(tot[mm & ~cl].mean()),
                                      "tot_flip_se": float(tot[mm & cl].std() / np.sqrt((mm & cl).sum())),
                                      "n_flip": int((mm & cl).sum())}
mm = cn == 2.5; e = pk[mm]; y = cl[mm]; cap = int(np.quantile(e, .98)); eb = np.minimum(e, cap)
R["clicks"]["p_given_peak"] = [{"n": int(v), "N": int((eb == v).sum()), "k": int(y[eb == v].sum())} for v in np.unique(eb)]
R["clicks"]["cap"] = cap

json.dump(R, open(OUT / "fast.json", "w"))
print(json.dumps({k: R[k] for k in ["detector", "submission_check", "baselines", "repcode", "herald_sweep"]}, indent=1, default=str)[:4000])
print({v: (R["clicks"]["by_size"][v]) for v in R["clicks"]["by_size"]})
