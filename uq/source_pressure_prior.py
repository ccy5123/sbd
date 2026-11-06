"""Source prior consistent with the measured pressures: sensitivity, not headline (audit point, 6 Nov).

The sampled stream draws V, T and d independently, so its median driving pressure is 0.14 mmHg, while Miller et al.
1988 (Br J Surg 75:1003) report a median rectal pressure rise of 8 mmHg (range -10 to 88, 54 events) while passing
flatus, and the valve onset is about 9 mmHg. The representative releases cannot be re-chosen without new CFD, so a
passage outside the class's levels keeps the nearest level's route (nose_oav holds outside them); the shares of
passages below and above the levels are reported to show how far that is stretched. Variants, on the headline
machinery (bare, 600 s, well-mixed floor, RANS mean doses, living room):
  (i) filtered: the headline stream, keeping passages with driving pressure >= 1 and >= 4 mmHg;
  (ii) pressure prior: the driving pressure is drawn, then the release follows from it. dp log-normal with median
      8 mmHg, truncated at 88 mmHg (rejection), sigma_ln chosen so that 88 mmHg is the expected largest of Miller's 54
      events (quantile 1 - 1 / 55, z = 2.09, sigma_ln = ln(88 / 8) / 2.09 = 1.15); sigma_ln 0.8 is the narrower
      alternative. Non-positive rises (Miller's range starts at -10 mmHg) are not represented: the orifice equation
      needs a positive pressure, and what drives those passages (the resting gradient) was not measured, so the prior
      is conditional on a positive rise. V from its prior (Suarez 1997, measured), d from its prior, C_d, g_reduced from
      the passage; u0 = C_d sqrt(2 dp / rho_gas), Q = u0 pi d^2 / 4, T = V / Q. The duration bound 0.3-20 s of the
      T prior is not applied in the variants 'free' (the share outside it is reported) and is enforced by redrawing
      dp and d in the variants 'T bound'.
Reported per variant, for both observers: silent share, detection (a), intensity (b) and remembered silent-worse
share for the sofa, the lift (person behind, all three), the day (central) and equal weight per scene, and the share
of each class's passages with M0 outside its representative levels.
Usage (repo root): python3 uq/source_pressure_prior.py -> uq/source_pressure_prior.json
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "uq"))
import four_outcomes_v4 as fv  # noqa: E402
from intensity_robustness import ATT, criterion_b, weightings  # noqa: E402

g0, rh = fv.rs.g0, fv.rh
MMHG = 133.322  # Pa
MEDIAN, TOP, N_MILLER = 8.0, 88.0, 54
Z_TOP = float(norm.ppf(1.0 - 1.0 / (N_MILLER + 1)))
SIGMA = float(np.log(TOP / MEDIAN) / Z_TOP)
T_BOUND = g0.RELEASE_PRIOR["T"]
SETTINGS = ("sofa", "lift, behind", "lift", "day, central", "equal per scene")


def pressure_release(sigma, bound):
    """draw (rng, p) -> Release for rs.simulate: dp log-normal (median 8 mmHg), truncated at 88; see module docstring."""
    def draw(rng, p):
        rho_gas = p["rho_air"] * (1.0 - p["g_reduced"] / p["g"])
        for _ in range(100000):
            dp = MEDIAN * np.exp(sigma * rng.standard_normal())
            if dp > TOP:
                continue
            V, d = g0.logu(rng, *g0.RELEASE_PRIOR["V"]), g0.logu(rng, *g0.RELEASE_PRIOR["d"])
            u0 = p["C_d"] * np.sqrt(2.0 * dp * MMHG / rho_gas)
            T = 4.0 * V / (np.pi * d**2 * u0)
            if not bound or T_BOUND[0] <= T <= T_BOUND[1]:
                return g0.Release(V=V, T=T, d=d)
        raise RuntimeError("no release within the duration bound")
    return draw


def levels_outside(sim):
    """Per class: share of the passages with M0 below, within and above its representative levels (sofa run)."""
    res = json.loads((fv.RES / "sofa_v4_multi.json").read_text())
    M0, osc = sim["Q"] * sim["u0"], sim["osc"].astype(bool)
    out = {}
    for cls, mask in (("silent", ~osc), ("audible", osc)):
        m = sorted(r["M0"] for r in res["releases"].values() if r["class"] == cls)
        x = M0[mask]
        out[cls] = {"levels_M0": [m[0], m[-1]], "share_below": float(np.mean(x < m[0])),
                    "share_within": float(np.mean((x >= m[0]) & (x <= m[-1]))), "share_above": float(np.mean(x > m[-1])),
                    "median_M0": float(np.median(x)) if x.size else None}
    return out


def report(name, sim):
    out = fv.compute(sim=sim)
    w = weightings()
    res = {"n": int(sim["V"].size), "silent_share": out["frac_silent"],
           "dp_mmHg": dict(zip(("p10", "median", "p90"), (np.percentile(sim["dp"], [10, 50, 90]) / MMHG).tolist())),
           "T_s": dict(zip(("p10", "median", "p90"), np.percentile(sim["T"], [10, 50, 90]).tolist())),
           "share_T_outside_bound": float(np.mean((sim["T"] < T_BOUND[0]) | (sim["T"] > T_BOUND[1]))),
           "M0_levels": levels_outside(sim), "by": {}}
    for obs in rh.OBS:
        by = {}
        for s in SETTINGS:
            if s.startswith("lift, "):
                by[s] = criterion_b(out, "bystander", obs, {"elevator": 1.0}, nose=s[6:])
            else:
                by[s] = criterion_b(out, "bystander", obs, w[s])
        by["releaser, day"] = criterion_b(out, "releaser", obs, w["day, central"])
        res["by"][obs] = by

    def f(x):
        return (f"(a) {100 * x['pi_s']:5.2f}/{100 * x['pi_l']:5.2f} (b) {100 * x['silent_stronger']:4.1f}/"
                f"{100 * x['audible_stronger']:4.1f}/{100 * x['tie']:4.1f} [{x['pair_mass_both']:.1e}] "
                f"mem {100 * x['remembered_silent_worse']:4.1f}")
    lv = res["M0_levels"]
    print(f"{name}: n {res['n']}, silent {100 * res['silent_share']:.1f} %, dp median {res['dp_mmHg']['median']:.2f} mmHg, "
          f"T median {res['T_s']['median']:.2f} s, outside 0.3-20 s {100 * res['share_T_outside_bound']:.1f} %; M0 silent "
          f"below/above {100 * lv['silent']['share_below']:.1f}/{100 * lv['silent']['share_above']:.1f} %, audible "
          f"{100 * lv['audible']['share_below']:.1f}/{100 * lv['audible']['share_above']:.1f} %")
    for s in SETTINGS:
        print(f"   {s:16s} {f(res['by'][ATT][s])}")
    return res


def main():
    base = fv.passages()
    keep_mm = lambda lim: base["dp"] / MMHG >= lim  # noqa: E731
    out = {"prior": {"median_mmHg": MEDIAN, "truncated_at_mmHg": TOP, "sigma_ln": SIGMA, "z_top": Z_TOP,
                     "non_positive_rises": "not represented; prior conditional on a positive rise (see docstring)"},
           "T_bound_s": list(T_BOUND), "variants": {}}
    v = out["variants"]
    print(f"sigma_ln {SIGMA:.3f}")
    v["headline stream"] = report("headline stream", base)
    for lim in (1.0, 4.0):
        keep = keep_mm(lim)
        name = f"filtered, dp >= {lim:g} mmHg"
        v[name] = {"share_kept": float(keep.mean()), **report(name, {k: x[keep] for k, x in base.items()})}
    for name, sigma, bound in ((f"pressure prior, sigma {SIGMA:.2f}, free", SIGMA, False),
                               (f"pressure prior, sigma {SIGMA:.2f}, T bound", SIGMA, True),
                               ("pressure prior, sigma 0.80, free", 0.8, False)):
        v[name] = report(name, fv.passages(draw=pressure_release(sigma, bound)))
    (ROOT / "uq/source_pressure_prior.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
