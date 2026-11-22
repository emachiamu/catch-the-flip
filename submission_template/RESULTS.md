# Catch the flip: results of team *(your team name)*

Notebook: `notebooks/11_challenge_template.py` (HTML export with outputs: `11_challenge_template.html`).
Figures in `figures/` are produced by `scripts/physics_slides/` from the same data.

## Results table

| quantity | value | how obtained |
| --- | --- | --- |
| bit-flip rate $\Gamma_Z$ of the nominal device at the four cat sizes (units of $\kappa_2$) | 1.70e-03 / 7.82e-04 / 3.50e-04 / 1.53e-04 | slowest Liouvillian eigenvalue (`rates.spectrum`), Fock cutoff checked at N = 20, 24, 28 |
| phase-flip rate $\Gamma_X$ of the nominal device at the four cat sizes | 0.099 / 0.123 / 0.147 / 0.171 | spectrum; agrees with $2\kappa_1[(1+2n_{th})\bar n + n_{th}]$ |
| flip probability per segment, nominal and hidden device, at the four cat sizes | nominal 14.4 % / 7.2 % / 3.4 % / 1.5 %; hidden 26.2 % / 11.3 % / 8.4 % / 4.3 % | nominal: spectrum, $\frac12(1-e^{-\Gamma_Z T})$; hidden: flip-label fractions of the validation split |
| buffer photons emitted during a flip against cat size (nominal device), and how you defined it | 2.4 / 4.3 / 5.4 / 6.5; fits $\bar n^2\kappa_2\tau$ with $\tau$ = 0.58 | excess clicks of flip-labelled over flip-free segments (tier A), divided by $\eta_A$ = 0.8 |
| your detector: AUC, $1 - \rho_{70}$, and yield, TPR, FPR, S at your decisions, on the validation split | AUC 0.768, $1-\rho_{70}$ 0.561, yield 0.70, TPR 0.69, FPR 0.27, S 3.45 | 5-fold out-of-fold, per-cat-size logistic regression on 7 matched-filter features of I |
| your detector: fraction of each cat size that you discard, on the validation split | 100 % / 67 % / 30 % / 12 % | `scoring.by_cat_size`, out-of-fold |
| your detector: $1 - \rho_{70}$ of your final submission on the hidden test split (leaderboard score) | (copy from the leaderboard) | leaderboard |
| $P(\text{flip} \mid n)$ for segments with a large burst (click records of the nominal device, one cat size), and what it means | 0.48 ± 0.04 for n ≥ 5 clicks in one time unit, $\bar n$ = 2.5 | saturates near 50 %: a burst marks a visit to the saddle, from which the memory can fall into either lobe |
| best S of an oracle that knows `pneg` (photon-counting simulations of the nominal device) | 0.95 (rule pneg > 0.5); S = 3.41 flagging the top 30 % | pneg of the 300 photon-counting segments of step 1.4 (nominal device, $\bar n$ = 2.5) |
| logical bit-flip probability per cycle (one cycle = one segment, at the cat size of your choice), d = 5: no herald, post-selected (with yield), Pauli-frame corrected | 0.183 / 0.111 (yield 0.52) / 0.376 | hidden device, $\bar n$ = 3.5, our decisions: rho 0.56, TPR 0.51, FPR 0.10 |

## Step 1–2: the flip and its burst

* **Noise bias.** On the nominal device $\Gamma_Z \propto e^{-1.62\,\bar n}$ (Liouvillian spectrum, converged in the
  Fock cutoff), while $\Gamma_X$ grows linearly. The primer's $2\kappa_1\bar n$ misses the thermal terms: loss and
  thermal photons flip the parity, dephasing does not, and $2\kappa_1[(1+2n_{th})\bar n + n_{th}]$ matches the spectrum
  to 1 %.
* **What a flip radiates.** On the click records the extra clicks of flip segments sit within about one time unit of
  the densest cluster. The excess per flip grows as $\bar n^2\kappa_2\tau$ with $\tau \approx 0.58/\kappa_2$
  (`figures/f04_burst_photons.png`): a flip spends about half a time unit near the saddle, where
  $\langle a^2\rangle \approx 0$ and the buffer emits at $\kappa_2\bar n^2$. Big cats flip rarely but loudly.
* **Not every flip label has a burst.** The label is a Bernoulli draw from `pneg`. Memories that end near the saddle,
  or flip and flip back, give labels without a clean burst, so the burst size averaged over flip labels is an
  underestimate.

## Step 3: the detector

* **Where the information is.** A burst covers ~0.3 % of a record. The matched-filter SNR is
  $d' = \bar n\sqrt{2\tau} \approx 2$–$4$; averaging the whole segment divides it by $\sqrt{T_{\rm seg}/\tau}\approx 19$.
  This is why the mean of $I$ scores 0.12, below "cat size alone" (0.32).
