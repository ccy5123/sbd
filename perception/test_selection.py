"""Tests for the selection ('memory filter') model, Theorem 3."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from selection import compare, noticed, p_greater


def _independent(n=200_000, p_h=0.3, p_s=0.4, seed=1):
    rng = np.random.default_rng(seed)
    heard = rng.random(n) < p_h
    smelled = rng.random(n) < p_s
    intensity = np.where(smelled, rng.lognormal(1.0, 0.5, n), 0.0)
    return heard, smelled, intensity


def test_theorem3_bystander_independent_sound_and_smell():
    heard, smelled, intensity = _independent()
    r = compare(~heard, intensity, smelled, noticed(heard, smelled, "bystander"))
    assert r["P_smelly_silent"] == 1.0                    # every remembered silent passage smelled
    assert abs(r["P_smelly_audible"] - 0.4) < 0.01         # audible ones smell at the base rate
    assert abs(r["gap_P_smelly"] - (1 - 0.4)) < 0.01       # bias = 1 - P(S | H)
    truth = compare(~heard, intensity, smelled, np.ones_like(heard))
    assert abs(truth["P_belief"] - 0.5) < 0.01             # no real difference ...
    assert r["P_belief"] > 0.75                             # ... but memory produces the belief


def test_emitter_has_no_bias():
    heard, smelled, intensity = _independent()
    keep = noticed(heard, smelled, "emitter")
    assert keep.all()
    a = compare(~heard, intensity, smelled, keep)
    b = compare(~heard, intensity, smelled, np.ones_like(heard))
    assert a == b


def test_anosmic_never_remembers_a_silent_passage():
    heard, smelled, intensity = _independent()
    r = compare(~heard, intensity, smelled, noticed(heard, smelled, "anosmic"))
    assert r["n_silent"] == 0


def test_p_greater_ties_and_order():
    assert p_greater(np.array([1.0]), np.array([1.0])) == 0.5
    assert p_greater(np.array([2.0, 2.0]), np.array([1.0, 3.0])) == 0.5
    assert p_greater(np.array([5.0]), np.array([0.0, 0.0, 1.0])) == 1.0
    assert np.isnan(p_greater(np.array([]), np.array([1.0])))
