# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "aqora[pyarrow]>=0.39",
#     "catchtheflip",
#     "dynamiqs==0.3.7",
#     "marimo>=0.23.3",
#     "matplotlib>=3.8",
#     "numpy>=2.0",
#     "scipy>=1.12",
#     "scikit-learn>=1.4",
#     "pandas>=2.0",
# ]
#
# [tool.uv.sources]
# catchtheflip = { path = "..", editable = true }
# ///

# Extension by ChatGPT for completion of challenge Steps 1, 2, 4.
# Standalone notebook: no catchflip_capstone.py import is needed.
# It uses the official catchtheflip package and the labelled Aqora datasets.
# The original detector and WLS prediction code is preserved, and all detector
# validation uses OUT-OF-FOLD predictions.
# Without tierA/tierB datasets and catchtheflip, data-based analyses cannot run.

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
    # Photon loss and thermal excitation change parity; pure dephasing a^dag a does not.
    # Tutorial 4: Gamma_X ~ 2 kappa1 [(1+2 nth) nbar + nth].
    gx_est = 2*p.kappa1*((1+2*p.nth)*p.nbar+p.nth)
    print(f"Parity-flip estimate incl. thermal photons = {gx_est:.5f}; Liouvillian Gamma_X = {sp['gamma_x']:.5f}")
    print(f"flip probability per segment of {T_seg:g}: {rates.flip_probability(sp['gamma_z'], T_seg):.4f}")

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
        _fig_zoom, _ax_zoom=plt.subplots(figsize=(8.5,3.1))
        _mask=(t >= t_flip-7) & (t <= t_flip+7)
        _ax_zoom.plot(t[_mask], z[_mask],label='conditional <Z_L>')
        _ax_zoom.axhline(0,ls=':',color='gray')
        for _click in burst_clicks:
            _ax_zoom.axvline(_click,color='tab:red',alpha=.3)
        _ax_zoom.set(xlabel='Time (1/kappa2)',ylabel='<Z_L>',
                     title='First negative-going transition; red lines: buffer clicks')
        plt.tight_layout();_fig_zoom
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
    return (seg,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 2: the burst

    ### 2.1 Clicks in flip segments against flip-free segments

    Use the labelled *nominal* Tier A click dataset, which is accessible on Aqora.
    It can be analysed without running the expensive Step 1.4 simulation first.
    """)
    return


@app.cell
def _(mo, np, plt, records):
    # Step 2.1: labelled Tier A photon counts from the installed catchtheflip API.
    # This cell does NOT import catchflip_capstone and does NOT need the costly
    # 300-segment simulation from Step 1.4 to have run first.
    def peak_clicks_in_window(record, width=1.0):
        """Maximum detected clicks in any half-open interval of length width."""
        times = np.asarray(record, dtype=float)
        times = np.sort(times[np.isfinite(times)])  # Tier A pads each record with NaN
        if len(times) == 0:
            return 0
        hits = np.searchsorted(times, times + width, side='left') - np.arange(len(times))
        return int(hits.max())

    click_data = None
    burst_peaks = None
    _tier_a_path = mo.notebook_dir().parent / 'data' / 'tierA_train.npz'
    try:
        click_data = records.load_dataset(_tier_a_path)  # Aqora fallback if no local .npz
    except (FileNotFoundError, ImportError, OSError, RuntimeError, ValueError) as _err:
        print('Step 2.1: Tier A train data are not accessible in this runtime.')
        print('In Aqora, run this notebook inside the challenge workspace; otherwise put')
        print(f'tierA_train.npz at {_tier_a_path}.')
        print(f'Dataset loader message: {_err}')
    if click_data is not None:
        _times = np.asarray(click_data['clicktimes'])
        _labels = np.asarray(click_data['labels']).astype(bool)
        if _times.ndim != 2 or len(_labels) != len(_times):
            raise ValueError(f'Invalid Tier A click/label arrays: {_times.shape}, {len(_labels)}')
        _totals = np.sum(np.isfinite(_times), axis=1)
        burst_peaks = np.fromiter(
            (peak_clicks_in_window(row, width=1.0) for row in _times),
            dtype=int, count=len(_times),
        )
        for _metric_name, _values in [('total clicks / segment', _totals),
                                       ('max clicks in a 1-unit window', burst_peaks)]:
            _flip = float(np.mean(_values[_labels])) if np.any(_labels) else float('nan')
            _no_flip = float(np.mean(_values[~_labels])) if np.any(~_labels) else float('nan')
            print(f'{_metric_name}: flip labels {_flip:.3f}; no-flip labels {_no_flip:.3f}')
        print(f'Tier A nominal click data: {len(_labels)} segments, {_labels.sum()} flip labels.')
        print('Short-window peaks target the localized burst; total clicks also contain background kicks.')
        _fig, _axes = plt.subplots(1, 2, figsize=(10.5, 3.7))
        for _ax, _vals, _title in zip(
            _axes,
            (_totals, burst_peaks),
            ('All clicks (full 200 units)', 'Maximum clicks in one time unit'),
        ):
            _bins = min(35, max(4, len(np.unique(_vals))))
            _ax.hist(_vals[~_labels], bins=_bins, density=True, histtype='step',
                     label='No flip label')
            if np.any(_labels):
                _ax.hist(_vals[_labels], bins=_bins, density=True, histtype='step',
                         label='Flip label')
            _ax.set(xlabel=_title, ylabel='Density', title=_title)
            _ax.legend(fontsize=8)
        plt.tight_layout()
        _fig
        print('Important: labels are sampled final-readout outcomes; a burst is evidence, not proof, of a flip.')
    return burst_peaks, click_data


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2.2 Scaling with the cat size

    **Below we measure the nominal Tier A click data**: loop over `nbar` (keep the other parameters), measure the burst size, the
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
def _(burst_peaks, click_data, np, plt):
    # Step 2.2: empirical scaling on nominal Tier A data (no new simulations).
    if click_data is None or burst_peaks is None:
        print('Step 2.2 skipped: Step 2.1 could not load labelled Tier A click records.')
    else:
        _labels = np.asarray(click_data['labels']).astype(bool)
        _sizes = np.asarray(click_data['nbar'])
        _clicks = np.asarray(click_data['clicktimes'])
        _totals = np.sum(np.isfinite(_clicks), axis=1)
        _rows = []
        for _size in np.unique(_sizes):
            _m = _sizes == _size
            _flip = _m & _labels
            _no = _m & (~_labels)
            _rows.append((float(_size), float(np.mean(_labels[_m])),
                          float(np.mean(burst_peaks[_flip])) if np.any(_flip) else float('nan'),
                          float(np.mean(burst_peaks[_no])) if np.any(_no) else float('nan'),
                          float(np.mean(_totals[_flip])) if np.any(_flip) else float('nan'),
                          float(np.mean(_totals[_no])) if np.any(_no) else float('nan')))
        print('Cat size | Flip label fraction | Max 1-unit clicks (flip/no) | Total clicks (flip/no)')
        for _r in _rows:
            print(f'{_r[0]:7.1f} | {_r[1]:18.2%} | {_r[2]:6.2f} / {_r[3]:6.2f} | '
                  f'{_r[4]:6.2f} / {_r[5]:6.2f}')
        _x = np.array([r[0] for r in _rows]); _p = np.array([r[1] for r in _rows])
        _fig, _axes = plt.subplots(1, 2, figsize=(9.5, 3.5))
        _axes[0].plot(_x, _p, 'o-')
        _axes[0].set(xlabel='Cat size nbar', ylabel='Final flip-label fraction',
                     title='Flip labels versus cat size')
        _axes[1].plot(_x, [r[2] for r in _rows], 'o-', label='Flip labels')
        _axes[1].plot(_x, [r[3] for r in _rows], 's-', label='No-flip labels')
        _axes[1].set(xlabel='Cat size nbar', ylabel='Peak clicks in 1 time unit',
                     title='Local burst versus background')
        _axes[1].legend(fontsize=8)
        plt.tight_layout(); _fig
        print('These are observed click-record statistics, not measurements of the hidden device.')
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
    _fig    # The opt-in sweep below varies kappa_b at fixed effective kappa_2.
    # The optional two-mode spectrum uses rates.spectrum(model, n_eig=6). Mind the memory:
    # about 30 s and 1.2 GB with Nb = 6; with the Nb = 8 of this cell it takes minutes and 2.7 GB, more than the Aqora workspace has.
    # Nb = 6 changes Gamma_Z by 0.03 % here.
    return


@app.cell
def _(mo):
    run_buffer_sweep = mo.ui.run_button(label="Optional: run costly two-mode buffer-bandwidth sweep")
    run_buffer_sweep
    return (run_buffer_sweep,)


@app.cell
def _(mo, models, p, rates, run_buffer_sweep):
    mo.stop(not run_buffer_sweep.value)
    for _kb in [4.0, 8.0, 16.0]:
        _params = models.TwoModeParams(nbar=p.nbar, kappa1=p.kappa1, nth=p.nth,
            kappa_phi=p.kappa_phi, kappa_b=_kb, Na=p.N, Nb=6)
        _model = models.two_mode(_params)
        _rate = rates.spectrum(_model,n_eig=6)
        print(f"kappa_b={_kb:g}, g2={_params.g2:.4f}, "
              f"4*g2^2/kappa_b={4*_params.g2**2/_kb:.3f}, Gamma_Z={_rate['gamma_z']:.5e}")
    print("These are simulated nominal devices; this sweep does not identify private hidden-device parameters.")
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
    return submission_dir, test, val


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

            clf = LogisticRegression(C=5.0, max_iter=1000, random_state=42)
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

    # Save ensemble predictions to tierB.csv
    my_score = test_scores
    my_decision = (my_score > np.quantile(my_score, protocol.YIELD)).astype(int)
    scoring.write_submission(submission_dir / "tierB.csv", my_score, my_decision)
    print("Successfully written ensemble predictions to submission_template/tierB.csv!")
    return (val_cv_scores,)


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

    How informative is a burst about the logical qubit? A photon counter is a useful
    microscope for this question, so this cell uses the labelled click records of the nominal
    device (`tierA_train.npz`, the dataset of tutorial 5). They give the probability of a flip
    label given the size $n$ of the burst of a segment, and the distributions of $n$ in flip
    and flip-free segments, at one cat size. This cell uses the maximum clicks in a one-unit window for $n$, not the
    full-segment total count. Then ask the same question of your heterodyne
    detector: what does its score say about the label when it is at its largest?
    """)
    return


