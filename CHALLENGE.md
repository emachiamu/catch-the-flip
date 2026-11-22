# Catch the flip: the challenge

*Alice & Bob, PushQuantum Hackathon, Munich, November 2026.* Read
[`docs/THEORY.md`](docs/THEORY.md) first; it defines every symbol used below. Times and rates
are in units of the two-photon dissipation rate $\kappa_2$ ($1/\kappa_2 \approx 0.16\ \mu$s for
$\kappa_2/2\pi = 1$ MHz).

## The story

A dissipative cat qubit keeps its two logical states, $|{+\alpha}\rangle$ and
$|{-\alpha}\rangle$, alive with an engineered two-photon dissipation that flows through a
*buffer* resonator. Bit flips are exponentially rare, and when one happens the buffer
radiates a short burst of photons: the memory has to leave the code space to cross from one
lobe to the other, and the buffer radiates exactly when the memory is out of the code space.
Everything else that kicks the memory out of the code space (a thermal photon, a dephasing
event) also makes the buffer radiate, a little.

You get records of the buffer output of a cat qubit at four cat sizes, simulated with the
same tools Alice & Bob uses, with and without labels. Build the best flip detector you can,
understand why it works, and find out what a herald is worth. A burst tells you *that* something happened to
the memory and *when*. Does it also tell you *what* happened to the logical qubit? Heralded
runs can be discarded; can a heralded flip also be undone with a logical $X$, and what else
could a decoder do with the herald? You will answer from the data.

The challenge is inspired by a recent theory paper by researchers at EPFL and Alice & Bob
(`docs/THEORY.md`, section 8). You do not need it to solve the challenge; read it afterwards
and compare it with what you found.

## What you will learn

* how a dissipative cat qubit is protected, and why its bit flips are rare but not silent;
* quantum trajectories: what a measurement record tells you about a quantum state, and how to
  check a stochastic simulation against the master equation;
* signal detection under noise and model mismatch: features, ROC curves, operating points,
  and a device you can only partly simulate;
* what a flag on an error is worth for error correction, and how far a measurement can go
  in repairing a qubit.

## Device sheet

The **nominal device** is the single-mode model of the primer with the parameters below, at
four cat sizes. You can simulate it (`catchtheflip.models.nominal_model(nbar=3.0)`), compute
its rates, and generate as much labelled data of it as you want
(`scripts/generate_dataset.py`).

| parameter | value | note |
| --- | --- | --- |
| cat size $\bar n = \alpha^2$ | 2, 2.5, 3 and 3.5 | every dataset mixes the four; $\alpha = $ 1.41 to 1.87 |
| two-photon rate $\kappa_2$ | 1 | the unit |
| single-photon loss $\kappa_1$ | 0.02 | phase flips, no kick; $\Gamma_X \simeq 2\kappa_1\bar n$ without thermal photons |
| thermal occupation $n_{th}$ | 0.1 | thermal jumps at rate $\kappa_1 n_{th}(\bar n + 1)$ |
| dephasing $\kappa_\varphi$ | 0.02 | dephasing jumps at rate $\kappa_\varphi(\bar n^2 + \bar n)$ |
| Fock cutoff $N$ | 24 up to $\bar n = 2.5$, 28 above | the default of `nominal_model`; check convergence yourself |
| segment duration $T_{\rm seg}$ | 200 | prepared in $+\alpha$ at $t=0$, Z readout at $T_{\rm seg}$ |
| heterodyne detector | efficiency $\eta_B = $ 1 (an ideal detector), 400 bins per segment (0.5 time units each) | the scored records: $I$ and $Q$, dataset *tier B* |
| photon counter | efficiency $\eta_A = $ 0.8, dark counts 0.02 per unit time | tutorial 5 and the physics questions: click times, dataset *tier A* |

**Two kinds of records, one of them scored.** The challenge is scored on *heterodyne*
records (the Aqora dataset *tier B*): this is how the output of a superconducting resonator
is usually measured, and there the burst of a flip sits under the vacuum noise. The *click
records* of a photon counter (the dataset *tier A*) show the same physics in plain sight.
Tutorial 5 uses them to go through the job of a detector once, and they remain a microscope
for the physics questions of steps 2 and 4. There is no submission and no score for the
click records.

