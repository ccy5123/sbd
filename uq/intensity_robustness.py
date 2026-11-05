"""Robustness of criterion (b), intensity when smelled, under every robustness variation of the ESM.

Criterion (b) (uq/comparison_criteria.py): among pairs of one silent and one audible passage in which both are
smelled, the shares silent stronger (A_s > J A_a), audible stronger (A_a > J A_s) and tie, i.e. both_s_gt / both,
both_l_gt / both and both_tie / both of four_outcomes.pair_terms. For several scenes the shares are ratios of weighted
sums (scene weight x mean term over the scene's rows), not averages of ratios, so a scene enters a day average in
proportion to its weight times its both-smelled pair mass; that mass ('pair_mass_both', the probability that a random
silent-audible pair is smelled twice) and each scene's share of it ('both_mass_share_by_scene') are reported with
every result, and per scene the Kish effective number of passages behind it (weights p, silent and audible passages
separately; row values averaged with weights = the row's both-smelled mass), to show how few passages carry it.
Weightings: sofa, lift (elevator), standing, day averages with the central, home-centred and office-centred frequency
weights, and equal weight per scene. Bystanders (the neighbour's nose; every non-releaser nose of the lift) and the
releaser; both observers (attentive, Amoore thresholds; distracted); bare, 600 s unless stated.
Variants (each one factor or one documented combination; everything else as the headline):
  * gains (four_outcomes_v4.compute gain hook, (silent, audible) multipliers on the OAV): mesh 3.0 on silent doses, LES
    class peak factors (median 2.2 / 1.3, adverse pairing 6.6 / 0.27) and their products, as in uq/combined_adverse.py;
    release order: S50 released alone gives 2.4x the neighbour dose it gets released fourth in the four-release sofa
    run (ESM validation, mesh bullet: 0.17 against 0.071), applied as a silent-only gain of 2.4, alone and with the
    LES median factors (and mesh);
  * dose interpolation (analyze_multi.INTERP): log-linear (headline), nearest, lower, and the adverse bracket of
    uq/interp_perception_sensitivity.py (silent passages the larger, audible ones the smaller neighbouring level);
  * just-noticeable ratio J (routing_headline.JND) 1.15, 1.28 (headline), 1.45; ties are part of (b);
  * psychometric tail: the detection-law variants of uq/tail_sensitivity.py;
  * driving-pressure cap (uq/pressure_cap.py): none, and 72, 88 (headline), 108, 171 mmHg, by clipping (the source
    model) and by truncation of the uncapped stream;
  * clothing: per-passage clothed shares 0.70 and 0.85, and all trousers. Only sofa upright and the standing pair
    (still air, ventilated) have trousers runs, so these aggregates contain the sofa (upright only) and standing
    scenes and no lift; 'bare, same scenes' is the like-for-like bare comparison (the same three cases, bare).
The default run is checked against uq/comparison_criteria.json (every (b) entry there, to 1e-12) and against the
rounded headline numbers. No module default is changed (every switch is restored in a finally block).
Usage (repo root): python3 uq/intensity_robustness.py -> uq/intensity_robustness.json
"""
import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "uq"))
import four_outcomes_v4 as fv  # noqa: E402

fo, rh, am = fv.fo, fv.rh, fv.am
ATT, DIS = rh.OBS
GROUPS = {"bystander": lambda r: r["nose"] != "culprit", "releaser": lambda r: r["nose"] == "culprit"}
SAME_SCENE_CASES = ("sofa_v4_multi", "stand_still_v4_multi", "stand_vent_v4_multi")  # bare cases with a trousers twin
B_KEYS = ("both", "both_s_gt", "both_l_gt", "both_tie")


def weightings():
    f = fo.frequency_weights()
    return {"sofa": {"sofa": 1.0}, "lift": {"elevator": 1.0}, "standing": {"standing": 1.0},
            "day, central": f["frequency, central"], "day, home": f["frequency, home"],
            "day, office": f["frequency, office"], "equal per scene": {sc: 1.0 for sc in fo.SCENES}}


