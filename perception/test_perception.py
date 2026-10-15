"""Checks for the perception model.  Run: python3 -m pytest perception -q"""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

_spec = importlib.util.spec_from_file_location("perc", Path(__file__).with_name("model.py"))
pm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pm)
PERIOD, TI, VT = 5.0, 0.42, 6.3e-4


def test_each_inhalation_has_the_tidal_volume():
    t = np.arange(0, 30, 0.001)
    q = pm.inspiratory_flow(t, PERIOD, TI, VT)
    _, vols = pm.breath_doses(t, np.ones_like(t), q)
    assert np.allclose(vols[1:-1], VT, rtol=2e-3)


def test_constant_concentration_is_sampled_exactly():
    t = np.arange(0, 30, 0.001)
    q = pm.inspiratory_flow(t, PERIOD, TI, VT, phase=0.3)
    means, _ = pm.breath_doses(t, np.full_like(t, 7.0), q)
    assert np.allclose(means, 7.0)


def test_breath_hold_suppresses_inhalation():
    t = np.arange(0, 40, 0.01)
    q = pm.inspiratory_flow(t, PERIOD, TI, VT, hold=(1.0, 21.0))
    assert np.all(q[(t >= 1.0) & (t < 21.0)] == 0.0)
    assert q[(t >= 21.0) & (t < 21.0 + TI * PERIOD)].max() > 0


def test_long_hold_dodges_a_short_puff():
    t = np.arange(0, 60, 0.01)
    c = pm.puff_series(t, 1.0, 10.0, 1.0)
    q = pm.inspiratory_flow(t, PERIOD, TI, VT, hold=(0.5, 25.0))
    assert pm.worst_breath(t, c, q) < 1e-3


def test_gamma_star_is_break_even():
    R, n = np.array([0.8]), 0.3
    g = pm.gamma_star(R[0], n)
    assert pm.p_belief(R, n, [g * 0.999])[0] == 0.0
    assert pm.p_belief(R, n, [g * 1.001])[0] == 1.0


@pytest.mark.parametrize("tau,a_inf", [(30.0, 0.2), (120.0, 0.5)])
def test_adaptation_limits(tau, a_inf):
    assert pm.adaptation(0.0, tau, a_inf) == pytest.approx(1.0)
    assert pm.adaptation(1e6, tau, a_inf) == pytest.approx(a_inf)
