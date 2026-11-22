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
    # Tutorial 5: Catching flips in click records

    Tutorial 4 monitored one small cat that we simulated ourselves. This tutorial takes a
    dataset of the challenge format and goes through the whole job of a flip detector once,
    on records where the physics can be seen by eye: the **click records** of a photon counter
    on the buffer output (the dataset *tier A*).

    * what a dataset of the challenge holds, and what a flip looks like in a record;
    * what a detector is, and how the leaderboard scores it;
    * three simple detectors, and a puzzle that the challenge asks you to solve.

    **Nothing in this tutorial is scored or handed in.** The challenge asks for the same job
    on the *heterodyne* records (the dataset *tier B*), where the burst of a flip sits under
    the vacuum noise; the template notebook starts there. The click records stay available
    as a microscope for the physics questions of the challenge (steps 2 and 4).

    Times are in units of $1/\kappa_2$ (see `docs/THEORY.md`).
    """)
    return


@app.cell
def _():
    import numpy as np
    import matplotlib.pyplot as plt

    from catchtheflip import protocol, records, scoring

    return np, plt, protocol, records, scoring


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 1. The dataset

    A *segment* is one memory experiment: the cat is prepared in $|{+lpha}    angle$, its
    buffer output is recorded for $T_{    m seg} = 200$, and the cat is read out. The label is 1
    when the readout gave $-lpha$: the cat has flipped. Every split mixes segments of four
    cat sizes in random order, and the array `nbar` gives the cat size of each segment.

    * `train`: the *nominal device*, the one of the device sheet, which you can simulate;
    * `val`: the *hidden test device*, whose buffer has a finite bandwidth and whose memory
      has a small Kerr non-linearity. It is the device of the leaderboard.

    `records.load_dataset` reads a split from the Aqora dataset, or from a file of that name
    if you put one in `data/`.
    """)
    return


@app.cell
def _(mo, np, records):
    data_dir = mo.notebook_dir().parent / "data"                 # a split is read from Aqora unless its file is in this folder
    train = records.load_dataset(data_dir / "tierA_train.npz")   # nominal device, labelled
    val = records.load_dataset(data_dir / "tierA_val.npz")       # hidden device, labelled
    print(train["meta"])
    for _name, _d in [("train (nominal device)", train), ("val (hidden device)", val)]:
        print(f"\n{_name}: {len(_d['nbar'])} segments, {int(_d['labels'].sum())} flip labels")
        for _v in np.unique(_d["nbar"]):
            _m = _d["nbar"] == _v
            _n = np.sum(~np.isnan(_d["clicktimes"][_m]), axis=1)
            print(f"   cat size {_v:g}: {_m.sum():5d} segments, {_d['labels'][_m].mean():6.2%} with a flip label, {_n.mean():4.1f} clicks per segment")
    return train, val


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Two trends run against each other, and they will matter in section 4: a bigger cat flips
    less often, and it clicks more often. Most clicks have nothing to do with a flip. A
    thermal photon or a dephasing event kicks the memory out of its code space for a moment,
    the buffer brings it back and sometimes emits a photon (tutorial 4, section 2), and the
    counter adds dark counts.

    ## 2. What a flip looks like

    A record is a list of click times. Here are eight records with a flip label and eight
    without, at the largest cat size of the nominal device. The red bar marks the time unit
    of each record that holds the most clicks, and the number on the right counts them.
    """)
    return


@app.cell
def _(np, plt, records, train):
    def densest_window(clicks, width=1.0):
        """Start and number of clicks of the window of duration `width` that holds the most clicks."""
        if len(clicks) == 0:
            return 0.0, 0
        counts = np.searchsorted(clicks, clicks + width, side="left") - np.arange(len(clicks))
        k = int(np.argmax(counts))
        return float(clicks[k]), int(counts[k])

    _sel = train["nbar"] == 3.5
    _clicks = records.unpad_clicks(train["clicktimes"][_sel])
    _labels = train["labels"][_sel]
    _fig, _ax = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
    for _axis, _title, _lab in [(_ax[0], "flip label", 1), (_ax[1], "no flip label", 0)]:
        for _row, _k in enumerate(np.flatnonzero(_labels == _lab)[:8]):
            _c = _clicks[_k]
            _t0, _n = densest_window(_c)
            _axis.plot(_c, np.full_like(_c, _row), "|", ms=11, color="C0")
            _axis.plot([_t0, _t0 + 1.0], [_row - 0.38, _row - 0.38], color="C3", lw=3, solid_capstyle="butt")
            _axis.text(203, _row, str(_n), va="center", fontsize=9, color="C3")
        _axis.set_title(f"{_title}, cat size 3.5 (nominal device)")
        _axis.set_xlabel(r"time $[1/\kappa_2]$")
        _axis.set_xlim(0, 200)
    _ax[0].set_ylabel("record")
    _ax[0].set_yticks(range(8))
    plt.tight_layout()
    _fig
    return (densest_window,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Most records with a flip label hold a tight cluster of clicks, a **burst**: the buffer
    radiates while the memory is out of its code space, and a flip is the longest excursion
    there is. The records without a flip label hold nothing of the kind, only the sparse
    clicks of the background. Zoom on a burst (change `set_xlim`) to see how long it lasts.

    Look again, though: not every record with a flip label shows a burst. Step 2 of the
    challenge asks why, and step 4 asks the mirror question, what a record with a burst and
    *no* flip label is.

    ## 3. A detector, and how it is scored

    A detector takes the record and the cat size of a segment and returns a **score**: any
    real number, where higher means more suspicious. The crudest score is the total number of
    clicks of the segment.

    The leaderboard discards the 30 % of the segments with the highest scores, all cat sizes
    together, and compares the fraction of flips among the segments that are kept with the
    fraction of flips among all segments:

    $$\rho_{70} = \frac{p_{\rm flip}(\text{kept segments})}{p_{\rm flip}(\text{all segments})}.$$

    It reports the **flip suppression** $1 - \rho_{70}$: 0 for scores that carry no
    information, 1 when every flip was discarded. `scoring.rho_at_yield` computes it on any
    labelled split, and `scoring.postselection_curve` gives $\rho$ for every yield (the
    fraction of segments kept).
    """)
    return


