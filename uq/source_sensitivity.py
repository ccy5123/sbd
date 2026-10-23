"""Sensitivity of the silent share and of the headline to the source and acoustic assumptions (A4 of
manuscript/preprint/interface_plan.md section 9). Neither the release duration T nor the effective orifice diameter d
has been measured for a passage (log-uniform priors, params.yaml T_release, d_orifice), and the oscillation onset
pressure P_th is bracketed by brass lips and oesophageal speech, not anal tissue. Each variant changes one of them and
reruns (i) the analytic Monte Carlo (gate0/run_gate0.monte_carlo: silent/audible pairs, R at the neighbour, inhaled,
no clothing) and (ii) the v4 four-outcome headline (uq/four_outcomes_v4.compute: share of passages that are
physically silent; bystanders, bare, frequency-weighted central case, attentive and distracted observers).
Usage (repo root): python3 uq/source_sensitivity.py [n] -> uq/source_sensitivity.json
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "uq"))
import four_outcomes_v4 as fv  # noqa: E402

g0 = fv.rs.g0
BASE_REL = dict(g0.RELEASE_PRIOR)
BASE_PTH = g0.SAMPLED["P_th"]
VARIANTS = {  # name: (release prior changes, P_th (low, high) or None)
    "baseline": ({}, None),
    "P_th fixed low (0.6 kPa)": ({}, (600.0, 600.0)),
    "P_th fixed high (2.5 kPa)": ({}, (2500.0, 2500.0)),
    "T upper bound 5 s (was 20)": ({"T": (BASE_REL["T"][0], 5.0)}, None),
    "T lower bound 1 s (was 0.3)": ({"T": (1.0, BASE_REL["T"][1])}, None),
    "d upper bound 4 mm (was 8)": ({"d": (BASE_REL["d"][0], 4e-3)}, None),
    "d lower bound 2 mm (was 1)": ({"d": (2e-3, BASE_REL["d"][1])}, None),
}


def run(n):
    out = {}
    for name, (rel, pth) in VARIANTS.items():
        g0.RELEASE_PRIOR.clear(); g0.RELEASE_PRIOR.update(BASE_REL); g0.RELEASE_PRIOR.update(rel)
        g0.SAMPLED["P_th"] = (*pth, True) if pth else BASE_PTH
        mc = g0.monte_carlo(n)
        r = mc["R_nb_conc_phi_inh_none"]
        ho = fv.compute(n)
        s = ho["summary_bare_600s_bystanders"]["frequency, central"]
        out[name] = {"frac_silent": ho["frac_silent"], "R_median": float(np.median(r)), "P_R_gt_1": float(np.mean(r > 1)),
                     **{f"headline {o[:10]}": {k: s[o]["physics"][k] for k in ("none", "silent_worse", "audible_worse")}
                        | {"memory_silent_worse": (s[o]["memory"] or {}).get("silent_worse")} for o in fv.rh.OBS}}
        print(f"{name:28s} silent {out[name]['frac_silent']:.2f}  R med {out[name]['R_median']:.2f}  P(R>1) "
              f"{out[name]['P_R_gt_1']:.2f}  " + "  ".join(
                  f"{o[:10]} S/A {100 * s[o]['physics']['silent_worse']:.1f}/{100 * s[o]['physics']['audible_worse']:.1f}"
                  for o in fv.rh.OBS))
    g0.RELEASE_PRIOR.clear(); g0.RELEASE_PRIOR.update(BASE_REL); g0.SAMPLED["P_th"] = BASE_PTH
    return out


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    res = {"n": n, "variants": run(n)}
    (ROOT / "uq/source_sensitivity.json").write_text(json.dumps(res, indent=1))
