# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "aqora[pyarrow]>=0.39",
#     "catchtheflip",
#     "dynamiqs==0.3.7",
#     "marimo>=0.23.3",
#     "matplotlib>=3.8",
#     "numpy>=2.0",
# ]
#
# [tool.uv.sources]
# catchtheflip = { path = "..", editable = true }
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Catch the flip: challenge template

    This notebook walks through the four steps of `CHALLENGE.md`. Cells marked **TODO** are
    yours. Keep every computation under a few minutes; if a cell takes longer, reduce the
    number of segments. Units: $\kappa_2 = 1$. A *segment* is one memory experiment of
    duration $T_{\rm seg} = 200$; the datasets hold segments at four cat sizes.

    The detector of step 3 works on the **heterodyne records** (the dataset *tier B*), the
    only records of the leaderboard. Tutorial 5 goes through the same job on click records,
    where a burst can be seen by eye: run it first.

    marimo is reactive: editing a cell reruns every cell that depends on it, including the
    simulations of a few minutes. To decide yourself when expensive cells run, switch the
    runtime to *lazy* (notebook settings, "On cell change: lazy"): dependent cells are then
    marked stale instead of rerun. Tutorial 1 lists the other differences with Jupyter.
    """)
    return


@app.cell
def _():
    from dataclasses import replace

    import numpy as np
    import matplotlib.pyplot as plt
    import dynamiqs as dq

    from catchtheflip import leaderboard, models, protocol, simulate, rates, records, scoring, repcode

    dq.set_precision("double")
    p = models.SingleModeParams()              # the nominal device of the device sheet, at the cat size 2.5
    device = models.single_mode(p)             # other cat sizes: models.nominal_model(nbar=3.0)
    T_seg = protocol.T_SEG                     # 200: the duration of a segment
    print(p, "| cat sizes of the datasets:", protocol.CAT_SIZES, "| T_seg =", T_seg)
    return (
        T_seg,
        device,
        dq,
        leaderboard,
        models,
        np,
        p,
        plt,
        protocol,
        rates,
        records,
        repcode,
        replace,
        scoring,
        simulate,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 1: watch a cat flip

    ### 1.1 The buffer channel is dark in the code space
    """)
    return


@app.cell
def _(device, dq):
    L2 = device.L_buffer
    for _name, _psi in [("|+alpha>", device.psi0), ("a^dag|+alpha>", (device.a.dag() @ device.psi0).unit()),
                        ("a^dag a|+alpha>", (device.a.dag() @ device.a @ device.psi0).unit())]:
        print(f"{_name:18s} buffer click rate = {float(dq.expect(L2.dag() @ L2, _psi).real):.3f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.2 Rates from the Liouvillian spectrum, and their convergence in $N$
    """)
    return


@app.cell
def _(T_seg, device, models, p, protocol, rates, replace):
    sp = rates.spectrum(device)
    print(f"Gamma_Z = {sp['gamma_z']:.3e} (T_Z = {1 / sp['gamma_z']:.0f}),  Gamma_X = {sp['gamma_x']:.3e},  2 kappa_1 nbar = {2 * p.kappa1 * p.nbar:.3f}")
    # Parity X_L = exp(i pi a^dag a). Loss (a) and thermal excitation (a^dag) change the photon number by one and flip
    # the parity; dephasing (a^dag a) conserves it. With the thermal terms: Gamma_X ~ 2 kappa_1 [(1 + 2 nth) nbar + nth].
    _gx_primer = 2 * p.kappa1 * p.nbar
    _gx_thermal = 2 * p.kappa1 * ((1 + 2 * p.nth) * p.nbar + p.nth)
    print(f"Gamma_X estimates: primer 2 kappa_1 nbar = {_gx_primer:.4f}, with thermal photons = {_gx_thermal:.4f}, spectrum = {sp['gamma_x']:.4f}")
    print(f"flip probability per segment of {T_seg:g}: {rates.flip_probability(sp['gamma_z'], T_seg):.4f}")

    for N_val in [p.N - 4, p.N, p.N + 4]:  # test N = 20, 24, 28
        dev_N = models.single_mode(replace(p, N=N_val))
        sp_N = rates.spectrum(dev_N)
        print(f"N = {N_val}: Gamma_Z = {sp_N['gamma_z']:.4e}")

    # Results table, rows 1-2: Gamma_Z and Gamma_X of the nominal device at the four cat sizes
    res_rates = {}
    for _nb in protocol.CAT_SIZES:
        _s = rates.spectrum(models.nominal_model(nbar=_nb))
        res_rates[_nb] = {"gamma_z": float(_s["gamma_z"]), "gamma_x": float(_s["gamma_x"]),
                          "p_flip": float(rates.flip_probability(_s["gamma_z"], T_seg))}
        print(f"nominal nbar = {_nb}: Gamma_Z = {_s['gamma_z']:.3e}, Gamma_X = {_s['gamma_x']:.4f}, flip probability per segment = {res_rates[_nb]['p_flip']:.4f}")
    return res_rates, sp


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.3 One long trajectory
    """)
    return


