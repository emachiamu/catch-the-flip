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
