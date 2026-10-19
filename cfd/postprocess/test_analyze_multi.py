"""Tests for the multi-release analysis (analyze_multi.py) on synthetic nose-probe series."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_multi as am

RELS = am.sofa_case.MULTI_RELEASES


def shape(tp):
    """Same arrival history after every release: an early puff (10 s) and a larger late one (45 s)."""
    tp = np.maximum(tp, 0.0)
    return np.exp(-((tp - 10.0) / 3.0) ** 2) + 2.0 * np.exp(-((tp - 45.0) / 5.0) ** 2)


def write_case(tmp, name="sofa_v4_multi", t_end=None, scale=None):
    """Probe files s1..s4 (releaser, neighbour); release k gives s = c V_k shape(t - t_rel,k) at both noses."""
    rels, t0, gap, window = am.release_plan(Path(name))
    t_end = t_end or t0 + gap * (len(rels) - 1) + window
    t = np.round(np.arange(0.0, t_end + 1e-9, 0.05), 6)
    d = tmp / name / "postProcessing/noses/0"
    d.mkdir(parents=True)
    for k, (_, V, _, _) in enumerate(rels, 1):
        a = 1e-3 * V / am.V0 * (scale[k - 1] if scale else 1.0)
        s = a * shape(t - (t0 + gap * (k - 1))) * (t >= t0 + gap * (k - 1))
        np.savetxt(d / f"s{k}", np.column_stack([t, s, 0.5 * s]), header="Time 0 1")
    return tmp / name


def run(case):
    am.main(case, ["releaser", "neighbour"])
    return json.loads((case / "multi_result.json").read_text())


def test_equal_mass_is_the_same_for_every_release(tmp_path):
    res = run(write_case(tmp_path))
    at_v0 = [r["neighbour"]["by_window"]["150"]["worst_breath_OAV_mean_at_V0"] for r in res["releases"].values()]
    assert len(at_v0) == 4 and at_v0[0] > 0
    assert np.allclose(at_v0, at_v0[0], rtol=1e-6)  # OAV linear in the released volume


def test_classes_levels_and_noses(tmp_path):
    res = run(write_case(tmp_path))
    assert {n: r["class"] for n, r in res["releases"].items()} == {"A90": "audible", "A50": "audible",
                                                                   "S90": "silent", "S50": "silent"}
    r = res["releases"]["A90"]
    assert np.isclose(r["neighbour"]["worst_breath_OAV_mean"], 0.5 * r["releaser"]["worst_breath_OAV_mean"])


def test_nested_windows(tmp_path):
    w = run(write_case(tmp_path))["releases"]["S50"]["releaser"]["by_window"]
    vals = [w[k]["worst_breath_OAV_max"] for k in ("30", "60", "120", "150")]
    assert vals[0] < vals[1]                           # the late puff (45 s) is outside the 30 s window
    assert np.all(np.diff(vals) >= -1e-12)             # worst breath never drops as the window grows


def test_windows_not_reached_are_left_out(tmp_path):
    res = run(write_case(tmp_path, t_end=145.0))     # stops 54.8 s after the last release, 144.8 s after the first
    assert set(res["releases"]["S50"]["releaser"]["by_window"]) == {"30"}
    assert set(res["releases"]["A90"]["releaser"]["by_window"]) == {"30", "60", "120"}


def test_les_case_timing():
    rels, t0, gap, window = am.release_plan(Path("sofa_v4_multi_les"))
    assert len(rels) == 6 and np.isclose(t0, 60.2) and window == am.sofa_case.LES_WINDOW


def _result(per_v_by_level, cls="audible"):
    """Minimal result dict: level name -> (M0, per-volume OAV), V = 1e-4 m^3."""
    rel = {}
    for name, (m0, y) in per_v_by_level.items():
        rel[name] = {"class": cls, "M0": m0, "V": 1e-4,
                     "n": {"by_window": {"60": {"worst_breath_OAV_mean": y * 1e-4}}}}
    return {"releases": rel}


def test_nose_oav_scaling_and_interpolation():
    res = _result({"L50": (1e-4, 2.0), "L90": (1e-2, 8.0)})
    assert np.isclose(am.nose_oav(res, "n", 60, 1e-4, 1e-4, "audible"), 2.0e-4)       # at a level: OAV_k
    assert np.isclose(am.nose_oav(res, "n", 60, 3e-4, 1e-4, "audible"), 6.0e-4)       # x V / V_k
    assert np.isclose(am.nose_oav(res, "n", 60, 1e-4, 1e-3, "audible"), 4.0e-4)       # log-log midpoint
    clamped = am.nose_oav(res, "n", 60, np.full(2, 1e-4), np.array([1e-8, 1.0]), "audible")
    assert np.allclose(clamped, [2.0e-4, 8.0e-4])                                     # no extrapolation
    with pytest.raises(ValueError):
        am.nose_oav(res, "n", 60, 1e-4, 1e-3, "silent")


def test_nose_oav_zero_level_and_repeats():
    res = _result({"L50": (1e-4, 0.0), "L90": (1e-2, 8.0)})
    assert np.isclose(am.nose_oav(res, "n", 60, 1e-4, 1e-3, "audible"), 4.0e-4)       # linear when a level is 0
    rep = _result({"L50": (1e-4, 2.0), "L50b": (1e-4, 4.0), "L90": (1e-2, 8.0)})
    assert np.isclose(am.nose_oav(rep, "n", 60, 1e-4, 1e-4, "audible"), 3.0e-4)       # repeats averaged
