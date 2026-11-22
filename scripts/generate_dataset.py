#!/usr/bin/env python
"""Generate a challenge dataset (public records file + private ground-truth file).

Examples
--------
Nominal device at the cat size 3, tier A, 300 labelled segments, on a laptop (about one
segment per second):

    python scripts/generate_dataset.py --tier A --nbar 3 --n 300 --seed 1 \
        --out data/tierA_mini.npz --labels

A custom device described by a JSON file of parameters (see catchtheflip.models), private
ground truth kept aside:

    python scripts/generate_dataset.py --tier B --params-json device.json --n 5000 --seed 7 \
        --out tierB_test.npz --private tierB_test_private.npz
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))  # the workspace, if the package is not installed

from catchtheflip import datasets, models, protocol  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tier", choices=["A", "B"], required=True)
    p.add_argument("--n", type=int, required=True, help="number of segments")
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--out", required=True, help="public .npz file")
    p.add_argument("--private", default=None, help="private .npz file with labels and privileged info")
    p.add_argument("--labels", action="store_true", help="include the labels in the public file")
    p.add_argument("--params-json", default=None, help="JSON file with model parameters (default: nominal device)")
    p.add_argument("--nbar", type=float, default=2.5, help="cat size of the nominal device (ignored with --params-json)")
    p.add_argument("--T-seg", type=float, default=protocol.T_SEG)
    p.add_argument("--eta", type=float, default=None, help="detection efficiency (default 0.8 for A, 1 for B)")
    p.add_argument("--dark-rate", type=float, default=protocol.DARK_RATE)
    p.add_argument("--n-bins", type=int, default=protocol.N_BINS)
    p.add_argument("--method", default=None)
    p.add_argument("--dt", type=float, default=None, help="time step (default 2e-3 for A, 5e-4 for B)")
    p.add_argument("--chunk", type=int, default=500)
    args = p.parse_args()

    if args.params_json:
        with open(args.params_json) as f:
            params = models.params_from_dict(json.load(f))
    else:
        params = models.SingleModeParams(nbar=args.nbar, N=protocol.fock_cutoff(args.nbar))
    eta = args.eta
    t0 = time.time()
    data = datasets.generate(
        params, args.tier, args.n, args.seed, T_seg=args.T_seg, eta=eta, dark_rate=args.dark_rate,
        n_bins=args.n_bins, method=args.method, dt=args.dt, chunk=args.chunk,
    )
    public, private = datasets.split(data, with_labels=args.labels)
    datasets.save(public, private if args.private else None, args.out, args.private)
    n_flips = int(data["labels"].sum())
    print(f"{args.n} segments in {time.time() - t0:.0f} s, {n_flips} flips ({n_flips / args.n:.2%}), written to {args.out}")


if __name__ == "__main__":
    main()
