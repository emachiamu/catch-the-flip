# /// script
# requires-python = ">=3.11"
# dependencies = [
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
    # Tutorial 4: Monitoring a cat qubit, quantum trajectories with dynamiqs

    The three previous tutorials simulate the *average* evolution of a cat qubit with the
    Lindblad master equation. In this challenge the buffer output of the cat is **measured**,
    continuously, and we want to know what a single run looks like given its measurement
    record. This is the realm of *quantum trajectories* (unravelings of the master equation).
    dynamiqs ships four stochastic solvers; we use two of them:

    * `dq.jssesolve`: jump unraveling, the record is a list of **click times** (photon counting),
    * `dq.dssesolve`: diffusive unraveling, the record is a noisy **continuous signal**
      (homodyne or heterodyne detection).

    Along the way we meet the central physical fact of the challenge: *the buffer channel is
    dark as long as the memory sits in the code space, and shines when it does not.*

    Everything is in units of $\kappa_2 = 1$ (see `docs/THEORY.md`). The helper package
    `catchtheflip` builds the models and wraps the solvers; feel free to look at its source,
    it is short.
    """)
    return


@app.cell
def _():
    import numpy as np
    import matplotlib.pyplot as plt
    import dynamiqs as dq

    from catchtheflip import models, simulate, rates, records, scoring

    dq.set_precision("double")
    return dq, models, np, plt, rates, records, scoring, simulate


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The model and its channels

    We use a small, deliberately noisy cat ($\bar n = 1.5$, strong dephasing) so that bit flips
    happen within a few hundred time units. The challenge device is quieter and bigger.
    """)
    return


@app.cell
def _(models):
    p = models.SingleModeParams(nbar=1.5, kappa1=0.02, nth=0.1, kappa_phi=0.05, N=16)
    m = models.single_mode(p)
    print("channels:", m.channels)
    for _name, _op in zip(m.channels, m.jump_ops):
        print(f"  {_name:10s} jump operator of shape {_op.shape}")
    return m, p


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The buffer channel $L_2 = \sqrt{\kappa_2}(a^2 - \alpha^2)$ annihilates both $|\pm\alpha\rangle$:
    its click rate $\langle L_2^\dagger L_2\rangle$ vanishes in the code space. Kick the memory
    out (here: add one photon with $a^\dagger$) and the channel lights up.
    """)
    return


@app.cell
def _(dq, m):
    a = m.a
    L2 = m.L_buffer
    psi_code = m.psi0                                   # |+alpha>
    psi_kicked = (a.dag() @ psi_code).unit()            # a^dagger |alpha>, normalised
    for _name, _psi in [("|+alpha>", psi_code), ("a^dag |+alpha>", psi_kicked)]:
        _rate = dq.expect(L2.dag() @ L2, _psi).real
        print(f"buffer click rate in {_name:16s}: {float(_rate):.3f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. One trajectory: watch the cat flip

    `simulate.long_trajectory` runs `dq.jssesolve` with all channels unravelled as jumps and
    records $\langle Z_L\rangle(t) = 1 - 2P(x<0)$, the expectation of the Z readout of the
    conditional state, together with the click times of every channel. Only the buffer clicks
    are *observable* in the challenge; the others are privileged information that we use here
    to understand what happens.
    """)
    return


