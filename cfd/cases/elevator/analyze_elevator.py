"""Scenario C ('elevator whodunit') analysis: who smells what, and can the occupants tell who did it?

Reads cfd/runs/elev_{FL,BL}_{silent,audible}: nose probes (order FL, FR, BL, BR; both stages concatenated) and the
nose-height plane (breathing-zone disc r = 5 cm, head ring r = 25 cm). Release at t = 0.2 s; window 60 s.
Mirror symmetry about y = 0 gives the culprits FR and BR from FL and BL (noses relabelled FL<->FR, BL<->BR), so the
full 4 x 4 culprit -> nose matrix is known for each mode.

Attribution (odour only; the sound of an audible release is a separate cue, not modelled). Each occupant j other
than the culprit c reacts with probability p_cj = Phi(log2(scale * OAV_cj) / sd) (uq/observer_ps.py observer models:
scale converts trained-panel OAV to the observer's), independently, where OAV_cj is the expected worst-breath OAV at
j's nose over the window. Two culprit behaviours:
  'stays still'  - the culprit never reacts;
  'acts along'   - the culprit reacts like a bystander would at their own nose (probability p_cc).
Observers see only WHO reacted. With a uniform prior over the four occupants, the posterior for culprit k given the
reaction set is proportional to P(set | k). Reported per mode, observer model and culprit behaviour:
  P(no one reacts)   - the passage goes unnoticed, no whodunit;
  P(correct)         - probability that the maximum-posterior guess is the culprit (ties split evenly); chance 0.25;
  mean posterior     - expected posterior probability on the true culprit.
Folk rule 'he who smelt it dealt it': with the culprit acting along, the first occupant whose nose-probe OAV reaches
the observer's threshold (scale * OAV >= 1, attentive observer) is accused. Reported: who is first for each culprit.
Usage (repo root): python3 cfd/cases/elevator/analyze_elevator.py [runs_dir]
"""
import importlib.util
import itertools
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
case = _load("elev_case", ROOT / "cfd/cases/elevator/make_case.py")
sys.path.insert(0, str(ROOT / "uq"))
from observer_ps import detect, observers

oav, P = sofa.oav, sofa.P
NAMES = case.NAMES                       # probe order: FL, FR, BL, BR
MIRROR = {"FL": "FR", "FR": "FL", "BL": "BR", "BR": "BL"}
MODES = ("silent", "audible")
HEAD_DX = -0.03                          # head centre relative to the occupant position (manikin.standing)
OBSERVERS = ("attentive, Amoore thresholds", "distracted (everyday)")
NOTICE_SCALES = (1.0, 0.05)              # trained panel; attentive population (params thr_scale_typ)


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
            hx = case.manikin.OCCUPANTS[n][0] + HEAD_DX
            rb.append(a[np.hypot(a[:, 0] - px, a[:, 1] - py) < r_bz, 3].mean())
            rr.append(a[np.hypot(a[:, 0] - hx, a[:, 1] - py) < r_head, 3].max())
        bz.append(rb)
        ring.append(rr)
    return np.array(t), np.array(bz), np.array(ring)


def branch(path: Path):
    t, s = sofa.read_probe(path)
    tz, bz, ring = zone_series(path)
    out = {}
    for i, n in enumerate(NAMES):
        m = sofa.metrics(t, s[:, i])
        o = np.array([oav(x, P) for x in np.maximum(s[:, i], 0.0)])
        m["t_notice_s"] = {str(sc): (float(t[np.argmax(sc * o >= 1)] - sofa.T_REL) if (sc * o >= 1).any() else None)
                           for sc in NOTICE_SCALES}
        m.update({"bz_peak_OAV": oav(float(bz[:, i].max()), P), "head_ring_peak_OAV": oav(float(ring[:, i].max()), P),
                  "t_head_ring_peak_s": float(tz[np.argmax(ring[:, i])] - sofa.T_REL)})
        out[n] = m
    return out, (t, s)


