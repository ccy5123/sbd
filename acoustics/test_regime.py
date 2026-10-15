"""Checks for the M2 acoustic model.  Run: python3 -m pytest acoustics -q"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gate0"))
sys.path.insert(0, str(ROOT / "acoustics"))
from model import load_params, nominal  # noqa: E402
import regime as ac  # noqa: E402

P = nominal(load_params())


@pytest.mark.parametrize("f,expected", [(10**1.8, -26.2), (100, -19.1), (10**2.2, -13.4), (10**2.4, -8.6), (1000, 0.0)])  # exact base-10 centre frequencies
def test_a_weighting_matches_iec_table(f, expected):
    assert float(ac.a_weighting(f)) == pytest.approx(expected, abs=0.15)


def test_erb_glasberg_moore():
    assert ac.erb(np.array([100, 160, 200, 250])) == pytest.approx([35.5, 42.0, 46.3, 51.7], abs=0.1)


def test_monopole_half_space_level():
    """Q' = 1e-4 m^3/s amplitude at 150 Hz, r = 1 m, rigid half space -> ~56 dB SPL (rms)."""
    p = {**P, "alpha_mod": 1.0, "n_harm": 1, "A_cloth": 0.0}
    _, spl = ac.harmonic_spl(1e-4, 150.0, p, r=1.0)
    assert float(spl[..., 0]) == pytest.approx(56.0, abs=0.6)


def test_background_scaling_reproduces_dba():
    f = ac.OCTAVES
    dens = ac.background_spectral_density(f, 40.0, -5.0)
    band = dens + 10 * np.log10(0.7071 * f)
    la = 10 * np.log10(np.sum(10 ** ((band + ac.a_weighting(f)) / 10)))
    assert la == pytest.approx(40.0, abs=1e-6)


def test_low_driving_pressure_is_silent_and_high_is_audible():
    assert ac.classify(1e-5, 0.010, P, "living") == ac.S1           # 10 mL/s through 10 mm: no oscillation
    assert ac.classify(2e-4, 0.002, P, "living") == ac.AUDIBLE      # 200 mL/s through 2 mm
    assert ac.classify(2e-4, 0.002, P, "subway") in (ac.S3, ac.AUDIBLE)


def test_onset_velocity_consistent_with_classification():
    u = ac.u_onset(P)
    d = 0.004
    q_just_below = 0.98 * u * np.pi * d**2 / 4
    q_just_above = 1.02 * u * np.pi * d**2 / 4
    assert ac.classify(q_just_below, d, P, None) == ac.S1
    assert ac.classify(q_just_above, d, P, None) != ac.S1