@app.cell
def _(m, np, plt, simulate):
    traj = simulate.long_trajectory(m, T=400.0, seed=3, dt=2e-3)
    t, zl = traj["t"], traj["z"]

    _fig, _ax = plt.subplots(2, 1, figsize=(9, 5), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    _ax[0].plot(t, zl, lw=1)
    _ax[0].axhline(0, color="k", lw=0.5)
    _ax[0].set_ylabel(r"$\langle Z_L\rangle = 1 - 2P(x<0)$")
    for _k, _name in enumerate(m.channels):
        _c = traj["clicktimes"][_k]
        _c = _c[~np.isnan(_c)]
        _ax[1].plot(_c, np.full_like(_c, _k), "|", ms=12)
    _ax[1].set_yticks(range(len(m.channels)))
    _ax[1].set_yticklabels([f"{_name} ({np.sum(~np.isnan(traj['clicktimes'][_k]))})" for _k, _name in enumerate(m.channels)])
    _ax[1].set_xlabel(r"time $[1/\kappa_2]$")
    plt.tight_layout()
    _fig
    return t, traj, zl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Two things to notice.

    1. **Loss clicks do nothing visible**: $a|\alpha\rangle = \alpha|\alpha\rangle$, the state
       is an eigenstate of the jump. (They flip the parity, i.e. the logical $X$, which we do
       not plot.)
    2. **Thermal and dephasing clicks** kick the state out of the code space; the buffer then
       sometimes clicks while the stabilisation brings the state back. Most of the time the
       state comes back to the same lobe. Occasionally $\langle Z_L\rangle$ drops: a bit flip.
       Look at where it drops *to*. What the conditional state is after a flip, and why, is a
       question of step 1 of the challenge.

    Zoom on the buffer click that pulled $\langle Z_L\rangle$ down the most, and look at what
    happens before and after it. Do not expect a fireworks display with this small cat: the
    burst of a flip is of order $\bar n^2 \kappa_2 \tau$ photons, only a few at $\bar n = 1.5$,
    and many drops of $\langle Z_L\rangle$ in this unraveling are gradual (one dephasing kick at
    a time).
    The burst grows quickly with the cat size; that is the point of step 2 of the challenge.
    Statistically, though, flip segments do carry more buffer clicks (section 3).
    """)
    return


@app.cell
def _(m, np, plt, t, traj, zl):
    c_buf = traj["clicktimes"][m.buffer_index]
    c_buf = c_buf[~np.isnan(c_buf)]
    _k = np.searchsorted(t, c_buf)                       # first saved time after each buffer click
    before, after = zl[np.maximum(_k - 1, 0)], zl[np.minimum(_k + 1, len(t) - 1)]
    _j = int(np.argmax(before - after))                  # the click that pulled <Z_L> down the most
    t_flip = c_buf[_j]
    window = (t_flip - 10, t_flip + 12)

    _fig, _ax = plt.subplots(figsize=(9, 3))
    _ax.plot(t, zl, lw=1)
    _ax.plot(c_buf, np.full_like(c_buf, 1.1), "r|", ms=15, label="buffer clicks")
    _ax.set_xlim(window)
    _ax.set_xlabel(r"time $[1/\kappa_2]$")
    _ax.set_ylabel(r"$\langle Z_L\rangle$")
    _ax.legend()
    plt.tight_layout()
    print(f"buffer click at t = {t_flip:.1f}: <Z_L> from {before[_j]:.2f} to {after[_j]:.2f}")
    print("buffer clicks per unit time over the whole run:", round(len(c_buf) / 400.0, 3))
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Segments, readout and labels

    The challenge data are *segments*: the memory is prepared in $|+\alpha\rangle$, monitored
    for $T_{\rm seg}$, then read out in $Z$. `simulate.counting_segments` returns, for each
    segment, the buffer click times and `pneg`, the probability that the readout gives
    $-\alpha$ (the weight of the conditional state on $x<0$). The label of a segment is a
    *sample* of that readout (`records.sample_labels`).
    """)
    return


@app.cell
def _(m, np, records, simulate):
    seg = simulate.counting_segments(m, n_segments=300, T_seg=20.0, seed=1)
    labels = records.sample_labels(seg["pneg"], rng=0)
    n_clicks = np.sum(~np.isnan(seg["clicktimes"]), axis=1)
    print(f"flip probability per segment: {labels.mean():.3f}  ({labels.sum()} flips in {len(labels)} segments)")
    print(f"mean buffer clicks: flip segments {n_clicks[labels == 1].mean():.2f}, others {n_clicks[labels == 0].mean():.2f}")
    return labels, seg


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The average over segments must agree with the master equation: this is the standard sanity
    check of any trajectory simulation (and of the time step `dt`).
    """)
    return


@app.cell
def _(labels, m, np, seg, simulate):
    p_me = simulate.master_equation_pneg(m, 20.0)[-1]
    print(f"P(-alpha at T_seg): trajectories {seg['pneg'].mean():.4f} +- {seg['pneg'].std() / np.sqrt(len(labels)):.4f}, master equation {p_me:.4f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    And the rates can be read off the Liouvillian spectrum without any time evolution:
    $\langle Z_L\rangle(t) = e^{-\Gamma_Z t}$ gives $P(-\alpha, T) = (1 - e^{-\Gamma_Z T})/2$.
    """)
    return


