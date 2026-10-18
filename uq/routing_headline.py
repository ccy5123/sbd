"""Routing-aware headline: how often is a silent passage, as actually emitted, stronger at a nose, scene by scene?

Gate 0 (M7) gives the as-emitted ratio without routing (median 0.92 at the neighbour, P(R > 1) = 0.47). The CFD shows
that routing (what stands behind the releaser, ventilation) changes the equal-mass ratio by more than an order of
magnitude, so the Gate 0 number is replaced here by one number per CFD scene and nose.

Method. Each CFD scene gives the expected worst-breath OAV at each nose for the same 92 mL released silently and
audibly (equal mass). The odorant is a passive scalar and OAV is linear in concentration, so a release of volume V
gives OAV x V / 92 mL along the same route. Each Gate 0 Monte Carlo draw supplies one silent and one audible release
as emitted (volumes V_s, V_l, classed by the acoustic onset of M2):
    OAV_s = OAV_s,CFD x V_s / V0,   OAV_l = OAV_l,CFD x V_l / V0,   R = OAV_s / OAV_l.
In Gate 0 itself this factorisation is exact: R_as-emitted = R_equal-mass x V_s / V_l for every draw.
[APPROXIMATION] The route is taken as independent of the volume: a larger or smaller release keeps the CFD route.
For silent releases (momentum negligible against the body plume) this is close; for audible ones the jet length
grows with volume, so the audible routes are fixed at the median release.

Reported per scene and nose: P(R > 1); the perceptual split at the olfactory JND (as in M7); and the probability that
the passage is noticed at all by an attentive and a distracted observer (uq/observer_ps.py), silent and audible.
If both releases give zero at a nose (nothing arrives within the window), R is set to 1 (indistinguishable).
Usage (repo root): python3 uq/routing_headline.py -> uq/routing_headline.json
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gate0"))
sys.path.insert(0, str(ROOT / "uq"))
import run_gate0 as g0
from observer_ps import detect, observers

V0 = 9.2e-5
JND = 1.0 + g0.P0["weber_C"]
OBS = ("attentive, Amoore thresholds", "distracted (everyday)")


def scenes():
    """(scene, nose role, window s, OAV silent, OAV audible) at equal mass, from the CFD result files."""
    out = []
    wb = "worst_breath_OAV_mean"
    sofa_files = (("sofa, upright", "results_W30s.json"), ("sofa, reclined 4.5 deg", "results_rec4.5.json"),
                  ("sofa, leaning forward 10 deg", "results_rec-10.json"),
                  ("sofa, upright (120 s)", "results.json"))
    for name, f in sofa_files:
        d = json.loads((ROOT / "cfd/cases/sofa" / f).read_text())
        win = d.get("window_s", 30.0)
        for nose, role in (("own nose (releaser)", "culprit"), ("neighbour's nose", "beside")):
            out.append((name, role, win, d["silent"][nose][wb], d["audible"][nose][wb]))
    e = json.loads((ROOT / "cfd/cases/elevator/results.json").read_text())["branches"]
    roles = {"FL": {"FL": "culprit", "FR": "beside", "BL": "behind", "BR": "diagonal behind"},
             "BL": {"BL": "culprit", "BR": "beside", "FL": "in front", "FR": "diagonal in front"}}
    for c, label in (("FL", "elevator, front row (person behind)"), ("BL", "elevator, back row (wall behind)")):
        for n, role in roles[c].items():
            out.append((label, role, 60.0, e[f"{c}_silent"][n][wb], e[f"{c}_audible"][n][wb]))
    sp = ROOT / "cfd/cases/standing/results.json"
    if sp.exists():
        s = json.loads(sp.read_text())["branches"]
        for v, label in (("still", "standing pair, still air"), ("vent", "standing pair, office ventilation")):
            if f"{v}_silent" in s and f"{v}_audible" in s:
                for n, role in (("C", "culprit"), ("N", "facing")):
                    out.append((label, role, 60.0, s[f"{v}_silent"][n][wb], s[f"{v}_audible"][n][wb]))
    return out


def evaluate(o_s, o_l, vs, vl, obs):
    a_s, a_l = o_s * vs / V0, o_l * vl / V0
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where((a_s == 0) & (a_l == 0), 1.0, a_s / np.maximum(a_l, 1e-300))
    lr, j = np.log10(np.maximum(r, 1e-300)), np.log10(JND)
    res = {"OAV_equal_mass": [o_s, o_l], "R_equal_mass": (o_s / o_l if o_l > 0 else None),
           "P_R_gt_1": float(np.mean(r > 1.0)), "median_R": float(np.median(r)),
           "P_silent_perceptibly_worse": float(np.mean(lr > j)),
           "P_indistinguishable": float(np.mean(np.abs(lr) <= j)),
           "P_audible_perceptibly_worse": float(np.mean(lr < -j)), "noticed": {}}
    res["given_noticed"] = {}
    for name in OBS:
        scale, sd = obs[name][0], obs[name][1]
        p_s, p_l = detect(scale * a_s, sd), detect(scale * a_l, sd)
        res["noticed"][name] = {"silent": float(np.mean(p_s)), "audible": float(np.mean(p_l))}
        w = 1.0 - (1.0 - p_s) * (1.0 - p_l)      # probability that at least one of the pair is noticed
        res["given_noticed"][name] = {"P_any_noticed": float(np.mean(w)),
                                      "w_sum": float(np.sum(w)), "w_silent_stronger": float(np.sum(w * (r > 1.0))),
                                      "P_R_gt_1": (float(np.sum(w * (r > 1.0)) / np.sum(w)) if np.sum(w) > 0 else None)}
    return res


def main():
    mc = g0.monte_carlo()
    vs, vl = mc["V_s"], mc["V_l"]
    obs = observers()
    out = {"n_mc": int(vs.size), "JND_conc_ratio": JND, "volume_ratio_median": float(np.median(vs / vl)),
           "gate0_neighbour_P_R_gt_1": float(np.mean(mc["R_nb_conc_phi_inh_none"] > 1.0)), "scenes": []}
    print(f"volume ratio V_s/V_l median {np.median(vs / vl):.2f};  Gate 0 neighbour P(R>1) "
          f"{out['gate0_neighbour_P_R_gt_1']:.2f}")
    for scene, role, win, o_s, o_l in scenes():
        r = evaluate(o_s, o_l, vs, vl, obs)
        r.update({"scene": scene, "nose": role, "window_s": win})
        out["scenes"].append(r)
        att = r["noticed"][OBS[0]]
        print(f"{scene:38s} {role:18s} R_eq {r['R_equal_mass'] if r['R_equal_mass'] is None else round(r['R_equal_mass'], 3)!s:>7}"
              f"  P(R>1) {r['P_R_gt_1']:.2f}  silent worse {r['P_silent_perceptibly_worse']:.2f}"
              f"  audible worse {r['P_audible_perceptibly_worse']:.2f}"
              f"  noticed (attentive) s {att['silent']:.2f} a {att['audible']:.2f}"
              f"  | given noticed {r['given_noticed'][OBS[0]]['P_R_gt_1'] if r['given_noticed'][OBS[0]]['P_R_gt_1'] is None else round(r['given_noticed'][OBS[0]]['P_R_gt_1'], 2)}"
              f" (P any {r['given_noticed'][OBS[0]]['P_any_noticed']:.3f})")
    by = [s for s in out["scenes"] if s["nose"] != "culprit" and "120 s" not in s["scene"]]
    own = [s for s in out["scenes"] if s["nose"] == "culprit" and "120 s" not in s["scene"]]
    for tag, grp in (("bystanders", by), ("culprit", own)):
        p = [s["P_R_gt_1"] for s in grp]
        summ = {"n": len(grp), "P_R_gt_1_range": [min(p), max(p)], "P_R_gt_1_equal_weight": float(np.mean(p))}
        print(f"{tag}: P(R>1) range {min(p):.2f}-{max(p):.2f}, equal-weight mean {np.mean(p):.2f} (n = {len(grp)})")
        for name in OBS:
            g = [s["given_noticed"][name] for s in grp]
            pooled = sum(x["w_silent_stronger"] for x in g) / sum(x["w_sum"] for x in g)
            summ[f"P_R_gt_1_given_noticed | {name}"] = pooled
            summ[f"P_any_noticed_mean | {name}"] = float(np.mean([x["P_any_noticed"] for x in g]))
            print(f"   {name}: P(silent stronger | at least one noticed), pooled over noses {pooled:.2f}; "
                  f"mean P(any noticed) {summ[f'P_any_noticed_mean | {name}']:.3f}")
        out[f"summary_{tag}"] = summ
    (ROOT / "uq/routing_headline.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