@app.cell
def _(device, np, plt, simulate):
    traj = simulate.long_trajectory(device, T=1500.0, seed=1)    # ~30 s; flips are rare, look for drops of <Z_L>
    t, z = traj["t"], traj["z"]                                   # <Z_L> = 1 - 2 P(x < 0), what the Z readout samples
    _fig, _ax = plt.subplots(2, 1, figsize=(10, 5), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    _ax[0].plot(t, z, lw=0.8); _ax[0].set_ylabel(r"$\langle Z_L\rangle$")
    for _k, _name in enumerate(device.channels):
        _c = traj["clicktimes"][_k]; _c = _c[~np.isnan(_c)]
        _ax[1].plot(_c, np.full_like(_c, _k), "|", ms=10)
    _ax[1].set_yticks(range(len(device.channels))); _ax[1].set_yticklabels(device.channels); _ax[1].set_xlabel("time")
    plt.tight_layout()

    # Zoom on the first flip and count buffer clicks
    flip_indices = np.where(np.diff(np.sign(z)) < 0)[0]
    if len(flip_indices) > 0:
        t_flip = t[flip_indices[0]]
        buf_clicks = traj["clicktimes"][device.channels.index("buffer")]
        buf_clicks = buf_clicks[~np.isnan(buf_clicks)]
        burst_clicks = buf_clicks[(buf_clicks >= t_flip - 5) & (buf_clicks <= t_flip + 5)]
        print(f"First bit flip at t = {t_flip:.1f}. Buffer clicks in +/- 5 time units: {len(burst_clicks)}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.4 Segments and the master-equation check
    """)
    return


@app.cell
def _(T_seg, device, np, rates, records, simulate, sp):
    seg = simulate.counting_segments(device, n_segments=300, T_seg=T_seg, seed=2)   # ~2-5 min: one to two click-record segments per second
    labels = records.sample_labels(seg["pneg"], rng=0)
    p_me = simulate.master_equation_pneg(device, T_seg)[-1]
    print(f"flip probability: segments {seg['pneg'].mean():.4f} +- {seg['pneg'].std() / np.sqrt(len(labels)):.4f}, master equation {p_me:.4f}, spectrum {rates.flip_probability(sp['gamma_z'], T_seg):.4f}")
    print(f"{labels.sum()} flip labels in {len(labels)} segments")
    return labels, seg


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 2: the burst

    ### 2.1 Clicks in flip segments against flip-free segments
    """)
    return


@app.cell
def _(labels, np, seg):
    n_clicks = np.sum(~np.isnan(seg["clicktimes"]), axis=1)
    print("mean buffer clicks per segment: flip", n_clicks[labels == 1].mean() if labels.any() else "n/a", " no flip", n_clicks[labels == 0].mean())
    return


@app.cell
def _(mo, np, plt, records):
    # Where are the extra clicks in time? Align every click record of the nominal device (tier A) on its densest
    # cluster: the one-time-unit window with the most clicks, and histogram the click times around it.
    clicks_a = records.load_dataset(mo.notebook_dir().parent / "data" / "tierA_train.npz")

    def peak_window(row, width=1.0):
        """Largest number of clicks in a window of `width`, and the start time of that window."""
        _t = np.sort(row[np.isfinite(row)])
        if len(_t) == 0:
            return 0, np.nan
        _hits = np.searchsorted(_t, _t + width, side="left") - np.arange(len(_t))
        _k = int(np.argmax(_hits))
        return int(_hits[_k]), float(_t[_k])

    _pw = [peak_window(r) for r in clicks_a["clicktimes"]]
    burst_peak = np.array([w[0] for w in _pw])           # burst statistic: max clicks in one time unit
    _t0 = np.array([w[1] for w in _pw])
    _lab = clicks_a["labels"].astype(bool)
    _bins = np.arange(-10, 10.5, 0.5)
    _fig, _ax = plt.subplots(figsize=(8, 3.5))
    for _sel, _name in [(_lab, "flip label"), (~_lab, "no flip")]:
        _rel = (clicks_a["clicktimes"][_sel] - _t0[_sel, None]).ravel()
        _h, _ = np.histogram(_rel[np.isfinite(_rel)], _bins)
        _ax.step(_bins[:-1], _h / _sel.sum() / 0.5, where="post", label=_name)
    _ax.set(xlabel="time from the start of the densest 1-unit window", ylabel="clicks per segment per unit time",
            title="Nominal click records (all cat sizes), aligned on the densest cluster"); _ax.legend()
    plt.tight_layout()
    print("The extra clicks of flip segments sit within ~1 time unit of the densest window: the burst.")
    print("Away from it both classes show the same flat background of kicks and dark counts.")
    _fig
    return burst_peak, clicks_a, peak_window


@app.cell
def _(labels, np, peak_window, seg):
    # Not every flip label comes with a burst. The label is a Bernoulli draw from pneg, the probability that the
    # readout finds the memory at x < 0. A memory that ends near the saddle (pneg ~ 0.5), or that flips and flips back,
    # gives labels with little or no burst; conversely a burst that ends back in the original lobe gives no label.
    _pk = np.array([peak_window(r)[0] for r in seg["clicktimes"]])
    _pneg = np.asarray(seg["pneg"])
    _big = _pk >= np.quantile(_pk, 0.95)
    print(f"simulated segments: {np.sum(labels)} flip labels; of these, pneg > 0.9 in {np.mean(_pneg[labels == 1] > 0.9):.0%}, "
          f"pneg < 0.5 in {np.mean(_pneg[labels == 1] < 0.5):.0%} (flip labels drawn without a completed flip)")
    print(f"segments with the 5 % largest bursts: mean pneg = {_pneg[_big].mean():.2f}, fraction with pneg > 0.5 = {np.mean(_pneg[_big] > 0.5):.0%}")
    print("Consequence: averaging the burst over flip labels mixes in label-noise segments without a burst, so the mean")
    print("burst size per flip label underestimates the burst of a completed flip.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2.2 Scaling with the cat size

    **TODO**: loop over `nbar` (keep the other parameters), measure the burst size, the
    background and the flip probability. The click records of the nominal device
    (`tierA_train.npz`) cover the four cat sizes of the challenge; go beyond with your own
    simulations. Mind the Fock cutoff and the number of
    segments you need to see a few flips (the spectrum tells you the flip probability in
    advance).
    """)
    return


@app.cell
def _(T_seg, models, rates):
    for _nbar in [1.5, 2.0, 4.0]:
        _m = models.nominal_model(nbar=_nbar)           # picks the Fock cutoff of the datasets: check it
        _s = rates.spectrum(_m)
        print(f"nbar = {_nbar}: N = {_m.params.N}, Gamma_Z = {_s['gamma_z']:.2e}, flips per segment {rates.flip_probability(_s['gamma_z'], T_seg):.3%}")
    return


@app.cell
def _(burst_peak, clicks_a, np, plt, protocol):
    # Burst size, background and flip probability against the cat size, from the nominal click records.
    # Definition: buffer photons emitted during a flip = (mean clicks of flip segments - mean clicks of flip-free
    # segments) / eta_A. This counts the extra light of a flip-labelled segment; label noise (previous cell) makes it a
    # slight underestimate of the burst of a completed flip.
    _lab = clicks_a["labels"].astype(bool); _nb = clicks_a["nbar"]
    _tot = np.sum(np.isfinite(clicks_a["clicktimes"]), axis=1)
    res_burst = {}
    for _v in protocol.CAT_SIZES:
        _m = _nb == _v; _f = _m & _lab; _n = _m & ~_lab
        res_burst[_v] = {"p_flip": float(_lab[_m].mean()),
                         "photons": float((_tot[_f].mean() - _tot[_n].mean()) / protocol.ETA_A),
                         "photons_err": float(_tot[_f].std() / np.sqrt(_f.sum()) / protocol.ETA_A),
                         "background_rate": float(_tot[_n].mean() / protocol.T_SEG),
                         "peak_flip": float(burst_peak[_f].mean()), "peak_noflip": float(burst_peak[_n].mean())}
    _x = np.array(protocol.CAT_SIZES); _y = np.array([res_burst[v]["photons"] for v in _x])
    burst_tau = float(np.sum(_y * _x**2) / np.sum(_x**4))       # least-squares fit of N = nbar^2 kappa_2 tau
    print("nbar | flip prob | photons per flip | background clicks/unit time | peak clicks in 1 unit (flip / no flip)")
    for _v, _r in res_burst.items():
        print(f"{_v:4} | {_r['p_flip']:8.2%} | {_r['photons']:5.2f} +- {_r['photons_err']:.2f} | {_r['background_rate']:.3f} | "
              f"{_r['peak_flip']:.2f} / {_r['peak_noflip']:.2f}")
    print(f"fit N_burst = nbar^2 kappa_2 tau: tau = {burst_tau:.2f} (units 1/kappa_2), the time a flip spends near the saddle")
    _fig, _ax = plt.subplots(1, 2, figsize=(10, 3.5))
    _ax[0].errorbar(_x, _y, [res_burst[v]["photons_err"] for v in _x], fmt="o", label="data")
    _xf = np.linspace(1.8, 3.7, 50); _ax[0].plot(_xf, burst_tau * _xf**2, "--", label=rf"$\bar n^2\tau$, $\tau$ = {burst_tau:.2f}")
    _ax[0].set(xlabel=r"$\bar n$", ylabel="buffer photons per flip"); _ax[0].legend()
    _ax[1].semilogy(_x, [res_burst[v]["p_flip"] for v in _x], "o-")
    _ax[1].set(xlabel=r"$\bar n$", ylabel="flip probability per segment")
    plt.tight_layout()
    print("Large cats flip rarely (exponentially) but loudly (~nbar^2): the burst gets easier to see as flips get rarer.")
    _fig
    return burst_tau, res_burst


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2.3 The buffer as a real mode
    """)
    return


@app.cell
def _(models, p, plt, simulate):
    m2 = models.two_mode(models.TwoModeParams(nbar=p.nbar, kappa1=p.kappa1, nth=p.nth, kappa_phi=p.kappa_phi, kappa_b=4.0, Na=p.N, Nb=8))
    traj2 = simulate.long_trajectory(m2, T=100.0, seed=3, dt=1e-3)    # ~1 min; dt <= 1e-3 for the two-mode model
    _fig, _ax = plt.subplots(2, 1, figsize=(10, 4), sharex=True)
    _ax[0].plot(traj2["t"], traj2["z"]); _ax[0].set_ylabel(r"$\langle Z_L\rangle$")
    _ax[1].plot(traj2["t"], traj2["nb"]); _ax[1].set_ylabel(r"$\langle b^\dagger b\rangle$"); _ax[1].set_xlabel("time")
    plt.tight_layout()
    _fig
    return


@app.cell
def _(T_seg, models, p, rates):
    # Vary kappa_b at fixed kappa_2 = 4 g2^2 / kappa_b (Nb = 6: ~30 s and 1.2 GB per spectrum).
    res_kappa_b = {}
    for _kb in [4.0, 8.0, 16.0]:
        _pp = models.TwoModeParams(nbar=p.nbar, kappa1=p.kappa1, nth=p.nth, kappa_phi=p.kappa_phi, kappa_b=_kb, Na=p.N, Nb=6)
        _gz = float(rates.spectrum(models.two_mode(_pp), n_eig=6)["gamma_z"])
        res_kappa_b[_kb] = _gz
        print(f"kappa_b = {_kb:4g}: g2 = {_pp.g2:.2f}, g2*alpha / kappa_b = {_pp.g2 * _pp.alpha / _kb:.2f}, "
              f"Gamma_Z = {_gz:.3e}, flip probability per segment = {rates.flip_probability(_gz, T_seg):.4f}")
    print("A narrower buffer (smaller kappa_b) flips more: adiabatic elimination needs kappa_b >> g2*alpha, and when it fails")
    print("the effective confinement is weaker. The burst is low-pass filtered with a response time ~2/kappa_b (0.25 at")
    print("kappa_b = 8, below one 0.5-unit bin of tier B), so the flip rate changes much more than the burst shape.")
    return (res_kappa_b,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 3: the detector

    The detector works on the heterodyne records, the Aqora dataset
    [tier B](https://aqora.io/datasets/Alice_Bob/catch-the-flip-tier-b): the two quadratures
    $I$ and $Q$ of the buffer output, averaged over 400 bins of half a time unit. Every split
    mixes segments of four cat sizes (array `nbar`), and the leaderboard discards the 30 %
    most suspicious segments of the whole test split. `records.load_dataset` reads a split
    from Aqora, or from a file of that name if you put one in `data/`.

    A burst is a negative step in $I$ of height $\sqrt{2\eta}\,\alpha^2$ and duration $\tau$,
    under white noise of standard deviation $\sqrt{1/\text{bin duration}} = 1.41$ per bin.
    The crudest statistic is the mean of $I$ over the whole segment. Load the data, look at
    the two crudest detectors, then build yours.
    """)
    return


@app.cell
def _(mo, np, plt, protocol, records, scoring):
    data_dir = mo.notebook_dir().parent / "data"                  # a split is read from Aqora unless its file is in this folder
    submission_dir = mo.notebook_dir().parent / "submission_template"
    train = records.load_dataset(data_dir / "tierB_train.npz")    # nominal device, labelled
    val = records.load_dataset(data_dir / "tierB_val.npz")        # hidden device, labelled
    test = records.load_dataset(data_dir / "tierB_test.npz")      # hidden device, no labels: the leaderboard
    print(train["meta"], "| I and Q:", train["I"].shape, train["I"].dtype)
    for _name, _d in [("train (nominal device)", train), ("val (hidden device)", val)]:
        print(f"{_name}: flip fraction per cat size",
              {float(_v): round(float(_d["labels"][_d["nbar"] == _v].mean()), 4) for _v in np.unique(_d["nbar"])})

    def mean_dip(I):
        return -I.mean(axis=1, dtype=np.float64)                  # a flip pulls I down for a moment

    # two detectors that need no thought: the mean of I over the whole segment, and the cat size alone (smallest cats first)
    for _name, _score in [("mean of I", mean_dip(val["I"])), ("cat size alone", -val["nbar"])]:
        _r = scoring.rho_at_yield(_score, val["labels"])
        print(f"\n{_name}: 1 - rho_70 = {_r['suppression']:.2f} on validation ({_r['flips_discarded']} of {_r['flips_total']} flips discarded with 30 % of the segments)")
        for _v, _b in scoring.by_cat_size(_score, val["labels"], val["nbar"]).items():
            print(f"   cat size {_v:g}: {_b['discarded']:5.1%} of its segments discarded, {_b['flips_discarded']} of {_b['flips_total']} flips")
        _Y, _rho = scoring.postselection_curve(_score, val["labels"])
        plt.plot(_Y, _rho, label=_name)
    plt.axvline(protocol.YIELD, color="k", ls=":", lw=0.8); plt.legend()
    plt.xlabel("yield (fraction of segments kept)"); plt.ylabel(r"residual flip fraction $\rho$"); plt.title("validation split (hidden device)")
    plt.gca()
    return data_dir, mean_dip, submission_dir, test, val


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Why the mean of $I$ does worse than not looking at the records.** A burst is a dip of height
    $\sqrt2\,\bar n$ lasting $\tau \approx 0.6$ out of 200 time units. Averaged over the segment its signal is diluted
    by $\tau/T_{\rm seg}$ while the noise only falls as $1/\sqrt{400}$: the matched-filter SNR $d' = \bar n\sqrt{2\tau}$
    (2 to 4) drops by $\sqrt{T_{\rm seg}/\tau} \approx 19$ to $d' \approx 0.2$. The mean of $I$ then ranks almost at random,
    and it spends its 30 % evenly over the cat sizes (29 / 28 / 31 / 30 % above). "Cat size alone" uses no record at all
    but spends the whole budget on the cat sizes that flip most (all of $\bar n = 2$ and $2.5$, 37.5 % of $3$): the prior
    is worth more than a nearly blind statistic. A good detector must use both: the record (a localised matched filter)
    and the prior (a calibrated posterior per cat size).
    """)
    return


@app.cell
def _(np, protocol, scoring, submission_dir, test, val):
    import scipy.ndimage
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold
    from sklearn.preprocessing import StandardScaler

    def extract_features(I_data):
        I = I_data.astype(np.float32)
        I_c = I - I.mean(axis=-1, keepdims=True)

        s2 = scipy.ndimage.uniform_filter1d(I_c, size=2, axis=-1)
        s3 = scipy.ndimage.uniform_filter1d(I_c, size=3, axis=-1)
        s4 = scipy.ndimage.uniform_filter1d(I_c, size=4, axis=-1)

        d2 = -np.min(s2, axis=-1)
        d3 = -np.min(s3, axis=-1)
        d4 = -np.min(s4, axis=-1)

        a20 = np.sum(np.maximum(0.0, -s3 - 2.0), axis=-1)
        a25 = np.sum(np.maximum(0.0, -s3 - 2.5), axis=-1)
        a30 = np.sum(np.maximum(0.0, -s3 - 3.0), axis=-1)
        nbel = np.sum(s3 < -2.5, axis=-1).astype(np.float32)

        return np.column_stack([d2, d3, d4, a20, a25, a30, nbel])

    X_val = extract_features(val["I"])
    y_val = val["labels"]
    nb_val = val["nbar"]

    X_test = extract_features(test["I"])
    nb_test = test["nbar"]

    # 5-Fold Stratified Cross-Validation
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    val_cv_scores = np.zeros(len(y_val))
    test_scores = np.zeros(len(nb_test))

    for train_idx, val_idx in skf.split(X_val, y_val):
        for nb in [2.0, 2.5, 3.0, 3.5]:
            m_tr = (nb_val[train_idx] == nb)
            m_va = (nb_val[val_idx] == nb)
            m_te = (nb_test == nb)

            scaler = StandardScaler()
            X_tr_s = scaler.fit_transform(X_val[train_idx][m_tr])
            X_va_s = scaler.transform(X_val[val_idx][m_va])
            X_te_s = scaler.transform(X_test[m_te])

            clf = LogisticRegression(C=5.0, max_iter=500, random_state=42)
            clf.fit(X_tr_s, y_val[train_idx][m_tr])

            # Honest Out-of-Fold prediction (evaluated on data the model wasn't trained on)
            val_cv_scores[val_idx[m_va]] = clf.predict_proba(X_va_s)[:, 1]

            # Accumulate ensemble prediction for the unlabelled test split
            test_scores[m_te] += clf.predict_proba(X_te_s)[:, 1] / 5.0

    # Evaluate the honest out-of-fold performance
    _ev = scoring.evaluate(val_cv_scores, val_cv_scores > np.quantile(val_cv_scores, protocol.YIELD), y_val)
    _lb = _ev["leaderboard"]

    print(f"Honest 5-Fold CV (Unseen data): 1 - rho_70 = {_lb['suppression']:.4f}, AUC = {_ev['auc']:.4f}")
    print(f"Leaderboard Points: {scoring.leaderboard_points(_lb['suppression']):.2f} / 10.0")

    # Results table: yield, TPR, FPR, S at our decisions, and the share of each cat size we discard (validation, out-of-fold)
    _dec = val_cv_scores > np.quantile(val_cv_scores, protocol.YIELD)
    _sc = scoring.score(_dec, y_val); _ps = scoring.postselection(_dec, y_val)
    res_det = {"auc": float(_ev["auc"]), "suppression": float(_lb["suppression"]), "yield": float(_ps["yield"]),
               "tpr": float(_sc["tpr"]), "fpr": float(_sc["fpr"]), "S": float(_sc["S"]),
               "by_size": {k: float(b["discarded"]) for k, b in scoring.by_cat_size(val_cv_scores, y_val, nb_val).items()}}
    print(f"at our decisions: yield {res_det['yield']:.3f}, TPR {res_det['tpr']:.3f}, FPR {res_det['fpr']:.3f}, S {res_det['S']:.3f}")
    for _v, _b in scoring.by_cat_size(val_cv_scores, y_val, nb_val).items():
        print(f"   cat size {_v:g}: {_b['discarded']:5.1%} of its segments discarded, {_b['flips_discarded']} of {_b['flips_total']} flips")
    # Operating point as a cost ratio: discarding when P(flip | record) > t is Bayes-optimal for zeta = 1/t - 1
    _t = float(np.quantile(val_cv_scores, protocol.YIELD)); res_det["threshold"] = _t; res_det["zeta"] = 1 / _t - 1
    print(f"operating point: discard if P(flip | record, nbar) > {_t:.3f}, Bayes-optimal for a missed flip costing "
          f"zeta = {1 / _t - 1:.1f} false alarms (needs calibrated posteriors: no class weights)")
    # Trade-off curve rho(Y) on validation for three detector designs
    import matplotlib.pyplot as _plt
    _fig, _ax = _plt.subplots(figsize=(6, 3.8))
    for _name, _s in [("our detector (out-of-fold)", val_cv_scores), ("cat size alone", -nb_val + 1e-9 * np.random.default_rng(0).random(len(nb_val))),
                      ("mean of I", -val["I"].mean(axis=1, dtype=np.float64))]:
        _Y, _rho = scoring.postselection_curve(_s, y_val); _ax.plot(_Y, _rho, label=_name)
    _ax.axvline(protocol.YIELD, color="k", ls=":", lw=0.8); _ax.legend()
    _ax.set(xlabel="yield Y", ylabel=r"residual flip fraction $\rho(Y)$", title="Trade-off curve, validation split")
    _plt.tight_layout()

    # Save ensemble predictions to tierB.csv
    my_score = test_scores
    my_decision = (my_score > np.quantile(my_score, protocol.YIELD)).astype(int)
    scoring.write_submission(submission_dir / "tierB.csv", my_score, my_decision)
    print("Successfully written ensemble predictions to submission_template/tierB.csv!")
    _fig
    return res_det, val_cv_scores


@app.cell(hide_code=True)
def _(leaderboard, mo):
    save_button = mo.ui.run_button(label="Save for the leaderboard")
    mo.vstack(
        [
            mo.md(
                rf"""
    ### Submit to the live leaderboard

    The [leaderboard]({leaderboard.LEADERBOARD_URL}) scores the file
    `submission_template/tierB.csv` on the hidden labels of the test split. It takes two steps:

    1. Press the button below and sign in with the account your team submits with. This copies
       the file written by the cell above to the Aqora store of that account.
    2. Open the [leaderboard]({leaderboard.LEADERBOARD_URL}), sign in with the same account,
       type your team name and press **Submit**.

    The leaderboard shows the score of your **last** file, not the best of your files: compare
    your detectors on the validation split, and submit the one you believe in.
    """
            ),
            save_button,
        ]
    )
    return (save_button,)


@app.cell
async def _(leaderboard, mo, save_button, submission_dir):
    mo.stop(not save_button.value)
    _account = await leaderboard.save_signed_in(submission_dir / "tierB.csv")
    mo.callout(
        mo.md(
            f"Saved `submission_template/tierB.csv` to the Aqora store of **@{_account}**. Now open the "
            f"[leaderboard]({leaderboard.LEADERBOARD_URL}), sign in as @{_account} and press **Submit**."
        ),
        kind="success",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 4: what the herald is worth (capstone)

    ### 4.1 What does a burst tell you?

    How informative is a burst about the logical qubit? A photon counter is the best
    microscope for this question, so this cell uses the labelled click records of the nominal
    device (`tierA_train.npz`, the dataset of tutorial 5). They give the probability of a flip
    label given the size $n$ of the burst of a segment, and the distributions of $n$ in flip
    and flip-free segments, at one cat size. This cell uses our burst statistic of step 2 for
    $n$: the largest number of clicks within one time unit. Then ask the same question of your heterodyne
    detector: what does its score say about the label when it is at its largest?
    """)
    return


@app.cell
def _(burst_peak, clicks_a, np, plt):
    clicks_train = clicks_a                              # click records of the nominal device, labelled (loaded in step 2)

    nbar_41 = 2.5                                        # one cat size at a time
    sel_41 = clicks_train["nbar"] == nbar_41
    n_train = burst_peak[sel_41].astype(int)             # burst statistic of step 2: the largest number of clicks in one time unit
    y_train = clicks_train["labels"][sel_41].astype(bool)
    n_lo, n_hi = np.quantile(n_train, [0.02, 0.98]).astype(int)        # few segments in the tails: pool them
    n_binned = np.clip(n_train, n_lo, n_hi)
    n_values = np.arange(n_lo, n_hi + 1)
    counts = np.array([np.sum(n_binned == k) for k in n_values])
    flips = np.array([np.sum(y_train & (n_binned == k)) for k in n_values])
    p_flip_n = flips / counts
    err = np.sqrt(p_flip_n * (1 - p_flip_n) / counts)
    _fig, _ax = plt.subplots(1, 2, figsize=(10, 3.5))
    _ax[0].errorbar(n_values, p_flip_n, err, fmt="o")
    _ax[0].set_xlabel(f"$n$ (first and last points: $n \\leq {n_lo}$, $n \\geq {n_hi}$)"); _ax[0].set_ylabel(r"$P(\mathrm{flip} \mid n)$")
    _ax[0].set_title(f"cat size {nbar_41}, click records of the nominal device")
    _ax[1].plot(n_values, flips / flips.sum(), "o-", label="flip segments")
    _ax[1].plot(n_values, (counts - flips) / (counts - flips).sum(), "s-", label="flip-free segments")
    _ax[1].set_yscale("log"); _ax[1].set_xlabel("$n$"); _ax[1].set_ylabel(r"$P(n \mid \cdot)$"); _ax[1].legend()
    plt.tight_layout()
    res_41 = {"n": int(n_values[-1]), "p": float(p_flip_n[-1]), "err": float(err[-1])}
    print(f"P(flip | n >= {n_hi}) = {p_flip_n[-1]:.2f} +- {err[-1]:.2f}: it saturates near 50 %, it does not go to 1.")
    print("Why: a large burst means the memory went far from its lobe, near the saddle. From there it falls back into")
    print("either lobe, or ends near the origin (pneg ~ 0.5, see step 2.1 with the simulated pneg), and the label is a")
    print("coin flip of pneg. A burst says 'the memory was at the saddle', not 'the memory is now in the other lobe'.")
    _fig
    return (res_41,)


@app.cell
def _(np, protocol, val, val_cv_scores):
    # The same question for the heterodyne detector: what does its score say about the label at its largest?
    _y = val["labels"].astype(bool)
    for _v in protocol.CAT_SIZES:
        _m = val["nbar"] == _v; _s = val_cv_scores[_m]; _top = _s >= np.quantile(_s, 0.95)
        print(f"cat size {_v}: top 5 % of scores, P(flip) = {_y[_m][_top].mean():.2f} (prior {_y[_m].mean():.2f})")
    print("Even the most suspicious heterodyne records are flips well under 100 % of the time: label noise plus detector noise.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 4.2 Post-selection against Pauli-frame correction

    Post-selection discards segments; correction would apply a logical $X$ to the flagged
    ones. Compare the two with `catchtheflip.scoring.score` (the correction score $S$) and
    `catchtheflip.repcode`. On your own simulations you also know `pneg`, the readout
    probability of every segment. An *oracle* that flags segments by the `pneg` of
    `simulate.counting_segments` has seen every jump of every channel, more than any detector
    of the buffer output can know. What is its $S$, and why?
    """)
    return


@app.cell
def _(np, protocol, repcode, scoring, val, val_cv_scores):
    nbar_42 = 3.5                                        # one cat size at a time
    sel_42 = val["nbar"] == nbar_42
    feature_val = val_cv_scores[sel_42]                  # our detector (out-of-fold scores of step 3)
    labels_val = val["labels"][sel_42]
    for _q in [0.5, 0.7, 0.9, 0.95, 0.99]:
        _thr = np.quantile(feature_val, _q)
        _sc = scoring.score(feature_val > _thr, labels_val)
        _ps = scoring.postselection(feature_val > _thr, labels_val)
        print(f"flag score > {_thr:.3f}: correction S = {_sc['S']:.2f} (TPR {_sc['tpr']:.2f}, FPR {_sc['fpr']:.4f}) | post-selection: yield {_ps['yield']:.3f}, rho {_ps['rho']:.2f}")
    print("Correction helps (S < 1) only if TPR p > FPR (1 - p), i.e. a flag precision above 50 %: never reached here.")

    # Repetition code, one cycle = one segment, cat size 3.5 of the hidden device, with the decisions of the
    # leaderboard (top 30 % of the pooled scores) restricted to this cat size.
    _dec = (val_cv_scores > np.quantile(val_cv_scores, protocol.YIELD))[sel_42]
    _ps = scoring.postselection(_dec, labels_val); _sc = scoring.score(_dec, labels_val)
    p_flip = float(labels_val.mean())
    res_rep = {"nbar": nbar_42, "p": p_flip, "rho": float(_ps["rho"]), "yield": float(_ps["yield"]), "tpr": float(_sc["tpr"]), "fpr": float(_sc["fpr"]), "d": {}}
    for _d in [3, 5, 7]:
        _m = repcode.postselected_memory(_d, p_flip, rho=_ps["rho"], yield_per_qubit=_ps["yield"])
        res_rep["d"][_d] = {"none": float(repcode.logical_bitflip_probability(_d, p_flip)), "post": float(_m["p_logical_bitflip_kept"]),
                            "yield": float(_m["yield"]), "corr": float(repcode.logical_bitflip_probability(_d, p_flip, tpr=_sc["tpr"], fpr=_sc["fpr"]))}
        _r = res_rep["d"][_d]
        print(f"d = {_d}: logical bit flips per cycle {_r['none']:.4f} without herald, {_r['post']:.4f} post-selected "
              f"(yield {_r['yield']:.2f} per cycle), {_r['corr']:.4f} Pauli-frame corrected (TPR {_sc['tpr']:.2f}, FPR {_sc['fpr']:.3f})")
    print("A bit flip commutes with the X_i X_i+1 stabilisers: any odd number of flips is a logical flip, so the")
    print("logical bit-flip probability grows with d. The herald is worth more for bigger codes, used to discard.")
    return (res_rep,)


@app.cell
def _(np, plt, seg):
    # The oracle: flags by the pneg of the photon-counting simulations of step 1.4 (nominal device, nbar = 2.5).
    # pneg is conditioned on every jump of every channel: more than any detector of the buffer output can know.
    _pneg = np.asarray(seg["pneg"], dtype=float)
    _p0 = float(_pneg.mean())
    _order = np.argsort(_pneg)
    _flag30 = np.zeros(len(_pneg), bool); _flag30[_order[int(round(0.7 * len(_pneg))):]] = True
    _rho_oracle = float(_pneg[~_flag30].mean() / _p0)
    # Expected residual flip probability when X is applied to flagged segments: flagged ones flip with 1 - pneg
    _S = lambda flag: float(np.mean(np.where(flag, 1 - _pneg, _pneg)) / _p0)
    _best = _pneg > 0.5                                   # the best possible correction rule
    res_oracle = {"p0": _p0, "rho30": _rho_oracle, "S30": _S(_flag30), "S_best": _S(_best), "frac_gt_half": float(np.mean(_best))}
    print(f"oracle on {len(_pneg)} simulated segments: mean pneg {_p0:.4f}; post-selection of the top 30 %: rho = {_rho_oracle:.3f}")
    print(f"oracle correction: S = {res_oracle['S30']:.2f} flagging the top 30 %, best S = {res_oracle['S_best']:.3f} with the rule pneg > 0.5 "
          f"({res_oracle['frac_gt_half']:.1%} of segments)")
    print("Even the oracle barely corrects: after a burst the memory usually sits near the saddle (pneg ~ 0.1-0.5), not in")
    print("the other lobe, so the readout outcome is not yet decided. Post-selection works, correction does not.")
    _fig, _ax = plt.subplots(figsize=(6, 3.3))
    _ax.hist(_pneg, bins=np.linspace(0, 1, 26)); _ax.set_yscale("log")
    _ax.set(xlabel="pneg", ylabel="segments", title="Oracle view: distribution of pneg (nominal, nbar = 2.5)")
    plt.tight_layout(); _fig
    return (res_oracle,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 4.3 Sealed prediction (Sunday 09:00): Bernoulli errors and Weighted Fit

    On Sunday morning at 09:00, a new mystery cat size $\bar{n}^\star$ is announced.
    Below is the complete, statistically rigorous fit:
    1. Exact Bernoulli/binomial standard errors $\sigma_p = \sqrt{p(1-p)/N}$ for each cat size.
    2. Analytical error propagation from $p$ to the bit-flip rate $\Gamma_Z$ and $\ln \Gamma_Z$.
    3. Weighted Least Squares (WLS) linear fit of $\ln \Gamma_Z$ vs $\bar{n}$.
    4. Prediction function `predict_sealed_cat(nbar_star)` with honest $\pm 1\sigma$ error bars.
    """)
    return


@app.cell
def _(np, plt, val):
    # 1. Flip-label counts per cat size on the hidden device (Validation set)
    _nbar_pts = np.array([2.0, 2.5, 3.0, 3.5])
    _N_pts = np.array([int(np.sum(val["nbar"] == _v)) for _v in _nbar_pts])
    _k_pts = np.array([int(np.sum((val["nbar"] == _v) & (val["labels"] == 1))) for _v in _nbar_pts])
    _T_seg_fit = 200.0

    # 2. Exact Bernoulli / binomial standard error: sigma_p = sqrt(p * (1 - p) / N)
    _p_pts = _k_pts / _N_pts
    _sigma_p = np.sqrt(_p_pts * (1.0 - _p_pts) / _N_pts)

    print("Observed flip probabilities with Bernoulli error bars on the hidden device:")
    for _v, _prob, _std_err, _N, _k in zip(_nbar_pts, _p_pts, _sigma_p, _N_pts, _k_pts):
        print(f"  nbar={_v:3.1f} (N={_N:4d}, k={_k:3d}): p = {_prob:.4f} +/- {_std_err:.4f} ({_prob*100:5.2f} +/- {_std_err*100:4.2f}%)")

    # 3. Propagate error to Gamma_Z and ln(Gamma_Z)
    _gamma_pts = -np.log(1.0 - 2.0 * _p_pts) / _T_seg_fit
    _sigma_gamma = (2.0 / (_T_seg_fit * (1.0 - 2.0 * _p_pts))) * _sigma_p
    _y_log = np.log(_gamma_pts)
    _sigma_log = _sigma_gamma / _gamma_pts  # error on ln(Gamma_Z)
    _weights = 1.0 / (_sigma_log ** 2)

    # 4. Weighted least squares fit of ln(Gamma_Z) as a polynomial in nbar (degree 1: linear, 2: with a quadratic term)
    def _wls(deg):
        _A = np.column_stack([_nbar_pts ** j for j in range(deg + 1)])
        _cov = np.linalg.inv(_A.T @ (_weights[:, None] * _A))
        _beta = _cov @ (_A.T @ (_weights * _y_log))
        _chi2 = float(np.sum(_weights * (_y_log - _A @ _beta) ** 2))
        _dof = len(_nbar_pts) - (deg + 1)
        return _beta, _cov, _chi2, _dof

    _fits = {deg: _wls(deg) for deg in (1, 2)}
    for _deg, (_beta, _cov, _chi2, _dof) in _fits.items():
        print(f"degree {_deg}: coefficients {np.round(_beta, 3)}, chi2/dof = {_chi2:.2f}/{_dof}, error scale sqrt(chi2/dof) = {np.sqrt(_chi2 / _dof):.2f}")

    # 5. Prediction function for Sunday. The binomial error bar is inflated by sqrt(chi2/dof) when chi2/dof > 1,
    # because the points are not exactly on the curve: the scatter around the fit is then part of the uncertainty.
    def predict_sealed_cat(nbar_star, deg=1, inflate=True):
        _beta, _cov, _chi2, _dof = _fits[deg]
        _x_vec = np.array([float(nbar_star) ** j for j in range(deg + 1)])
        _scale = max(1.0, np.sqrt(_chi2 / _dof)) if inflate else 1.0
        _sigma_log_star = np.sqrt(float(_x_vec @ _cov @ _x_vec)) * _scale

        _gamma_star = np.exp(float(_x_vec @ _beta))
        _p_star = 0.5 * (1.0 - np.exp(-_gamma_star * _T_seg_fit))
        _sigma_p_star = 0.5 * _T_seg_fit * np.exp(-_gamma_star * _T_seg_fit) * _gamma_star * _sigma_log_star
        return float(_p_star), float(_sigma_p_star)

    print("\nSealed-prediction candidates (p_flip in %):")
    for _test_nbar in [2.8, 4.0]:
        for _deg in (1, 2):
            _p0, _e0 = predict_sealed_cat(_test_nbar, _deg, inflate=False)
            _p1, _e1 = predict_sealed_cat(_test_nbar, _deg, inflate=True)
            print(f"  nbar={_test_nbar}, degree {_deg}: {_p0*100:.2f} +/- {_e0*100:.2f} (binomial only), +/- {_e1*100:.2f} (inflated)")

    # Calibration plot
    _fig, _ax = plt.subplots(figsize=(6.5, 3.8))
    _ax.errorbar(_nbar_pts, _p_pts * 100, yerr=_sigma_p * 100, fmt="o", color="k", capsize=4, label="Hidden device (validation labels)")
    _n_plot = np.linspace(1.8, 4.5, 100)
    for _deg, _col in [(1, "C1"), (2, "C2")]:
        _p_plot = np.array([predict_sealed_cat(_v, _deg)[0] * 100 for _v in _n_plot])
        _err_plot = np.array([predict_sealed_cat(_v, _deg)[1] * 100 for _v in _n_plot])
        _ax.plot(_n_plot, _p_plot, _col + "-", label=f"degree {_deg} fit")
        _ax.fill_between(_n_plot, _p_plot - _err_plot, _p_plot + _err_plot, color=_col, alpha=0.2)
    _ax.set_yscale("log")
    _ax.set_xlabel(r"Cat size $\bar{n}$")
    _ax.set_ylabel(r"Flip probability per segment $p_{\rm flip}$ [%]")
    _ax.set_title(r"Sealed prediction: $\pm 1\sigma$ bands inflated by $\sqrt{\chi^2/{\rm dof}}$")
    _ax.legend()
    plt.tight_layout()
    _fig
    return (predict_sealed_cat,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 4.4 Physics-based sealed prediction: fit $(\kappa_b, K)$ of the hidden device

    The hidden device is the two-mode model (finite buffer bandwidth $\kappa_b$) with a Kerr term $K$.
    Instead of a polynomial in $\bar n$, fit these two parameters to the validation flip fractions:

    1. Calibrate $c(\bar n) = p_\text{train} / p_\text{spectrum, nominal}$ on the nominal device
       (absorbs readout error and finite-sample effects of the labels).
    2. Scan $(\kappa_b, K)$, predict $c(\bar n)\,p_\text{two-mode}(\bar n)$, binomial $\chi^2$ against validation counts.
    3. The spread over the $\Delta\chi^2 \le 2.3$ region gives the error bar at $\bar n^\star$.

    Compared side by side with the WLS fit of 4.3: agreement means the result is robust, a gap is model uncertainty.

    **TODO (Sunday, when $\bar n^\star$ is announced):** put $\bar n^\star$ in the comparison cell below, look at
    WLS vs physics together, and decide which prediction (or combination, with the gap added to the error bar)
    we submit. Not decided yet: the physics fit matters mostly if $\bar n^\star$ is outside $[2, 3.5]$.
    """)
    return


@app.cell
def _(data_dir, mo, models, np, protocol, rates, records, val):
    _train = records.load_dataset(data_dir / "tierB_train.npz")
    ph_sizes = np.unique(val["nbar"])
    _n_val = np.array([np.sum(val["nbar"] == v) for v in ph_sizes])
    _k_val = np.array([np.sum(val["labels"][val["nbar"] == v]) for v in ph_sizes])
    _p_tr = np.array([_train["labels"][_train["nbar"] == v].mean() for v in ph_sizes])

    def ph_p_two_mode(nb, kappa_b, kerr, Nb=4):
        _pp = models.TwoModeParams(nbar=nb, kappa_b=kappa_b, kerr=kerr, Na=protocol.fock_cutoff(nb), Nb=Nb)
        return rates.flip_probability(rates.spectrum(models.two_mode(_pp))["gamma_z"], protocol.T_SEG)

    _p_nom = np.array([rates.flip_probability(rates.spectrum(models.nominal_model(nbar=v))["gamma_z"], protocol.T_SEG) for v in ph_sizes])
    ph_calib = _p_tr / _p_nom
    print("calibration c(nbar):", np.round(ph_calib, 3))

    # ~5 s per spectrum, 80 spectra: a few minutes. Refine the grid around the minimum for a tighter error bar.
    ph_kappa_bs = np.array([2.0, 4.0, 8.0, 16.0, 32.0])
    ph_kerrs = np.array([0.0, 0.02, 0.05, 0.1])
    _P = np.zeros((len(ph_kappa_bs), len(ph_kerrs), len(ph_sizes)))
    with mo.status.progress_bar(total=_P[..., 0].size) as _bar:
        for _i, _kb in enumerate(ph_kappa_bs):
            for _j, _K in enumerate(ph_kerrs):
                _P[_i, _j] = ph_calib * np.array([ph_p_two_mode(v, _kb, _K) for v in ph_sizes])
                _bar.update()
    ph_chi2 = np.sum((_k_val - _n_val * _P) ** 2 / (_n_val * _P * (1 - _P)), axis=-1)
    _i, _j = np.unravel_index(np.argmin(ph_chi2), ph_chi2.shape)
    print(f"best: kappa_b = {ph_kappa_bs[_i]}, K = {ph_kerrs[_j]}, chi2 = {ph_chi2[_i, _j]:.1f} (4 points, 2 parameters)")

    def predict_physics(nbar_star):
        """Median and [min, max] over the Delta chi^2 <= 2.3 region. Calibration interpolated in log,
        held constant outside [2, 3.5] (an extra, unquantified uncertainty there)."""
        _c = np.exp(np.interp(nbar_star, ph_sizes, np.log(ph_calib)))
        _ok = np.argwhere(ph_chi2 - ph_chi2.min() <= 2.3)
        _ps = np.array([_c * ph_p_two_mode(nbar_star, ph_kappa_bs[a], ph_kerrs[b]) for a, b in _ok])
        return float(np.median(_ps)), float(_ps.min()), float(_ps.max())

    return ph_chi2, ph_kappa_bs, ph_kerrs, predict_physics


@app.cell
def _(
    NBAR_STAR,
    np,
    ph_chi2,
    ph_kappa_bs,
    ph_kerrs,
    plt,
    predict_physics,
    predict_sealed_cat,
):
    _fig, _ax = plt.subplots(figsize=(5, 4))
    _im = _ax.pcolormesh(ph_kerrs, ph_kappa_bs, np.log10(ph_chi2 - ph_chi2.min() + 1), shading="nearest")
    _ax.contour(ph_kerrs, ph_kappa_bs, ph_chi2 - ph_chi2.min(), levels=[2.3], colors="w")
    _ax.set_yscale("log"); _ax.set_xlabel("Kerr $K$"); _ax.set_ylabel(r"$\kappa_b$")
    _ax.set_title(r"$\log_{10}(\Delta\chi^2+1)$, white: $\Delta\chi^2=2.3$"); _fig.colorbar(_im)

    print("Side by side, p_flip in % (WLS: value +/- inflated 1 sigma; physics: median [min, max]):")
    print(f"{'nbar*':>6} | {'WLS deg 1':>16} | {'WLS deg 2':>16} | {'physics (kappa_b, K)':>26}")
    for _nb in [2.75, 4.0] + ([NBAR_STAR] if NBAR_STAR is not None else []):     # NBAR_STAR: set in the cell below
        _w1, _e1 = predict_sealed_cat(_nb, 1)
        _w2, _e2 = predict_sealed_cat(_nb, 2)
        _pm, _lo, _hi = predict_physics(_nb)
        print(f"{_nb:6.2f} | {_w1*100:7.3f} +/- {_e1*100:5.3f} | {_w2*100:7.3f} +/- {_e2*100:5.3f} | "
              f"{_pm*100:7.3f} [{_lo*100:.3f}, {_hi*100:.3f}]")
    _fig
    return


@app.cell
def _():
    # SUNDAY 09:00: put the announced cat size here (for example 2.75), then rerun. None = not announced yet.
    NBAR_STAR = None
    return (NBAR_STAR,)


@app.cell
def _(NBAR_STAR, np, predict_physics, predict_sealed_cat, submission_dir):
    # Sealed prediction. Central value: WLS degree 1 (statistically preferred: the quadratic term has Delta chi2 = 1.7
    # for one parameter). Error: its 1 sigma inflated by sqrt(chi2/dof). Outside the data range [2, 3.5] the half spread
    # of the three models (WLS 1, WLS 2, physics fit) is added in quadrature as a model-extrapolation uncertainty.
    sealed = None
    if NBAR_STAR is None:
        print("NBAR_STAR not set: no sealed prediction written yet.")
    else:
        _p1, _e1 = predict_sealed_cat(NBAR_STAR, 1)
        _p2, _ = predict_sealed_cat(NBAR_STAR, 2)
        _pm, _, _ = predict_physics(NBAR_STAR)
        _spread = 0.0 if 2.0 <= NBAR_STAR <= 3.5 else (max(_p1, _p2, _pm) - min(_p1, _p2, _pm)) / 2
        _err = float(np.hypot(_e1, _spread))
        sealed = {"nbar": NBAR_STAR, "p": _p1, "err": _err}
        _text = (f"Sealed prediction, hidden device, cat size nbar* = {NBAR_STAR}\n"
                 f"Flip probability per segment (T_seg = 200): {100 * _p1:.2f} % +/- {100 * _err:.2f} % (1 sigma)\n"
                 f"Method: weighted least-squares fit of ln Gamma_Z (from the flip-label fractions of the hidden-device "
                 f"validation split, binomial errors) linear in nbar, error inflated by sqrt(chi2/dof)"
                 + ("" if _spread == 0 else ", plus the spread of a quadratic fit and a two-mode (kappa_b, K) physics fit added in quadrature")
                 + "; cross-checked against the two-mode physics model.\n")
        (submission_dir / "sealed_prediction.txt").write_text(_text)
        print(_text)
    return (sealed,)


@app.cell
def _(
    burst_tau,
    mo,
    np,
    protocol,
    res_41,
    res_burst,
    res_det,
    res_oracle,
    res_rates,
    res_rep,
    submission_dir,
    val,
):
    # The results table of submission_template/README.md, filled from the cells above.
    _sz = protocol.CAT_SIZES
    _hid = {v: float(val["labels"][val["nbar"] == v].mean()) for v in _sz}
    _d5 = res_rep["d"][5]
    _rows = [
        ("bit-flip rate $\\Gamma_Z$ of the nominal device at the four cat sizes (units of $\\kappa_2$)",
         " / ".join(f"{res_rates[v]['gamma_z']:.2e}" for v in _sz), "slowest Liouvillian eigenvalue (`rates.spectrum`), Fock cutoff checked at N = 20, 24, 28"),
        ("phase-flip rate $\\Gamma_X$ of the nominal device at the four cat sizes",
         " / ".join(f"{res_rates[v]['gamma_x']:.3f}" for v in _sz), "spectrum; agrees with $2\\kappa_1[(1+2n_{th})\\bar n + n_{th}]$"),
        ("flip probability per segment, nominal and hidden device, at the four cat sizes",
         "nominal " + " / ".join(f"{100 * res_rates[v]['p_flip']:.1f} %" for v in _sz) + "; hidden " + " / ".join(f"{100 * _hid[v]:.1f} %" for v in _sz),
         "nominal: spectrum, $\\frac12(1-e^{-\\Gamma_Z T})$; hidden: flip-label fractions of the validation split"),
        ("buffer photons emitted during a flip against cat size (nominal device), and how you defined it",
         " / ".join(f"{res_burst[v]['photons']:.1f}" for v in _sz) + f"; fits $\\bar n^2\\kappa_2\\tau$ with $\\tau$ = {burst_tau:.2f}",
         "excess clicks of flip-labelled over flip-free segments (tier A), divided by $\\eta_A$ = 0.8"),
        ("your detector: AUC, $1 - \\rho_{70}$, and yield, TPR, FPR, S at your decisions, on the validation split",
         f"AUC {res_det['auc']:.3f}, $1-\\rho_{{70}}$ {res_det['suppression']:.3f}, yield {res_det['yield']:.2f}, TPR {res_det['tpr']:.2f}, FPR {res_det['fpr']:.2f}, S {res_det['S']:.2f}",
         "5-fold out-of-fold, per-cat-size logistic regression on 7 matched-filter features of I"),
        ("your detector: fraction of each cat size that you discard, on the validation split",
         " / ".join(f"{100 * res_det['by_size'][v]:.0f} %" for v in _sz), "`scoring.by_cat_size`, out-of-fold"),
        ("your detector: $1 - \\rho_{70}$ of your final submission on the hidden test split (leaderboard score)",
         "(copy from the leaderboard)", "leaderboard"),
        ("$P(\\text{flip} \\mid n)$ for segments with a large burst (click records of the nominal device, one cat size), and what it means",
         f"{res_41['p']:.2f} ± {res_41['err']:.2f} for n ≥ {res_41['n']} clicks in one time unit, $\\bar n$ = 2.5",
         "saturates near 50 %: a burst marks a visit to the saddle, from which the memory can fall into either lobe"),
        ("best S of an oracle that knows `pneg` (photon-counting simulations of the nominal device)",
         f"{res_oracle['S_best']:.2f} (rule pneg > 0.5); S = {res_oracle['S30']:.2f} flagging the top 30 %",
         "pneg of the 300 photon-counting segments of step 1.4 (nominal device, $\\bar n$ = 2.5)"),
        ("logical bit-flip probability per cycle (one cycle = one segment, at the cat size of your choice), d = 5: no herald, post-selected (with yield), Pauli-frame corrected",
         f"{_d5['none']:.3f} / {_d5['post']:.3f} (yield {_d5['yield']:.2f}) / {_d5['corr']:.3f}",
         f"hidden device, $\\bar n$ = {res_rep['nbar']}, our decisions: rho {res_rep['rho']:.2f}, TPR {res_rep['tpr']:.2f}, FPR {res_rep['fpr']:.2f}"),
    ]
    results_table = "| quantity | value | how obtained |\n| --- | --- | --- |\n" + "\n".join(f"| {a} | {b} | {c} |" for a, b, c in _rows)
    (submission_dir / "results_table.md").write_text(results_table + "\n")
    mo.md("### Results table (written to `submission_template/results_table.md`)\n\n" + results_table)
    return (results_table,)


if __name__ == "__main__":
    app.run()
