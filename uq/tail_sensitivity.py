"""Psychometric-tail sensitivity of the v4 headline (robustness analyses, HANDOFF next task 1).

The bystander OAVs of the v4 scenes sit far below the observers' 50 % points (attentive OAV 20, distracted OAV 520),
so every detection probability in the headline comes from the low tail of Phi(log2(s OAV) / sd), where Amoore &
Hautala (1983) say the data do not support extrapolation. Each variant replaces the detection law of one or both
observers and reruns uq/four_outcomes_v4.compute on the same passages:
  * slope: attentive sd 1, 2 (baseline), 3, 4 binary steps; distracted sd 2, 3.5 (baseline), 5;
  * tail shape: probit (baseline); logistic in log2 OAV with the probit's variance (scale sd sqrt(3) / pi, heavier
    tail); probit with a hard floor, p = 0 below the Nagata trained-panel threshold (OAV < 1), since no untrained
    observer should detect what a trained panel does not; the deterministic Nagata observer p = 1(OAV >= 1) (Gate 0).
Reported: bystanders, bare, 600 s, frequency-weighted (central case and the home / office bounds): physics
silent-worse and audible-worse shares, their ratio, and the remembered silent-worse share; the question is whether
audible-worse >> silent-worse (~17:1) and the memory share (~90 %) keep their direction.
Usage (repo root): python3 uq/tail_sensitivity.py -> uq/tail_sensitivity.json
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "uq"))
import four_outcomes_v4 as fv  # noqa: E402

ATT, DIS = fv.rh.OBS
OBS = fv.observers()
S_ATT, SD_ATT = OBS[ATT][0], OBS[ATT][1]
S_DIS, SD_DIS = OBS[DIS][0], OBS[DIS][1]
FREQ = ("frequency, central", "frequency, home", "frequency, office")


def probit(s, sd):
    return lambda A: norm.cdf(np.log2(np.maximum(s * A, 1e-300)) / sd)


def logistic(s, sd):
    return lambda A: 1.0 / (1.0 + np.exp(-np.log2(np.maximum(s * A, 1e-300)) / (sd * np.sqrt(3.0) / np.pi)))


def floored(s, sd):
    return lambda A: np.where(A >= 1.0, norm.cdf(np.log2(np.maximum(s * A, 1e-300)) / sd), 0.0)


def nagata(A):
    return (A >= 1.0).astype(float)


VARIANTS = {  # name: (attentive law, distracted law)
    "baseline (probit, sd 2 / 3.5)": (probit(S_ATT, SD_ATT), probit(S_DIS, SD_DIS)),
    **{f"attentive sd {sd:g}": (probit(S_ATT, sd), probit(S_DIS, SD_DIS)) for sd in (1.0, 3.0, 4.0)},
    **{f"distracted sd {sd:g}": (probit(S_ATT, SD_ATT), probit(S_DIS, sd)) for sd in (2.0, 5.0)},
    "logistic tail": (logistic(S_ATT, SD_ATT), logistic(S_DIS, SD_DIS)),
    "hard floor at Nagata OAV 1": (floored(S_ATT, SD_ATT), floored(S_DIS, SD_DIS)),
    "Nagata deterministic (both)": (nagata, nagata),
}


def summarise(out, key="summary_bare_600s_bystanders"):
    s = out[key]
    res = {}
    for name in fv.rh.OBS:
        r = {}
        for tag in FREQ:
            ph, me = s[tag][name]["physics"], s[tag][name]["memory"]
            r[tag] = {"silent_worse": ph["silent_worse"], "audible_worse": ph["audible_worse"], "none": ph["none"],
                      "audible_to_silent": ph["audible_worse"] / ph["silent_worse"] if ph["silent_worse"] > 0 else None,
                      "memory_silent_worse": me["silent_worse"] if me else None,
                      "pi_s": s[tag][name]["pi_s"], "pi_l": s[tag][name]["pi_l"]}
        res[name] = r
    return res


def main():
    sim = fv.passages()
    out = {"n_events": int(sim["V"].size), "group": "bystanders, bare, 600 s", "variants": {}}
    fmt = lambda x: "  -  " if x is None else f"{x:5.1f}"
    print(f"{'variant':32s} observer    silent / audible worse (%)  audible:silent  memory silent (%)  [home-office ratio]")
    for vname, (att, dis) in VARIANTS.items():
        res = summarise(fv.compute(sim=sim, detectors={ATT: att, DIS: dis}))
        out["variants"][vname] = res
        for name in fv.rh.OBS:
            c = res[name]["frequency, central"]
            rr = [res[name][t]["audible_to_silent"] for t in FREQ[1:]]
            mem = None if c["memory_silent_worse"] is None else 100 * c["memory_silent_worse"]
            print(f"{vname:32s} {name[:10]:10s}  {100 * c['silent_worse']:6.2f} / {100 * c['audible_worse']:6.2f}"
                  f"       {fmt(c['audible_to_silent'])}           {fmt(mem)}        "
                  f"[{fmt(rr[0])} - {fmt(rr[1])}]")
    (ROOT / "uq/tail_sensitivity.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
