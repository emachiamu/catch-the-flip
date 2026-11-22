# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "aqora[pyarrow]>=0.39",
#     "catchtheflip",
#     "dynamiqs==0.3.7",
#     "marimo>=0.25",
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
def _(T_seg, device, models, p, rates, replace):
    sp = rates.spectrum(device)
    print(f"Gamma_Z = {sp['gamma_z']:.3e} (T_Z = {1 / sp['gamma_z']:.0f}),  Gamma_X = {sp['gamma_x']:.3e},  2 kappa_1 nbar = {2 * p.kappa1 * p.nbar:.3f}")
    # TODO: compare Gamma_X with the estimate of the primer: which channels flip the parity, and which do not?
    print(f"flip probability per segment of {T_seg:g}: {rates.flip_probability(sp['gamma_z'], T_seg):.4f}")    # TODO: repeat with N = p.N - 4 and p.N + 4: rates.spectrum(models.single_mode(replace(p, N=...)))

    for N_val in [p.N - 4, p.N, p.N + 4]:  # test N = 20, 24, 28
        dev_N = models.single_mode(replace(p, N=N_val))
        sp_N = rates.spectrum(dev_N)
        print(f"N = {N_val}: Gamma_Z = {sp_N['gamma_z']:.4e}")
    return (sp,)


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
    return (t, z, traj)


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
    # TODO: the difference is small against the clicks of a whole segment. Where are the extra clicks in time?
    # Align the records on their densest cluster of clicks. The click records of tutorial 5 (data/tierA_train.npz, the
    # nominal device) hold hundreds of flips per cat size: more than you can simulate in an hour.
    # TODO: not every flip label comes with a burst. Why not, and what does that do to the burst size? (look at pneg)
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
    _fig    # TODO: vary kappa_b at fixed kappa_2 = 4 g2^2 / kappa_b. How do the burst and the flip rate change?
    # The flip rate of the two-mode model comes from its spectrum too: rates.spectrum(model, n_eig=6). Mind the memory:
    # about 30 s and 1.2 GB with Nb = 6; with the Nb = 8 of this cell it takes minutes and 2.7 GB, more than the Aqora workspace has.
    # Nb = 6 changes Gamma_Z by 0.03 % here.
    return


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
    plt.gca()    # TODO: why does the mean of I do worse than not looking at the records at all? Where does each detector spend its 30 %?
    return data_dir, mean_dip, submission_dir, test, val