@app.cell
def _(burst_peaks, click_data, np, plt, val, val_cv_scores):
    # Step 4.1: Tier A photon-counting burst evidence and Tier B detector precision.
    _fig, _axes = plt.subplots(1, 3, figsize=(13.0, 3.8))
    if click_data is None or burst_peaks is None:
        for _ax in _axes[:2]:
            _ax.text(.5, .5, 'Tier A data unavailable', ha='center', va='center', transform=_ax.transAxes)
            _ax.set_axis_off()
    else:
        _cat = 2.5
        _size = np.asarray(click_data['nbar'])
        _labels_a = np.asarray(click_data['labels']).astype(bool)
        _group = _size == _cat
        _events = np.asarray(burst_peaks)[_group]
        _y_a = _labels_a[_group]
        if not np.any(_group):
            raise ValueError('Cat size 2.5 not present in Tier A train data')
        _cap = int(np.quantile(_events, .98))
        _binned = np.minimum(_events, _cap)
        _xx, _p, _lo, _hi, _pf, _pn = [], [], [], [], [], []
        for _v in np.unique(_binned):
            _take = _binned == _v
            _N = int(np.sum(_take))
            _k = int(np.sum(_y_a[_take]))
            _rate = _k / _N
            _z = 1.96
            _den = 1 + _z * _z / _N
            _center = (_rate + _z * _z / (2 * _N)) / _den
            _delta = (_z / _den) * np.sqrt(_rate*(1-_rate)/_N + _z*_z/(4*_N*_N))
            _xx.append(int(_v)); _p.append(_rate)
            _lo.append(max(0, _center-_delta)); _hi.append(min(1, _center+_delta))
            _pf.append(_k / max(1, int(_y_a.sum())))
            _pn.append((_N-_k) / max(1, int((~_y_a).sum())))
        _xx = np.asarray(_xx); _p=np.asarray(_p)
        _axes[0].errorbar(_xx, _p, yerr=[_p-np.array(_lo), np.array(_hi)-_p],
                          fmt='o-', capsize=3)
        _axes[0].set(xlabel='Maximum clicks in 1 time unit (last bin >= cap)',
                     ylabel='P(flip label | count)', title=f'Nominal Tier A, nbar={_cat}')
        _axes[1].plot(_xx, _pf, 'o-', label='Flip label')
        _axes[1].plot(_xx, _pn, 's-', label='No flip label')
        _axes[1].set(xlabel='Peak click count', ylabel='P(count | label)',
                     yscale='log', title='Burst size conditioned on readout')
        _axes[1].legend(fontsize=8)
    _ys = np.asarray(val['labels']).astype(bool)
    _score = np.asarray(val_cv_scores)
    _order = np.argsort(_score, kind='stable')[::-1]
    for _fraction in [0.01, 0.05, 0.10, 0.30]:
        _n = max(1, int(round(_fraction * len(_ys))))
        _k = int(np.sum(_ys[_order[:_n]]))
        print(f'Tier B out-of-fold scores: top {_fraction:.0%}, '
              f'flip labels {_k}/{_n}, precision={_k/_n:.2%}')
    _groups = np.array_split(np.argsort(_score, kind='stable'), 10)
    _score_means = [np.mean(_score[_g]) for _g in _groups]
    _label_rates = [np.mean(_ys[_g]) for _g in _groups]
    _axes[2].plot(_score_means, _label_rates, 'o', label='OOF score bins')
    _axes[2].plot([0,1], [0,1], '--', color='gray', label='Ideal calibration')
    _axes[2].set(xlabel='Estimated flip probability', ylabel='Observed label rate',
                 title='Tier B reliability check', xlim=(0,1), ylim=(0,1))
    _axes[2].legend(fontsize=8)
    plt.tight_layout(); _fig
    print('Calibration is a diagnostic, not a guarantee; readout labels are stochastic.')
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
def _(np, plt, protocol, repcode, scoring, val, val_cv_scores):
    # Step 4.2a: actual held-out detector scores, using the installed package API.
    _labels = np.asarray(val['labels']).astype(bool)
    _scores = np.asarray(val_cv_scores, dtype=float)
    _size = np.asarray(val['nbar'])
    def _flag_top_fraction(fraction):
        _n_keep = int(round((1-fraction) * len(_scores)))
        _flag = np.ones(len(_scores), dtype=bool)
        _flag[np.argsort(_scores, kind='stable')[:_n_keep]] = False
        return _flag

    _flag30 = _flag_top_fraction(1-protocol.YIELD)
    _post = scoring.postselection(_flag30, _labels)
    _corr = scoring.score(_flag30, _labels)
    _c = scoring.confusion(_flag30, _labels)
    _precision = _c['tp'] / max(_c['tp']+_c['fp'], 1)
    print('Hidden-device Tier B, out-of-fold classifier, globally pooled top 30%:')
    print(f"  yield={_post['yield']:.3f}, rho={_post['rho']:.4f}, "
          f"suppression={1-_post['rho']:.4f}")
    print(f"  TPR={_corr['tpr']:.4f}, FPR={_corr['fpr']:.4f}, "
          f"flag precision={_precision:.3%}, correction S={_corr['S']:.4f}")
    print('Applying logical X helps iff P(flip label | flagged)>50%; the 30% discard budget is not an optimal X threshold.')
    _fractions = np.array([.01, .02, .05, .10, .20, .30, .40, .50])
    _post_rates = []
    _x_rates = []
    for _fraction in _fractions:
        _f = _flag_top_fraction(float(_fraction))
        _p = scoring.postselection(_f, _labels)
        _s = scoring.score(_f, _labels)
        _cm = scoring.confusion(_f, _labels)
        _precision_f = _cm['tp']/max(_cm['tp']+_cm['fp'], 1)
        _post_rates.append(_p['p_kept'])
        _x_rates.append(_labels.mean()*_s['S'])
        print(f'  flagged {_fraction:5.0%}: p_kept={_p["p_kept"]:.4%}, '
              f'S={_s["S"]:.3f}, flagged precision={_precision_f:.2%}')
    _fig, _ax = plt.subplots(figsize=(8.3, 3.8))
    _ax.plot(_fractions, _post_rates, 'o-', label='Post-selection: p among kept')
    _ax.plot(_fractions, _x_rates, 's-', label='Hypothetical X: residual p')
    _ax.axhline(float(np.mean(_labels)), ls='--', color='gray', label='No herald')
    _ax.axvline(.3, ls=':', color='black', label='30% challenge budget')
    _ax.set(xlabel='Fraction of segments flagged', ylabel='Flip-label probability',
            title='Step 4.2: measured post-selection versus hypothetical X')
    _ax.legend(fontsize=8)
    plt.tight_layout(); _fig

    # The repetition code expects a single physical flip probability per qubit.
    # Use one cat size, not the mixed-size pooled dataset.
    _single_size = 3.5
    _one = _size == _single_size
    _y1 = _labels[_one]
    _f1 = _flag30[_one]
    _p1 = float(np.mean(_y1))
    _single_post = scoring.postselection(_f1, _y1)
    _single_cor = scoring.score(_f1, _y1)
    print(f'For repetition-code illustrations: fixed cat size nbar={_single_size}, '
          f'p_flip={_p1:.4%}, per-qubit yield={_single_post["yield"]:.3f}')
    for _d in (3,5,7):
        _without = repcode.logical_bitflip_probability(_d, _p1)
        _corrected = repcode.logical_bitflip_probability(
            _d, _p1, tpr=_single_cor['tpr'], fpr=_single_cor['fpr'])
        _ps = repcode.postselected_memory(
            _d, _p1, rho=_single_post['rho'], yield_per_qubit=_single_post['yield'])
        print(f'  distance {_d}: no herald {_without:.5f}; '
              f'conditional post-selection {_ps["p_logical_bitflip_kept"]:.5f} '
              f'(joint yield {_ps["yield"]:.2%}); '
              f'hypothetical X {_corrected:.5f}')
    print('Repetition-code calculations assume independent qubits; they are not measured logical-QEC performance.')
    return