def criterion_b(out, group, obs, weights, cloth="bare", win=600, cases=None):
    """(b) shares, both-smelled pair mass and each scene's share of it, for one group, observer and weighting."""
    rows = [r for r in out["rows"] if GROUPS[group](r) and r["clothing"] == cloth and r["window_s"] == win
            and (cases is None or r["case"] in cases) and r["by_observer"][obs]["terms"] is not None]
    tot, W, contrib, ess = dict.fromkeys(B_KEYS, 0.0), 0.0, {}, {}
    for sc, w in weights.items():
        g = [r for r in rows if fo.scene_of(r) == sc]
        if not g or w == 0:
            continue
        W += w
        m = {k: float(np.mean([r["by_observer"][obs]["terms"][k] for r in g])) for k in B_KEYS}
        for k in B_KEYS:
            tot[k] += w * m[k]
        contrib[sc] = w * m["both"]
        if "ess" in g[0]["by_observer"][obs]:
            b = np.array([r["by_observer"][obs]["terms"]["both"] for r in g])
            e = np.array([r["by_observer"][obs]["ess"] for r in g])
            ess[sc] = (dict(zip(("silent", "audible"), (b @ e / b.sum()).tolist())) if b.sum() > 0 else None)
    if W == 0 or tot["both"] <= 0:
        return None
    return {"silent_stronger": tot["both_s_gt"] / tot["both"], "audible_stronger": tot["both_l_gt"] / tot["both"],
            "tie": tot["both_tie"] / tot["both"], "pair_mass_both": tot["both"] / W,
            "both_mass_share_by_scene": {sc: c / tot["both"] for sc, c in contrib.items()},
            **({"kish_effective_passages": ess[next(iter(ess))]} if len(contrib) == 1 and ess else {})}


def summarise(out, cloth="bare", win=600, cases=None):
    return {grp: {obs: {name: criterion_b(out, grp, obs, w, cloth, win, cases) for name, w in weightings().items()}
                  for obs in rh.OBS} for grp in GROUPS}


def _kish(p):
    s2 = float(np.sum(p * p))
    return float(np.sum(p)) ** 2 / s2 if s2 > 0 else 0.0


@contextmanager
def switches(interp=None, jnd=None):
    """Temporarily set the interpolation rule and the just-noticeable ratio (restored afterwards)."""
    old = am.INTERP, rh.JND, am.nose_oav
    try:
        if interp == "adverse bracket":
            f, pick = am.nose_oav, {"silent": np.maximum, "audible": np.minimum}
            am.nose_oav = lambda res, nose, win, V, M0, cls: pick[cls](f(res, nose, win, V, M0, cls, rule="lower"),
                                                                       f(res, nose, win, V, M0, cls, rule="upper"))
        elif interp is not None:
            am.INTERP = interp
        if jnd is not None:
            rh.JND = jnd
        yield
    finally:
        am.INTERP, rh.JND, am.nose_oav = old


def run(sim, interp=None, jnd=None, **kw):
    """four_outcomes_v4.compute with the Kish effective numbers of every pair_terms call attached to its row."""
    calls, orig = [], fv.pair_terms

    def capture(a_s, p_s, a_l, p_l, J):
        calls.append((_kish(p_s), _kish(p_l)))
        return orig(a_s, p_s, a_l, p_l, J)

    fv.pair_terms = capture
    try:
        with switches(interp, jnd):
            out = fv.compute(sim=sim, **kw)
    finally:
        fv.pair_terms = orig
    assert len(calls) == len(out["rows"]) * len(rh.OBS)
    for i, row in enumerate(out["rows"]):
        for k, obs in enumerate(rh.OBS):
            row["by_observer"][obs]["ess"] = calls[i * len(rh.OBS) + k]
    return out


def check_headline(s):
    """The default run against uq/comparison_criteria.json and the rounded headline numbers (attentive, %)."""
    ref = json.loads((ROOT / "uq/comparison_criteria.json").read_text())
    assert ref["cap"] and os.environ.get("SBD_NO_DP_CAP") is None, "headline check needs the capped stream"
    names = {"sofa": "sofa", "elevator": "lift", "standing": "standing", "day (central weights)": "day, central",
             "equal per scene": "equal per scene"}
    dev, n = 0.0, 0
    for key, c in ref["by"].items():
        grp, obs10, wname = (x.strip() for x in key.split("|"))
        obs = next(o for o in rh.OBS if o[:10] == obs10)
        mine, theirs = s[grp][obs][names[wname]], c["b_intensity_when_both_smelled"]
        for a, b in (("silent_stronger", "silent_stronger"), ("audible_stronger", "audible_stronger"), ("tie", "tie"),
                     ("pair_mass_both", "pair_mass_both")):
            dev, n = max(dev, abs(mine[a] - theirs[b])), n + 1
    rounded = {("bystander", "sofa"): (29.5, 58.9, 11.6), ("bystander", "lift"): (53.7, 34.6, 11.8),
               ("bystander", "day, central"): (47.7, 40.6, 11.8), ("bystander", "equal per scene"): (53.6, 34.6, 11.8),
               ("releaser", "day, central"): (43.8, 45.3, 10.9)}
    for (grp, w), v in rounded.items():
        x = s[grp][ATT][w]
        got = tuple(100 * x[k] for k in ("silent_stronger", "audible_stronger", "tie"))
        assert all(abs(a - b) <= 0.06 for a, b in zip(got, v)), (grp, w, got, v)  # lift silent is 53.645
    x = s["bystander"][ATT]["standing"]
    assert (round(100 * x["silent_stronger"]), round(100 * x["audible_stronger"]), round(100 * x["tie"])) == (73, 14, 12)
    print(f"headline (b) vs uq/comparison_criteria.json: {n} values, max |difference| {dev:.1e}")
    if dev > 1e-12:
        raise SystemExit("headline (b) differs from uq/comparison_criteria.json")
    return dev