@app.cell
def _(m, p, rates):
    sp = rates.spectrum(m)
    gx_estimate = 2 * p.kappa1 * ((1 + 2 * p.nth) * p.nbar + p.nth)   # loss and thermal jumps flip the parity
    print(f"Gamma_Z = {sp['gamma_z']:.3e}  (T_Z = {1 / sp['gamma_z']:.0f}),  Gamma_X = {sp['gamma_x']:.3e}  (2 kappa_1 [(1 + 2 n_th) nbar + n_th] = {gx_estimate:.3f})")
    print(f"predicted P(-alpha, 20) = {rates.flip_probability(sp['gamma_z'], 20.0):.4f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. A first detector, and the challenge metrics

    Count the buffer clicks of each segment and rank the segments by that count. The
    leaderboard discards the 30 % most suspicious segments, computes the residual flip
    fraction $\rho_{70}$ among the rest (`catchtheflip.scoring.rho_at_yield`) and reports the
    flip suppression $1 - \rho_{70}$ (higher is better); the AUC summarises the whole ranking.
    Try a smarter feature, for example the maximum number of clicks in any window of two time
    units: bursts are short. (The segments of this tutorial last 20 time units to keep it
    fast. The challenge datasets use segments of 200, at four cat sizes mixed in one file.)
    """)
    return


@app.cell
def _(labels, np, records, scoring, seg):
    obs = records.apply_counting_imperfections(seg["clicktimes"], T_seg=20.0, eta=0.8, dark_rate=0.02, rng=0)
    feature_total = np.sum(~np.isnan(obs), axis=1)

    def max_in_window(clicktimes, width=2.0):
        out = []
        for c in records.unpad_clicks(clicktimes):
            out.append(max((np.sum((c >= t0) & (c < t0 + width)) for t0 in c), default=0))
        return np.array(out)

    feature_window = max_in_window(obs)
    for _name, _f in [("total clicks", feature_total), ("max clicks in a window of 2", feature_window)]:
        _r = scoring.rho_at_yield(_f, labels)
        print(f"{_name:30s}: AUC = {scoring.auc(_f, labels):.3f}, 1 - rho_70 = {_r['suppression']:.2f} ({_r['flips_discarded']} of {_r['flips_total']} flips discarded with 30 % of the segments)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    With this small, noisy cat the bursts are weak (a flip emits about $\bar n^2 \kappa_2\tau$
    photons) and the background of kicks is strong, so the ranking is poor. The challenge
    device has bigger cats, from $\bar n = 2$ to $3.5$. Part of your job is to understand how
    the burst, the background and the flip rate scale with $\bar n$, and what a good ranking is
    worth for a logical qubit (`docs/THEORY.md`, section 7, and step 4 of the challenge).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Heterodyne records

    Real buffer outputs are usually measured with a heterodyne detector rather than a photon
    counter. `simulate.heterodyne_segments` returns the two quadratures $I$ and $Q$ of the
    output field, binned in time, with white noise of variance (1/bin duration) on top, for a
    detection efficiency `eta`. The expected signal during a burst is
    $\sqrt{2\eta}\,\mathrm{Re}\langle a^2 - \alpha^2\rangle \approx -\sqrt{2\eta}\,\alpha^2$:
    negative, in the $I$ quadrature.

    A word on the integrator. `heterodyne_segments` uses the scheme of Rouchon and Ralph
    (`dq.method.Rouchon1`), which keeps the state physical at every step. The textbook
    Euler-Maruyama scheme (`method="euler"`) is fine for this short segment of a small cat. For
    the segments of the challenge (200 time units, cats up to $\bar n = 3.5$) it is not: rare
    large noise increments scramble the state, and the flip probability comes out two to four
    times too large, whatever the time step. A stochastic simulation that runs is not yet a
    simulation that is right: compare its average with the master equation, as in section 3.
    """)
    return


