"""The headline under different comparison criteria (what 'the silent passage is worse' means).

The four outcomes of uq/four_outcomes_v4 mix two things: whether a passage is smelled at all (detection) and, when
both are smelled, which is stronger (intensity). This script separates them, for the same passages, noses, observers
and scene weights, from the pair terms of four_outcomes.pair_terms (pairs of one silent and one audible passage,
drawn independently; p = detection probability, A = worst-breath OAV):
  (a) detection:   P(silent smelled) = pi_s against P(audible smelled) = pi_l;
  (b) intensity:   among pairs in which both are smelled, silent stronger / audible stronger / tie (just-noticeable
                   ratio J); because the draws are independent this is also the comparison of a smelled silent
                   passage with a smelled audible one. Also the detection-weighted median OAV of smelled passages;
  (c) combined:    the four outcomes of the headline (a passage not smelled counts as deadliness zero);
  (d) any smelled: (c) among pairs in which at least one passage is smelled;
  (e) remembered:  the bystander's remembered shares (Proposition 3), as in the headline.
Per scene (bare, 600 s, RANS mean doses) and as day averages (frequency weights, central, and equal per scene);
conditional quantities of a day average are ratios of weighted sums, not averages of ratios.
Usage (repo root): python3 uq/comparison_criteria.py -> uq/comparison_criteria.json
  (set SBD_NO_DP_CAP=1 for the stream without the driving-pressure limit; the output name gets _nocap)
"""
import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "uq"))
import four_outcomes_v4 as fv  # noqa: E402

fo, rh = fv.fo, fv.rh
KEY_CLOTH, KEY_WIN = "bare", 600


def weighted_median(a, w):
    if w.sum() <= 0:
        return None
    i = np.argsort(a)
    c = np.cumsum(w[i])
    return float(a[i][np.searchsorted(c, 0.5 * c[-1])])


def main():
    calls = []
    orig = fv.pair_terms

    def capture(a_s, p_s, a_l, p_l, J):
        calls.append((a_s, p_s, a_l, p_l))
        return orig(a_s, p_s, a_l, p_l, J)

    fv.pair_terms = capture
    try:
        out = fv.compute()
    finally:
        fv.pair_terms = orig
    nobs = len(rh.OBS)
    assert len(calls) == len(out["rows"]) * nobs
    J = rh.JND
    # per row and observer: pair terms plus detection-weighted median OAV of smelled passages
    recs = []
    for i, row in enumerate(out["rows"]):
        if row["clothing"] != KEY_CLOTH or row["window_s"] != KEY_WIN:
            continue
        for k, obs in enumerate(rh.OBS):
            a_s, p_s, a_l, p_l = calls[i * nobs + k]
            t = row["by_observer"][obs]["terms"]
            recs.append({"scene": fo.scene_of(row), "nose": row["nose"], "obs": obs, "t": t,
                         "med_s": weighted_median(a_s, p_s), "med_l": weighted_median(a_l, p_l)})

    def agg(sel, weights):
        """Weighted sums of the pair terms over scenes (rows of a scene averaged first)."""
        tot, W = {}, 0.0
        for sc, w in weights.items():
            rs_ = [r for r in sel if r["scene"] == sc]
            if not rs_ or w == 0:
                continue
            W += w
            for key in rs_[0]["t"]:
                tot[key] = tot.get(key, 0.0) + w * np.mean([r["t"][key] for r in rs_])
        t = {k: v / W for k, v in tot.items()}
        ph = fo.physics(t)
        any_ = 1 - ph["none"]
        both = t["both"]
        crit = {
            "a_detection": {"silent_smelled": t["pi_s"], "audible_smelled": t["pi_l"]},
            "b_intensity_when_both_smelled": ({"silent_stronger": t["both_s_gt"] / both,
                                               "audible_stronger": t["both_l_gt"] / both,
                                               "tie": t["both_tie"] / both, "pair_mass_both": both}
                                              if both > 0 else None),
            "c_combined": ph,
            "d_among_any_smelled": ({k: ph[k] / any_ for k in ("silent_worse", "audible_worse", "tie")}
                                    if any_ > 0 else None),
        }
        return crit

    res = {"cap": os.environ.get("SBD_NO_DP_CAP") is None, "JND": J, "by": {}}
    freq = fo.frequency_weights()["frequency, central"]
    weightings = {"sofa": {"sofa": 1}, "elevator": {"elevator": 1}, "standing": {"standing": 1},
                  "day (central weights)": freq, "equal per scene": {sc: 1.0 for sc in fo.SCENES}}
    for obs in rh.OBS:
        for group, keep in (("bystander", lambda r: r["nose"] != "culprit"), ("releaser", lambda r: r["nose"] == "culprit")):
            sel = [r for r in recs if r["obs"] == obs and keep(r)]
            for name, w in weightings.items():
                c = agg(sel, w)
                if name in fo.SCENES:
                    rs_ = [r for r in sel if r["scene"] == name]
                    c["median_OAV_when_smelled"] = {"silent": float(np.median([r["med_s"] for r in rs_ if r["med_s"] is not None])) if any(r["med_s"] is not None for r in rs_) else None,
                                                    "audible": float(np.median([r["med_l"] for r in rs_ if r["med_l"] is not None])) if any(r["med_l"] is not None for r in rs_) else None}
                if group == "bystander":
                    mem = out[f"summary_{KEY_CLOTH}_{KEY_WIN}s_bystanders"]
                    src = (mem["per_scene"].get(name) if name in fo.SCENES else
                           mem["frequency, central"] if name.startswith("day") else mem["equal per scene"])
                    c["e_remembered"] = src[obs]["memory"] if src else None
                res["by"][f"{group} | {obs[:10]} | {name}"] = c
    name = "comparison_criteria" + ("" if res["cap"] else "_nocap") + ".json"
    (ROOT / "uq" / name).write_text(json.dumps(res, indent=1))
    pct = lambda x: "  -  " if x is None else f"{100 * x:5.2f}"  # noqa: E731
    for key, c in res["by"].items():
        a, b, cc, d = (c["a_detection"], c["b_intensity_when_both_smelled"], c["c_combined"],
                       c["d_among_any_smelled"])
        e = c.get("e_remembered")
        m = c.get("median_OAV_when_smelled")
        print(f"{key:48s} (a) {pct(a['silent_smelled'])}/{pct(a['audible_smelled'])}"
              f"  (b) {pct(b and b['silent_stronger'])}/{pct(b and b['audible_stronger'])}/{pct(b and b['tie'])}"
              f"  (c) {pct(cc['silent_worse'])}/{pct(cc['audible_worse'])}"
              f"  (d) {pct(d and d['silent_worse'])}/{pct(d and d['audible_worse'])}"
              + (f"  (e) {pct(e['silent_worse'])}" if e else "")
              + (f"  medOAV {m['silent']:.3g}/{m['audible']:.3g}" if m and m['silent'] is not None and m['audible'] is not None else ""))
    print("wrote", name)


if __name__ == "__main__":
    main()
