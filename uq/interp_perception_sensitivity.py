"""Sensitivity of the headline to the dose interpolation rule and to the perception inputs (JRSI pre-submission
review, 5 Nov 2026).

1. Interpolation rule (cfd/postprocess/analyze_multi.nose_oav, module switch INTERP). A passage's dose per released
   volume comes from its class's two representative releases (silent S50/S90, audible A50/A90):
     * log-linear: interpolated linearly in log M0 between the levels (log of the dose), held outside (headline);
     * nearest: the dose of the level nearest in log M0 (a step at the geometric mean of the two M0);
     * lower: the dose of the level at or below the passage's M0 (the lower neighbour; above the top level, the top
       level, as in the headline). If the dose per volume rises with M0 this lowers every passage between the levels,
       the adverse direction for audible passages (and the favourable one for silent ones);
     * adverse bracket (not a rule of its own): between the levels, each silent passage takes the larger and each
       audible passage the smaller of its two neighbouring levels' doses, at every nose, whichever way the dose runs
       with M0 there (analyze_multi rules "upper" and "lower").
2. Perception inputs. The just-noticeable concentration ratio J = 1 + Weber fraction (routing_headline.JND, 1.28 from
   weber_C 0.28) is set to 1.15 and 1.45. The Stevens exponent n_stevens (0.28, range 0.20-0.45) does not enter the
   four outcomes: detection is Phi(log2(s x OAV) / sd) and the pair comparison is A_i > J A_j on the OAV (a
   concentration ratio, as the Weber fraction weber_C is dC/C), and intensity = OAV^n is monotone in OAV, so the
   order and the JND test are the same for every n > 0. It is therefore not varied.
Headline key as in uq/combined_adverse.py: bystanders, bare, 600 s, RANS mean doses (gain 1, 1). The default run is
checked against uq/four_outcomes_v4.json (every scene and weighting, both observers, to 1e-12; the file was
written on another machine and differs in the last bit of a double). The doses per volume of the levels and the share
of each class's passages below, between and above its levels' M0 are written under 'levels'.
Usage (repo root): python3 uq/interp_perception_sensitivity.py -> uq/interp_perception_sensitivity.json
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "uq"))
import four_outcomes_v4 as fv  # noqa: E402

KEY = "summary_bare_600s_bystanders"
TAGS = ("frequency, central", "frequency, home", "frequency, office", "equal per scene")
RULES = ("log-linear", "nearest", "lower", "adverse bracket")
WEBER = (0.15, 0.28, 0.45)


def summary(s):
    """Physics (and memory) shares of the headline key, every scene and weighting, both observers."""
    return {"per_scene": {sc: {o: x[o]["physics"] for o in fv.rh.OBS} for sc, x in s["per_scene"].items()},
            **{t: {o: {"physics": s[t][o]["physics"], "memory": s[t][o]["memory"]} for o in fv.rh.OBS} for t in TAGS}}


def run(sim, rule="log-linear", jnd=None):
    am, rh = fv.am, fv.rh
    old = am.INTERP, rh.JND, am.nose_oav
    try:
        if rule == "adverse bracket":
            f = am.nose_oav
            pick = {"silent": np.maximum, "audible": np.minimum}
            am.nose_oav = lambda res, nose, win, V, M0, cls: pick[cls](f(res, nose, win, V, M0, cls, rule="lower"),
                                                                       f(res, nose, win, V, M0, cls, rule="upper"))
        else:
            am.INTERP = rule
        if jnd is not None:
            rh.JND = jnd
        return fv.compute(sim=sim)[KEY]
    finally:
        am.INTERP, rh.JND, am.nose_oav = old


def levels(sim):
    """Per bare v4 case: the class levels (M0, dose per volume at each bystander nose, 600 s) and the share of the
    class's passages below, between and above the levels' M0."""
    V, M0, osc = sim["V"], sim["Q"] * sim["u0"], sim["osc"].astype(bool)
    out = {}
    for case, (scene, cloth) in fv.CASES.items():
        f = fv.RES / f"{case}.json"
        if cloth != "bare" or not f.exists():
            continue
        res = json.loads(f.read_text())
        noses = (fv.ELEVATOR_NOSES if scene.startswith("elevator") else fv.ROLE).keys()
        out[case] = {}
        for cls, mask in (("silent", ~osc), ("audible", osc)):
            rel = {k: r for k, r in res["releases"].items() if r["class"] == cls}
            m = sorted(r["M0"] for r in rel.values())
            x = M0[mask]
            out[case][cls] = {
                "levels": {k: {"M0": r["M0"], "dose_per_V_600s": {n: r[n]["by_window"]["600"]["worst_breath_OAV_mean"] / r["V"]
                                                                   for n in noses if "600" in r[n]["by_window"]}}
                           for k, r in rel.items()},
                "M0_ratio_top_bottom": m[-1] / m[0],
                "share_below": float(np.mean(x < m[0])), "share_between": float(np.mean((x >= m[0]) & (x <= m[-1]))),
                "share_above": float(np.mean(x > m[-1]))}
    return out


def line(name, s):
    o = fv.rh.OBS[0]
    ps = s["per_scene"]
    f = lambda d: f"{100 * d['silent_worse']:6.2f} / {100 * d['audible_worse']:6.2f}"  # noqa: E731
    dc, eq = s["frequency, central"][o], s["equal per scene"][o]
    mem = dc["memory"]["silent_worse"] if dc["memory"] else float("nan")
    print(f"{name:22s} sofa {f(ps['sofa'][o])} | lift {f(ps['elevator'][o])} | standing {f(ps['standing'][o])} | "
          f"day {f(dc['physics'])} (memory silent worse {100 * mem:5.1f}) | equal {f(eq['physics'])}")


def main():
    sim = fv.passages()
    out = {"headline": KEY, "observer_reported": fv.rh.OBS[0], "JND_headline": fv.rh.JND,
           "n_stevens_enters": False, "levels": levels(sim), "interpolation": {}, "weber": {}}
    # default run against the headline file
    ref = json.loads((ROOT / "uq/four_outcomes_v4.json").read_text())[KEY]
    base = run(sim)
    # (the file was written on another machine: shares agree to the last bit or two of a double, from summation order)
    pairs = [(base["per_scene"][sc][o]["physics"][k], ref["per_scene"][sc][o]["physics"][k]) for sc in ref["per_scene"]
             for o in fv.rh.OBS for k in fv.OUTCOMES]
    pairs += [(base[t][o][part][k], ref[t][o][part][k]) for t in TAGS for o in fv.rh.OBS for part in ("physics", "memory")
              if ref[t][o][part] for k in fv.OUTCOMES]
    dev = max(abs(a - b) for a, b in pairs)
    out["default_max_abs_deviation_from_four_outcomes_v4_json"] = dev
    print(f"default run vs uq/four_outcomes_v4.json: {len(pairs)} shares, max |difference| {dev:.1e}")
    if dev > 1e-12:
        raise SystemExit("default run differs from uq/four_outcomes_v4.json")
    print("attentive bystander, bare, 600 s: silent worse / audible worse (%)")
    for rule in RULES:
        s = base if rule == "log-linear" else run(sim, rule=rule)
        out["interpolation"][rule] = summary(s)
        line(f"interp {rule}", out["interpolation"][rule])
    for w in WEBER:
        s = base if w == 0.28 else run(sim, jnd=1.0 + w)
        out["weber"][f"{w:g}"] = {"JND": 1.0 + w, **summary(s)}
        line(f"Weber {w:g} (J {1 + w:.2f})", out["weber"][f"{w:g}"])
    (ROOT / "uq/interp_perception_sensitivity.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
