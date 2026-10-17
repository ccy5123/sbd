"""Selection ('memory filter') model for the origin of the belief that silent passages are deadlier.

Theorem 3 (Berkson / collider form). Let H = the passage is heard, S = it is smelled (receptor OAV >= detection
threshold). An observer remembers a passage iff they noticed it, N = H or S. Then, whatever the joint law of (H, S),

    P(S | not H, N) = 1,        P(S | H, N) = P(S | H).

So among remembered passages every silent one smelled, while audible ones smelled only at the base rate; the gap is
1 - P(S | H) even when H and S are independent. An observer whose noticing does not depend on S (the emitter, who
feels every release) has N = 1 and no bias: the selection rate of S is zero (Boyd's h1 = 0 case, Snoep et al. 2014).

Intensity is I = OAV^n for smelled passages and 0 otherwise (perception/model.stevens). The 'belief' is the
probability that a remembered silent passage is perceived as stronger than a remembered audible one, P(I_s > I_a),
with ties counted half.
"""
from __future__ import annotations

import numpy as np


def noticed(heard: np.ndarray, smelled: np.ndarray, observer: str) -> np.ndarray:
    """Which passages enter the observer's memory. 'bystander': heard or smelled; 'emitter': all;
    'anosmic': heard only."""
    heard, smelled = np.asarray(heard, bool), np.asarray(smelled, bool)
    if observer == "bystander":
        return heard | smelled
    if observer == "emitter":
        return np.ones_like(heard)
    if observer == "anosmic":
        return heard.copy()
    raise ValueError(observer)


def p_greater(a: np.ndarray, b: np.ndarray) -> float:
    """P(X > Y) for X drawn from a and Y from b, ties counted half (exact, via sorting)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.size == 0 or b.size == 0:
        return float("nan")
    b = np.sort(b)
    lo = np.searchsorted(b, a, side="left")
    hi = np.searchsorted(b, a, side="right")
    return float(np.mean((lo + 0.5 * (hi - lo)) / b.size))


def compare(silent: np.ndarray, intensity: np.ndarray, smelled: np.ndarray, keep: np.ndarray) -> dict:
    """Silent-vs-audible statistics over the passages in `keep` (silent = classified silent by the observer)."""
    s, a = keep & silent, keep & ~silent
    out = {"n_silent": int(s.sum()), "n_audible": int(a.sum()),
           "P_smelly_silent": float(smelled[s].mean()) if s.any() else float("nan"),
           "P_smelly_audible": float(smelled[a].mean()) if a.any() else float("nan"),
           "mean_I_silent": float(intensity[s].mean()) if s.any() else float("nan"),
           "mean_I_audible": float(intensity[a].mean()) if a.any() else float("nan"),
           "P_belief": p_greater(intensity[s], intensity[a])}
    out["gap_P_smelly"] = out["P_smelly_silent"] - out["P_smelly_audible"]
    return out