def full_matrix(res, mode):
    """culprit -> nose -> metrics for all four culprits, using the mirror image for FR and BR."""
    mat = {}
    for c in ("FL", "BL"):
        mat[c] = res[f"{c}_{mode}"]
        mat[MIRROR[c]] = {MIRROR[n]: v for n, v in res[f"{c}_{mode}"].items()}
    return mat


def attribution(mat, scale, sd, acts_along=False):
    """Odour-only whodunit with reaction sets; see module docstring."""
    p = {c: {j: float(detect(np.array([scale * mat[c][j]["worst_breath_OAV_mean"]]), sd)[0])
             for j in NAMES} for c in NAMES}
    if not acts_along:
        for c in NAMES:
            p[c][c] = 0.0
    correct = post_true = p_none = 0.0
    for c in NAMES:
        for react in itertools.product((0, 1), repeat=4):
            r = dict(zip(NAMES, react))
            pr = np.prod([p[c][j] if r[j] else 1 - p[c][j] for j in NAMES])
            if pr == 0:
                continue
            like = {k: np.prod([p[k][j] if r[j] else 1 - p[k][j] for j in NAMES]) for k in NAMES}
            z = sum(like.values())
            post = {k: v / z for k, v in like.items()}
            best = [k for k, v in post.items() if np.isclose(v, max(post.values()))]
            correct += pr * (1.0 / len(best) if c in best else 0.0) / 4
            post_true += pr * post[c] / 4
            if not any(react):
                p_none += pr / 4
    return {"P_no_one_reacts": p_none, "P_correct": correct, "mean_posterior_true": post_true,
            "p_react": p}


def first_noticer(arrivals, scale):
    """Folk rule: for each culprit, the occupant whose probe OAV first reaches 1/scale (None if no one)."""
    out = {}
    for c, row in arrivals.items():
        t = {j: v[str(scale)] for j, v in row.items() if v[str(scale)] is not None}
        out[c] = (min(t, key=t.get), t) if t else (None, t)
    return out


def main(runs: Path):
    res = {}
    for c in ("FL", "BL"):
        for mode in MODES:
            path = runs / f"elev_{c}_{mode}"
            if (path / "postProcessing/noses").exists():
                res[f"{c}_{mode}"], _ = branch(path)
    out = {"branches": res, "attribution": {}}
    obs = observers()
    for mode in MODES:
        if not all(f"{c}_{mode}" in res for c in ("FL", "BL")):
            continue
        mat = full_matrix(res, mode)
        for name in OBSERVERS:
            scale, sd, _, _ = obs[name]
            for along in (False, True):
                tag = "acts along" if along else "stays still"
                out["attribution"][f"{mode} | {name} | culprit {tag}"] = attribution(mat, scale, sd, along)
        arr = {c: {j: mat[c][j]["t_notice_s"] for j in NAMES} for c in NAMES}
        for sc in NOTICE_SCALES:
            fn = first_noticer(arr, sc)
            out.setdefault("first_noticer", {})[f"{mode} | scale {sc}"] = {
                c: {"first": f, "times_s": tt} for c, (f, tt) in fn.items()}
    (ROOT / "cfd/cases/elevator/results.json").write_text(json.dumps(out, indent=1))
    for k, v in out.get("first_noticer", {}).items():
        print(k, {c: (r["first"], {j: round(x, 1) for j, x in r["times_s"].items()}) for c, r in v.items()})
    for k, v in res.items():
        print(k, "  ".join(f"{n}: wb {m['worst_breath_OAV_mean']:.3g} bz {m['bz_peak_OAV']:.3g}" for n, m in v.items()))
    for k, v in out["attribution"].items():
        print(f"{k:70s} none {v['P_no_one_reacts']:.2f}  correct {v['P_correct']:.2f}  "
              f"posterior {v['mean_posterior_true']:.2f}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "cfd/runs")
