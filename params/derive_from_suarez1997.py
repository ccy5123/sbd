"""Derive per-passage volume and buoyancy (reduced gravity g') from Suarez et al. 1997, Table 1.

Table 1 (16 subjects, standard diet supplemented with pinto beans + lactulose, 4-h collection):
volume (mL / 4 h), number of passages, and % H2, CO2, CH4, O2, N2.
"""
import numpy as np

# subject: (vol_mL, passages, H2, CO2, CH4, O2, N2)   -- transcribed from Suarez et al. 1997, Table 1
T1 = [
    (106, 3, 22.7, 50.9, 0.008, 2.5, 23.7), (342, 5, 8.3, 37.5, 25.6, 3.2, 25.3),
    (328, 4, 29.5, 27.9, 0.005, 5.5, 37.2), (454, 6, 19.5, 32.2, 24.0, 2.8, 19.5),
    (817, 7, 12.0, 46.4, 28.5, 1.4, 11.7), (517, 6, 59.2, 19.9, 0.005, 2.7, 18.3),
    (394, 7, 49.2, 29.8, 0.20, 3.1, 17.7), (500, 5, 41.2, 25.0, 8.6, 3.0, 22.2),
    (129, 4, 38.8, 9.0, 0.005, 4.17, 48.0), (1657, 8, 31.6, 62.8, 0.002, 1.0, 5.4),
    (881, 9, 51.5, 29.2, 0.003, 2.9, 16.5), (785, 7, 54.5, 22.9, 0.005, 1.8, 20.6),
    (303, 3, 63.0, 27.0, 0.003, 2.1, 7.9), (343, 4, 14.7, 29.2, 0.006, 9.3, 46.6),
    (677, 4, 19.5, 58.8, 0.006, 3.5, 18.2), (1033, 5, 32.8, 46.8, 2.2, 3.4, 17.0),
]
M = np.array([2.016, 44.01, 16.04, 32.00, 28.013])  # g/mol: H2, CO2, CH4, O2, N2
M_AIR, R, P = 28.965, 8.314462618, 101325.0
T_GAS, T_ROOM, G = 310.15, 295.15, 9.80665

arr = np.array(T1, dtype=float)
per_passage = arr[:, 0] / arr[:, 1]
frac = arr[:, 2:] / arr[:, 2:].sum(axis=1, keepdims=True)
M_mix = frac @ M
rho_gas = P * M_mix * 1e-3 / (R * T_GAS)
rho_air = P * M_AIR * 1e-3 / (R * T_ROOM)
g_red = G * (rho_air - rho_gas) / rho_air
g_red_iso = G * (rho_air - P * M_mix * 1e-3 / (R * T_ROOM)) / rho_air  # gas cooled to room temperature

if __name__ == "__main__":
    print("per-passage volume (mL): min %.0f  median %.0f  max %.0f  mean %.0f" %
          (per_passage.min(), np.median(per_passage), per_passage.max(), per_passage.mean()))
    print("composition sum (%):", np.round(arr[:, 2:].sum(axis=1), 1))
    print("M_mix (g/mol):", np.round(M_mix, 2))
    print("rho_air(22C) = %.4f kg/m3" % rho_air)
    print("g' at 37 C (m/s^2): min %.2f median %.2f max %.2f" % (g_red.min(), np.median(g_red), g_red.max()))
    print("g' after cooling to room T (m/s^2): min %.2f median %.2f max %.2f" %
          (g_red_iso.min(), np.median(g_red_iso), g_red_iso.max()))
    print("fraction negatively buoyant at 37 C: %.2f ; after cooling: %.2f" % ((g_red < 0).mean(), (g_red_iso < 0).mean()))
