"""Gate 0 analytic order-of-magnitude model (Module 0 of the research plan).

Chain: release (V, T, d) -> near-field momentum/buoyancy dilution (phase 1)
       -> hand-off to ambient flow (CBL / room air)
       -> advection + turbulent puff growth to a nose (phase 2)
       -> receptor concentration (instantaneous peak and inhalation-averaged).

All concentrations are returned as phi = X_receptor / X_source (mole-fraction ratio),
so they apply to any odorant carried passively with the flatus (H2S, CH3SH, DMS).

Key physical idea (derived in gate0_report.md, section 2): for any momentum-conserving
release - steady jet, starting jet or puff, laminar or turbulent - the dilution reached
by the time the cloud's self-induced velocity has decayed to the ambient velocity u_h
scales as D_1 ~ beta * u0/u_h. The governing near-field parameter is therefore the
velocity ratio Si = u0_eff/u_h (the "Silencer number"), not the Reynolds number.

Conservative choices (biased AGAINST hypothesis H1, so that any surviving silent-release
penalty is robust):
  * turbulent-jet constants are used even for laminar (silent) releases, which
    over-states silent-release mixing;
  * the receptor is assumed to sit on the cloud centreline for both releases;
  * centreline (not cross-section-averaged) jet concentrations are used for the loud jet.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml
from scipy.special import erf

PARAMS_PATH = Path(__file__).resolve().parents[1] / "params" / "params.yaml"
TWO_PI_15 = (2.0 * np.pi) ** 1.5


def load_params(path: Path = PARAMS_PATH) -> dict:
    """Return {group: {name: entry}} where entry has value/low/high/units/status."""
    with open(path) as fh:
        return yaml.safe_load(fh)


def nominal(params: dict) -> dict:
    """Flatten to {name: nominal value}."""
    return {k: v["value"] for group in params.values() for k, v in group.items()}


def source_mole_fraction_ppb(c_umol_per_L: float, T_gas: float, p: float = 101325.0) -> float:
    """Convert a molar concentration (umol/L) in flatus to a mole fraction in ppbv."""
    molar_volume_L = 8.314462618 * T_gas / p * 1e3  # L/mol
    return c_umol_per_L * 1e-6 * molar_volume_L * 1e9


@dataclass
class Release:
    V: float  # emitted volume, m^3
    T: float  # release duration, s
    d: float  # effective orifice diameter, m

    @property
    def u0(self) -> float:
        return 4.0 * self.V / (np.pi * self.d**2 * self.T)

    def reynolds(self, nu_gas: float) -> float:
        return self.u0 * self.d / nu_gas


def effective_source(rel: Release, clothing: str, p: dict) -> tuple[float, float, float | None]:
    """Momentum sink of clothing.

    Returns (u_eff, d_eff, dilution_cap). For porous trousers the gas leaves the fabric at
    the Darcy velocity set by the (upper-bound) stagnation pressure of the impinging jet,
    u_perm = a * (0.5 rho u0^2) / 125 Pa, where a is the air permeability at 125 Pa.
    The source area grows accordingly (mass conservation). A skirt is an open-bottom
    mixing chamber: the free jet dilutes at most to the enclosed volume.
    """
    u0 = rel.u0
    if clothing in ("none", "skirt"):
        cap = p["V_skirt"] / rel.V if clothing == "skirt" else None
        return u0, rel.d, cap
    a = {"denim": p["a_denim"], "leggings": p["a_leggings"]}[clothing]
    dp = 0.5 * p["rho_air"] * u0**2
    u_eff = min(u0, a * dp / 125.0)
    area = (rel.V / rel.T) / max(u_eff, 1e-12)
    return u_eff, float(np.sqrt(4.0 * area / np.pi)), None


def phase1(rel: Release, p: dict, clothing: str = "none") -> dict:
    """Near-field dilution until the cloud's self-induced velocity decays to u_handoff."""
    u_h = p["u_handoff"]
    u_eff, d_s, cap = effective_source(rel, clothing, p)
    rho_ratio = 1.0 - p["g_reduced"] / p["g"]  # rho_0 / rho_a
    d_star = d_s * np.sqrt(rho_ratio)

    D_mom, x_h, regime = 1.0, 0.0, "no-momentum"
    if u_eff > u_h:
        M0 = u_eff**2 * np.pi * d_s**2 / 4.0  # kinematic momentum flux, m^4/s^2
        G = p["Gamma_sj"]
        x_f = G * M0**0.25 * rel.T**0.5  # starting-jet front at end of release
        u_f = G**2 * np.sqrt(M0) / (2.0 * x_f)  # front velocity at end of release
        if u_f <= u_h:  # hand-off during the jet phase
            x_h = G**2 * np.sqrt(M0) / (2.0 * u_h)
            D_mom = x_h / (p["K_c"] * d_star)
            regime = "starting-jet"
        else:  # jet becomes a puff; puff velocity ~ x^-3, puff volume ~ x^3
            x_h = x_f * (u_f / u_h) ** (1.0 / 3.0)
            D_mom = x_f / (p["K_c"] * d_star) * (x_h / x_f) ** 3
            regime = "puff"
        D_mom = max(1.0, D_mom)

    # buoyant thermal: r = alpha z, w = c_th sqrt(B)/z with c_th = sqrt(3/(2 pi alpha^3))/2
    a_t = p["alpha_th"]
    B = p["g_reduced"] * rel.V
    c_th = 0.5 * np.sqrt(3.0 / (2.0 * np.pi * a_t**3))
    z_h = c_th * np.sqrt(B) / u_h
    D_buoy = max(1.0, (4.0 / 3.0) * np.pi * a_t**3 * z_h**3 / rel.V)

    D1 = max(D_mom, D_buoy, 1.0)
    if cap is not None:
        D1 = min(D1, max(cap, 1.0))
        x_h = 0.0  # jet is confined under the skirt
    return {"D1": D1, "D_mom": D_mom, "D_buoy": D_buoy, "x_h": x_h, "u_eff": u_eff,
            "Si": u_eff / u_h, "regime": regime}


