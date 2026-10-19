"""PLAN v4 E2'/E4: nose metrics of a multi-release run (releases on separate scalars s1..sN, 30 s apart).

For each release k (MULTI_RELEASES, or LES_RELEASES for a '_les' case, in cfd/cases/sofa/make_case.py; the standing
case uses the same releases) and nose, over the window from its release to the end of its own window (150 s RANS,
90 s LES): peak s and OAV, arrival time (OAV >= 1), worst-breath OAV (mean and max over breathing phases, as in
cfd/cases/sofa/analyze_sofa.py), time above OAV 1, and s at the end of the window (start of the well-mixed tail).
The worst-breath OAV is also given for the nested windows WINDOWS (first W s after release) that the run reaches, and
at equal mass: x V0 / V_k, the 92 mL basis of the earlier single-release results (uq/routing_headline.py), so the
headline scripts can read both alike.
Each release is tagged with its class (A = audible, S = silent) and momentum level (M0). nose_oav() turns the levels of
a class into the OAV of any passage (V, M0) by V/V_rep scaling within the class.
Writes <case>/multi_result.json.
Usage: python3 cfd/postprocess/analyze_multi.py <multi_case> [--noses releaser,neighbour]
(probe order is releaser, neighbour in both the sofa and the standing case)
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cfd/cases/sofa"))
import analyze_sofa as an  # noqa: E402  read_probe, breath_metrics, oav, P

_spec = importlib.util.spec_from_file_location("sofa_case", ROOT / "cfd/cases/sofa/make_case.py")
sofa_case = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sofa_case)

V0 = 9.2e-5                          # m^3, equal-mass basis of the single-release runs (uq/routing_headline.V0)
WINDOWS = (30.0, 60.0, 120.0, 150.0)  # s after release; 300 and 600 s come from the well-mixed tail
CLASSES = {"A": "audible", "S": "silent"}


def release_plan(case: Path):
    """(releases, first release time, gap, window) of a multi-release case; '_les' cases use the LES set."""
    if case.name.endswith("_les"):
        rels, gap = sofa_case.release_set("les")
        return rels, 0.2 + sofa_case.LES_SPINUP, gap, sofa_case.LES_WINDOW
    rels, gap = sofa_case.release_set("rans")
    return rels, 0.2, gap, sofa_case.MULTI_WINDOW


def worst_breath(t, s):
    wb_mean, wb_max = an.breath_metrics(t, s)
    return an.oav(wb_mean, an.P), an.oav(wb_max, an.P)


def release_metrics(t, s, t_rel, V):
    o = np.array([an.oav(x, an.P) for x in np.maximum(s, 0.0)])
    above = o >= 1.0
    dt = np.gradient(t)
    wb_mean, wb_max = worst_breath(t, s)
    by_window = {}
    for W in WINDOWS:
        if t[-1] - t_rel < W - 0.5:  # run (or this release's window) does not reach W yet
            continue
        m = t <= t_rel + W + 1e-9
        wm, wx = worst_breath(t[m], s[m])
        by_window[f"{W:g}"] = {"worst_breath_OAV_mean": wm, "worst_breath_OAV_max": wx,
                               "worst_breath_OAV_mean_at_V0": wm * V0 / V, "worst_breath_OAV_max_at_V0": wx * V0 / V}
    return {"peak_s": float(s.max()), "peak_OAV": float(o.max()), "t_peak_s": float(t[np.argmax(s)] - t_rel),
            "t_arrival_s": float(t[np.argmax(above)] - t_rel) if above.any() else None,
            "time_above_OAV1_s": float(np.sum(dt[above])), "exposure_s_dt": float(np.trapezoid(s, t)),
            "worst_breath_OAV_mean": wb_mean, "worst_breath_OAV_max": wb_max,
            "s_end": float(np.mean(s[t >= t[-1] - 5.0])), "by_window": by_window}


def nose_oav(result, nose, window, V, M0, cls, stat="worst_breath_OAV_mean"):
    """OAV at `nose` over the first `window` s for passages of volume V (m^3) and exit momentum flux M0 (m^4/s^2) in
    class cls ('silent' or 'audible'); V and M0 may be arrays.

    The class's levels give the response per released volume, OAV_k / V_k (releases at the same M0, e.g. the repeated
    LES medians, are averaged first). Between levels it is interpolated linearly in log M0, of its log when every
    level is > 0 and of the value itself otherwise (a zero level stays zero); outside the levels' M0 range it is held
    at the nearest level (no extrapolation). The result is that response x V.
    [APPROXIMATION] At a given M0 the route does not depend on V: a larger or smaller passage keeps the route of the
    representative release, and the concentration scales with the released volume (passive scalar, linear transport).
    """
    key = f"{window:g}"
    per_v = {}
    for r in result["releases"].values():
        if r["class"] != cls or key not in r[nose]["by_window"]:
            continue
        per_v.setdefault(r["M0"], []).append(r[nose]["by_window"][key][stat] / r["V"])
    if not per_v:
        raise ValueError(f"no {cls} level reaches the {key} s window at {nose}")
    m0 = np.array(sorted(per_v))
    y = np.array([np.mean(per_v[m]) for m in m0])
    x = np.log(np.clip(np.asarray(M0, dtype=float), m0[0], m0[-1]))
    if np.all(y > 0):
        resp = np.exp(np.interp(x, np.log(m0), np.log(y)))
    else:
        resp = np.interp(x, np.log(m0), y)
    return resp * np.asarray(V, dtype=float)


def main(case: Path, noses):
    rels, t_rel0, gap, window = release_plan(case)
    out = {"case": case.name, "V0": V0, "windows": [f"{W:g}" for W in WINDOWS], "releases": {}}
    for k, (name, V, T, d) in enumerate(rels, 1):
        src = sofa_case.equivalent_source(V, T, d)
        t_rel = t_rel0 + gap * (k - 1)
        t, s = an.read_probe(case, f"s{k}")
        m = (t >= t_rel) & (t <= t_rel + window + 1e-9)
        if m.sum() < 10:
            print(f"s{k}: not enough samples yet (run reaches t = {t[-1]:.1f} s)")
            continue
        r = {"class": CLASSES[name[0]], "level": name, "V": V, "T": T, "d": d, "u0": src["u0"], "M0": src["M0"],
             "u_eq": src["u_eq"], "dilution": src["dilution"], "t_release": t_rel, "window_end": float(t[m][-1] - t_rel)}
        for j, nose in enumerate(noses):
            r[nose] = release_metrics(t[m], s[m, j], t_rel, V)
        out["releases"][name] = r
    (case / "multi_result.json").write_text(json.dumps(out, indent=1))
    for name, r in out["releases"].items():
        line = "  ".join(f"{n}: wb@V0 " + " ".join(f"{w}s {x['worst_breath_OAV_mean_at_V0']:.3g}"
                                                   for w, x in r[n]["by_window"].items())
                         + f"  arr {r[n]['t_arrival_s']}" for n in noses)
        print(f"{name} ({r['class']}, u0 {r['u0']:.1f} m/s, M0 {r['M0']:.3g}, window {r['window_end']:.0f} s)  {line}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("--noses", default="releaser,neighbour")
    a = ap.parse_args()
    main(Path(a.case), a.noses.split(","))