@app.cell
def _(np, protocol, scoring, submission_dir, test, val):
    import scipy.ndimage
    from sklearn.linear_model import LogisticRegression

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

    val_scores = np.zeros(len(y_val))
    test_scores = np.zeros(len(nb_test))

    for nb in [2.0, 2.5, 3.0, 3.5]:
        m_val = (nb_val == nb)
        m_test = (nb_test == nb)
    
        clf = LogisticRegression(C=1.0, max_iter=500, random_state=42)
        clf.fit(X_val[m_val], y_val[m_val])
    
        val_scores[m_val] = clf.predict_proba(X_val[m_val])[:, 1]
        test_scores[m_test] = clf.predict_proba(X_test[m_test])[:, 1]

    _ev = scoring.evaluate(val_scores, val_scores > np.quantile(val_scores, protocol.YIELD), val["labels"])
    _lb, _op, _c = _ev["leaderboard"], _ev["operating_point"], _ev["correction"]

    print(f"Validation: 1 - rho_70 = {_lb['suppression']:.4f}, AUC = {_ev['auc']:.4f}")
    print(f"Leaderboard Points: {scoring.leaderboard_points(_lb['suppression']):.2f} / 10.0")

    my_score = test_scores
    my_decision = (my_score > np.quantile(my_score, protocol.YIELD)).astype(int)
    scoring.write_submission(submission_dir / "tierB.csv", my_score, my_decision)
    print("Successfully written submission_template/tierB.csv!")
    return


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
    and flip-free segments, at one cat size. This cell uses the total number of clicks for
    $n$: replace it by your burst statistic of step 2 (the largest number of clicks within
    one time unit, say) and look again. Then ask the same question of your heterodyne
    detector: what does its score say about the label when it is at its largest?
    """)
    return


@app.cell
def _(data_dir, np, plt, records):
    clicks_train = records.load_dataset(data_dir / "tierA_train.npz")    # click records of the nominal device, labelled

    def total_clicks(clicktimes):
        return np.sum(~np.isnan(clicktimes), axis=1).astype(float)

    nbar_41 = 2.5                                        # one cat size at a time
    sel_41 = clicks_train["nbar"] == nbar_41
    n_train = total_clicks(clicks_train["clicktimes"][sel_41]).astype(int)    # TODO: your burst statistic instead
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
    _fig    # TODO: what happens at large n, and why? Simulate segments (step 1) and look at pneg for the segments with a large burst.
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
def _(mean_dip, np, repcode, scoring, val):
    nbar_42 = 3.5                                        # one cat size at a time
    sel_42 = val["nbar"] == nbar_42
    feature_val = mean_dip(val["I"][sel_42])                         # TODO: your detector instead
    labels_val = val["labels"][sel_42]
    for _q in [0.5, 0.7, 0.9, 0.95]:
        _thr = np.quantile(feature_val, _q)
        _sc = scoring.score(feature_val > _thr, labels_val)
        _ps = scoring.postselection(feature_val > _thr, labels_val)
        print(f"flag score > {_thr:.3f}: correction S = {_sc['S']:.2f} (TPR {_sc['tpr']:.2f}, FPR {_sc['fpr']:.4f}) | post-selection: yield {_ps['yield']:.3f}, rho {_ps['rho']:.2f}")
    # TODO: simulate segments yourself (step 1), keep pneg, and compute the oracle's S and rho. Look at the
    # distribution of pneg among flagged segments. Then the repetition code, one cycle = one segment:
    p_flip = float(labels_val.mean())
    for _d in [3, 5, 7]:
        print(f"d = {_d}: logical bit flips per cycle {repcode.logical_bitflip_probability(_d, p_flip):.4f} without herald, "
              f"{repcode.logical_bitflip_probability(_d, p_flip, tpr=0.6, fpr=0.1):.4f} with 'correction' at TPR 0.6 / FPR 0.1, "
              f"{repcode.logical_bitflip_probability(_d, p_flip * 0.4):.4f} with post-selection rho = 0.4 (and a yield of 0.7^{_d} per cycle)")
    return


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
    # 1. Empirical counts per cat size on the hidden device (Validation set)
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

    # 4. Weighted Least Squares (WLS) fit: ln(Gamma_Z) = b0 - c * nbar
    _weights = 1.0 / (_sigma_log ** 2)
    _A_mat = np.column_stack([np.ones_like(_nbar_pts), -_nbar_pts])
    _cov_mat = np.linalg.inv(_A_mat.T @ (_weights[:, None] * _A_mat))
    _beta_vec = _cov_mat @ (_A_mat.T @ (_weights * _y_log))
    _b0_fit, _c_decay = _beta_vec[0], _beta_vec[1]

    print(f"\nWLS Fit Results:")
    print(f"  ln(Gamma_0) = {_b0_fit:.4f} +/- {np.sqrt(_cov_mat[0, 0]):.4f}")
    print(f"  Decay constant c = {_c_decay:.4f} +/- {np.sqrt(_cov_mat[1, 1]):.4f}")

    # 5. Prediction function for Sunday
    def predict_sealed_cat(nbar_star):
        _x_vec = np.array([1.0, -float(nbar_star)])
        _log_gamma_star = float(_x_vec @ _beta_vec)
        _var_log_star = float(_x_vec @ _cov_mat @ _x_vec)
        _sigma_log_star = np.sqrt(_var_log_star)

        _gamma_star = np.exp(_log_gamma_star)
        _p_star = 0.5 * (1.0 - np.exp(-_gamma_star * _T_seg_fit))

        _sigma_gamma_star = _gamma_star * _sigma_log_star
        _sigma_p_star = 0.5 * _T_seg_fit * np.exp(-_gamma_star * _T_seg_fit) * _sigma_gamma_star

        return float(_p_star), float(_sigma_p_star)

    # Example test prediction for Sunday
    _test_nbar = 2.8
    _p_pred, _err_pred = predict_sealed_cat(_test_nbar)
    print(f"\nExample prediction for Sunday (e.g. nbar={_test_nbar}):")
    print(f"  p_flip = {_p_pred:.4f} +/- {_err_pred:.4f} ({_p_pred*100:.2f} +/- {_err_pred*100:.2f}%)")

    # Calibration plot
    _fig, _ax = plt.subplots(figsize=(6.5, 3.8))
    _ax.errorbar(_nbar_pts, _p_pts * 100, yerr=_sigma_p * 100, fmt="o", color="C0", capsize=4, label="Hidden device (Validation data)")
    _n_plot = np.linspace(1.8, 3.8, 100)
    _p_plot = np.array([predict_sealed_cat(_v)[0] * 100 for _v in _n_plot])
    _err_plot = np.array([predict_sealed_cat(_v)[1] * 100 for _v in _n_plot])
    _ax.plot(_n_plot, _p_plot, "C1-", label=f"WLS Fit (c={_c_decay:.2f})")
    _ax.fill_between(_n_plot, _p_plot - _err_plot, _p_plot + _err_plot, color="C1", alpha=0.2, label=r"$\pm 1\sigma$ uncertainty band")
    _ax.set_xlabel(r"Cat size $\bar{n}$")
    _ax.set_ylabel(r"Flip probability per segment $p_{\rm flip}$ [%]")
    _ax.set_title("Sealed Prediction Calibration Curve")
    _ax.legend()
    plt.tight_layout()
    _fig
    return (predict_sealed_cat,)


if __name__ == "__main__":
    app.run()
