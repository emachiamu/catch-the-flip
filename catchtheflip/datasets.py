"""Dataset generation: records + labels for the two datasets of the challenge.

Tier A: photon-counting records of the buffer channel (click times, finite efficiency,
        dark counts): the tutorial data.
Tier B: heterodyne records of the buffer channel (I and Q, binned, finite efficiency): the
        records of the leaderboard.

`generate` simulates one block of segments at one cat size; `assemble` concatenates blocks
(for example produced in parallel on a cluster), `pool` mixes the cat sizes into one
shuffled dataset, and `split` separates what participants see from the private ground truth.
Every segment carries its cat size in the array `nbar`.
"""

from __future__ import annotations

import numpy as np

from . import models, protocol, records, simulate


def generate(
    params,
    tier: str,
    n: int,
    seed: int,
    T_seg: float = protocol.T_SEG,
    eta: float | None = None,
    dark_rate: float = protocol.DARK_RATE,
    n_bins: int = protocol.N_BINS,
    method: str | None = None,
    dt: float | None = None,
    chunk: int = 500,
    nmaxclick: int = 256,
) -> dict:
    """Simulate `n` segments of a model and return records, labels and privileged info.

    Args:
        params: `SingleModeParams` or `TwoModeParams`.
        tier: "A" (photon counting) or "B" (heterodyne).
        n, seed: number of segments and PRNG seed (also seeds the detector imperfections
            and the readout sampling, with fixed offsets).
        T_seg: segment duration (1/kappa_2 units).
        eta: detection efficiency (tier A: thinning; tier B: heterodyne efficiency). Defaults
            to the protocol of the challenge (0.8 for tier A, 1 for tier B).
        dark_rate: dark-count rate per unit time (tier A only).
        n_bins: number of bins of the heterodyne records (tier B only).
        method: integration method. Tier A: "euler" by default (fixed step `dt`; use
            dt <= 1e-3 for the two-mode model) or "event" (adaptive). Tier B: "rouchon" by
            default, or "euler" (Euler-Maruyama, unreliable for long segments of big cats, see
            `simulate.heterodyne_segments`). Always validate against `master_equation_pneg`.
        dt: time step (default 2e-3 for tier A, 5e-4 for tier B).
        chunk, nmaxclick: solver controls, see `simulate`.
    """
    model = models.build(params)
    if eta is None:
        eta = protocol.ETA_A if tier == "A" else protocol.ETA_B
    if dt is None:
        dt = 2e-3 if tier == "A" else 5e-4
    rng = np.random.default_rng(seed + 10_007)
    nbar = np.full(n, params.nbar)
    meta = {
        "tier": tier,
        "T_seg": T_seg,
        "eta": eta,
        "n": n,
        "seed": seed,
        "params": params.to_dict(),
        "dt": dt,
        "method": method,
    }
    if tier == "A":
        method = method or "euler"  # the published datasets: EulerJump, validated against mesolve
        out = simulate.counting_segments(
            model, n, T_seg, seed=seed, dt=dt, method=method, nmaxclick=nmaxclick, chunk=chunk
        )
        clean = out["clicktimes"]
        observed = records.apply_counting_imperfections(clean, T_seg, eta=eta, dark_rate=dark_rate, rng=rng)
        labels = records.sample_labels(out["pneg"], rng=rng)
        meta.update({"dark_rate": dark_rate, "method": method})
        return {
            "clicktimes": observed,
            "nbar": nbar,
            "labels": labels,
            "pneg": out["pneg"],
            "clean_clicktimes": clean,
            "nclicks": out["nclicks"],
            "channels": list(out["channels"]),
            "meta": meta,
        }
    if tier == "B":
        method = method or "rouchon"
        out = simulate.heterodyne_segments(
            model, n, T_seg, n_bins=n_bins, eta=eta, seed=seed, dt=dt, method=method, chunk=chunk
        )
        labels = records.sample_labels(out["pneg"], rng=rng)
        meta.update({"n_bins": n_bins, "method": method})
        return {
            "I": out["I"].astype(np.float16),  # noise std 1.41 per bin: float16 resolution (~1e-3) is plenty
            "Q": out["Q"].astype(np.float16),
            "nbar": nbar,
            "labels": labels,
            "pneg": out["pneg"],
            "meta": meta,
        }
    raise ValueError("tier must be 'A' or 'B'")


PUBLIC_KEYS = {"A": ("clicktimes", "nbar"), "B": ("I", "Q", "nbar")}
PRIVATE_KEYS = {"A": ("labels", "pneg", "clean_clicktimes", "nclicks"), "B": ("labels", "pneg")}


