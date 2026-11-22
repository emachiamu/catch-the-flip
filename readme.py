# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.25",
# ]
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
    # Catch the flip

    *When a cat qubit flips, its buffer shouts. Can you hear it?*

    **Alice & Bob challenge at the PushQuantum Hackathon, Munich, 20–22 November 2026**

    Alice & Bob builds quantum computers out of *cat qubits*: superconducting resonators whose
    two logical states are two coherent states of light, $|{+\alpha}\rangle$ and
    $|{-\alpha}\rangle$, held in place by an engineered dissipation that removes photons two
    by two. The reward is a huge *noise bias*: bit flips ($+\alpha \leftrightarrow -\alpha$) are
    exponentially rare, phase flips are not. A repetition code then takes care of the phase
    flips. The one error it cannot see is the rare bit flip.

    But **a bit flip is not silent**. The *buffer* mode that stabilises the cat is dark as long
    as the cat sits in its code space, and it emits a burst of photons when the cat leaves the
    code space to cross from one lobe to the other. Listen to the buffer, and you know *when*
    something happened to the qubit. Do you also know *what* happened? Runs in which the buffer
    shouted can be discarded (post-selection); can a heralded flip also be undone, and what
    could an error-correcting code do with the flag? That is the subtle question of this
    challenge.

    Your job in 24 hours: simulate a monitored cat qubit, understand the burst, build a
    detector that catches flips in noisy measurement records of the buffer output, for cats of
    four sizes mixed in one file (hidden ground truth, scored online), and work out what your
    detector is worth for a logical qubit. Then take the open route of your choice: a better
    detector, a sharper simulation, or a piece of physics nobody asked you for.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Where to start

    Clone this workspace (button **Clone**) and work in your copy. Every member of a team can
    have a copy; choose one account per team for the leaderboard.

    1. Read `CHALLENGE.md`, the challenge statement, and `docs/THEORY.md`, the physics primer.
    2. New to cat qubits or to `dynamiqs`? Run tutorials 1 to 3 of `notebooks/` before the event.
    3. Run `notebooks/04_tutorial_monitoring_a_cat.py`: quantum trajectories, click records,
       heterodyne records and the dark buffer.
    4. Run `notebooks/05_tutorial_catching_flips_in_click_records.py`: a dataset of the
       challenge format, what a flip looks like in a record, what a detector is and how it is
       scored. It uses click records, where a flip can be seen by eye, and nothing in it is
       handed in.
    5. Run `notebooks/10_challenge_template.py`. It walks through the four steps of the
       challenge, builds a first detector for the heterodyne records and writes a submission
       file, `submission_template/tierB.csv`. Save that file with the button of the notebook, then
       sign in on the [live leaderboard](https://aqora.io/Alice_Bob/catch-the-flip-leaderboard),
       type your team name and press **Submit** to get your first score. Then improve it.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The data

    The measurement records are two Aqora datasets. Each is one table with one row per segment
    and a column `split` (`train`, `val` or `test`), and its page describes the columns.

    | dataset | records | role | segments (train, val, test) |
    | --- | --- | --- | --- |
    | [Alice_Bob/catch-the-flip-tier-b](https://aqora.io/datasets/Alice_Bob/catch-the-flip-tier-b) | two quadratures of a heterodyne detector | **the records of the challenge**: your detector works on them, and the leaderboard scores them | 15 000, 7 500, 22 500 |
    | [Alice_Bob/catch-the-flip-tier-a](https://aqora.io/datasets/Alice_Bob/catch-the-flip-tier-a) | click times of a photon counter | tutorial 5 and the physics questions; not scored, nothing to submit | 30 000, 15 000, 30 000 |

    In the notebooks, `catchtheflip.records.load_dataset("data/tierB_train.npz")` returns the
    `train` split of tier B as NumPy arrays, and likewise for the five other splits. It reads the
    split from the Aqora dataset, or from a file of that name if you put one in `data/`.
    `data/README.md` describes the arrays.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What is in this workspace

    | | |
    | --- | --- |
    | `CHALLENGE.md` | **the challenge statement**: device sheet, the four steps, open routes, deliverables, scoring, rules |
    | `docs/THEORY.md` | the physics in eight sections: cat qubits, the buffer, why flips shine, unravelings, labels, rates, what a herald could buy, further reading |
    | `notebooks/01…03_tutorial_*.py` | tutorials: `dynamiqs`, open quantum systems, cat qubits (read before the event) |
    | `notebooks/04_tutorial_monitoring_a_cat.py` | tutorial: quantum trajectories, click records, heterodyne records, the dark buffer |
    | `notebooks/05_tutorial_catching_flips_in_click_records.py` | tutorial: a dataset of the challenge format, a flip in a record, a detector and its score, on click records |
    | `notebooks/10_challenge_template.py` | a template that walks through the four steps and writes a first submission file |
    | `catchtheflip/` | helper package: models, rates from the Liouvillian spectrum, stochastic simulations, records, scoring, repetition code |
    | `data/` | `data/README.md`: what the datasets hold (the records themselves are the two Aqora datasets above) |
    | `scripts/` | `generate_dataset.py` (make your own labelled data), `score_submission.py` |
    | `submission_template/` | what to hand in |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Working with the notebooks

    The notebooks are [marimo](https://marimo.io) notebooks: plain Python files, reactive (a cell
    reruns when a variable it uses changes), with one definition per global variable. If you come
    from Jupyter, read the note at the top of tutorial 1 or the
    [marimo guide for Jupyter users](https://docs.marimo.io/guides/coming_from/jupyter/).

    Each notebook declares the packages it needs in its header. Tutorials 4 and 5 and the
    template also use the helper package `catchtheflip` of this workspace.

    The simulations use [dynamiqs](https://www.dynamiqs.org) (JAX), and nothing needs a GPU. Most
    computations run in seconds to minutes. The statistics of step 2 can take 10 to 20 minutes per
    cat size once flips get rare: plan them and start them early. If something takes longer, you
    are probably simulating more than you need (ask a mentor).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Rules, leaderboard and questions

    The [track page](https://aqora.io/challenges/pushquantum-hackathon-2026/tracks/alice-bob-pushquantum-2026)
    has the schedule, the judging criteria and the
    [rules](https://aqora.io/challenges/pushquantum-hackathon-2026/tracks/alice-bob-pushquantum-2026/rules).
    Ask technical questions in the
    [track discussion](https://aqora.io/challenges/pushquantum-hackathon-2026/tracks/alice-bob-pushquantum-2026/discussions),
    or ask the Alice & Bob mentors, who are on site during the whole hacking phase.

    The challenge is inspired by a recent theory paper by researchers at EPFL and Alice & Bob
    (the reference is in `docs/THEORY.md`, section 8). You do not need it, and you will get
    more out of it after the hackathon, once you have found the answers yourself.

    *Tutorials 1–3 are adapted from the Alice & Bob challenges at MIT iQuHACK 2025 and
    DuQuantum 2026. Everything here is released under the MIT license.*
    """)
    return


if __name__ == "__main__":
    app.run()