@app.cell
def _(np, seg):
    # Step 4.2b: optional privileged oracle from Step 1.4, which is expensive.
    # The counting simulation conditions pneg on every physical jump channel.
    _pneg = np.asarray(seg['pneg'], dtype=float)
    if _pneg.size:
        _f = np.ones(len(_pneg), dtype=bool)
        _f[np.argsort(_pneg, kind='stable')[:int(round(.7*len(_pneg)))]] = False
        _p0 = float(np.mean(_pneg))
        _p_kept = float(np.mean(_pneg[~_f]))
        _p_x30 = float(np.mean(np.where(_f, 1-_pneg, _pneg)))
        _optimal = float(np.mean(np.minimum(_pneg, 1-_pneg)))
        print('Privileged counting-simulation oracle: NOT accessible to the buffer detector.')
        print(f'  original pneg mean {_p0:.5f}; top-30% post-selection {_p_kept:.5f}; '
              f'X on top 30% {_p_x30:.5f}; optimal rule pneg>0.5 {_optimal:.5f}.')
        print('Oracle numbers are for the simulated NOMINAL device, not the hidden test device.')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 4.3 Sealed prediction (Sunday 09:00): Bernoulli errors and Weighted Fit

    On Sunday morning at 09:00, a new mystery cat size $\bar{n}^\star$ is announced.
    Below is a label-based weighted-rate fit with approximate uncertainty propagation:
    1. Plug-in binomial standard errors (normal approximation) $\sigma_p = \sqrt{p(1-p)/N}$ for each cat size.
    2. Analytical error propagation from $p$ to the bit-flip rate $\Gamma_Z$ and $\ln \Gamma_Z$.
    3. Weighted Least Squares (WLS) linear fit of $\ln \Gamma_Z$ vs $\bar{n}$.
    4. Prediction function `predict_sealed_cat(nbar_star)` with approximate $\pm 1\sigma$ fit error bars; extrapolation model uncertainty must be assessed separately.
    """)
    return


@app.cell
def _(np, plt, val):
    # 1. Flip-label counts per cat size on the hidden device (Validation set)
    _nbar_pts = np.array([2.0, 2.5, 3.0, 3.5])
    _N_pts = np.array([int(np.sum(val["nbar"] == _v)) for _v in _nbar_pts])
    _k_pts = np.array([int(np.sum((val["nbar"] == _v) & (val["labels"] == 1))) for _v in _nbar_pts])
    _T_seg_fit = 200.0

    # 2. Plug-in normal-approximate binomial standard error: sigma_p = sqrt(p * (1 - p) / N)
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

    # Fit-and-uncertainty plot (not a calibration plot)
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
    _ax.set_title(r"Sealed prediction: approximate fit bands inflated by $\sqrt{\chi^2/{\rm dof}}$")
    _ax.legend()
    plt.tight_layout()
    _fig
    return


if __name__ == "__main__":
    app.run()