* **Design.** Seven features of the centred $I$ quadrature: deepest dip of 2-, 3- and 4-bin boxcars (a generalised
  likelihood-ratio scan for a burst of unknown onset), the area below −2.0 / −2.5 / −3.0 of the 3-bin trace, and the
  number of bins below −2.5 (sustained flip against brief kick). One standardised L2 logistic regression per cat size
  (the prior differs by size), no class weights, so the outputs are calibrated posteriors on one scale. Trained on the
  hidden-device validation split, 5-fold out-of-fold; the five fold models are averaged on the test split.
* **Why a posterior.** Each discard costs one segment and removes $P(\text{flip}\mid\text{record},\bar n)$ flips in
  expectation, so the best 30 % are the 30 % with the highest posterior (a fractional knapsack). Our detector spends
  the budget on all of $\bar n = 2$, 67 % of 2.5, 30 % of 3 and only the loudest 12 % of 3.5.
* **Operating point.** The 30 % cut discards when $P(\text{flip}\mid\text{record},\bar n) > 0.077$, which is
  Bayes-optimal if a missed flip costs $\zeta = 11.9$ false alarms.
* **Comparison of designs** (out-of-fold $1-\rho_{70}$): mean of $I$ 0.12; cat size alone 0.32; single 3-bin dip
  0.35; gradient boosting 0.50; nominal-trained model transferred 0.54; histogram likelihood ratio 0.55; Gaussian
  matched filter 0.551; **ours 0.561** (AUC 0.768). Q features (rotation, $I^2+Q^2$, Q veto) all lowered the score:
  there is no burst in Q (`figures/f09_ps_curve.png`).

## Step 4: what the herald is worth

* **A burst is not a completed flip.** On the click records at $\bar n = 2.5$, $P(\text{flip}\mid n)$ rises with the
  burst size but saturates near 50 % (`figures/f05_p_given_peak.png`). A large burst means the memory visited the
  saddle; from there it falls into either lobe. In the photon-counting simulations, only about 1 % of segments end
  with `pneg` > 0.5: a heralded memory usually sits in between, not in the other lobe.
* **It cannot be undone by a logical X.** Correction helps only if the flag precision exceeds 50 %
  (TPR·p > FPR·(1−p)). Our flags reach 45 % at the top 1 % and 18 % at the top 30 %, so S > 1 at every threshold
  (`figures/f12_herald.png`). Even the oracle that knows `pneg` reaches only S ≈ 0.95. A heralded flip is an erasure-like
  event ("this qubit was disturbed"), not a logical X at a known time.
* **Repetition code.** A bit flip commutes with the $X_iX_{i+1}$ stabilisers, so any odd number of flips is a logical
  flip and the bit-flip probability grows with $d$. At $\bar n = 3.5$ (hidden device, our decisions) post-selection
  lowers it, while Pauli-frame correction more than doubles it (table above). The herald is usable only by discarding
  cycles, or by an outer code against bit flips that treats heralded flips as erasures (distance $d$ corrects $d-1$
  erasures against $(d-1)/2$ unheralded errors).
* **What it would take.** Larger $\bar n$ (burst ∝ $\bar n^2$, prior ∝ $e^{-c\bar n}$), higher detection efficiency
  and fewer dark counts raise the burst contrast; a wider buffer ($\kappa_b$) lowers the flip rate itself. None of
  these fixes the readout ambiguity of a memory left near the saddle.

## Hidden device and sealed prediction

The hidden device flips 1.7–2.8× more than the nominal one, and the ratio grows with $\bar n$ (fitted slope
$c = 1.30$ against 1.62). Scanning the two-mode model over $(\kappa_b, K)$ against the validation flip fractions
(`figures/f13_chi2map.png`) gives **$\kappa_b \approx 8$, $K \lesssim 0.02$** (best $\chi^2 = 8.5$; only
$(8, 0)$ and $(8, 0.02)$ inside $\Delta\chi^2 \le 2.3$). Kerr up to 0.1 changes the rates by only a few percent at
$\kappa_b = 8$, and no burst appears in Q, which a Kerr rotation would cause: the finite buffer bandwidth is what
weakens the hidden cat.

Sealed prediction (`sealed_prediction.txt`): weighted least-squares fit of $\ln\Gamma_Z$ linear in $\bar n$
($\chi^2/\text{dof} = 9.0/2$, error inflated by $\sqrt{\chi^2/\text{dof}}$). Inside [2, 3.5] it agrees with the
quadratic fit and the physics fit (at $\bar n = 2.75$: 10.6 ± 0.9 %, 9.9 ± 1.7 %, 10.1 %). Outside, the model spread
is added in quadrature (`figures/f15_sealed.png`).

## Two things AI got wrong

1. The sealed-prediction cell first computed flip rates from our own discard flags instead of the labels; caught by
   requiring $p = k/N$ to reproduce the published 26.2 / 11.3 / 8.4 / 4.3 %.
2. An in-sample score (0.571) was reported as the result; the 5-fold out-of-fold score is 0.561.
