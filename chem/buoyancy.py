"""Chemistry layer, part 2: what makes a passage rise or sink? Decomposition of the reduced gravity
g' = g (rho_air - rho_gas) / rho_air into a thermal and a compositional part, with and without water vapour.

Compositions: Suarez et al. 1997 Table 1 (16 subjects; % H2, CO2, CH4, O2, N2 by gas chromatography, i.e. dry basis),
as in params/derive_from_suarez1997.py. Air at 22 C, 50 % RH. Flatus leaves at 37 C; whether it is saturated with
water vapour has not been measured [ASSUMPTION: bracketed between dry and saturated, p_w(37 C) = 6.28 kPa].
  thermal part       : g (1 - T_air/T_gas) for gas of air's molar mass
  compositional part : g (M_air - M_gas) / M_air at equal temperature
Usage (repo root): python3 chem/buoyancy.py -> chem/buoyancy.json
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "params"))
from derive_from_suarez1997 import M_AIR, T1, T_GAS, T_ROOM, G, M, P

M_W = 18.015
P_W_37 = 6280.0                  # saturation vapour pressure at 37 C (Pa)
P_SAT_22 = 2645.0                # saturation vapour pressure at 22 C (Pa)
P_W_22 = 0.5 * P_SAT_22          # 50 % RH at 22 C (Pa)


def molar_mass(frac_dry, x_w):
    return (1 - x_w) * (frac_dry @ M) + x_w * M_W


def main():
    arr = np.array(T1, dtype=float)
    frac = arr[:, 2:] / arr[:, 2:].sum(axis=1, keepdims=True)
    x_w_air = P_W_22 / P
    m_air = (1 - x_w_air) * M_AIR + x_w_air * M_W
    rho_air = P * m_air / (8.314462618 * T_ROOM)
    out = {}
    for label, x_w in (("dry", 0.0), ("saturated at 37 C", P_W_37 / P)):
        m_gas = molar_mass(frac, x_w)
        rho_gas = P * m_gas / (8.314462618 * T_GAS)
        g_red = G * (rho_air - rho_gas) / rho_air
        thermal = G * (1 - T_ROOM / T_GAS)
        comp = G * (m_air - m_gas) / m_air
        # cooled to room temperature: composition alone remains; excess water condenses (capped at saturation)
        cooled = G * (m_air - molar_mass(frac, min(x_w, P_SAT_22 / P))) / m_air
        out[label] = {"g_reduced_median": float(np.median(g_red)), "g_reduced_min": float(g_red.min()),
                      "g_reduced_max": float(g_red.max()), "fraction_sinking_hot": float((g_red < 0).mean()),
                      "thermal_part": float(thermal), "compositional_median": float(np.median(comp)),
                      "compositional_min": float(comp.min()), "compositional_max": float(comp.max()),
                      "fraction_sinking_after_cooling": float((cooled < 0).mean()),
                      "M_gas_median": float(np.median(m_gas))}
        o = out[label]
        print(f"{label:18s} g' median {o['g_reduced_median']:+.2f} ({o['g_reduced_min']:+.2f} to {o['g_reduced_max']:+.2f})"
              f" m/s2; thermal {o['thermal_part']:+.2f}; compositional median {o['compositional_median']:+.2f}"
              f" ({o['compositional_min']:+.2f} to {o['compositional_max']:+.2f}); sinking hot {o['fraction_sinking_hot']:.2f},"
              f" after cooling {o['fraction_sinking_after_cooling']:.2f}; M median {o['M_gas_median']:.2f} g/mol")
    co2 = arr[:, 3]
    out["corr_g_CO2"] = float(np.corrcoef(co2, G * (m_air - molar_mass(frac, 0.0)) / m_air)[0, 1])
    print(f"corr(composition part, %CO2) = {out['corr_g_CO2']:.2f}")
    (ROOT / "chem/buoyancy.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
