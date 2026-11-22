"""catchtheflip: helper package for the Alice & Bob "Catch the flip" hackathon challenge.

Units: the two-photon dissipation rate kappa_2 sets the unit of rate, so times are in
units of 1/kappa_2 unless stated otherwise.
"""

from . import leaderboard, models, protocol, rates, records, repcode, scoring, simulate

__version__ = "0.2.0"
__all__ = ["leaderboard", "models", "protocol", "rates", "records", "repcode", "scoring", "simulate", "__version__"]
