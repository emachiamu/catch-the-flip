# Catch the flip

**Alice & Bob challenge at the PushQuantum Hackathon, Munich, 20–22 November 2026**

<p align="center"><em>When a cat qubit flips, its buffer shouts. Can you hear it?</em></p>

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
detector is worth for a logical qubit:
what post-selection buys, whether a heralded flip can be undone with a logical $X$, and what
an error-correcting code could do with the herald. Then take the open route of your choice: a better
detector, a sharper simulation, or a piece of physics nobody asked you for.

The challenge is inspired by a recent theory paper by researchers at EPFL and Alice & Bob
(the reference is in `docs/THEORY.md`, section 8). You do not need it, and you will get
more out of it after the hackathon, once you have found the answers yourself.

## What is in the workspace

| | |
| --- | --- |
| [`CHALLENGE.md`](CHALLENGE.md) | **the challenge statement**: device sheet, the four steps, open routes, deliverables, scoring, rules |
| [`docs/THEORY.md`](docs/THEORY.md) | the physics in eight sections: cat qubits, the buffer, why flips shine, unravelings, labels, rates, what a herald could buy, further reading |
| `notebooks/01…03_tutorial_*.py` | tutorials ([marimo](https://marimo.io) notebooks): `dynamiqs`, open quantum systems, cat qubits (read before the event) |
| `notebooks/04_tutorial_monitoring_a_cat.py` | tutorial: quantum trajectories, click records, heterodyne records, the dark buffer |
| `notebooks/05_tutorial_catching_flips_in_click_records.py` | tutorial: a dataset of the challenge format, what a flip looks like, what a detector is and how it is scored, on click records (nothing to hand in) |
| `notebooks/10_challenge_template.py` | a template that walks through the four steps and writes a first submission file for the heterodyne records |
| `catchtheflip/` | helper package: models, rates from the Liouvillian spectrum, stochastic simulations, records, scoring, repetition code |
| `data/` | [`data/README.md`](data/README.md): what the datasets hold. The records themselves are two Aqora datasets (see [The data](#the-data)) |
| `scripts/` | `generate_dataset.py` (make your own labelled data), `score_submission.py` |
| `submission_template/` | what to hand in |

## Where to run it

**On Aqora.** Open the workspace [Alice_Bob/catch-the-flip](https://aqora.io/Alice_Bob/catch-the-flip) of the
[track](https://aqora.io/challenges/pushquantum-hackathon-2026/tracks/alice-bob-pushquantum-2026) and clone it (button **Clone**): you get your own copy, where the notebooks run
with nothing to install. Every member of a team can have a copy; choose one account per team
for the leaderboard.

**On your laptop.** Python 3.11 or newer, a laptop CPU is enough (nothing in this challenge
needs a GPU). In a copy of this folder (the mentors have an archive of it):

```bash
python -m venv .venv && source .venv/bin/activate      # or conda / uv
pip install -e ".[dev,aqora]"
aqora login                                              # once: the data is read from Aqora
marimo edit notebooks/                                   # open the notebooks
```

The notebooks are [marimo](https://marimo.io) notebooks: plain Python files, reactive (a cell
reruns when a variable it uses changes), with one definition per global variable. If you come
from Jupyter, read the note at the top of tutorial 1 or the
[marimo guide for Jupyter users](https://docs.marimo.io/guides/coming_from/jupyter/). Each
notebook also declares its dependencies in its header, so `uvx marimo edit --sandbox
notebooks/04_tutorial_monitoring_a_cat.py` runs it in an isolated environment without the
`pip install` above.

The simulations use [dynamiqs](https://www.dynamiqs.org) (JAX). Most computations run in
seconds to minutes on a laptop (one to two click-record segments of 200 time units per second,
one heterodyne segment in about two seconds). The
statistics of step 2 can take 10 to 20 minutes per cat size once flips get rare: plan them
and start them early. If something takes longer, you are probably simulating more than you
need (ask a mentor).

## The data

The measurement records are two datasets on Aqora:

* [tier B, heterodyne detection](https://aqora.io/datasets/Alice_Bob/catch-the-flip-tier-b): **the records of the challenge**. Your detector works on them, and the leaderboard scores them.
* [tier A, photon counting](https://aqora.io/datasets/Alice_Bob/catch-the-flip-tier-a): click records of the same cat, where a flip can be seen by eye. Tutorial 5 uses them, and they help with the physics questions. Nothing about them is scored or submitted.

The notebooks read them with `catchtheflip.records.load_dataset`, and
[`data/README.md`](data/README.md) describes what they hold.

## Timeline

* **Friday**: kick-off, the challenge is unveiled. Read `CHALLENGE.md` and `docs/THEORY.md`,
  run the tutorials.
* **Saturday, 24 h of hacking**: steps 1 to 4. Submit detector outputs to the
  [live leaderboard](https://aqora.io/Alice_Bob/catch-the-flip-leaderboard)
  as you go (see `CHALLENGE.md`).
* **Sunday morning**: at 09:00 we announce the cat size of the sealed prediction, due at
  09:30; then the deadline for your last file on the leaderboard and for your folder,
  15-minute presentations and judging.

## Rules in short

* Teams of 2 to 5. One submission account per team.
* **AI assistants are welcome** (ChatGPT, Claude, Copilot, …) for code, derivations and
  explanations. Use them to go faster, then check what they give you: the judges will ask you
  to explain every number you show, and one slide of your presentation must list two things
  an AI tool got wrong and how you caught them.
* Your notebooks must run from top to bottom, hand them in with their outputs (a marimo
  notebook stores none: export it with `marimo export html notebook.py -o notebook.html`,
  or with *Download as HTML* in the notebook menu of the editor),
  and every figure must be reproducible
  from your code.
* The hidden test labels are hidden for everybody: do not try to reconstruct them by
  regenerating the data (the generator seed of the test set is private and the test device
  differs from the nominal one).

## Judging

| criterion | weight |
| --- | --- |
| physics insight: correctness, depth, the "why" behind every choice, the sealed prediction | 40 % |
| scored result on the hidden test split of the heterodyne records: flip suppression after post-selection, counted in points, not in ranks (`CHALLENGE.md`, step 3) | 30 % |
| originality: ideas beyond the template, the open routes of `CHALLENGE.md` or your own, ablations | 20 % |
| clarity: notebooks, write-up and presentation | 10 % |

Depth beats breadth: a team that takes one open route to a clear answer ranks above a team
that touches everything superficially. The leaderboard score carries a statistical
uncertainty of about ±0.015: a difference of less than 0.03 between two teams is not a
difference.

## Mentors and contact

David Schlegel (Alice & Bob, device theory and simulation), on site during the whole
hacking phase. Questions before the event: the [track discussion](https://aqora.io/challenges/pushquantum-hackathon-2026/tracks/alice-bob-pushquantum-2026/discussions) on Aqora.

*Tutorials 1–3 are adapted from the Alice & Bob challenges at MIT iQuHACK 2025 and
DuQuantum 2026. Everything here is released under the MIT license.*
