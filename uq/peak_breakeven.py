"""Peak-factor break-even (robustness analyses, HANDOFF next task 1).

The v4 doses are RANS means; the LES runs will give a peak factor (instantaneous breath / mean breath). Before they land,
this asks how large a factor would have to be to change the answer:
  (a) per scene, at the bystander nose: the multiplier that lifts each representative silent release (S90, S50 as
      emitted, 150 s worst breath, cfd/results_v4/<case>.json) to OAV 1 (Nagata trained-panel threshold) and OAV 20
      (attentive observer's 50 % point); the audible levels are listed for comparison;
  (b) in the headline (uq/four_outcomes_v4: bystanders, bare, 600 s, frequency-weighted; central case and the home /
      office bounds): the smallest multiplier k at which silent-worse >= audible-worse, (i) uniform, k on every OAV,
      and (ii) silent-only, k on the physically silent passages alone (a silent-specific peak factor). Scanned over
      k = 1-1e4 on a log grid, then bisected; 'not reached' if silent-worse stays below audible-worse up to 1e4.
Compare with the LES peak factors when they land (HANDOFF next task 3).
Usage (repo root): python3 uq/peak_breakeven.py -> uq/peak_breakeven.json
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "uq"))
import four_outcomes_v4 as fv  # noqa: E402

KEY = "summary_bare_600s_bystanders"
TAGS = ("frequency, central", "frequency, home", "frequency, office")
LOGK = np.arange(0.0, 4.0001, 0.1)
TARGETS = (1.0, 20.0)


def per_scene():
    out = {}
    for case, (scene, cloth) in fv.CASES.items():
        f = fv.RES / f"{case}.json"
        if not f.exists():
            continue
        rel = json.loads(f.read_text())["releases"]
        # bystander probes: the neighbour, or each non-culprit nose of the elevator (one row per nose)
        noses = ([n for n, role in fv.ELEVATOR_NOSES.items() if role != "culprit"] if scene.startswith("elevator")
                 else ["neighbour"])
        for nose in noses:
            row = {"scene": scene, "clothing": cloth, "nose": nose}
            for lvl, r in rel.items():
                o = r[nose]["by_window"]["150"]["worst_breath_OAV_mean"]
                row[lvl] = {"OAV": o, **({f"k_to_OAV{t:g}": (t / o if o > 0 else None) for t in TARGETS}
                                        if r["class"] == "silent" else {})}
            out[case if nose == "neighbour" else f"{case} {nose}"] = row
    return out


def margins(sim, gain):
    """silent-worse minus audible-worse (physics) per observer and frequency case at this gain."""
    s = fv.compute(sim=sim, gain=gain)[KEY]
    return {(o, t): s[t][o]["physics"]["silent_worse"] - s[t][o]["physics"]["audible_worse"]
            for o in fv.rh.OBS for t in TAGS}, s


def breakeven(sim, mode):
    gain = (lambda k: (k, k)) if mode == "uniform" else (lambda k: (k, 1.0))
    curve = []
    for lk in LOGK:
        m, s = margins(sim, gain(10 ** lk))
        curve.append({"k": float(10 ** lk), **{f"{o[:10]} | {t}": {"silent_worse": s[t][o]["physics"]["silent_worse"],
                                                                  "audible_worse": s[t][o]["physics"]["audible_worse"]}
                                               for o in fv.rh.OBS for t in TAGS}, "_m": m})
    res = {}
    for o in fv.rh.OBS:
        for t in TAGS:
            ms = [c["_m"][o, t] for c in curve]
            i = next((j for j, v in enumerate(ms) if v >= 0), None)
            if i is None:
                res[f"{o[:10]} | {t}"] = None
                continue
            if i == 0:
                res[f"{o[:10]} | {t}"] = 1.0
                continue
            lo, hi = LOGK[i - 1], LOGK[i]
            for _ in range(20):
                mid = 0.5 * (lo + hi)
                lo, hi = (mid, hi) if margins(sim, gain(10 ** mid))[0][o, t] < 0 else (lo, mid)
            res[f"{o[:10]} | {t}"] = float(10 ** hi)
    for c in curve:
        del c["_m"]
    return res, curve


def main():
    sim = fv.passages()
    out = {"scenes_bystander_150s": per_scene(), "headline": KEY, "k_max": float(10 ** LOGK[-1])}
    print("(a) bystander nose, 150 s worst breath (as emitted): OAV, and k to reach OAV 1 / 20 for the silent levels")
    for case, row in out["scenes_bystander_150s"].items():
        lv = "  ".join(f"{l} {row[l]['OAV']:.3g}" + (f" (k {row[l]['k_to_OAV1']:.3g} / {row[l]['k_to_OAV20']:.3g})"
                                                   if "k_to_OAV1" in row[l] else "") for l in ("A90", "A50", "S90", "S50"))
        print(f"  {case:27s} {lv}")
    print("(b) smallest k with silent-worse >= audible-worse (None: not reached up to 1e4)")
    for mode in ("uniform", "silent only"):
        res, curve = breakeven(sim, mode)
        out[f"breakeven_{mode}"] = res
        out[f"curve_{mode}"] = curve
        for k, v in res.items():
            print(f"  {mode:12s} {k:40s} {'not reached' if v is None else f'{v:.3g}'}")
    (ROOT / "uq/peak_breakeven.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