The rates depend on the cat size:

| cat size $\bar n$ | 2 | 2.5 | 3 | 3.5 |
| --- | --- | --- | --- | --- |
| bit-flip rate $\Gamma_Z$ (Liouvillian spectrum) | 1.70 × 10⁻³ | 7.82 × 10⁻⁴ | 3.50 × 10⁻⁴ | 1.53 × 10⁻⁴ |
| $T_Z = 1/\Gamma_Z$ | 589 | 1280 | 2860 | 6550 |
| phase-flip rate $\Gamma_X$ | 0.099 | 0.123 | 0.147 | 0.171 |
| flip probability per segment (master equation) | 14.6 % | 7.30 % | 3.40 % | 1.51 % |
| flip labels in the training split of the heterodyne records (tier B) | 15.8 ± 1.2 % | 6.7 ± 0.6 % | 3.0 ± 0.3 % | 1.59 ± 0.14 % |
| flip labels in the training split of the click records (tier A) | 14.4 ± 0.8 % | 7.2 ± 0.4 % | 3.7 ± 0.2 % | 1.45 ± 0.09 % |

The phase-flip rate follows $\Gamma_X \simeq 2\kappa_1[(1 + 2n_{th})\bar n + n_{th}]$ (thermal
photons flip the parity too). The flip probability per segment is
$\tfrac12(1 - e^{-\Gamma_Z T_{\rm seg}})$ plus a readout error of the order of that of the $+\alpha$ lobe
($\Phi(-2\alpha)$ for an ideal coherent state, section 5 of the primer: 0.23 % at
$\bar n = 2$, 0.01 % at $\bar n = 3.5$), which the master equation includes. The training
splits scatter around the master-equation values with binomial errors.

The device is deliberately noisy (strong dephasing, thermal photons) so that flips are
frequent enough to be simulated and seen within the hackathon. Real devices are quieter and
use bigger cats; the physics is the same.

The **hidden test device** (validation and test splits) has the same noise rates and the same
four cat sizes, but its buffer is a real resonator of finite bandwidth $\kappa_b$ (two-mode
model, `catchtheflip.models.two_mode`) and its memory has a small Kerr non-linearity $K$ (a term $-\tfrac K2 a^{\dagger 2} a^2$ in the
Hamiltonian: the frequency of the memory depends on its photon number).
The values of $\kappa_b$ and $K$ are private, and they are the same at every cat size. The
hidden device flips one and a half to three times more often than the nominal one, by a
factor that depends on the cat size: the labelled validation splits tell you by how much.

## Steps

Steps 1 and 2 are guided and every team should complete them; step 3 is scored on the
leaderboard; step 4 is the open capstone and weighs most in the physics-insight part of the
grade. The template notebook `notebooks/10_challenge_template.py` walks through all four,
and tutorial 5 (`notebooks/05_tutorial_catching_flips_in_click_records.py`) shows the job of
step 3 on click records first.
The open routes at the end are where originality is graded. Not every team will answer
every question: steps 1 to 3 and the first two points of step 4 (what a burst tells you, whether a
heralded flip can be undone) are the core, the rest is depth. Budget your simulations: a laptop simulates one to two click-record segments of the nominal
device per second (a heterodyne segment takes about two seconds),
so a few hundred segments per point (minutes) for step 2, more at large $\bar n$ where flips
are rare; start long runs early and keep them in the background. The training splits already
hold thousands of labelled segments at every cat size.

### Step 1: watch a cat flip (guided)

1. Build the nominal device, verify that $|\pm\alpha\rangle$ are dark for the buffer channel
   and that a kicked state ($a^\dagger|\alpha\rangle$, $a^\dagger a|\alpha\rangle$) is not.
2. Compute $\Gamma_Z$ and $\Gamma_X$ from the Liouvillian spectrum
   (`catchtheflip.rates.spectrum`) and compare $\Gamma_X$ with the estimate of the primer.
   Which channels flip the parity, and which do not? Check the convergence with the Fock
   cutoff $N$.
