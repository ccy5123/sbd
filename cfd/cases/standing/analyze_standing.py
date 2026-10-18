"""Scenario D' ('standing pair') analysis: silent vs audible at the culprit's and the neighbour's nose, still air vs
office ceiling ventilation.

Reads cfd/runs/stand_{still,vent}_{silent,audible}: nose probes (order C, N; both stages concatenated) and the
nose-height plane (breathing-zone disc r = 5 cm, head ring r = 25 cm). Release at t = 0.2 s; window 60 s.
Writes cfd/cases/standing/results.json.
Usage (repo root): python3 cfd/cases/standing/analyze_standing.py [runs_dir]
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sofa = _load("analyze_sofa", ROOT / "cfd/cases/sofa/analyze_sofa.py")
case = _load("stand_case", ROOT / "cfd/cases/standing/make_case.py")
oav, P = sofa.oav, sofa.P
NAMES = case.NAMES                       # probe order: C (culprit), N (neighbour)
VENTS, MODES = ("still", "vent"), ("silent", "audible")
HEAD_DX = -0.03                          # head centre relative to the body centre, along the facing direction


def zone_series(path: Path, r_bz=0.05, r_head=0.25):
    d = path / "postProcessing/planes"
    times = sorted((q for q in d.iterdir() if q.name.replace(".", "").isdigit()), key=lambda q: float(q.name))
    t, bz, ring = [], [], []
    for q in times:
        f = q / "noseHeight.xy"
        if not f.exists():
            continue
        a = np.loadtxt(f)
        t.append(float(q.name))
        rb, rr = [], []
        for n in NAMES:
            px, py, _ = case.nose_probe(n)
            x, y, fac = case.manikin.PAIR[n]
            hx = x + fac * HEAD_DX
            rb.append(a[np.hypot(a[:, 0] - px, a[:, 1] - py) < r_bz, 3].mean())
            rr.append(a[np.hypot(a[:, 0] - hx, a[:, 1] - y) < r_head, 3].max())
        bz.append(rb)
        ring.append(rr)
    return np.array(t), np.array(bz), np.array(ring)


def branch(path: Path):
    t, s = sofa.read_probe(path)
    tz, bz, ring = zone_series(path)
    out = {}
    for i, n in enumerate(NAMES):
        m = sofa.metrics(t, s[:, i])
        m.update({"bz_peak_OAV": oav(float(bz[:, i].max()), P), "head_ring_peak_OAV": oav(float(ring[:, i].max()), P),
                  "t_head_ring_peak_s": float(tz[np.argmax(ring[:, i])] - sofa.T_REL)})
        out[n] = m
    return out


def main(runs: Path):
    res = {"branches": {}, "R_silent_over_audible": {}}
    for v in VENTS:
        for mode in MODES:
            p = runs / f"stand_{v}_{mode}"
            if (p / "postProcessing/noses").exists():
                res["branches"][f"{v}_{mode}"] = branch(p)
        if all(f"{v}_{m}" in res["branches"] for m in MODES):
            s, a = res["branches"][f"{v}_silent"], res["branches"][f"{v}_audible"]
            res["R_silent_over_audible"][v] = {
                n: {k: (s[n][k] / a[n][k] if a[n][k] > 0 else None)
                    for k in ("worst_breath_OAV_mean", "bz_peak_OAV", "peak_OAV", "exposure_s_dt")} for n in NAMES}
    (ROOT / "cfd/cases/standing/results.json").write_text(json.dumps(res, indent=1))
    for b, r in res["branches"].items():
        print(b, "  ".join(f"{n}: wb {r[n]['worst_breath_OAV_mean']:.3g} bz {r[n]['bz_peak_OAV']:.3g} "
                           f"t_arr {r[n]['t_arrival_s']}" for n in NAMES))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "cfd/runs")
