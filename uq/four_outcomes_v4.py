"""Four outcomes, physics and memory on one population, from the PLAN v4 CFD (A2 of manuscript/preprint/
interface_plan.md section 9). Same passages, observers, pair algebra and aggregation as uq/four_outcomes.py; only the
route changes:
  * old: one 92 mL CFD release per class and scene (30-60 s), OAV = m x (V / V0) x OAV_CFD(scene, nose, class);
  * v4: the four representative releases per scene (A90, A50, S90, S50 on scalars s1..s4, cfd/results_v4/<case>.json)
    give the response per released volume at each class's momentum levels; a passage of volume V and exit momentum
    flux M0 = Q u0 gets OAV = m x nose_oav(result, nose, window, V, M0, class) (cfd/postprocess/analyze_multi.py:
    log-interpolated in M0 between the class's levels, held outside them; [APPROXIMATION] the route depends on M0 but
    not on V).
Windows: 150 s from the run, 300 and 600 s from the well-mixed tail (validated on the 10-minute reference runs).
Scenes: sofa (three postures) and standing pair (still air, ventilated), bare; clothed variants are reported
separately as they arrive (standing, still air, trousers so far). The elevator waits for its v4 run; scene weights are
renormalised over the scenes present. RANS mean doses: the LES peak factor is not applied yet.
Usage (repo root): python3 uq/four_outcomes_v4.py -> uq/four_outcomes_v4.json
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "uq"))
import four_outcomes as fo  # noqa: E402
from four_outcomes import OUTCOMES, aggregate, frequency_weights, memory_mass, pair_terms, physics, rh, rs  # noqa: E402
from observer_ps import detect, observers  # noqa: E402

_spec = importlib.util.spec_from_file_location("analyze_multi", ROOT / "cfd/postprocess/analyze_multi.py")
am = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(am)

RES = ROOT / "cfd/results_v4"
WINDOWS = (150, 600)
# v4 case -> (scene name as in four_outcomes.nose_distances, set); roles: releaser = culprit, neighbour = bystander
CASES = {
    "sofa_v4_multi": ("sofa, upright", "bare"),
    "sofa_rec4.5_v4_multi": ("sofa, reclined 4.5 deg", "bare"),
    "sofa_rec-10_v4_multi": ("sofa, leaning forward 10 deg", "bare"),
    "stand_still_v4_multi": ("standing pair, still air", "bare"),
    "stand_vent_v4_multi": ("standing pair, office ventilation", "bare"),
    "sofa_tr_v4_multi": ("sofa, upright", "trousers"),
    "stand_still_tr_v4_multi": ("standing pair, still air", "trousers"),
    "stand_vent_tr_v4_multi": ("standing pair, office ventilation", "trousers"),
}
ROLE = {"releaser": "culprit", "neighbour": None}
CLOTHED_SHARES = (0.7, 0.85)  # share of passages in long trousers; 1.0 is the trousers set
MIX_SEED = 20261029  # bystander role name from nose_distances (beside / facing)


def passages(n=rs.N_EVENTS):
    """The Theorem 3 passage stream with hearing at every nose distance (reusable across compute() calls)."""
    return rs.simulate(n=n, distances=sorted(set(fo.nose_distances().values())))


def compute(n=rs.N_EVENTS, sim=None, detectors=None, gain=(1.0, 1.0)):
    """All rows and summaries for n passages (dict as written to uq/four_outcomes_v4.json).
    Robustness hooks (defaults reproduce the headline): sim, a passages() result to reuse; detectors, observer name
    (rh.OBS) -> function OAV -> detection probability, replacing observer_ps; gain, (silent, audible) multipliers on the
    OAV of physically silent / audible passages (e.g. a peak factor)."""
    dists = fo.nose_distances()
    sim = passages(n) if sim is None else sim
    J = rh.JND
    V, M0, osc = sim["V"], sim["Q"] * sim["u0"], sim["osc"].astype(bool)
    obs = observers()
    if detectors is None:
        detectors = {name: (lambda A, s=obs[name][0], sd=obs[name][1]: detect(s * A, sd)) for name in rh.OBS}
    out = {"n_events": int(V.size), "JND": J, "observers": list(rh.OBS), "windows": WINDOWS, "rows": []}
    def add_rows(case, scene, cloth, oav_of):
        """Rows of one scene variant; oav_of(nose, win) -> OAV of every passage at that nose."""
        for nose in ("releaser", "neighbour"):
            role = "culprit" if nose == "releaser" else ("beside" if scene.startswith("sofa") else "facing")
            r = dists[scene, role]
            audible = osc if role == "culprit" else sim[f"heard_living@{r:.3f}"].astype(bool)
            for win in WINDOWS:
                A = sim["sulfur"] * oav_of(nose, win) * np.where(osc, gain[1], gain[0])
                row = {"case": case, "scene": scene, "clothing": cloth, "nose": role, "window_s": win, "distance_m": r,
                       "frac_audible": float(audible.mean()), "median_OAV_silent": float(np.median(A[~osc])),
                       "median_OAV_audible": float(np.median(A[osc])), "by_observer": {}}
                for name in rh.OBS:
                    p = detectors[name](A)
                    t = pair_terms(A[~audible], p[~audible], A[audible], p[audible], J)
                    mm = memory_mass(t, role)
                    row["by_observer"][name] = {"terms": t, "physics": physics(t),
                                                "memory": ({k: mm[k] / mm["_total"] for k in OUTCOMES}
                                                           if mm["_total"] > 0 else None),  # nothing smelled
                                                "memory_mass": mm}
                out["rows"].append(row)

    route = lambda res: (lambda nose, win: np.where(osc, am.nose_oav(res, nose, win, V, M0, "audible"),  # noqa: E731
                                                    am.nose_oav(res, nose, win, V, M0, "silent")))
    results = {case: json.loads((RES / f"{case}.json").read_text()) for case in CASES if (RES / f"{case}.json").exists()}
    for case, res in results.items():
        add_rows(case, *CASES[case], route(res))
    # clothed share: each passage is clothed with probability q, independently (user's choice 29 Oct: per passage),
    # so a silent and an audible passage of a pair may differ; variants with a trousers twin only
    clothed_draw = np.random.default_rng(MIX_SEED).random(V.size)
    for case, (scene, cloth) in CASES.items():
        twin = next((c for c, (sc, cl) in CASES.items() if sc == scene and cl == "trousers"), None)
        if cloth != "bare" or case not in results or twin not in results:
            continue
        bare, tro = route(results[case]), route(results[twin])
        for q in CLOTHED_SHARES:
            add_rows(case, scene, f"mixed {q:.2f}",
                     lambda nose, win, q=q: np.where(clothed_draw < q, tro(nose, win), bare(nose, win)))
    weights = {"equal per scene": {k: 1.0 for k in fo.SCENES}, **frequency_weights()}
    for cloth in ("bare", "trousers", *(f"mixed {q:.2f}" for q in CLOTHED_SHARES)):
        for win in WINDOWS:
            for grp, keep in (("bystanders", lambda s: s["nose"] != "culprit"), ("culprit", lambda s: s["nose"] == "culprit")):
                rows = [s for s in out["rows"] if keep(s) and s["clothing"] == cloth and s["window_s"] == win]
                if rows:
                    out[f"summary_{cloth.replace(' ', '')}_{win}s_{grp}"] = {
                        "n": len(rows), "scenes": sorted({s["scene"] for s in rows}),
                        "per_scene": {sc: aggregate([s for s in rows if fo.scene_of(s) == sc], None)
                                      for sc in fo.SCENES if any(fo.scene_of(s) == sc for s in rows)},
                        **{tag: aggregate(rows, w) for tag, w in weights.items()}}
    out["frac_silent"] = float(1.0 - osc.mean())
    return out


def main():
    out = compute()
    (ROOT / "uq/four_outcomes_v4.json").write_text(json.dumps(out, indent=1))
    pct = lambda d: " / ".join(f"{100 * d[k]:5.1f}" for k in OUTCOMES)
    print("none / silent worse / audible worse / tie (%): physics | memory")
    for key in [k for k in out if k.startswith("summary_")]:
        s = out[key]
        for tag in ("equal per scene", "frequency, central"):
            for name in rh.OBS:
                x = s[tag][name]
                mem = pct(x["memory"]) if x["memory"] else " (nothing remembered)"
                print(f"{key[8:]:26s} {tag:18s} {name[:10]:10s} {pct(x['physics'])} | {mem}  pi_s {x['pi_s']:.3f} pi_l {x['pi_l']:.3f}")


if __name__ == "__main__":
    main()
