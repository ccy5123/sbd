"""Module 2 - acoustics: when is a release silent, inaudible, masked or audible?

Chain (plan section 7):
  1. Oscillation onset (defines S1). The anal canal is treated as a soft-tissue self-oscillating flow valve
     (lip-reed / vocal-fold analogue; Ancalle et al. 2021). It oscillates when the transmural driving pressure
     exceeds a threshold P_th. The driving pressure is linked to the release through the orifice equation,
     dp = 0.5 rho (u0 / C_d)^2, with u0 = Q / A.
  2. Source strength. The valve modulates the volume flow; harmonic n carries an amplitude
     q_n = alpha_mod * Q * n^(harm_slope/6.02). It radiates as a monopole into a half space (the body and seat act
     as a baffle): p_n = 2 rho_air omega_n q_n / (4 pi r), with p_n as the peak amplitude.
  3. Audibility (defines S2). Every harmonic lies below the ISO 226 threshold of hearing T_f(f).
  4. Masking (defines S3). Every harmonic lies below max(T_f, the masked threshold). The masked threshold is the
     background spectral density plus the critical ratio (~17 dB below 500 Hz; Hawkins & Stevens 1950). The
     background spectrum is octave-band levels with a fixed slope, scaled to the room's dB(A).
"""
from __future__ import annotations

import numpy as np

S1, S2, S3, AUDIBLE = 0, 1, 2, 3
LABELS = {S1: "S1 · no oscillation (physically silent)", S2: "S2 · oscillating, below hearing threshold",
          S3: "S3 · audible in quiet, masked here", AUDIBLE: "audible"}
OCTAVES = np.array([31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000])
P_REF = 2e-5


def a_weighting(f):
    """IEC 61672-1 A-weighting (dB), analytic form."""
    f = np.asarray(f, dtype=float)
    f2 = f * f
    ra = (12194.0**2 * f2**2) / ((f2 + 20.6**2) * np.sqrt((f2 + 107.7**2) * (f2 + 737.9**2)) * (f2 + 12194.0**2))
    return 20 * np.log10(ra) + 2.0


def erb(f):
    """Equivalent rectangular bandwidth, Glasberg & Moore (1990): 24.7 (4.37 f/kHz + 1)."""
    return 24.7 * (4.37 * np.asarray(f, dtype=float) / 1000.0 + 1.0)


def threshold_of_hearing(f, table: dict):
    """Interpolate T_f (dB SPL) in log frequency from a {Hz: dB} table; clamp at the ends."""
    fs = np.array(sorted(table), dtype=float)
    ts = np.array([table[k] for k in sorted(table)], dtype=float)
    return np.interp(np.log10(f), np.log10(fs), ts)


def background_spectral_density(f, LA_total: float, slope_db_oct: float):
    """Spectral density level (dB re 20 uPa / Hz) of a background with octave levels L = L0 + slope*log2(f/1000),
    scaled so that its A-weighted total equals LA_total."""
    rel = slope_db_oct * np.log2(OCTAVES / 1000.0)
    la_rel = 10 * np.log10(np.sum(10 ** ((rel + a_weighting(OCTAVES)) / 10)))
    L0 = LA_total - la_rel
    L_oct = L0 + slope_db_oct * np.log2(np.asarray(f, dtype=float) / 1000.0)
    return L_oct - 10 * np.log10(0.7071 * np.asarray(f, dtype=float))  # octave bandwidth = 0.707 f


def critical_ratio(f, table: dict):
    """Critical ratio (dB) interpolated in log frequency from a {Hz: dB} table."""
    fs = np.array(sorted(table), dtype=float)
    return np.interp(np.log10(f), np.log10(fs), np.array([table[k] for k in sorted(table)], dtype=float))


def masked_threshold(f, LA_total, slope, cr_table):
    """Masked threshold of a tone (dB SPL) = background spectral density + critical ratio."""
    return background_spectral_density(f, LA_total, slope) + critical_ratio(f, cr_table)


def driving_pressure(Q, d, rho_gas, C_d):
    u0 = Q / (np.pi * d**2 / 4.0)
    return 0.5 * rho_gas * (u0 / C_d) ** 2


def harmonic_spl(Q, f0, p: dict, r: float | None = None):
    """SPL (dB) of harmonics n = 1..n_harm at distance r; returns (freqs, spl) with spl shaped (..., n_harm)."""
    r = p["r_listener"] if r is None else r
    n = np.arange(1, int(p["n_harm"]) + 1)
    f = f0 * n
    q1 = p["alpha_mod"] * np.asarray(Q, dtype=float)[..., None]
    qn = q1 * n ** (p["harm_slope"] / 6.0206)
    p_peak = 2.0 * p["rho_air"] * 2 * np.pi * f * qn / (4 * np.pi * r)
    spl = 20 * np.log10(p_peak / np.sqrt(2) / P_REF) - p["A_cloth"]
    return f, spl


def classify(Q, d, p: dict, background: str | None = "living", r: float | None = None, f0: float | None = None):
    """Vectorised S1/S2/S3/AUDIBLE classification for flow rate Q (m^3/s) and orifice diameter d (m)."""
    Q, d = np.broadcast_arrays(np.asarray(Q, dtype=float), np.asarray(d, dtype=float))
    f0 = p["f0_flatus"] if f0 is None else f0
    rho_gas = p["rho_air"] * (1.0 - p["g_reduced"] / p["g"])
    osc = driving_pressure(Q, d, rho_gas, p["C_d"]) > p["P_th"]
    f, spl = harmonic_spl(Q, f0, p, r)
    above_hearing = np.any(spl > threshold_of_hearing(f, p["T_f"]), axis=-1)
    out = np.where(osc, np.where(above_hearing, AUDIBLE, S2), S1)
    if background is not None:
        mt = masked_threshold(f, p[f"bg_{background}"], p["bg_slope"][background], p["CR"])
        above_mask = np.any(spl > np.maximum(threshold_of_hearing(f, p["T_f"]), mt), axis=-1)
        out = np.where((out == AUDIBLE) & ~above_mask, S3, out)
    return out


def u_onset(p: dict) -> float:
    """Exit velocity (Q/A) at oscillation onset: the acoustic replacement for Gate 0's u_audible placeholder."""
    rho_gas = p["rho_air"] * (1.0 - p["g_reduced"] / p["g"])
    return p["C_d"] * np.sqrt(2.0 * p["P_th"] / rho_gas)
