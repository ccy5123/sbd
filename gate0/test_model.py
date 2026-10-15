"""Limit and consistency checks for the Gate 0 model.  Run: python3 -m pytest gate0 -q"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import Release, load_params, nominal, phase1, phase2, ratio, receptor, source_mole_fraction_ppb  # noqa: E402

P = nominal(load_params())


def test_ppb_conversion():
    # 1.06 umol/L at 37 C -> RT/p = 25.45 L/mol -> 26.98 ppm
    assert source_mole_fraction_ppb(1.06, 310.15) == pytest.approx(26977, rel=1e-3)


def test_no_momentum_release_is_undiluted_in_near_field():
    rel = Release(V=5e-5, T=5.0, d=0.015)  # u0 ~ 0.06 m/s < u_handoff
    ph = phase1(rel, P)
    assert ph["D_mom"] == 1.0 and ph["x_h"] == 0.0


@pytest.mark.parametrize("u_h", [0.05, 0.1, 0.2])
def test_momentum_dilution_law(u_h):
    """Steady-jet hand-off dilution should approach (B_u/K_c)-like O(1) * u0/u_h."""
    p = {**P, "u_handoff": u_h, "g_reduced": 0.0}
    rel = Release(V=5e-3, T=50.0, d=0.006)  # long release -> steady starting-jet regime
    ph = phase1(rel, p)
    assert ph["regime"] == "starting-jet"
    beta = ph["D_mom"] / (rel.u0 / u_h)
    assert 0.3 < beta < 1.5


def test_puff_and_jet_give_same_order_of_dilution():
    p = {**P, "g_reduced": 0.0}
    short = phase1(Release(V=1e-4, T=0.2, d=0.006), p)
    long_ = phase1(Release(V=1e-2, T=20.0, d=0.006), p)  # same u0
    assert short["regime"] == "puff" and long_["regime"] == "starting-jet"
    assert 0.3 < short["D_mom"] / long_["D_mom"] < 1.5


def test_phase2_far_field_independent_of_initial_size():
    """At long times a Gaussian puff forgets its initial size: peak ~ m / (4 pi K t)^1.5."""
    K, t = 1e-3, 1e4
    for V_h in (1e-5, 1e-3):
        g, _ = phase2(V_h, t, K, 0.1, 1.5)
        peak_per_volume = g / V_h  # concentration per unit released volume
        expected = 1.0 / (4 * np.pi * K * t) ** 1.5
        assert peak_per_volume == pytest.approx(expected, rel=0.02)


def test_inhalation_average_never_exceeds_peak():
    for V_h in (1e-6, 1e-4, 1e-2):
        g_inst, g_inh = phase2(V_h, 3.0, 1e-4, 0.2, 1.5)
        assert g_inh <= g_inst + 1e-15


def test_equal_releases_give_unit_ratio():
    rel = Release(V=7e-5, T=1.0, d=0.006)
    for basis in ("mass", "conc"):
        assert ratio(rel, rel, P, 1.0, 0.1, basis) == pytest.approx(1.0)


def test_dense_trousers_equalise_releases():
    """Denim kills jet momentum: loud and silent releases end up with the same near-field dilution."""
    loud = receptor(Release(V=1e-4, T=0.3, d=0.004), P, 1.0, 0.1, clothing="denim")
    assert loud["D_mom"] == 1.0


def test_skirt_caps_dilution_at_enclosed_volume():
    rel = Release(V=1e-4, T=0.1, d=0.003)
    free = phase1(rel, P, "none")["D1"]
    skirt = phase1(rel, {**P, "V_skirt": 0.002}, "skirt")["D1"]
    assert skirt <= 0.002 / 1e-4 + 1e-9 < free