3. Run one long jump trajectory (`simulate.long_trajectory`), plot its
   $\langle Z_L\rangle(t)$ (the key `z`: the expectation of the Z readout, conditioned on
   everything the simulation has seen; its average over many runs decays as
   $e^{-\Gamma_Z t}$) and the click times of all channels. Find a flip. Zoom on it.
4. Simulate a few hundred segments (`simulate.counting_segments`, a few minutes) and
   compare the mean of `pneg`, the readout probability of $-\alpha$ of each segment, with the
   master equation (`simulate.master_equation_pneg`) and with the spectrum. Sample labels
   from `pneg` (`records.sample_labels`) and compare their mean too. This is your sanity check
   of the stochastic solver: with 300 segments at $\bar n = 2.5$ the mean of `pneg` is known
   to about ±10 %, enough to catch a gross error, not a bias of a few percent from the
   time step (that takes ~10⁴ segments).

*Deliverable*: the figures, the rates with their convergence check, and one paragraph on what
a flip looks like in a trajectory. What do $\langle Z_L\rangle$ and the buffer do while it
happens, and in which state is the memory afterwards?

### Step 2: the burst (guided, then open)

1. From the segments of step 1, compare the number of buffer clicks in flip segments and in
   flip-free segments. Where in time are the extra clicks? (Hint: align every record on its
   densest cluster of clicks and average; do the same with flip-free records, and ask why the
   comparison is needed. The click records of the nominal device, the training split of
   tier A, hold 230 to 300 flips at every cat size, which gives good statistics.)
   Careful: not every flip label comes with a burst. Why not, and what does that do to your
   estimate of the burst size? (Your own simulations give `pneg`.) Say how you define the
   burst size.
2. Repeat at the four cat sizes of the datasets, and beyond with your own simulations
   ($\bar n = 1.5$, $4$, as far as your laptop allows): how do the burst size, the background
   (clicks from kicks that do not flip) and the flip probability scale with $\bar n$? Compare the burst with the estimate $\bar n^2 \kappa_2 \tau$ of the
   primer and extract the burst duration $\tau$.
3. Two-mode model (`models.two_mode`): run a short trajectory with the buffer as a real
   mode and look at $\langle b^\dagger b\rangle(t)$. Does the elimination hold? How do the
   burst and the flip rate change as $\kappa_b$ is lowered at fixed $\kappa_2 = 4g_2^2/\kappa_b$?
   (Raise the buffer cutoff `Nb` as $\kappa_b$ drops: the buffer holds more photons during a
   burst.)

*Deliverable*: a plot of burst size and background versus $\bar n$, with the scaling law
you infer and its physical explanation.

### Step 3: the detector (scored)

