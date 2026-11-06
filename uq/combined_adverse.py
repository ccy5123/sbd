"""Combined adverse case for the headline (JRSI pre-submission review, 5 Nov 2026).

The robustness analyses of the ESM vary one factor at a time. Here the factors that can raise silent doses relative to
audible ones are applied together, as (silent, audible) multipliers on the OAV of physically silent / audible passages
(four_outcomes_v4.compute gain hook: on the CFD dose, below the well-mixed floor of the 600-s window), under every
scene weighting (central, home, office, equal per scene):
  * mesh: the 1.5x refinement factor of the median silent dose, 3.0 at the releaser's nose (0.55 at the neighbour;
    the larger one is applied to every silent dose, as in the ESM mesh bullet);
  * LES: the class peak factors, median 2.2 silent / 1.3 audible, and the adverse pairing 6.6 / 0.27
    (uq/les_peak_factor.json, 60 s windows, releases with RANS OAV >= 0.01);
  * combined: mesh x LES, central (6.6 / 1.3) and extreme (19.8 / 0.27).
The boundary-layer speed bias has no factor of its own and is not applied.
Headline key as in uq/peak_breakeven.py: bystanders, bare, 600 s.
Usage (repo root): python3 uq/combined_adverse.py -> uq/combined_adverse.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "uq"))
import four_outcomes_v4 as fv  # noqa: E402

KEY = "summary_bare_600s_bystanders"
TAGS = ("frequency, central", "frequency, home", "frequency, office", "equal per scene")
MESH, LES, LES_ADVERSE = 3.0, (2.2, 1.3), (6.6, 0.27)
GAINS = {
    "RANS mean": (1.0, 1.0),
    "mesh": (MESH, 1.0),
    "LES median": LES,
    "LES adverse pairing": LES_ADVERSE,
    "mesh x LES median": (MESH * LES[0], LES[1]),
    "mesh x LES adverse pairing": (MESH * LES_ADVERSE[0], LES_ADVERSE[1]),
}


def main():
    sim = fv.passages()
    out = {"headline": KEY, "gains": GAINS, "cases": {}}
    print("bystanders, bare: silent worse / audible worse (%) | remembered silent worse (%)")
    for name, gain in GAINS.items():
        s = fv.compute(sim=sim, gain=gain)[KEY]
        out["cases"][name] = {t: {o: {"physics": s[t][o]["physics"], "memory": s[t][o]["memory"]} for o in fv.rh.OBS}
                              for t in TAGS}
        out["cases"][name]["per_scene"] = {sc: {o: x[o]["physics"] for o in fv.rh.OBS} for sc, x in s["per_scene"].items()}
        for sc, x in s["per_scene"].items():
            o = fv.rh.OBS[0]
            print(f"{name:27s} {sc:18s} {o[:10]:10s} {100 * x[o]['physics']['silent_worse']:5.2f} / "
                  f"{100 * x[o]['physics']['audible_worse']:5.2f}")
        for t in TAGS:
            for o in fv.rh.OBS:
                ph, me = s[t][o]["physics"], s[t][o]["memory"]
                mem = f"{100 * me['silent_worse']:5.1f}" if me else "  -  "
                print(f"{name:27s} {t:18s} {o[:10]:10s} {100 * ph['silent_worse']:5.2f} / {100 * ph['audible_worse']:5.2f}"
                      f" | {mem}")
    # sofa alone: the smallest silent-only factor at which silent-worse >= audible-worse (attentive), by bisection in
    # log k on top of the RANS mean and on top of the median audible LES factor
    o = fv.rh.OBS[0]
    def margin(k, a):
        x = fv.compute(sim=sim, gain=(k, a))[KEY]["per_scene"]["sofa"][o]["physics"]
        return x["silent_worse"] - x["audible_worse"]
    out["sofa_breakeven_silent_only"] = {}
    for a in (1.0, LES[1]):
        lo, hi = 0.0, 4.0
        if margin(10 ** hi, a) < 0:
            out["sofa_breakeven_silent_only"][f"audible x{a:g}"] = None
            continue
        for _ in range(14):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if margin(10 ** mid, a) < 0 else (lo, mid)
        out["sofa_breakeven_silent_only"][f"audible x{a:g}"] = float(10 ** hi)
        print(f"sofa, attentive: silent-only factor to reverse (audible x{a:g}): {10 ** hi:.3g}")
    (ROOT / "uq/combined_adverse.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
