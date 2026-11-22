# Datasets

The measurement records are two datasets on Aqora:

* [Catch the flip, tier B: heterodyne detection](https://aqora.io/datasets/Alice_Bob/catch-the-flip-tier-b):
  **the records of the challenge**. Your detector works on them, and the leaderboard scores
  its test split.
* [Catch the flip, tier A: photon counting](https://aqora.io/datasets/Alice_Bob/catch-the-flip-tier-a):
  click records of the same cat, where a flip can be seen by eye. They are the data of
  tutorial 5 and a tool for the physics questions of steps 2 and 4. They are not scored, and
  nothing about them is submitted.

Each is one table with one row per segment and a column `split` (`train`, `val` or `test`).

`catchtheflip.records.load_dataset(path)` returns one split as a dictionary of NumPy arrays,
under the six file names of the table below: `load_dataset("data/tierB_train.npz")` reads
the `train` split of tier B from Aqora, or the file `data/tierB_train.npz` if there is one
(an `.npz` archive, also readable with `numpy.load`). This page describes these arrays; the
dataset pages describe the columns of the tables.

Each split comes with a dictionary `meta`: the segment duration `T_seg`, the
detection efficiency `eta`, the tier, the cat sizes and, for tier B, the number of bins
(for tier A, the dark-count rate). Times are in units of $1/\kappa_2$. Every segment starts
in $|{+\alpha}\rangle$ at $t = 0$ and ends with a Z readout at $t = T_{\rm seg} = 200$; the
label is 1 when the readout gave $-\alpha$.

Every file mixes segments of four cat sizes, $\bar n = 2$, $2.5$, $3$ and $3.5$, in the
proportions 1 : 2 : 4 : 8 (big cats flip less often, so they get more segments), in random
order. The array `nbar` gives the cat size of each segment.

| file | records | device | labels | segments | use |
| --- | --- | --- | --- | --- | --- |
| `tierB_train.npz` | heterodyne | nominal (the one you can simulate) | yes | 15 000 | design and train your detector |
| `tierB_val.npz` | heterodyne | hidden test device | yes | 7 500 | measure how your detector transfers to the real device |
| `tierB_test.npz` | heterodyne | hidden test device | **no** | 22 500 | your submission, scored on the leaderboard |
| `tierA_train.npz` | clicks | nominal | yes | 30 000 | tutorial 5; the burst and what it tells you (steps 2 and 4) |
| `tierA_val.npz` | clicks | hidden test device | yes | 15 000 | tutorial 5; the hidden device seen by a photon counter |
| `tierA_test.npz` | clicks | hidden test device | **no** | 30 000 | not scored: more unlabelled records of the hidden device, if you want them |

The hidden device differs from the nominal one in *kind*, not only in numbers: its buffer is
a real resonator of finite bandwidth (two-mode model) and its memory has a small Kerr
non-linearity, the same at every cat size. The noise rates $\kappa_1$, $n_{th}$,
$\kappa_\varphi$ and the cat sizes are the nominal ones. Fraction of flip labels:

| cat size $\bar n$ | 2 | 2.5 | 3 | 3.5 |
| --- | --- | --- | --- | --- |
| nominal device, master equation | 14.6 % | 7.30 % | 3.40 % | 1.51 % |
| `tierB_train.npz` | 15.8 ± 1.2 % | 6.7 ± 0.6 % | 3.0 ± 0.3 % | 1.59 ± 0.14 % |
| `tierA_train.npz` | 14.4 ± 0.8 % | 7.2 ± 0.4 % | 3.7 ± 0.2 % | 1.45 ± 0.09 % |
| `tierB_val.npz` (hidden device) | 26.2 ± 2.0 % | 11.3 ± 1.0 % | 8.4 ± 0.6 % | 4.3 ± 0.3 % |
| `tierA_val.npz` (hidden device) | 24.3 ± 1.4 % | 14.8 ± 0.8 % | 8.8 ± 0.4 % | 4.6 ± 0.2 % |

The errors are binomial. On the test split of tier B, the leaderboard score $1 - \rho_{70}$
carries a statistical uncertainty of about ±0.015.

## Common to both datasets

* `nbar`: `float64` array `(n_segments,)`, the cat size $\bar n = \alpha^2$ of each segment.
* `labels` (train and val only): `int8` array `(n_segments,)`.

## Tier B: heterodyne records (the challenge)

* `I`, `Q`: `float16` arrays `(n_segments, n_bins)`, the two quadratures of the buffer output
  averaged over bins of duration `T_seg / n_bins` = 0.5. Convention (dynamiqs): for the
  measured channel $L = \sqrt{\eta/2}\,(a^2 - \alpha^2)$ the record is
  $I = \langle L + L^\dagger\rangle + \xi(t)$ with $\xi$ white noise of variance 1 per unit
  time, so each bin carries Gaussian noise of standard deviation
  $\sqrt{n_{\rm bins}/T_{\rm seg}} = 1.41$. $Q$ is the same for $iL$.
* A note on the baseline of $I$. The simulation uses a first-order scheme with a fixed time
  step, which shifts the mean of $I$ in proportion to the step. The training records were
  simulated with a step of $1.6\times10^{-5}$: the mean of their $I$ agrees with the master
  equation of the nominal device within its statistical error (0.001 to 0.002, depending on
  the cat size). The validation and test records were simulated with a step of
  $5\times10^{-4}$ and are shifted by about $-0.004$: do not read physics into a baseline
  difference of that size. The mean of $Q$ is not affected.

## Tier A: click records (tutorial 5, not scored)

* `clicktimes`: array `(n_segments, n_max)` of click times of the buffer-output photon
  counter, sorted, padded with `NaN`. Detection efficiency `eta` and dark counts of rate
  `dark_rate` (per unit time, uniform in the segment) are already applied. The simulation
  resolves a click to one integration step (10⁻³ time units); click times are spread
  uniformly within that step, so real clicks and dark counts look alike. A segment holds
  12 to 19 clicks on average, depending on the device and the cat size.

## Submission format

One CSV for the heterodyne records, with a header and one row per segment of
`tierB_test.npz`, in order:

```
segment_id,score,decision
0,0.12,0
1,3.41,1
...
```

`score` is any real number (higher = more suspicious; the leaderboard discards the 30 %
highest scores of the file, all cat sizes together, and reports the flip suppression
$1 - \rho_{70}$, where $\rho_{70}$ is the residual flip fraction), `decision` is 0 or 1
(1 = discard; your own operating point, and the flags of the correction score $S$ of the
capstone, both reported on the validation split). `catchtheflip.scoring.write_submission`
writes this format; the leaderboard checks it strictly (three columns, rows in the order of
`segment_id`, finite scores, a file below 2 MB), and `catchtheflip.leaderboard.check` runs
the same checks on your file. `scripts/score_submission.py` scores a file of this format,
written for a labelled split (one row per segment of that split), against its labels.
The leaderboard shows the score with two decimals, and your final submission is one file
(`CHALLENGE.md`, step 3).

## Make your own data

`scripts/generate_dataset.py` produces labelled data of the nominal device at any cat size
and with any seed (one to two click-record segments per second on a laptop, one heterodyne
segment in about two seconds), and `catchtheflip.models`
lets you change the device to see what matters. Heterodyne records made with the default
step ($5\times10^{-4}$) have a baseline of $I$ that is 0.01 to 0.03 too low, more for big
cats: pass a smaller `--dt` if the baseline matters to you (the cost grows as $1/$`dt`). The test split cannot be regenerated: its seed
and its device parameters are private.
