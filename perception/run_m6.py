"""M6: perception layer figures and numbers.

Fig. 7  'The breath-hold strategy'  - what a breathing nose actually samples from a passing puff, and whether a warned
                                       listener can dodge it by holding their breath.
Fig. 11 'The preparedness break-even' - how large an expectation (prediction-error) amplification gamma must be for the
                                       belief to survive the physics; gamma* = R^-n.
Usage (repo root): python3 perception/run_m6.py  -> figures/fig7_breath_hold.png, figures/fig11_gamma.png,
                                                    perception/results.json
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gate0"))
sys.path.insert(0, str(ROOT / "perception"))
import run_gate0 as g0  # noqa: E402
from model import load_params, nominal  # noqa: E402  (gate0 model)
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("perc", ROOT / "perception/model.py")
pm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pm)

P = nominal(load_params())
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984"
BLUE, ORANGE, AQUA, RED = "#2a78d6", "#eb6834", "#1baf7a", "#e34948"
plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "text.color": INK, "font.size": 9, "axes.titlesize": 10, "axes.titleweight": "bold",
                     "axes.spines.top": False, "axes.spines.right": False})
PERIOD = 60.0 / P["f_breath"]
TI = P["Ti_Ttot"]
VT = P["V_tidal"]
DT = 0.01


def worst_ratio(ta, st, phase, hold=None, gain=1.0, t_end=None):
    """Worst-breath concentration relative to the instantaneous peak."""
    t_end = t_end or (ta + 6 * st + 2 * PERIOD + (hold[1] if hold else 0))
    t = np.arange(0.0, t_end, DT)
    c = pm.puff_series(t, 1.0, ta, st)
    q = pm.inspiratory_flow(t, PERIOD, TI, VT, phase, hold, gain)
    return pm.worst_breath(t, c, q)


def fig7(mc):
    audible_nb = np.c_[mc["ta_nb_l"], mc["st_nb_l"]]
    ta_med, st_med = np.median(audible_nb, axis=0)
    st_lo, st_hi = np.percentile(mc["st_nb_l"], [10, 90])
    phases = np.linspace(0, 1, 60, endpoint=False)
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.1), constrained_layout=True,
                             gridspec_kw={"width_ratios": [1.25, 1, 1.15]})
    # (a) time series
    ax = axes[0]
    t = np.arange(0, ta_med + 5 * st_med, DT)
    c = pm.puff_series(t, 1.0, ta_med, st_med)
    ax.plot(t, c, color=INK, lw=2, label="concentration at the nose")
    for k, (ph, col) in enumerate(((0.0, BLUE), (0.35, ORANGE), (0.7, AQUA))):
        q = pm.inspiratory_flow(t, PERIOD, TI, VT, ph)
        on = q > 0
        ax.fill_between(t, -0.08 - 0.07 * k, -0.02 - 0.07 * k, where=on, color=col, lw=0, step="mid")
        w = worst_ratio(ta_med, st_med, ph)
        ax.axhline(w, color=col, lw=1.2, ls=(0, (4, 2)))
        ax.text(t[-1] * 1.02, 0.80 - 0.09 * k, f"worst breath {w:.2f}", color=col, fontsize=7.5, va="center")
    ax.text(0.3, -0.27, "inhalations for three breathing phases", fontsize=7.5, color=INK2)
    ax.set_ylim(-0.32, 1.08); ax.set_xlim(0, t[-1] * 1.32)
    ax.set_xlabel("time after the release (s)"); ax.set_ylabel("C / C_peak")
    ax.set_title(f"a  A typical audible puff at the neighbour\n(arrival {ta_med:.0f} s, passage σ_t = {st_med:.1f} s)",
                 loc="left")
    # (b) worst breath vs phase (unwarned)
    ax = axes[1]
    out = {}
    for st, col, lab in ((st_lo, AQUA, "short passage (10th pct)"), (st_med, INK, "median passage"),
                         (st_hi, BLUE, "long passage (90th pct)")):
        r = np.array([worst_ratio(ta_med, st, ph) for ph in phases])
        ax.plot(phases, r, color=col, lw=1.8, label=f"{lab}, σ_t {st:.1f} s")
        out[lab] = {"sigma_t": float(st), "mean_worst_ratio": float(r.mean()), "P_worst_below_half": float(np.mean(r < 0.5))}
    ax.set_ylim(0, 1.02); ax.set_xlim(0, 1)
    ax.set_xlabel("breathing phase at the moment of release (cycles)"); ax.set_ylabel("worst breath / C_peak")
    ax.set_title("b  Unwarned: luck of the breathing phase", loc="left")
    ax.legend(frameon=False, fontsize=7.5, loc="lower left")
    # (c) warned breath-hold over the Monte Carlo of audible releases
    ax = axes[2]
    rng = np.random.default_rng(7)
    idx = rng.choice(len(audible_nb), 300, replace=False)
    holds = np.arange(0, 61, 3.0)
    p_dodge, med_ratio = [], []
    for H in holds:
        rs = []
        for i in idx:
            ta, st = audible_nb[i]
            ph = rng.uniform()
            hold = (P["t_react"], P["t_react"] + H) if H > 0 else None
            rs.append(worst_ratio(ta, st, ph, hold, P["recovery_gain"]))
        rs = np.array(rs)
        p_dodge.append(np.mean(rs < 0.1)); med_ratio.append(np.median(rs))
    ax.plot(holds, p_dodge, color=ORANGE, lw=2, marker="o", ms=4, label="P(dodge): worst breath < 10 % of peak")
    ax.plot(holds, med_ratio, color=INK, lw=1.6, ls=(0, (4, 2)), label="median worst breath / C_peak")
    ax.axvspan(P["H_max"] * 0 + 30, 90, color="#e4e3df", lw=0)
    ax.text(31, 0.93, "beyond typical voluntary\nbreath-hold (≈30–90 s)", fontsize=7.5, color=INK2, va="top")
    ax.set_xlim(0, 60); ax.set_ylim(0, 1.02)
    ax.set_xlabel("breath-hold duration H after hearing it (s)")
    ax.set_title("c  Warned: hold your breath (audible releases only)", loc="left")
    ax.legend(frameon=False, fontsize=7.5, loc="center left", bbox_to_anchor=(0.0, 0.45))
    fig.suptitle("Fig. 7 · The breath-hold strategy — the nose samples only while inhaling; the ear buys time to stop",
                 x=0.01, ha="left", fontsize=10, fontweight="bold")
    fig.savefig(ROOT / "figures/fig7_breath_hold.png", dpi=200)
    plt.close(fig)
    h_half = float(np.interp(0.5, p_dodge, holds)) if max(p_dodge) >= 0.5 else None
    return {"neighbour_audible_median_arrival_s": float(ta_med), "median_sigma_t_s": float(st_med),
            "unwarned": out, "warned_hold_s": holds.tolist(), "warned_P_dodge": [float(x) for x in p_dodge],
            "hold_for_50pct_dodge_s": h_half}


SCEN = [("R_nb_conc_phi_inh_none", "neighbour · as emitted", BLUE),
        ("R_own_conc_phi_inh_none", "own nose · as emitted", ORANGE),
        ("R_nb_mass_phi_inh_none", "neighbour · equal mass", AQUA),
        ("R_nb_conc_phi_inh_denim", "neighbour · as emitted · denim", RED)]


def fig11(mc):
    n = P["n_stevens"]
    gammas = np.geomspace(0.7, 4.0, 200)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.2, 4.3), constrained_layout=True)
    out = {}
    for key, lab, col in SCEN:
        R = mc[key]
        pb = pm.p_belief(R, n, gammas)
        gstar = float(pm.gamma_star(np.median(R), n))
        a1.plot(gammas, pb, color=col, lw=2, label=f"{lab}: γ* = {gstar:.2f}")
        a1.plot(gstar, 0.5, "o", color=col, ms=6, mec=SURFACE, mew=1.5)
        ns = np.linspace(0.15, 0.7, 40)
        a2.plot(ns, [pm.gamma_star(np.median(R), x) for x in ns], color=col, lw=2, label=lab)
        out[lab] = {"median_R": float(np.median(R)), "gamma_star_median": gstar,
                    "P_belief_gamma1": float(pm.p_belief(R, n, [1.0])[0]),
                    "P_belief_gamma1.5": float(pm.p_belief(R, n, [1.5])[0])}
    a1.axhline(0.5, color=MUTED, lw=0.8, ls=(0, (3, 3)))
    a1.axvline(1.0, color=INK, lw=0.8)
    a1.text(1.01, 0.03, "no expectation effect", fontsize=7.5, color=INK2, rotation=90, va="bottom")
    a1.set_xscale("log"); a1.set_xticks([0.7, 1, 1.5, 2, 3, 4]); a1.set_xticklabels(["0.7", "1", "1.5", "2", "3", "4"])
    a1.set_ylim(0, 1); a1.set_xlabel("γ, perceived-intensity amplification for an unwarned (silent) exposure")
    a1.set_ylabel("P(silent perceived as worse)")
    a1.set_title(f"a  How much surprise does the belief need? (Stevens n = {n})", loc="left")
    a1.legend(frameon=False, fontsize=7.5, loc="lower right")
    a2.axvspan(P.get("n_lo", 0.2), P.get("n_hi", 0.6), color="#e4e3df", lw=0)
    a2.axhline(1.0, color=INK, lw=0.8)
    a2.set_xlabel("Stevens exponent n"); a2.set_ylabel("break-even γ* at the median pair")
    a2.set_title("b  Break-even vs the steepness of the intensity law", loc="left")
    a2.set_ylim(0.6, 1.8)
    fig.suptitle("Fig. 11 · The preparedness break-even: γ* = R^(−n). Belief survives whenever unwarned noses amplify by more"
                 " than γ*", x=0.01, ha="left", fontsize=10, fontweight="bold")
    fig.savefig(ROOT / "figures/fig11_gamma.png", dpi=200)
    plt.close(fig)
    return out


def main():
    mc = g0.monte_carlo(n=6000)
    res = {"fig7": fig7(mc), "fig11": fig11(mc), "n_mc": int(mc["V_s"].size)}
    (ROOT / "perception/results.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