@app.cell
def _(m, np, plt, records, simulate):
    het = simulate.heterodyne_segments(m, n_segments=200, T_seg=20.0, n_bins=100, eta=0.5, seed=2)
    labels_h = records.sample_labels(het["pneg"], rng=1)
    tb = 0.5 * (het["t_bins"][1:] + het["t_bins"][:-1])
    _fig, _ax = plt.subplots(1, 2, figsize=(10, 3), sharey=True)
    for _axis, _lab, _title in [(_ax[0], 0, "a segment without flip"), (_ax[1], 1, "a segment with a flip")]:
        _k = np.where(labels_h == _lab)[0][0]
        _axis.plot(tb, het["I"][_k], lw=0.8, label="I")
        _axis.plot(tb, het["Q"][_k], lw=0.8, label="Q", alpha=0.6)
        _axis.plot(tb, np.convolve(het["I"][_k], np.ones(10) / 10, "same"), "k", lw=1.5, label="I, 10-bin average")
        _axis.set_title(_title)
        _axis.set_xlabel(r"time $[1/\kappa_2]$")
    _ax[0].legend(fontsize=8)
    plt.tight_layout()
    print("I record standard deviation:", round(float(het["I"].std()), 2), " (white noise: sqrt(1/0.2) =", round(np.sqrt(5), 2), ")")
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. The buffer as a real mode

    In the device the buffer is a resonator with decay rate $\kappa_b$, not an abstract
    channel. `models.two_mode` builds the memory + buffer model; its monitored channel is
    $i\sqrt{\kappa_b}\, b \simeq \sqrt{\kappa_2}(a^2 - \alpha^2)$ (the phase $i$ gives the burst
    the same sign as in the single-mode model). The adiabatic elimination of section 2 of the
    primer predicts the same physics with $\kappa_2 = 4 g_2^2 / \kappa_b$, and a buffer that lights up during a
    flip. The fixed-step integrator needs a smaller step here (`dt=1e-3`): the Hamiltonian
    terms of the two-mode model make larger steps unstable. (`method="event"` selects the
    adaptive event-based integrator of dynamiqs instead, whose maximum step `dtmax` sets how
    precisely the click times are resolved. Whatever the integrator, validate it against the
    master equation before trusting it.)
    """)
    return


@app.cell
def _(models, plt, simulate):
    p2 = models.TwoModeParams(nbar=1.5, kappa1=0.02, nth=0.1, kappa_phi=0.05, kappa_b=4.0, Na=14, Nb=6)
    m2 = models.two_mode(p2)
    print(f"g2 = {p2.g2:.3f}, eps_d = {p2.eps_d:.3f}, kappa_2 = 4 g2^2 / kappa_b = {4 * p2.g2**2 / p2.kappa_b:.2f}")
    traj2 = simulate.long_trajectory(m2, T=150.0, seed=5, dt=1e-3)
    _fig, _ax = plt.subplots(2, 1, figsize=(9, 4), sharex=True)
    _ax[0].plot(traj2["t"], traj2["z"])
    _ax[0].set_ylabel(r"$\langle Z_L\rangle$")
    _ax[1].plot(traj2["t"], traj2["nb"])
    _ax[1].set_ylabel(r"$\langle b^\dagger b\rangle$")
    _ax[1].set_xlabel(r"time $[1/\kappa_2]$")
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exercises

    1. Increase `nbar` to 2 and 2.5 (and `N` accordingly). How do the burst size and the
       number of background clicks per segment change? How does the flip probability change?
    2. Leave the dephasing channel unmonitored: simulate the segments with the stochastic
       master equation `dq.jsmesolve(m.H, m.jump_ops, thetas=[0, 0, 0, 0], etas=[1, 1, 1, 0], ...)`
       (efficiency 0 for the dephasing channel, whose effect is then averaged in the master
       equation; use `method=dq.method.EulerJump(dt=...)` and a `tsave` tuple whose times are
       multiples of `dt`). Does the *record* of the buffer channel change its statistics? Does
       the conditional $\langle Z_L\rangle(t)$ look the same?
    3. Compute $\Gamma_Z$ from the spectrum for $\bar n = 1, 1.5, \dots, 4$ and plot
       $\log \Gamma_Z$ against $\bar n$. Which error channel sets the slope?

    Each exercise defines new variables: in marimo a global name can be defined in one cell
    only, so pick new names (`p_ex1`, `m_ex1`, `seg_ex1`, …) or cell-local ones that start
    with an underscore.
    """)
    return


if __name__ == "__main__":
    app.run()