def _concatenate(arrays: list, key: str) -> np.ndarray:
    if key in ("clicktimes", "clean_clicktimes"):  # NaN-padded: trim the padding to the longest record
        n_max = max(int(np.sum(~np.isnan(a), axis=1).max(initial=0)) for a in arrays) + 1
        out = np.full((sum(len(a) for a in arrays), n_max), np.nan)
        row = 0
        for a in arrays:
            a = np.sort(a, axis=1)[:, :n_max]  # NaN last
            out[row : row + len(a), : a.shape[1]] = a
            row += len(a)
        return out
    return np.concatenate(arrays)


def drop_invalid(data: dict) -> dict:
    """Remove the segments whose simulation diverged (non-finite readout probability or
    record). It is rare: none of the heterodyne segments of the challenge was lost."""
    ok = np.isfinite(data["pneg"])
    for key in ("I", "Q"):
        if key in data:
            ok &= np.isfinite(data[key]).all(axis=1)
    if ok.all():
        return data
    out = {k: (v[ok] if isinstance(v, np.ndarray) and len(v) == len(ok) else v) for k, v in data.items()}
    out["meta"] = {**data["meta"], "n": int(ok.sum()), "dropped": int((~ok).sum())}
    return out


def assemble(blocks: list[dict]) -> dict:
    """Concatenate blocks produced by `generate` with the same tier and settings."""
    tier = blocks[0]["meta"]["tier"]
    out = {"meta": dict(blocks[0]["meta"])}
    out["meta"]["n"] = int(sum(b["meta"]["n"] for b in blocks))
    out["meta"]["seeds"] = [b["meta"]["seed"] for b in blocks]
    for key in PUBLIC_KEYS[tier] + PRIVATE_KEYS[tier]:
        out[key] = _concatenate([b[key] for b in blocks], key)
    if tier == "A":
        out["channels"] = blocks[0]["channels"]
    return out


def pool(parts: list[dict], seed: int | None = None) -> dict:
    """Mix assembled datasets of the same tier and protocol (one per cat size) into one.

    The segments are shuffled with a permutation drawn from `seed` (kept in order if `seed`
    is None), so that the position of a segment in the file carries no information. The
    cat size of every segment stays available in the array `nbar`.
    """
    tier = parts[0]["meta"]["tier"]
    out = {key: _concatenate([p[key] for p in parts], key) for key in PUBLIC_KEYS[tier] + PRIVATE_KEYS[tier]}
    n = len(out["labels"])
    if seed is not None:
        perm = np.random.default_rng(seed).permutation(n)
        out = {key: val[perm] for key, val in out.items()}
    meta = {k: v for k, v in parts[0]["meta"].items() if k not in ("params", "seed", "seeds", "n")}
    meta.update(
        {
            "n": n,
            "cat_sizes": sorted({float(p["meta"]["params"]["nbar"]) for p in parts}),
            "shuffle_seed": seed,
            "parts": [{k: p["meta"][k] for k in ("params", "n", "seeds") if k in p["meta"]} for p in parts],
        }
    )
    out["meta"] = meta
    if tier == "A":
        out["channels"] = parts[0]["channels"]
    return out


def split(data: dict, with_labels: bool, public_meta: dict | None = None) -> tuple[dict, dict]:
    """Separate the public file (records, labels if `with_labels`) from the private one."""
    tier = data["meta"]["tier"]
    public = {k: data[k] for k in PUBLIC_KEYS[tier]}
    if "clicktimes" in public:  # trim the NaN padding to the longest record
        public["clicktimes"] = _concatenate([public["clicktimes"]], "clicktimes")
    if with_labels:
        public["labels"] = data["labels"]
    pub_meta = {k: data["meta"][k] for k in ("tier", "T_seg", "eta", "n") if k in data["meta"]}
    if tier == "A":
        pub_meta["dark_rate"] = data["meta"].get("dark_rate")
    if tier == "B":
        pub_meta["n_bins"] = data["meta"].get("n_bins")
    pub_meta["cat_sizes"] = data["meta"].get("cat_sizes", sorted({float(x) for x in np.unique(data["nbar"])}))
    pub_meta.update(public_meta or {})
    public["meta"] = pub_meta
    private = {k: data[k] for k in PRIVATE_KEYS[tier] + ("nbar",)}
    private["meta"] = data["meta"]
    return public, private


def save(public: dict, private: dict | None, public_path, private_path=None) -> None:
    pm = public.pop("meta")
    records.save_dataset(public_path, meta=pm, **public)
    public["meta"] = pm
    if private is not None and private_path is not None:
        pm2 = private.pop("meta")
        records.save_dataset(private_path, meta=pm2, **private)
        private["meta"] = pm2
