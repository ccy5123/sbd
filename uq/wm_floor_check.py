"""Checks of the well-mixed floor of the windows beyond 150 s (cfd/postprocess/analyze_multi.WM_FLOOR, 6 Nov).

1. Switch: with the floor off (the module switch, as SBD_NO_WM_FLOOR=1) uq/four_outcomes_v4.compute reproduces the
   numbers of the last commit before the floor, REF, for every row and summary, by default and with a gain (the gain
   moved inside nose_oav so that it acts below the floor, not on it); every share to 1e-12.
2. Reference runs: the rule max(150 s worst breath, tail, well-mixed level at 150 s) against what the coupled 10-minute
   sofa runs give over 300 and 600 s (cfd/postprocess/tail_validation.json, 92 mL, one silent and one audible release;
   the run probes are not in the repo, the actual values stored there are), old rule alongside.
3. How much of the headline stands on the floor: per case and nose, the well-mixed OAV of the 92 mL basis, the share of
   silent and of audible passages at the floor at 600 s, and the median rise of the OAV over the 150 s window.
Usage (repo root): python3 uq/wm_floor_check.py -> uq/wm_floor_check.json
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "uq"))
import four_outcomes_v4 as fv  # noqa: E402

am = fv.am
REF = "7b96837"  # last commit before the floor


def at_ref(path):
    return json.loads(subprocess.run(["git", "-C", str(ROOT), "show", f"{REF}:{path}"], check=True, capture_output=True,
                                     text=True, encoding="utf-8").stdout)


def deviation(a, b):
    """Largest absolute difference between the numbers of two nested results (a's keys, walked in b)."""
    if isinstance(a, dict):
        return max((deviation(v, b[k]) for k, v in a.items()), default=0.0)
    if isinstance(a, (list, tuple)):
        return max((deviation(x, y) for x, y in zip(a, b)), default=0.0)
    if isinstance(a, bool) or not isinstance(a, (int, float)):
        assert a == b, (a, b)
        return 0.0
    return abs(a - b)


def check_switch(sim):
    ref = at_ref("uq/four_outcomes_v4.json")
    gain, key = (6.6, 1.3), "summary_bare_600s_bystanders"
    old = am.WM_FLOOR
    am.WM_FLOOR = False
    try:
        out = fv.compute(sim=sim)
        gained = fv.compute(sim=sim, gain=gain)[key]
    finally:
        am.WM_FLOOR = old
    dev = deviation(ref, json.loads(json.dumps(out)))
    ca = at_ref("uq/combined_adverse.json")["cases"]["mesh x LES median"]
    dev_gain = max(abs(ca[t][o]["physics"][k] - gained[t][o]["physics"][k])
                   for t in ("frequency, central", "equal per scene") for o in fv.rh.OBS for k in fv.OUTCOMES)
    print(f"floor off vs {REF}: four_outcomes_v4.json max |difference| {dev:.1e}; with gain {gain}: {dev_gain:.1e}")
    if max(dev, dev_gain) > 1e-12:
        raise SystemExit("the floor switch does not reproduce the numbers before the floor")
    return {"reference_commit": REF, "max_abs_deviation_default": dev, "max_abs_deviation_gain": dev_gain}


def check_reference():
    tv = json.loads((ROOT / "cfd/postprocess/tail_validation.json").read_text())
    out = {}
    for mode, r in tv.items():
        for nose in ("releaser", "neighbour"):
            x = r[nose]
            floor = am.an.oav(x["tail"]["C_wm_s_at_150"], am.an.P)
            for w, y in x["windows"].items():
                new = max(y["predicted_OAV_mean"], floor)
                row = {"floor_OAV": floor, "old_rule_OAV": y["predicted_OAV_mean"], "new_rule_OAV": new,
                       "actual_OAV": y["actual_OAV_mean"], "old_ratio": y["predicted_OAV_mean"] / y["actual_OAV_mean"],
                       "new_ratio": new / y["actual_OAV_mean"], "actual_over_floor": y["actual_OAV_mean"] / floor,
                       "late_rising": x["tail"]["late_rising"]}
                out[f"{mode} {nose} {w} s"] = row
                print(f"{mode:7s} {nose:9s} {w:>3s} s: floor {floor:.3g}, actual {row['actual_OAV']:.3g}, ratio old "
                      f"{row['old_ratio']:.2f}, new {row['new_ratio']:.2f}")
    return out


def share_on_floor(sim):
    V, M0, osc = sim["V"], sim["Q"] * sim["u0"], sim["osc"].astype(bool)
    out = {}
    for case, (scene, cloth) in fv.CASES.items():
        f = fv.RES / f"{case}.json"
        if not f.exists():
            continue
        res = json.loads(f.read_text())
        wm = am.wm_floor_per_V(res["V_room"], res["lambda_per_s"])
        noses = list(fv.ELEVATOR_NOSES) if scene.startswith("elevator") else ["releaser", "neighbour"]
        for nose in noses:
            row = {"scene": scene, "clothing": cloth, "V_room": res["V_room"], "lambda_per_s": res["lambda_per_s"],
                   "floor_OAV_at_92mL": wm * am.V0}
            for cls, mask in (("silent", ~osc), ("audible", osc)):
                d150 = am.nose_oav(res, nose, 150, V[mask], M0[mask], cls)
                d600 = am.nose_oav(res, nose, 600, V[mask], M0[mask], cls)
                row[cls] = {"share_at_floor": float(np.mean(d150 < wm * V[mask])),
                            "median_rise": float(np.median(d600 / d150))}
            out[f"{case} {nose}"] = row
            print(f"{case:26s} {nose:10s} floor at 92 mL {row['floor_OAV_at_92mL']:6.3g}  at floor silent "
                  f"{100 * row['silent']['share_at_floor']:5.1f} %, audible {100 * row['audible']['share_at_floor']:5.1f} %"
                  f"  median rise {row['silent']['median_rise']:7.3g} / {row['audible']['median_rise']:7.3g}")
    return out


def main():
    sim = fv.passages()
    res = {"switch": check_switch(sim), "reference_runs": check_reference(), "share_on_floor": share_on_floor(sim)}
    (ROOT / "uq/wm_floor_check.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