def line(name, s):
    def f(x):
        return "      -        " if x is None else (f"{100 * x['silent_stronger']:4.1f}/{100 * x['audible_stronger']:4.1f}/"
                                                    f"{100 * x['tie']:4.1f} {x['pair_mass_both']:.1e}")
    b, d = s["bystander"][ATT], s["bystander"][DIS]
    print(f"{name[:40]:40s} " + " | ".join(f(b[w]) for w in ("sofa", "lift", "day, central", "day, home", "day, office",
                                                              "equal per scene"))
          + f" || dis day {f(d['day, central'])} || rel day {f(s['releaser'][ATT]['day, central'])}")


def directions(s, grp="bystander", obs=ATT):
    """+1 silent stronger, -1 audible stronger, 0 equal (or no both-smelled mass) per weighting."""
    return {w: (0 if x is None else int(np.sign(x["silent_stronger"] - x["audible_stronger"])))
            for w, x in s[grp][obs].items()}


def main():
    import combined_adverse as ca
    import pressure_cap as pc
    import tail_sensitivity as ts
    g0 = fv.rs.g0
    sim = fv.passages()
    res = {"criterion": "(b) intensity when both are smelled: silent stronger / audible stronger / tie (JND)",
           "observers": list(rh.OBS), "JND_headline": rh.JND, "window_s": 600, "n_events": int(sim["V"].size),
           "weightings": weightings(), "families": {}}
    fam = res["families"]

    def add(family, name, s, **extra):
        fam.setdefault(family, {})[name] = {**extra, "directions_attentive_bystander": directions(s), "b": s}
        line(f"{family[:7]}: {name}", s)

    print("attentive bystander: silent/audible/tie (%) both-smelled mass  [sofa | lift | day central | day home | "
          "day office | equal]  || distracted day || releaser day")
    base_out = run(sim)
    base = summarise(base_out)
    res["headline_max_abs_deviation_from_comparison_criteria_json"] = check_headline(base)
    add("headline", "headline (capped 88 mmHg, log-linear, J 1.28, RANS mean, bare)", base)
    # gains: combined_adverse factors, release order
    order = 2.4
    gains = {**{k: v for k, v in ca.GAINS.items() if k != "RANS mean"},
             "release order (S50 alone, silent x2.4)": (order, 1.0),
             "release order x LES median": (order * ca.LES[0], ca.LES[1]),
             "release order x mesh x LES median": (order * ca.MESH * ca.LES[0], ca.LES[1])}
    for name, gain in gains.items():
        add("gains", name, summarise(run(sim, gain=gain)), gain_silent_audible=list(gain))
    for rule in ("nearest", "lower", "adverse bracket"):
        add("interpolation", rule, summarise(run(sim, interp=rule)))
    for j in (1.15, 1.45):
        add("JND", f"J {j:.2f}", summarise(run(sim, jnd=j)), JND=j)
    for name, (att, dis) in ts.VARIANTS.items():
        if name.startswith("baseline"):
            continue
        add("tail", name, summarise(run(sim, detectors={ATT: att, DIS: dis})))
    # driving-pressure cap: uncapped stream, clipping at other caps, truncation of the uncapped stream
    free = pc.stream(None)
    add("pressure cap", "none (uncapped)", summarise(run(free)))
    for name, mmhg in pc.CAPS.items():
        cap = mmhg * pc.MMHG
        if abs(cap - g0.P0["dp_max"]) > 1.0:
            add("pressure cap", f"clip {name}", summarise(run(pc.stream(cap))))
        keep = free["dp"] <= cap
        add("pressure cap", f"truncate {name}", summarise(run({k: v[keep] for k, v in free.items()})),
            share_discarded=float(1 - keep.mean()))
    # clothing: from the headline run (no recompute); scenes sofa upright and standing only
    add("clothing", "bare, same scenes (sofa upright, standing still / ventilated)",
        summarise(base_out, cases=SAME_SCENE_CASES), scenes="sofa upright; standing still air and ventilated")
    for cloth in ("mixed 0.70", "mixed 0.85", "trousers"):
        add("clothing", cloth, summarise(base_out, cloth=cloth), scenes="sofa upright; standing still air and ventilated")
    (ROOT / "uq/intensity_robustness.json").write_text(json.dumps(res, indent=1))
    print("wrote uq/intensity_robustness.json")


if __name__ == "__main__":
    main()
