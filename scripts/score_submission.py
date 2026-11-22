#!/usr/bin/env python
"""Score a CSV of scores against a labelled split (public scorer).

    python scripts/score_submission.py my_val_scores.csv data/tierB_val.npz

The CSV has the format of a submission and one row per segment of the labelled split it is
scored against: write it with `catchtheflip.scoring.write_submission` from your scores on
that split. Your leaderboard file has one row per segment of the *test* split, which has no
public labels, and cannot be scored here.

The leaderboard scores the hidden test split by the same rule with the private labels, and
shows only the flip suppression 1 - rho_70 (higher is better), where rho_70 is the residual
flip fraction after discarding the 30 % most suspicious segments of the file, all cat sizes
together. The other numbers (where the discarded segments come from, your operating point,
the AUC, the Pauli-frame correction score S of the capstone) are for the labelled validation
split; the organisers compute them on the test split after the deadline. The points are those
of the leaderboard criterion (CHALLENGE.md, step 3).
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))  # the workspace, if the package is not installed

from catchtheflip import leaderboard, records, scoring  # noqa: E402


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sub, data = sys.argv[1], sys.argv[2]
    d = records.load_dataset(data)
    if "labels" not in d:
        sys.exit("this dataset has no labels (hidden test set): submit on the leaderboard instead")
    try:
        leaderboard.check(pathlib.Path(sub).read_bytes())  # the format checks of the leaderboard
    except ValueError as error:
        sys.exit(f"the leaderboard would reject this file: {error}")
    out = scoring.score_submission(sub, d["labels"])
    lb, op, c = out["leaderboard"], out["operating_point"], out["correction"]
    print(f"leaderboard score: 1 - rho_70 = {lb['suppression']:.3f}, rho_70 = {lb['rho']:.3f}  (flip fraction {lb['p_flip']:.4f} -> {lb['p_kept']:.4f} after discarding 30 %: {lb['flips_discarded']} of {lb['flips_total']} flips removed)")
    print(f"   worth {scoring.leaderboard_points(lb['suppression']):.1f} points out of 10 for the leaderboard criterion")
    if "nbar" in d:
        scores = scoring.read_submission(sub)["score"]
        for nbar, r in scoring.by_cat_size(scores, d["labels"], d["nbar"]).items():
            print(f"   cat size {nbar:g}: {r['discarded']:5.1%} of {r['segments']} segments discarded, {r['flips_discarded']} of {r['flips_total']} flips removed")
    print(f"your operating point: yield = {op['yield']:.3f}, residual flip fraction rho = {op['rho']:.3f}")
    print(f"AUC = {out['auc']:.3f}")
    print(f"correction score at your decisions: S = {c['S']:.3f}  (TPR = {c['tpr']:.3f}, FPR = {c['fpr']:.4f})")


if __name__ == "__main__":
    main()
