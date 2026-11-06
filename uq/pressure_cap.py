"""Driving-pressure cap on the passage stream: uncapped against capped, and other caps (JRSI pre-submission review,
5 Nov 2026).

Reviewer's point: the release priors (V, T, d log-uniform, gate0/run_gate0.RELEASE_PRIOR) set the exit velocity
u0 = 4V / (pi d^2 T) without regard to the pressure that has to drive it. Through the orifice equation of the valve
model a passage needs dp = 1/2 rho_gas (u0 / C_d)^2, rho_gas = rho_air (1 - g_reduced / g), with the passage's own
C_d and g_reduced (the values that also set its oscillation onset). Since 5 Nov the source model caps it at params
dp_max = 88 mmHg (Miller et al. 1988, the largest rectal pressure rise measured while passing flatus) by clipping
(gate0/run_gate0.draw_release: V and d kept, u0 lowered to the cap, T lengthened; M0, oscillation and hearing follow).
This script reports, on the perception/run_selection stream of uq/four_outcomes_v4:
  * the required pressure of the uncapped stream (all, oscillating, silent passages);
  * the headline uncapped (dp_max None, the numbers before 5 Nov) and capped at 88 mmHg (the headline), for the ESM
    comparison: bystanders and releaser, bare, 600 s, every scene and weighting, both observers;
  * other caps, by clipping and by truncation (passages needing more than the cap discarded, the rest renormalised):
    72 mmHg, intrarectal pressure during simulated defecation, upper end of 20-72 mmHg (Lee & Bharucha 2016
    J Neurogastroenterol Motil 22:46, Tables 2-3; params.yaml dp_rectal note); 88 mmHg; 108 and 171 mmHg, peak
    intra-abdominal pressure of a cough and a jump in healthy adults (Cobb et al. 2005 J Surg Res 129:231,
    doi:10.1016/j.jss.2005.06.015), a ceiling for straining, not a flatus measurement.
Usage (repo root): python3 uq/pressure_cap.py -> uq/pressure_cap.json
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "uq"))
import four_outcomes_v4 as fv  # noqa: E402

g0 = fv.rs.g0
KEY = "summary_bare_600s_{}"
TAGS = ("frequency, central", "frequency, home", "frequency, office", "equal per scene")
MMHG = 133.322  # Pa
CAPS = {"72 mmHg (simulated defecation, Lee & Bharucha 2016)": 72.0,
        "88 mmHg (flatus maximum, Miller 1988)": 88.0,
        "108 mmHg (cough, Cobb 2005)": 107.6,
        "171 mmHg (jump, Cobb 2005)": 171.0}
UNCAPPED = {"sofa": (0.52, 9.22), "elevator": (22.3, 20.4), "standing": (0.04, 0.003),
            "frequency, central": (0.51, 6.86)}  # attentive, % (headline before 5 Nov)


def stream(dp_max):
    old = g0.P0["dp_max"]
    g0.P0["dp_max"] = dp_max
    try:
        return fv.passages()
    finally:
        g0.P0["dp_max"] = old


def dist_stats(dp, caps=(88.0, 150.0)):
    mm = dp / MMHG
    return {"n": int(dp.size), "median_kPa": float(np.median(dp) / 1e3), "p90_kPa": float(np.percentile(dp, 90) / 1e3),
            "median_mmHg": float(np.median(mm)), "p90_mmHg": float(np.percentile(mm, 90)),
            **{f"share_above_{c:g}_mmHg": float(np.mean(mm > c)) for c in caps}}


def headline(sim):
    s = fv.compute(sim=sim)
    out = {"frac_silent": s["frac_silent"]}
    for grp in ("bystanders", "culprit"):
        h = s[KEY.format(grp)]
        out[grp] = {"per_scene": {sc: {o: h["per_scene"][sc][o]["physics"] for o in fv.rh.OBS} for sc in h["per_scene"]},
                    **{t: {o: {"physics": h[t][o]["physics"], "memory": h[t][o]["memory"]} for o in fv.rh.OBS}
                       for t in TAGS}}
    return out


def line(name, r):
    o = fv.rh.OBS[0]
    b = r["bystanders"]
    f = lambda d: f"{100 * d['silent_worse']:6.2f} / {100 * d['audible_worse']:6.2f}"  # noqa: E731
    mem = b["frequency, central"][o]["memory"]
    print(f"{name:58s} sofa {f(b['per_scene']['sofa'][o])}  lift {f(b['per_scene']['elevator'][o])}"
          f"  stand {f(b['per_scene']['standing'][o])}  day {f(b['frequency, central'][o]['physics'])}"
          f"  equal {f(b['equal per scene'][o]['physics'])}  silent {100 * r['frac_silent']:4.1f}"
          f"  mem(day) {100 * mem['silent_worse']:4.1f}")


def main():
    free = stream(None)
    osc = free["osc"].astype(bool)
    out = {"observer_order": list(fv.rh.OBS), "dp_max_params_Pa": g0.P_RAW["source"]["dp_max"]["value"],
           "caps_mmHg": CAPS,
           "required_pressure_uncapped": {"all": dist_stats(free["dp"]), "audible (oscillating)": dist_stats(free["dp"][osc]),
                                          "silent": dist_stats(free["dp"][~osc])},
           "cases": {}}
    for k, v in out["required_pressure_uncapped"].items():
        print(f"required dp, {k:22s} median {v['median_mmHg']:7.1f} mmHg  p90 {v['p90_mmHg']:7.1f}  "
              f">88 {100 * v['share_above_88_mmHg']:5.1f} %  >150 {100 * v['share_above_150_mmHg']:5.1f} %")
    print("attentive bystander, silent worse / audible worse (%), bare 600 s")
    base = headline(free)
    o = fv.rh.OBS[0]
    for sc, (sw, aw) in UNCAPPED.items() if not fv.am.WM_FLOOR else ():  # the numbers before the well-mixed floor
        x = base["bystanders"]["per_scene"][sc][o] if sc in base["bystanders"]["per_scene"] else base["bystanders"][sc][o]["physics"]
        assert abs(100 * x["silent_worse"] - sw) < 0.01 + 0.005 * sw and abs(100 * x["audible_worse"] - aw) < 0.01 + 0.005 * aw, sc
    out["cases"]["uncapped"] = base
    line("uncapped", base)
    capped = fv.passages()  # the headline stream, params dp_max
    out["cases"]["capped (headline, params dp_max)"] = head = headline(capped)
    line("capped (headline, params dp_max)", head)
    hit = capped["u0"] < free["u0"]
    out["clipping_at_dp_max"] = {
        "share_clipped": float(hit.mean()), "share_oscillating_clipped": float(hit[osc].mean()),
        "oscillation_lost": int(np.sum(osc & ~capped["osc"])),
        "median_T_clipped_s": float(np.median(capped["T"][hit])), "max_T_clipped_s": float(capped["T"][hit].max()),
        "median_u0_oscillating_m_s": [float(np.median(free["u0"][osc])), float(np.median(capped["u0"][osc]))],
        "median_M0_oscillating": [float(np.median((free["Q"] * free["u0"])[osc])),
                                  float(np.median((capped["Q"] * capped["u0"])[osc]))],
        "heard_lost": {k: int(np.sum(free[k] & ~capped[k])) for k in free if k.startswith("heard_living@")}}
    print("clipping at dp_max:", json.dumps(out["clipping_at_dp_max"]))
    for name, mmhg in CAPS.items():
        cap = mmhg * MMHG
        keep = free["dp"] <= cap
        r = headline({k: v[keep] for k, v in free.items()})
        r.update({"share_discarded": float(1 - keep.mean()), "share_oscillating_discarded": float(1 - keep[osc].mean())})
        out["cases"][f"truncate {name}"] = r
        line(f"truncate {name}", r)
        r = headline(stream(cap)) if abs(cap - g0.P0["dp_max"]) > 1.0 else head
        out["cases"][f"clip {name}"] = r
        line(f"clip {name}", r)
    (ROOT / "uq/pressure_cap.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
