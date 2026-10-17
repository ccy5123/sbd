"""Chemistry layer, part 3: are the odorants conserved tracers over the 0-120 s of a passage?

Gas-phase loss: IUPAC recommended rate constants at 298 K (Atkinson et al. 2004, ACP 4:1461, Vol. I, SOx table:
reactions 85, 93, 94, 104, 105, 80, 83, 84, 146), cm3 molecule-1 s-1. DMS + OH is abstraction (4.8e-12) plus
addition in 1 bar air (1.7e-12). O3 + DMS is an upper limit; O3 + H2S and O3 + CH3SH are not evaluated by IUPAC.
Indoor oxidant levels: measured in an office by Fiorentino et al. 2023 (Atmos Environ 292:119398, Table 2 weighted
means OH 0.62e5-9.79e5 cm-3 over five experiments; daily mean O3 0.7-2.6 ppb). [ASSUMPTION] Worst case OH 1e6 cm-3
with O3 40 ppb (a well-ventilated room in summer); Cl 1e6 cm-3 only during hypochlorite cleaning; NO3 negligible.
Surface loss: no deposition velocity v_d is published for these gases indoors (null result); first-order loss
k = v_d * S/V with S/V = 3 m-1 is shown for a bracket of v_d.
Usage (repo root): python3 chem/reactivity.py -> chem/reactivity.json
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
K = {  # IUPAC k(298 K)
    "OH": {"H2S": 4.7e-12, "CH3SH": 3.3e-11, "DMS": 4.8e-12 + 1.7e-12},
    "Cl": {"H2S": 7.4e-11, "CH3SH": 2.0e-10, "DMS": 3.3e-10},
    "NO3": {"H2S": 1e-15, "CH3SH": 9.2e-13, "DMS": 1.1e-12},   # H2S value is an upper limit
    "O3": {"DMS": 1e-18},                                       # upper limit
}
PPB_TO_CM3 = 2.46e10  # molecules cm-3 per ppb at 298 K, 1 atm
SCENARIOS = {"office, measured low (Fiorentino 2023)": {"OH": 0.62e5, "O3": 0.7 * PPB_TO_CM3},
             "office, measured high (Fiorentino 2023)": {"OH": 9.79e5, "O3": 2.6 * PPB_TO_CM3},
             "upper bracket": {"OH": 1e6, "O3": 40 * PPB_TO_CM3},
             "hypochlorite cleaning": {"OH": 1e6, "O3": 10 * PPB_TO_CM3, "Cl": 1e6}}
WINDOW = 120.0  # s
S_OVER_V = 3.0  # m-1
V_DEP = (0.2, 0.05, 0.01, 0.002)  # cm/s


def main():
    out = {"gas_phase": {}, "deposition": {}}
    for sname, conc in SCENARIOS.items():
        out["gas_phase"][sname] = {}
        for gas in ("H2S", "CH3SH", "DMS"):
            k1 = sum(K[x].get(gas, 0.0) * c for x, c in conc.items())
            tau = 1 / k1
            lost = 1 - math.exp(-WINDOW / tau)
            out["gas_phase"][sname][gas] = {"lifetime_h": tau / 3600, "lost_in_120s": lost}
            print(f"{sname:40s} {gas:6s} lifetime {tau / 3600:9.1f} h   lost in 120 s {100 * lost:.3f} %")
    for v in V_DEP:
        k1 = v / 100 * S_OVER_V
        out["deposition"][f"v_d={v} cm/s"] = {"lifetime_s": 1 / k1, "lost_in_120s": 1 - math.exp(-WINDOW * k1)}
        print(f"deposition v_d {v:5.3f} cm/s: lifetime {1 / k1:8.0f} s, lost in 120 s {100 * (1 - math.exp(-WINDOW * k1)):.1f} %")
    (ROOT / "chem/reactivity.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