Design a detector that takes one heterodyne record ($I$ and $Q$, 400 bins each) and the cat
size of its segment, and returns a *score* (higher = more suspicious) and a yes/no
*decision* (1 = discard the segment). The records are the Aqora dataset
[tier B](https://aqora.io/datasets/Alice_Bob/catch-the-flip-tier-b). Every split mixes
segments of the four cat sizes, shuffled, with the cat size of each segment in the array
`nbar`. Train on `tierB_train.npz` (nominal device, labelled), check the transfer to the
real device on `tierB_val.npz` (hidden device, labelled), submit on `tierB_test.npz` (hidden
device, unlabelled) to the leaderboard. `catchtheflip.records.load_dataset` returns a split
under these file names (see `data/README.md`).

Tutorial 5 does the same job on the click records of a photon counter (the dataset
[tier A](https://aqora.io/datasets/Alice_Bob/catch-the-flip-tier-a)), where a burst can be
seen by eye. Run it first. The click records are not scored and nothing about them is
submitted; use them as you like to understand the physics.

The leaderboard figure of merit is the **flip suppression after post-selection at 70 %
yield**. The scorer discards the 30 % most suspicious segments of your submission (according
to your scores, all cat sizes together), computes the residual flip fraction

$$\rho_{70} = \frac{p_{\rm flip}(\text{kept segments})}{p_{\rm flip}(\text{all segments})},$$

and reports $1 - \rho_{70}$. Higher is better: $1 - \rho_{70} = 0$ means your scores carry
no information, $1 - \rho_{70} = 1$ means every flip was discarded, and it is negative if
your scores point the wrong way. The leaderboard uses your scores only and shows only this
number for your file, with two decimals, and the points it is worth. Segments with equal scores are ranked by their position in the
file, so a score with few distinct values leaves the cut at 30 % to chance: break ties with
a second, finer feature.

The test split is finite, so $1 - \rho_{70}$ carries a statistical uncertainty of about
±0.015, and about ±0.03 on the validation split with its 586 flips. A difference of less
than 0.03 between two detectors, or between two teams, is not a difference: compare your
designs on your own simulated data as well, not on the leaderboard alone. For the same
reason the leaderboard counts in the judging through points, not through ranks:

$$\text{points} = 10 \times \min\!\Big(1,\ \max\!\Big(0,\ \frac{(1 - \rho_{70}) - 0.30}{0.55 - 0.30}\Big)\Big).$$

A score of 0.30 is about what discarding the smallest cats gets without looking at any
record, and it is worth no points. A score of 0.55 or more is worth all 10
(`catchtheflip.scoring.leaderboard_points`). Above 0.55 the leaderboard cannot tell two
detectors apart, and your time is better spent on the physics of steps 2 and 4.

To get a score on the test split, save your file from the template notebook (button
**Save for the leaderboard**, or `catchtheflip.leaderboard.save` from a laptop), then sign in
on the [live leaderboard](https://aqora.io/Alice_Bob/catch-the-flip-leaderboard), type your
team name and press **Submit**. The leaderboard shows the score of the last file you
submitted. It has one line per account: use one account per team.

You may submit as often as you like. Your **final submission is one file**: the last one
you submitted before the deadline, not the best of your files. To go back to an earlier
detector, submit its file again.

The 30 % are a budget shared by the four cat sizes, and where you spend it is part of the
problem. A small cat flips five to ten times more often than a big one and its bursts are
weaker, so a score that ranks the records of one cat size well can still rank a small cat
against a big one badly. The template starts from the crudest detector, the mean of $I$ over
the whole segment. It does worse than discarding the smallest cats without looking at any
record, and so does counting all the clicks of a click record (tutorial 5). Work out why,
then beat both.

Your decisions define your own post-selection operating point. On the labelled validation
split, `catchtheflip.scoring.evaluate` and `scoring.by_cat_size` (or
`scripts/score_submission.py`, on a file of scores written for that split) report its yield
and residual flip fraction, the correction score $S$ of step 4 as if the same segments were
corrected with a logical $X$ instead of discarded, the AUC of your scores (the area under
the ROC curve: the probability that a random flip segment scores higher than a random
flip-free one), and the fraction of each cat size that your scores discard. On
the hidden test split, we compute these numbers for your final submission after the
deadline, for the judges.

Things worth thinking about:

* a burst lasts about one time unit and a segment lasts 200: where in the record is the
  information, and what does the rest of the record contribute?
* the dip of a burst is deeper in a big cat, the noise is the same at every cat size, and
  the flip rate falls exponentially with the cat size: what does a given dip mean in a small
  cat, and in a big one?
* scores of different cat sizes meet on one scale if they are probabilities. The
  probability of a flip given the record and the cat size combines a prior (how often a cat
  of this size flips, step 1) with the evidence of the record (the burst and the background,
  step 2);
* the readout that produced the labels is itself random;
* the real device is not the nominal one: it flips more often, by a factor that depends on
  the cat size, and its buffer filters the bursts. The validation split is smaller than the
  training split: decide what to learn from it, and what to take from the nominal device
  and from physics;
* for the decision, think in costs: if a missed flip costs $\zeta$ times as much as a false
  alarm, the Bayes-optimal rule discards a segment when the posterior probability of a flip
  given its record exceeds $1/(1 + \zeta)$. Which $\zeta$ does your operating point
  correspond to? (This needs calibrated probabilities, not just scores.)

*Deliverable*: your submission file, the trade-off curve $\rho(Y)$ (residual flips against
yield) on validation (we add the one on test), the operating point you chose and why, the
fraction of each cat size that you discard, and a comparison of at least two
detector designs.

### Step 4: what the herald is worth (capstone)

Post-selection throws qubits away; a quantum computer cannot do that. A herald is useful
for computing only if error correction can use it, and how it can be used depends on what a
heralded flip does to the qubit: is it a logical $X$ at a known time, or something else?
`docs/THEORY.md`, section 7, defines the vocabulary (Pauli-frame correction, erasures). Find
out from the data, then work out the consequences.

A strong answer shows:

* **what a burst tells you**: a photon counter is the best microscope for this question.
  With the labelled click records of the nominal device (the training split of tier A, the
  data of tutorial 5), at one cat size, plot
  $P(\text{label} = 1 \mid n)$ against the largest number $n$ of clicks that a segment shows
  within one time unit, and the distributions $P(n \mid \text{flip})$ and
  $P(n \mid \text{no flip})$. What do you see at large $n$, and what does it tell you about
  the state of the memory after a large burst? (Few segments have a large $n$: pool the tail.
  Your own simulations give `pneg`, the readout probability of each segment: look at it for
  the segments with a large burst.) Then ask the same of your heterodyne detector: how often
  do the segments it is most sure about carry a flip label?
* **whether a heralded flip can be undone**: the obvious use of a herald is a Pauli-frame
  update, a logical $X$ applied to every flagged segment. With a detector that catches a
  fraction TPR of the flips and flags a fraction FPR of the flip-free segments, the residual
  flip probability per segment is
  $p_{\rm eff} = p_{\rm flip}(1 - \mathrm{TPR}) + (1 - p_{\rm flip})\,\mathrm{FPR}$
  and the correction score is $S = p_{\rm eff}/p_{\rm flip}$ (`catchtheflip.scoring.score`).
  Plot $S$ against the decision threshold for your best detector and, on the training
  device, for an *oracle* that flags segments by their `pneg`. Take `pneg` from your own
  photon-counting simulations (`simulate.counting_segments`, which treats every channel as a
  photon counter): this oracle has seen every jump of every channel. Compare $S$ with
  $\rho_{70}$ for the same detectors and explain what you find. What does a heralded flip do
  to the logical qubit, and is that a logical $X$?
* **completed flips against aborted excursions**: run your detector on your own
  photon-counting simulations, whose `pneg` says where each memory ended. Among the segments
  it flags, which ones crossed to $-\alpha$, which ones came back, and which ones ended
  somewhere in between? Does the record tell them apart (burst size, duration)?
* **what it would take**: using your burst and background measurements of step 2, in which
  direction would one have to push the device (cat size, detector efficiency, dark counts,
  kick rates, the two-mode buffer bandwidth) to make heralds more reliable? Is a
  heralded flip *correctable*, and if not, what would it take? Quantify the logical bit-flip probability of
  a distance-$d$ phase-flip repetition code without herald, with post-selection and with
  Pauli-frame correction (`catchtheflip.repcode`; one QEC cycle is one segment, at the cat
  size of your choice). Can this
  code use the herald at all, given that its distance against bit flips is 1? What kind of
  code could, and how many heralded bit flips could it correct compared with unheralded
  ones?
* one thing we did not ask for (the open routes below are a starting point).

*Deliverable*: a short write-up (two pages) with the figures, and the results table of
`submission_template/README.md`.

### Sealed prediction (Sunday 09:00)

On Sunday morning we announce a cat size $\bar n^\star$ that is not in the datasets. Before
09:30 every team hands to the mentors, in writing, its predicted flip probability per segment ($T_{\rm seg} = 200$)
of the hidden device at $\bar n^\star$ (the same device with a different cat size, all its
other parameters unchanged), with an error bar, and one sentence on the method. The flip probability per segment is the fraction
of segments labelled 1 in a large dataset, readout error included, as in the device sheet.
We reveal the true value during the presentations. It counts in the physics-insight grade:
we look at the distance to the true value, at whether your error bar is honest, and at the
method.
Thirty minutes is too short to start from scratch: build your prediction as a function of
$\bar n$ during the hackathon.

## Open routes

The four steps are the backbone of the challenge. Beyond them the judges reward depth: one
open question taken seriously, with a clear answer (a negative result counts), weighs more
than many touched lightly. It feeds the originality grade and, when it explains physics, the
physics-insight grade. Here are routes we find promising; pick one or two, or bring your own.

**Numerical side**

* **The optimal detector is a quantum filter.** The best score a record can give is the
  posterior $P(\text{label} = 1 \mid \text{record})$: the readout probability of the memory
  state conditioned on the *observed* record alone, with everything unobserved averaged
  over. It needs one model per cat size and no training. The click records are the place
  to try the idea first: there it is a master equation integrated along each record. Between
  clicks, the master equation without the detected part of the buffer jumps,
  $\eta L\rho L^\dagger$; at a click, the update
  $\rho \to \eta L\rho L^\dagger + \gamma_d\,\rho$ (with $\gamma_d$ the dark-count rate),
  renormalised. What is the corresponding update for a heterodyne record, given that the
  records are averaged over bins of half a time unit? How close does your filter get to the
  oracle of step 4, and can you make it fast enough for 22 500 test records (a
  $24^2 \times 24^2$ propagator, batched over records)?
* **Spend the budget where it pays.** The 30 % are shared between the cat sizes. Which
  fraction of each cat size does your best detector discard, and what would the best
  possible detector do? How does the answer move with the budget (10 %, 50 %), and what does
  it say about the cat size you would choose for a device that is allowed to post-select?
* **Learning from simulations.** Train a classifier on the raw records (a 1D convolutional
  or recurrent network, gradient boosting on your own features) with as much simulated data
  as you need, including devices that differ from the nominal one. What does it learn that
  your hand-made features miss? Beware of overfitting the validation flips.
* **Rare events.** Flips get exponentially rarer with $\bar n$: at $\bar n = 5$ a segment of
  the nominal device flips with a probability of about 10⁻³, and a hundred flips take a day
  of laptop time. Can you do better, for example by conditioning on the
  first kick, by importance sampling, or with the smart sampling of the event integrator of
  dynamiqs (`dq.method.Event(smart_sampling=True)`)?
* **Trusting a solver.** Compare the fixed-step and the adaptive jump integrators
  (`method="euler"` with several `dt`, `method="event"` with several `dtmax`), the Fock
  cutoff, and the stochastic master equation `dq.jsmesolve` with efficiency 0 for the
  unmonitored channels. Which biases do you find against the master equation, at which
  cost?

**Physics side**

* **Identify the hidden device.** The labelled validation records carry fingerprints of
  the hidden device: its flip rate at four cat sizes, its background, the shape of its
  bursts, the mean of its records. How much can you infer about $\kappa_b$ and $K$, and which of the two matters? The
  answer feeds the sealed prediction directly.
* **Who causes the flips?** Your simulations record the jumps of every channel. Which kicks
  (thermal or dephasing) start the flips, with which probability per kick, and how does it
  change with $\bar n$? Which noise sets the exponent of $\Gamma_Z \propto e^{-c\,\bar n}$?
* **Anatomy of a flip.** Follow the conditional state through a burst
  (`return_states=True`, `save_states=True`): Wigner function, photon-number parity,
  distance to the code space. How long does it take to settle, and into what?
* **The burst as a waveform.** Align heterodyne records on bursts and average them: does
  the mean waveform follow $\langle a^2\rangle$ of the conditional state? How does a finite
  buffer bandwidth filter it? A homodyne detector set to the quadrature of the burst would
  not split the signal in two: by how much would it beat heterodyne?
* **What does the oracle see?** `simulate.heterodyne_segments` treats the unmonitored
  channels differently from `simulate.counting_segments` (`docs/THEORY.md`, section 4).
  Records and labels do not depend on that choice, but `pneg` does. Compute the oracle's
  correction score $S$ from the `pneg` of heterodyne simulations, explain the difference with
  step 4, and say what it implies for correcting heralded flips.
* **Beyond the repetition code.** Simulate a small code with a bit-flip distance larger
  than 1, for example an outer repetition code against bit flips built on top of
  phase-flip-protected cats, and compare its logical error rate with and without your
  heralds, decoded as you see fit.
* **Design the device.** Which cat size, buffer bandwidth and detector efficiency would make
  a herald worth having? Map the trade-off between flip rate, burst contrast and yield.

## Rules, AI, submissions

* AI assistants are allowed and encouraged for everything. You are responsible for what
  they produce: notebooks that run from top to bottom, handed in with their outputs, every number explained on request, one slide on
  "two things AI got wrong and how we caught them".
* Do not attempt to reconstruct the hidden labels (private seed, private device). Estimating
  the parameters of the hidden device from the public data is allowed, and it is one of the
  open routes. So is training on the labelled validation split.
* Compute: a laptop. If a computation takes more than 20 minutes, reduce it or ask a mentor.
* Hand in the folder described in `submission_template/README.md` on the
  [submission page](https://aqora.io/challenges/pushquantum-hackathon-2026/tracks/alice-bob-pushquantum-2026/submission)
  of the track before the deadline announced on site, and give a 15-minute presentation
  (10 + 5 questions). The leaderboard closes at the same deadline.

## Conventions, once and for all

* $\langle Z_L\rangle(t) = e^{-\Gamma_Z t}$ for the ensemble average (a single trajectory's
  conditional $\langle Z_L\rangle$ jumps around); the flip probability per segment is
  $\tfrac12(1 - e^{-\Gamma_Z T_{\rm seg}})$; $\Gamma_Z$ is the **bit-flip** rate (the rare
  one) and $T_Z = 1/\Gamma_Z$ the bit-flip time; $\Gamma_X$ is the **phase-flip** rate (the
  frequent one, $\simeq 2\kappa_1[(1 + 2n_{th})\bar n + n_{th}]$). A flip is named after the
  axis along which the state flips: a bit flip exchanges the eigenstates $|{\pm\alpha}\rangle$
  of $Z_L$, a phase flip the two cat states, the eigenstates of $X_L$. Some papers name the
  rates after the operator that causes the flip and write $\Gamma_X$ for the bit-flip rate.
* The buffer channel jump operator is $\sqrt{\kappa_2}(a^2 - \alpha^2)$ with $\alpha$ real
  and positive; in the two-mode model it is $i\sqrt{\kappa_b}\, b$, whose phase makes it
  $\simeq \sqrt{\kappa_2}(a^2 - \alpha^2)$ after elimination of the buffer, so that the burst
  has the same sign in both models.
* The heterodyne records (tier B) follow the dynamiqs convention
  $I = \langle L + L^\dagger\rangle + \xi$, $L = \sqrt{\eta/2}\,(a^2 - \alpha^2)$, white noise
  $\xi$ of unit variance per unit time, averaged over each bin; the burst is **negative in
  $I$** ($\langle a^2\rangle \to 0$ gives $I \to -\sqrt{2\eta}\,\alpha^2$).
* A label of 1 means the Z readout gave $-\alpha$ at the end of the segment. `pneg`, the
  readout probability of $-\alpha$ of a simulated segment, is privileged information: no
  record contains it, and it depends on how the simulation treats the unmonitored channels.
* Leaderboard: $1 - \rho_{70}$, flip suppression, where $\rho_{70}$ is the residual flip
  fraction after discarding the 30 % most suspicious segments of the heterodyne test split,
  which mixes the four cat sizes (higher is better; ±0.015). Capstone:
  $S$, residual flips after *correcting* flagged segments with a logical $X$ (1 = no gain).
* Erasure: an error at a known location (qubit and time) whose effect on the qubit is
  unknown. Herald: a flag raised by the record (here, a buffer burst) that marks when
  something happened to a qubit.
* Cycle: one round of error correction; in the challenge, one segment.
* Segment: one memory experiment of duration $T_{\rm seg} = 200$ at one of the cat sizes
  $\bar n = 2, 2.5, 3, 3.5$. The array `nbar` of every dataset gives the cat size of each
  segment.
