# Submission of team *(your team name)*

Fill in this folder and upload its files on the
[submission page](https://aqora.io/challenges/pushquantum-hackathon-2026/tracks/alice-bob-pushquantum-2026/submission)
of the track before the deadline announced on site (one zip archive is easiest). It holds:

1. `tierB.csv`, your final submission: one row per segment of the hidden test split of the
   heterodyne records, `segment_id,score,decision` (see `data/README.md`). It is the last
   file you submitted on the leaderboard: if the two differ, the one of the leaderboard
   counts.
2. Your notebooks and any scripts they need, each notebook with an export of its outputs
   (`marimo export html notebook.py -o notebook.html`, which also checks that it runs from
   top to bottom, or *Download as HTML* in the notebook menu of the editor).
3. `RESULTS.md` (or a PDF), your write-up of about two pages: the results table below,
   filled in, your figures and your answers to the capstone.
4. `slides.pdf`: the 15-minute presentation (one slide = "two things AI got wrong and how we
   caught them").
5. `sealed_prediction.txt`, a copy of the sealed prediction that you handed to the mentors
   on Sunday before 09:30: your predicted flip probability per segment
   ($T_{\rm seg} = 200$) of the hidden device at the cat size announced on Sunday at 09:00,
   with an error bar, and one sentence on how you got it.

## Results table

| quantity | value | how obtained |
| --- | --- | --- |
| bit-flip rate $\Gamma_Z$ of the nominal device at the four cat sizes (units of $\kappa_2$) | | spectrum, or a fit of the mean `pneg` of segments of several durations |
| phase-flip rate $\Gamma_X$ of the nominal device at the four cat sizes | | |
| flip probability per segment, nominal and hidden device, at the four cat sizes | | |
| buffer photons emitted during a flip against cat size (nominal device), and how you defined it | | |
| your detector: AUC, $1 - \rho_{70}$, and yield, TPR, FPR, S at your decisions, on the validation split | | |
| your detector: fraction of each cat size that you discard, on the validation split | | |
| your detector: $1 - \rho_{70}$ of your final submission on the hidden test split (leaderboard score) | | |
| $P(\text{flip} \mid n)$ for segments with a large burst (click records of the nominal device, one cat size), and what it means | | |
| best S of an oracle that knows `pneg` (photon-counting simulations of the nominal device) | | |
| logical bit-flip probability per cycle (one cycle = one segment, at the cat size of your choice), d = 5: no herald, post-selected (with yield), Pauli-frame corrected | | |