def phase2(V_h: float, t_travel: float, K: float, u_adv: float, T_insp: float) -> tuple[float, float]:
    """Gaussian puff of initial volume V_h advected for t_travel with eddy diffusivity K.

    Returns (g_inst, g_inh): peak concentration relative to the hand-off concentration,
    instantaneous and averaged over one inspiration of duration T_insp.
    """
    sigma0 = V_h ** (1.0 / 3.0) / np.sqrt(2.0 * np.pi)  # same peak as a uniform cloud of V_h
    sigma = np.sqrt(sigma0**2 + 2.0 * K * t_travel)
    g_inst = (sigma0 / sigma) ** 3
    sigma_t = sigma / u_adv  # passage time scale at a fixed nose
    f_inh = np.sqrt(2.0 * np.pi) * sigma_t / T_insp * erf(T_insp / (2.0 * np.sqrt(2.0) * sigma_t))
    return g_inst, g_inst * min(1.0, f_inh)


def receptor(rel: Release, p: dict, L: float, u_adv: float, clothing: str = "none",
             jet_toward_receptor: bool = False) -> dict:
    """Concentration at a nose at path length L (m) reached at transport speed u_adv (m/s)."""
    ph1 = phase1(rel, p, clothing)
    L_rem = max(0.0, L - ph1["x_h"]) if jet_toward_receptor else L
    t2 = L_rem / u_adv
    g_inst, g_inh = phase2(rel.V * ph1["D1"], t2, p["K_turb"], u_adv, p["T_insp"])
    phi_inst = g_inst / ph1["D1"]
    phi_inh = g_inh / ph1["D1"]
    return {**ph1, "t_travel": t2, "phi_inst": phi_inst, "phi_inh": phi_inh,
            "D_total": 1.0 / phi_inst, "Re": rel.reynolds(p["nu_gas"]), "u0": rel.u0}


def oav(phi: float, p: dict) -> float:
    """Summed odour activity value of H2S + CH3SH + DMS at the receptor."""
    total = 0.0
    for gas in ("H2S", "CH3SH", "DMS"):
        x0 = source_mole_fraction_ppb(p[f"c_{gas}"], p["T_gas"])
        total += x0 * phi / p[gas]
    return total


def ratio(rel_s: Release, rel_l: Release, p: dict, L: float, u_adv: float, basis: str,
          metric: str = "phi_inst", clothing: str = "none", jet_toward_receptor: bool = False) -> float:
    """C_silent / C_loud at the receptor.

    basis 'mass': equal emitted odorant mass  -> compare phi / V
    basis 'conc': equal source concentration  -> compare phi
    """
    rs = receptor(rel_s, p, L, u_adv, clothing, jet_toward_receptor)[metric]
    rl = receptor(rel_l, p, L, u_adv, clothing, jet_toward_receptor)[metric]
    if basis == "mass":
        return (rs / rel_s.V) / (rl / rel_l.V)
    if basis == "conc":
        return rs / rl
    raise ValueError(basis)
