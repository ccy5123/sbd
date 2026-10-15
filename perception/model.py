"""Module 4 (plan section 9) - perception: from nose concentration to what the owner of the nose experiences.

Pieces:
  * puff_series      Gaussian passage of the cloud at a nose: C(t) = C_pk exp(-(t - t_a)^2 / (2 sigma_t^2)).
  * breath_doses     the nose samples only while inhaling; each breath delivers its flow-weighted mean
                     concentration (sinusoidal inspiratory flow, duty cycle Ti/Ttot). The perceived peak is the worst
                     breath. A warned listener can hold their breath for H seconds from the warning onwards.
  * intensity        Stevens power law I = k OAV^n and a Weber-Fechner (log) category scale I = k_w log10(OAV).
  * adaptation       perceived intensity under sustained exposure: A(t) = a_inf + (1 - a_inf) exp(-t / tau).
  * preparedness     perceived ratio silent/audible = gamma * R^n (Stevens); the belief holds where it exceeds 1.
                     Break-even gamma* = R^-n.
"""
from __future__ import annotations

import numpy as np


def puff_series(t, c_peak, t_arrival, sigma_t):
    return c_peak * np.exp(-0.5 * ((t - t_arrival) / sigma_t) ** 2)


def inspiratory_flow(t, period, ti_frac, v_tidal, phase=0.0, hold=None, recovery_gain=1.0):
    """Instantaneous inspiratory flow q(t) (m^3/s). phase in [0, 1) shifts the cycle; hold = (t0, t1) suppresses
    breathing during [t0, t1) and restarts with an inhalation at t1 whose tidal volume is scaled by recovery_gain."""
    ti = ti_frac * period
    q = np.zeros_like(t, dtype=float)
    tau = np.mod(t / period + phase, 1.0) * period
    inhaling = tau < ti
    q[inhaling] = 0.5 * np.pi * v_tidal / ti * np.sin(np.pi * tau[inhaling] / ti)
    if hold is not None:
        t0, t1 = hold
        q[(t >= t0) & (t < t1)] = 0.0
        after = t >= t1
        tau2 = np.mod(t[after] - t1, period)
        q[after] = np.where(tau2 < ti, 0.5 * np.pi * v_tidal / ti * np.sin(np.pi * tau2 / ti), 0.0)
        first = (t >= t1) & (t < t1 + ti)
        q[first] *= recovery_gain
    return q


def breath_doses(t, c, q):
    """Split the record into inhalations; return per-breath mean concentration and inhaled volume."""
    on = q > 0
    edges = np.flatnonzero(np.diff(on.astype(int)))
    starts = list(np.flatnonzero(on[:1])) + [e + 1 for e in edges if not on[e]]
    means, vols = [], []
    dt = t[1] - t[0]
    for s in starts:
        e = s
        while e < len(q) and q[e] > 0:
            e += 1
        v = np.sum(q[s:e]) * dt
        if v > 0:
            means.append(np.sum(q[s:e] * c[s:e]) * dt / v)
            vols.append(v)
    return np.array(means), np.array(vols)


def worst_breath(t, c, q):
    m, _ = breath_doses(t, c, q)
    return float(m.max()) if m.size else 0.0


def stevens(oav, n, k=1.0):
    return k * np.power(np.maximum(oav, 0.0), n)


def log_scale(oav, k_w=1.0):
    return k_w * np.log10(np.maximum(oav, 1e-12))


def adaptation(t_exposed, tau, a_inf):
    return a_inf + (1.0 - a_inf) * np.exp(-np.maximum(t_exposed, 0.0) / tau)


def gamma_star(R, n):
    """Break-even expectation factor: the belief holds iff gamma > R^-n (Stevens law)."""
    return np.power(R, -n)


def p_belief(R, n, gamma):
    """P(perceived silent > perceived audible) for an array of physical ratios R and expectation factor gamma."""
    gamma = np.atleast_1d(gamma)
    return np.mean(gamma[:, None] * np.power(R[None, :], n) > 1.0, axis=1)
