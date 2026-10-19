"""PLAN v4 E2': nose metrics of a multi-release run (four releases on scalars s1..s4, 30 s apart).

For each release k (MULTI_RELEASES in cfd/cases/sofa/make_case.py) and nose, over the window from its release to
150 s later: peak s and OAV, arrival time (OAV >= 1), worst-breath OAV (mean and max over breathing phases, as in
cfd/cases/sofa/analyze_sofa.py), time above OAV 1, and s at the end of the window (start of the well-mixed tail).
Writes <case>/multi_result.json.
Usage: python3 cfd/postprocess/analyze_multi.py <multi_case> [--noses releaser,neighbour]
"""
import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cfd/cases/sofa"))
import analyze_sofa as an  # noqa: E402  read_probe, breath_metrics, oav, P

_spec = importlib.util.spec_from_file_location("sofa_case", ROOT / "cfd/cases/sofa/make_case.py")
sofa_case = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sofa_case)


def release_metrics(t, s, t_rel):
    o = np.array([an.oav(x, an.P) for x in np.maximum(s, 0.0)])
    above = o >= 1.0
    dt = np.gradient(t)
    wb_mean, wb_max = an.breath_metrics(t, s)
    return {"peak_s": float(s.max()), "peak_OAV": float(o.max()), "t_peak_s": float(t[np.argmax(s)] - t_rel),
            "t_arrival_s": float(t[np.argmax(above)] - t_rel) if above.any() else None,
            "time_above_OAV1_s": float(np.sum(dt[above])), "exposure_s_dt": float(np.trapezoid(s, t)),
            "worst_breath_OAV_mean": an.oav(wb_mean, an.P), "worst_breath_OAV_max": an.oav(wb_max, an.P),
            "s_end": float(np.mean(s[t >= t[-1] - 5.0]))}


def main(case: Path, noses):
    out = {"case": case.name, "releases": {}}
    t_rel0 = 0.2
    for k, (name, V, T, d) in enumerate(sofa_case.MULTI_RELEASES, 1):
        src = sofa_case.equivalent_source(V, T, d)
        t_rel = t_rel0 + sofa_case.MULTI_GAP * (k - 1)
        t, s = an.read_probe(case, f"s{k}")
        m = (t >= t_rel) & (t <= t_rel + sofa_case.MULTI_WINDOW)
        if m.sum() < 10:
            print(f"s{k}: not enough samples yet (run reaches t = {t[-1]:.1f} s)")
            continue
        r = {"V": V, "T": T, "d": d, "u0": src["u0"], "M0": src["M0"], "u_eq": src["u_eq"], "dilution": src["dilution"],
             "t_release": t_rel, "window_end": float(t[m][-1] - t_rel)}
        for j, nose in enumerate(noses):
            r[nose] = release_metrics(t[m], s[m, j], t_rel)
        out["releases"][name] = r
    (case / "multi_result.json").write_text(json.dumps(out, indent=1))
    for name, r in out["releases"].items():
        line = "  ".join(f"{n}: wb {r[n]['worst_breath_OAV_max']:.3g} peak {r[n]['peak_OAV']:.3g} arr {r[n]['t_arrival_s']}"
                         for n in noses)
        print(f"{name} (u0 {r['u0']:.1f} m/s, window {r['window_end']:.0f} s)  {line}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("--noses", default="releaser,neighbour")
    a = ap.parse_args()
    main(Path(a.case), a.noses.split(","))
