"""LES peak factors from the two sofa LES runs (PLAN v4 E4, HANDOFF next task 3).

The peak factor of a release at a nose is LES worst breath / RANS worst breath (worst_breath_OAV_mean, the mean over
breathing phases, cfd/results_v4/<case>.json) for the same scene, clothing, release level and window. The LES runs
(sofa upright, bare and trousers) have six releases, S50 A50 S90 A90 S50b A50b, so S50 and A50 have two realisations;
the RANS runs have one of each level. Windows 30 and 60 s after release (the LES window is 90 s, the RANS 150 s).
Summaries per class (silent / audible) and nose (releaser / neighbour): geometric mean, min and max of the factor,
(i) over all releases and (ii) only where the RANS level is >= LEVEL_MIN (near enough to the detection thresholds for
the factor to change an outcome; the factors far below come from RANS levels of 1e-5 to 1e-8, where an early LES
filament multiplies nothing that matters). Also: the realisation spread (S50 vs S50b, A50 vs A50b), the highest LES
bystander level of a silent release against OAV 1 and 20, and the headline (uq/four_outcomes_v4, bystanders, bare,
600 s, frequency-weighted) with class factors applied through compute(gain=(silent, audible)): the near-threshold
geometric means, the all-level geometric means, and an adverse case (largest near-threshold silent factor with the
smallest audible one). Compare with uq/peak_breakeven.json (silent-only factor ~14 flips the headline).
Usage (repo root): python3 uq/les_peak_factor.py -> uq/les_peak_factor.json
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "cfd/results_v4"
sys.path.insert(0, str(ROOT / "uq"))
import four_outcomes_v4 as fv  # noqa: E402

PAIRS = {"bare": ("sofa_v4_multi_les", "sofa_v4_multi"), "trousers": ("sofa_tr_v4_multi_les", "sofa_tr_v4_multi")}
WINDOWS = ("30", "60")
NOSES = ("releaser", "neighbour")
LEVEL_MIN = 0.01  # RANS OAV: a factor below this level cannot lift a release to OAV 1 (would need > 100)
KEY = "summary_bare_600s_bystanders"
TAGS = ("frequency, central", "frequency, home", "frequency, office")


def factors():
    rows = []
    for cloth, (les, rans) in PAIRS.items():
        L = json.loads((RES / f"{les}.json").read_text())["releases"]
        R = json.loads((RES / f"{rans}.json").read_text())["releases"]
        for k, l in L.items():
            r = R[k.rstrip("b")]
            for nose in NOSES:
                for w in WINDOWS:
                    ol = l[nose]["by_window"][w]["worst_breath_OAV_mean"]
                    orans = r[nose]["by_window"][w]["worst_breath_OAV_mean"]
                    rows.append({"clothing": cloth, "release": k, "class": l["class"], "nose": nose, "window": w,
                                 "LES": ol, "RANS": orans, "factor": ol / orans if orans > 0 else None})
    return rows


def stats(vals):
    v = np.array([x for x in vals if x])
    return {"n": int(v.size), "geomean": float(np.exp(np.log(v).mean())), "min": float(v.min()),
            "max": float(v.max())} if v.size else None


def summary(rows, w):
    out = {}
    for cls in ("silent", "audible"):
        for nose in NOSES:
            sel = [r for r in rows if r["class"] == cls and r["nose"] == nose and r["window"] == w]
            out[f"{cls} {nose}"] = {"all": stats([r["factor"] for r in sel]),
                                    "near_threshold": stats([r["factor"] for r in sel if r["RANS"] >= LEVEL_MIN])}
    for cls in ("silent", "audible"):
        sel = [r for r in rows if r["class"] == cls and r["window"] == w]
        out[f"{cls} both noses"] = {"all": stats([r["factor"] for r in sel]),
                                    "near_threshold": stats([r["factor"] for r in sel if r["RANS"] >= LEVEL_MIN])}
    return out


def spread(rows, w):
    """LES second realisation / first, same level, scene and nose."""
    out = {}
    for a, b in (("S50", "S50b"), ("A50", "A50b")):
        for cloth in PAIRS:
            for nose in NOSES:
                x = {r["release"]: r["LES"] for r in rows
                     if r["clothing"] == cloth and r["nose"] == nose and r["window"] == w and r["release"] in (a, b)}
                out[f"{a} {cloth} {nose}"] = x[b] / x[a] if x[a] > 0 else None
    return out


def headline(sim, gains):
    out = {}
    for name, g in gains.items():
        s = fv.compute(sim=sim, gain=g)[KEY]
        out[name] = {"gain_silent_audible": list(g),
                     **{f"{o[:10]} | {t}": {"physics": s[t][o]["physics"], "memory": s[t][o]["memory"]}
                        for o in fv.rh.OBS for t in TAGS}}
    return out


def main():
    rows = factors()
    out = {"level_min": LEVEL_MIN, "rows": rows, "summary": {w: summary(rows, w) for w in WINDOWS},
           "realisation_spread": {w: spread(rows, w) for w in WINDOWS}}
    les = {c: json.loads((RES / f"{p[0]}.json").read_text())["releases"] for c, p in PAIRS.items()}
    out["silent_bystander_max_LES"] = {
        c: {k: {"60": r["neighbour"]["by_window"]["60"]["worst_breath_OAV_mean"],
                "90": r["neighbour"]["worst_breath_OAV_mean"], "peak": r["neighbour"]["peak_OAV"]}
            for k, r in rel.items() if r["class"] == "silent"} for c, rel in les.items()}
    s60 = out["summary"]["60"]
    near = (s60["silent both noses"]["near_threshold"], s60["audible both noses"]["near_threshold"])
    allv = (s60["silent both noses"]["all"], s60["audible both noses"]["all"])
    gains = {"none": (1.0, 1.0),
             "near-threshold geomean": (near[0]["geomean"], near[1]["geomean"]),
             "all-level geomean": (allv[0]["geomean"], allv[1]["geomean"]),
             "adverse (max silent, min audible, near threshold)": (near[0]["max"], near[1]["min"])}
    out["headline"] = headline(fv.passages(), gains)

    print(f"peak factor LES / RANS, worst breath, 60 s window (near threshold: RANS >= {LEVEL_MIN:g})")
    for k, v in s60.items():
        f = lambda x: "-" if x is None else f"{x['geomean']:.3g} [{x['min']:.3g}-{x['max']:.3g}] n{x['n']}"
        print(f"  {k:24s} all {f(v['all']):32s} near {f(v['near_threshold'])}")
    print("realisation spread (b / a), 60 s:", {k: round(v, 3) for k, v in out["realisation_spread"]["60"].items()})
    print("silent releases, LES bystander (neighbour) OAV: 60 s / 90 s worst breath / instantaneous peak")
    for c, rel in out["silent_bystander_max_LES"].items():
        print(f"  {c:9s}", "  ".join(f"{k} {v['60']:.3g}/{v['90']:.3g}/{v['peak']:.3g}" for k, v in rel.items()))
    print("headline (bystanders, bare, 600 s): silent worse / audible worse (%), physics | memory")
    for name, h in out["headline"].items():
        print(f"  {name} gain {tuple(round(x, 3) for x in h['gain_silent_audible'])}")
        for k, x in h.items():
            if k == "gain_silent_audible":
                continue
            p, m = x["physics"], x["memory"]
            mem = "-" if not m else f"{100 * m['silent_worse']:.1f} / {100 * m['audible_worse']:.1f}"
            print(f"    {k:40s} {100 * p['silent_worse']:6.2f} / {100 * p['audible_worse']:6.2f}  | {mem}")
    (ROOT / "uq/les_peak_factor.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