@app.cell
def _(np, plt, protocol, scoring, val):
    def total_clicks(clicktimes):
        return np.sum(~np.isnan(clicktimes), axis=1).astype(float)

    score_total = total_clicks(val["clicktimes"])
    _r = scoring.rho_at_yield(score_total, val["labels"])
    print(f"total clicks, validation split: {_r['flips_discarded']} of {_r['flips_total']} flips are among the 30 % of the segments it discards")
    print(f"   flip fraction {_r['p_flip']:.4f} -> {_r['p_kept']:.4f} among the kept segments: rho_70 = {_r['rho']:.2f}, 1 - rho_70 = {_r['suppression']:.2f}")
    print(f"   AUC = {scoring.auc(score_total, val['labels']):.3f} (the probability that a flip segment scores higher than a flip-free one)")
    _Y, _rho = scoring.postselection_curve(score_total, val["labels"])
    plt.figure(figsize=(5, 3.2))
    plt.plot(_Y, _rho)
    plt.axvline(protocol.YIELD, color="k", ls=":", lw=0.8)
    plt.xlabel("yield (fraction of segments kept)")
    plt.ylabel(r"residual flip fraction $\rho$")
    plt.title("total clicks, validation split")
    plt.tight_layout()
    plt.gca()
    return (score_total,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Discarding 30 % of the segments at random would remove 30 % of the flips and leave
    $\rho_{70} = 1$. The total count does a little better than chance, and not much.

    ## 4. Three detectors and a puzzle

    Compare it with two others:

    * **the cat size alone**: discard the smallest cats first, without looking at any record.
      Small cats flip more often, so this is not as silly as it sounds;
    * **the densest time unit**: the largest number of clicks that a record holds within one
      time unit, the red bars of section 2 (tutorial 4 used the same idea).

    The 30 % are one budget for the four cat sizes. `scoring.by_cat_size` shows where a
    detector spends it.
    """)
    return


@app.cell
def _(densest_window, np, plt, protocol, records, score_total, scoring, val):
    def burst_count(clicktimes, width=1.0):
        return np.array([densest_window(c, width)[1] for c in records.unpad_clicks(clicktimes)], dtype=float)

    detectors = {
        "total clicks": score_total,
        "cat size alone": -val["nbar"],
        "densest time unit": burst_count(val["clicktimes"]),
    }
    plt.figure(figsize=(5.5, 3.4))
    for _name, _score in detectors.items():
        _r = scoring.rho_at_yield(_score, val["labels"])
        print(f"\n{_name}: 1 - rho_70 = {_r['suppression']:.2f} ({_r['flips_discarded']} of {_r['flips_total']} flips discarded with 30 % of the segments)")
        for _v, _b in scoring.by_cat_size(_score, val["labels"], val["nbar"]).items():
            print(f"   cat size {_v:g}: {_b['discarded']:5.1%} of its segments discarded, {_b['flips_discarded']:4d} of {_b['flips_total']} flips")
        _Y, _rho = scoring.postselection_curve(_score, val["labels"])
        plt.plot(_Y, _rho, label=_name)
    plt.axvline(protocol.YIELD, color="k", ls=":", lw=0.8)
    plt.legend()
    plt.xlabel("yield (fraction of segments kept)")
    plt.ylabel(r"residual flip fraction $\rho$")
    plt.title("validation split (hidden device)")
    plt.tight_layout()
    plt.gca()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Counting all the clicks of a record does **worse** than not looking at the records at
    all. Looking at the right place of the record, its densest time unit, beats both.

    Two remarks on the scores themselves. Both counts are integers, so hundreds to thousands of
    segments share the score at the 30 % cut, and the scorer ranks equal scores by their position in
    the file: a finer score breaks such ties better than chance. And the validation split is
    finite: with its 1257 flips, $1 - \rho_{70}$ is known to about ±0.02.

    ## Questions

    These are yours to think about; nothing here is handed in.

    1. Why does the total number of clicks lose to the cat size alone? The table of section 1
       and the budget tables above hold the answer.
    2. The densest time unit ranks the records of one cat size well. Look at where it spends
       the budget across cat sizes: is that where the flips are? What would make the scores
       of a small cat and of a big cat comparable?
    3. The scores above are computed on the hidden device. Compute them on the nominal device
       (`train`) too. What changes, and what does not?
    4. Change the width of the window in `burst_count`. Which width works best, and what does
       it tell you about the duration of a burst?

    ## From clicks to quadratures

    The challenge is scored on the **heterodyne** records (dataset *tier B*): no clicks, but
    the two quadratures $I$ and $Q$ of the buffer output, averaged over 400 bins of half a
    time unit (tutorial 4, section 5). There a burst is a dip of $I$ of depth
    $\sqrt{2}\,\bar n$ that lasts about as long as the bursts above, under white noise of
    standard deviation 1.41 per bin: you will not see it by eye in a single record. The job
    is the same, a score for every segment and one budget for four cat sizes, and so is the
    puzzle. The template notebook `10_challenge_template.py` takes over from here.
    """)
    return


if __name__ == "__main__":
    app.run()
