"""Chemistry layer, part 1: which sulfur compound carries the odour, and does OAV summation reproduce the chemical
removal experiments of Suarez et al. (1998)?

(a) OAV share of H2S, methanethiol (MeSH) and dimethyl sulfide (DMS) for the mean flatus composition (all subjects,
    men, women; Suarez 1998 Table 1) under two threshold sets:
      trained panel  - Nagata 2003 (H2S 0.41, MeSH 0.070, DMS 3.0 ppbv)
      population     - Amoore & Hautala 1983 geometric means (H2S 8.1, MeSH 1.6 ppbv) and, for DMS, which Amoore lacks,
                       the Wilby 1969 recognition median (2.0 ppbv).
(b) Removal check (Suarez 1998 Table 3): zinc acetate precipitates H2S and MeSH (ZnS, zinc thiolate), activated
    charcoal adsorbs all three. Predicted intensity ratio = (OAV_treated / OAV_untreated)^n with the Stevens exponent
    n = 0.28 (0.20-0.45, Collins 2001), compared with the two judges' rating ratios (0-8 category scale, so the
    comparison is a consistency check, not a fit).
Concentrations (umol/L or nmol/L of flatus) are converted to ppbv at 37 C, as in gate0/model.py.
Usage (repo root): python3 chem/odorants.py -> chem/odorants.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gate0"))
from model import load_params, nominal, source_mole_fraction_ppb

P = nominal(load_params())
GASES = ("H2S", "MeSH", "DMS")
THRESHOLDS = {"trained panel (Nagata 2003)": {"H2S": 0.41, "MeSH": 0.070, "DMS": 3.0},
              "population (Amoore & Hautala 1983; DMS: Wilby 1969)": {"H2S": 8.1, "MeSH": 1.6, "DMS": 2.0}}
# Suarez 1998 Table 1, mean umol/L
COMPOSITION = {"all (n = 87)": {"H2S": 1.06, "MeSH": 0.21, "DMS": 0.08},
               "men (n = 52)": {"H2S": 0.59, "MeSH": 0.19, "DMS": 0.08},
               "women (n = 35)": {"H2S": 1.77, "MeSH": 0.24, "DMS": 0.07}}
# Suarez 1998 Table 3, mean nmol/L and mean ratings (judge 1, judge 2)
TREATMENTS = {
    "activated charcoal (n = 9)": {"none": ({"H2S": 1365, "MeSH": 445, "DMS": 80.1}, (4.1, 6.5)),
                                   "treated": ({"H2S": 4.5, "MeSH": 1.8, "DMS": 0.9}, (0.1, 0.4))},
    "zinc acetate (n = 16)": {"none": ({"H2S": 526, "MeSH": 189, "DMS": 29.3}, (2.5, 5.8)),
                              "treated": ({"H2S": 17.1, "MeSH": 16.7, "DMS": 18.5}, (0.7, 3.4))},
}
N_STEVENS = (0.28, 0.20, 0.45)


def oavs(c_umol: dict, thr: dict) -> dict:
    return {g: source_mole_fraction_ppb(c_umol[g], P["T_gas"]) / thr[g] for g in GASES}


def main():
    out = {"shares": {}, "removal": {}}
    for tname, thr in THRESHOLDS.items():
        for cname, c in COMPOSITION.items():
            o = oavs(c, thr)
            tot = sum(o.values())
            out["shares"][f"{tname} | {cname}"] = {"OAV_total": tot, **{f"share_{g}": o[g] / tot for g in GASES}}
            print(f"{tname[:14]:14s} {cname:15s} OAV {tot:9.3g}  " +
                  "  ".join(f"{g} {100 * o[g] / tot:4.1f}%" for g in GASES))
    thr = THRESHOLDS["trained panel (Nagata 2003)"]
    for name, d in TREATMENTS.items():
        o0 = sum(oavs({g: v * 1e-3 for g, v in d["none"][0].items()}, thr).values())
        o1 = sum(oavs({g: v * 1e-3 for g, v in d["treated"][0].items()}, thr).values())
        ratio = o1 / o0
        pred = {f"n={n:g}": ratio ** n for n in N_STEVENS}
        judges = [t / u for t, u in zip(d["treated"][1], d["none"][1])]
        dms_share = oavs({g: v * 1e-3 for g, v in d["treated"][0].items()}, thr)["DMS"] / o1
        out["removal"][name] = {"OAV_untreated": o0, "OAV_treated": o1, "OAV_ratio": ratio,
                                "predicted_intensity_ratio": pred, "judge_rating_ratios": judges,
                                "DMS_share_after": dms_share}
        print(f"{name:28s} OAV {o0:8.3g} -> {o1:8.3g} (x{ratio:.3f}); predicted I ratio "
              + ", ".join(f"{k} {v:.2f}" for k, v in pred.items())
              + f"; judges {judges[0]:.2f}, {judges[1]:.2f}; DMS share after {dms_share:.1%}")
    (ROOT / "chem/odorants.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
