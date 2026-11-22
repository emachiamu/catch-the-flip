"""What a herald buys a repetition code of cat qubits.

The repetition code of cat qubits corrects phase flips (the frequent errors) with the
stabilisers X_i X_{i+1}, the products of the parities of neighbouring cats. A bit flip of a
data qubit commutes with every stabiliser: it is invisible to the syndromes and is a logical
bit flip on its own (the code has distance 1 against bit flips). Two uses of a herald are
modelled here:

* post-selection: a cycle in which any qubit is flagged is discarded (`postselected_memory`);
* Pauli-frame correction: a flagged qubit is "corrected" by a logical X gate, and a false alarm
  applies a wrong update, which *is* a flip. TPR and FPR are measured against the readout
  labels, so the formula below holds whatever state a flagged qubit is in. Whether such a
  correction helps depends on what a heralded flip does to the qubit (step 4 of the
  challenge).

Per QEC cycle (one segment) and per data qubit, the residual flip probability with
Pauli-frame correction is

    p_eff = p_flip (1 - TPR) + (1 - p_flip) FPR,

and the logical bit-flip probability of a distance-d code is the probability of an odd
number of residual flips (two bit flips act as a product of stabilisers and cancel), ~ d p_eff for
small p_eff. The logical phase-flip probability
with majority-vote decoding of ideal syndromes is
    sum_{k > d/2} C(d, k) p_phase^k (1 - p_phase)^(d-k),

with p_phase the phase-flip probability of one data qubit per cycle.
"""

from __future__ import annotations

from math import comb

import numpy as np


def residual_flip_probability(p_flip: float, tpr: float, fpr: float) -> float:
    return p_flip * (1.0 - tpr) + (1.0 - p_flip) * fpr


def logical_bitflip_probability(d: int, p_flip: float, tpr: float = 0.0, fpr: float = 0.0) -> float:
    """Logical bit-flip probability per cycle: odd number of residual flips among d qubits."""
    p = residual_flip_probability(p_flip, tpr, fpr)
    return 0.5 * (1.0 - (1.0 - 2.0 * p) ** d)


def postselected_memory(d: int, p_flip: float, rho: float, yield_per_qubit: float) -> dict:
    """A memory experiment that discards a cycle whenever any of the d qubits is flagged.

    With a detector of residual flip fraction `rho` at yield `yield_per_qubit` per qubit,
    the logical bit-flip probability per *kept* cycle is that of flips of probability
    rho * p_flip, and the fraction of kept cycles is yield_per_qubit ** d.
    """
    return {
        "p_logical_bitflip_kept": logical_bitflip_probability(d, rho * p_flip),
        "yield": yield_per_qubit**d,
        "p_logical_bitflip_no_herald": logical_bitflip_probability(d, p_flip),
    }


def logical_phaseflip_probability(d: int, p_phase: float) -> float:
    """Logical phase-flip probability per cycle with majority vote over d data qubits."""
    return float(sum(comb(d, k) * p_phase**k * (1 - p_phase) ** (d - k) for k in range(d // 2 + 1, d + 1)))


def monte_carlo_memory(
    d: int, n_cycles: int, p_flip: float, p_phase: float, tpr: float = 0.0, fpr: float = 0.0, n_runs: int = 1000, rng=None
) -> dict:
    """Monte-Carlo memory experiment of a distance-d repetition code (ideal syndromes).

    Each cycle: every data qubit suffers a phase flip with probability p_phase (corrected by
    majority vote, a logical phase flip when more than d/2 qubits flipped) and a bit flip with
    probability p_flip. Each flip is heralded with probability `tpr`, each flip-free qubit
    raises a false alarm with probability `fpr`; a herald triggers a logical X gate on the qubit.
    Returns the fraction of runs with a logical bit flip and with a logical phase flip after
    `n_cycles` cycles, plus the analytic per-cycle values for comparison.
    """
    rng = np.random.default_rng(rng)
    bit_err = np.zeros(n_runs, dtype=bool)
    phase_err = np.zeros(n_runs, dtype=bool)
    for _ in range(n_cycles):
        flips = rng.random((n_runs, d)) < p_flip
        heralds = np.where(flips, rng.random((n_runs, d)) < tpr, rng.random((n_runs, d)) < fpr)
        net = flips ^ heralds  # an unheralded flip survives; a false alarm creates a flip
        bit_err ^= net.sum(axis=1) % 2 == 1  # odd number of data flips = logical bit flip
        phase_flips = rng.random((n_runs, d)) < p_phase
        phase_err ^= phase_flips.sum(axis=1) > d / 2
    return {
        "p_logical_bitflip": float(bit_err.mean()),
        "p_logical_phaseflip": float(phase_err.mean()),
        "per_cycle_bitflip": logical_bitflip_probability(d, p_flip, tpr, fpr),
        "per_cycle_phaseflip": logical_phaseflip_probability(d, p_phase),
    }
