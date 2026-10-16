"""M7: uncertainty quantification, regime map and the headline P(SBD).

Deviation from PLAN.md section 11 (recorded in uq/m7_report.md): the surrogate is the validated Gate 0 analytic model,
not a 30-60 case CFD Latin hypercube (one sofa branch costs 1-2 h on 4 cores). The two Scenario A CFD branches are
used as a check that exposes what Gate 0 does not model (routing by posture and geometry).

Outputs
  (a) regime map: log10 R (equal emitted mass, inhalation-averaged, neighbour-type room air K = 1e-3 m^2/s) over the
      Silencer number of the audible comparator and the travel time, with the acoustic onset Si_onset = u_onset/u_h
      and the perceptual band |log R| < log(1 + Weber C) (concentration JND), Theorem 2 asymptote R -> 1.
  (b) first-order Sobol indices of log10 R by the given-data (binning) estimator on the Gate 0 Monte Carlo sample
      (the rejection sampling of silent/audible pairs rules out a Saltelli design), with bootstrap intervals.
  (c) headline P(SBD) in three layers: physical (P(R > 1)), perceptual (silent perceptibly worse / indistinguishable /
      audible perceptibly worse at the JND), and the memory layer from perception/selection.json.
Usage (repo root): python3 uq/run_m7.py -> figures/fig10_regime_uq.png, uq/results.json
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gate0"))
sys.path.insert(0, str(ROOT / "acoustics"))
import run_gate0 as g0  # noqa: E402
from model import Release, phase1, ratio  # noqa: E402  (gate0 model)
from regime import u_onset  # noqa: E402

P0 = g0.P0
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984"
SILENT_C, AUDIBLE_C, NEUTRAL_C = "#2a78d6", "#eb6834", "#c3c2b7"
JND = 1.0 + P0["weber_C"]  # concentration ratio at the olfactory just-noticeable difference
SEED = 20261016

SOBOL_INPUTS = {  # mc key: (label, log-transform)
    "K_turb": ("eddy diffusivity K", True), "u_room": ("room air speed", True),
    "L_neighbour": ("neighbour distance", False), "u_handoff": ("hand-off speed u_h", False),
    "P_th": ("sphincter onset pressure", True), "C_d": ("discharge coefficient", False),
    "g_reduced": ("buoyancy g′", False), "T_insp": ("inhalation time", False),
    "V_s": ("silent: volume", True), "T_s": ("silent: duration", True), "d_s": ("silent: orifice", True),
    "V_l": ("audible: volume", True), "T_l": ("audible: duration", True), "d_l": ("audible: orifice", True),
}


def regime_map():
    p = {**P0, "K_turb": 1e-3}
    u_adv = 0.1
    silent = g0.REF_SILENT
    T_sweep = np.geomspace(8.0, 0.05, 110)
    t_sweep = np.geomspace(0.5, 60.0, 90)
    Si = np.empty(T_sweep.size)
    R = np.empty((t_sweep.size, T_sweep.size))
    for j, T in enumerate(T_sweep):
        loud = Release(V=g0.V_LOUD, T=T, d=6.0e-3)
        Si[j] = phase1(loud, p)["Si"]
        for i, t in enumerate(t_sweep):
            R[i, j] = ratio(silent, loud, p, L=t * u_adv, u_adv=u_adv, basis="mass", metric="phi_inh")
    si_onset = u_onset(p) / p["u_handoff"]
    return {"Si": Si, "t": t_sweep, "log10R": np.log10(R), "Si_onset": float(si_onset),
            "Si_silent_ref": float(phase1(silent, p)["Si"])}


def sobol_first_order(x, y, bins=20, n_boot=200, rng=None):
    """Given-data estimator S_i = Var(E[Y | X_i]) / Var(Y) with quantile bins, bias-corrected, bootstrap 90 % CI."""
    rng = rng or np.random.default_rng(SEED)

    def est(xx, yy):
        edges = np.quantile(xx, np.linspace(0, 1, bins + 1))
        idx = np.clip(np.searchsorted(edges, xx, side="right") - 1, 0, bins - 1)
        means = np.bincount(idx, yy, bins) / np.maximum(np.bincount(idx, minlength=bins), 1)
        cnt = np.bincount(idx, minlength=bins)
        v = np.var(yy)
        s = np.sum(cnt * (means - yy.mean()) ** 2) / yy.size / v
        return s - (bins - 1) / yy.size  # remove the positive bias of binned conditional means
    s = est(x, y)
    boots = []
    for _ in range(n_boot):
        k = rng.integers(0, y.size, y.size)
        boots.append(est(x[k], y[k]))
    return float(s), [float(np.percentile(boots, 5)), float(np.percentile(boots, 95))]


def layers(R):
    lr = np.log10(R)
    j = np.log10(JND)
    rng = np.random.default_rng(SEED + 1)
    boot = [np.mean(rng.choice(R, R.size) > 1.0) for _ in range(400)]
    return {"P_SBD": float(np.mean(R > 1.0)), "P_SBD_90CI": [float(np.percentile(boot, 5)),
                                                           float(np.percentile(boot, 95))],
            "median_R": float(10 ** np.median(lr)),
            "P_silent_perceptibly_worse": float(np.mean(lr > j)),
            "P_indistinguishable": float(np.mean(np.abs(lr) <= j)),
            "P_audible_perceptibly_worse": float(np.mean(lr < -j))}


def memory_layer():
    sel = json.loads((ROOT / "perception/selection.json").read_text())
    rows = sorted(sel["base_rate_sweep"], key=lambda r: r["p_S_nb"])
    ps = np.array([r["p_S_nb"] for r in rows])
    bel = np.array([r["belief_bystander"] for r in rows])
    ok = np.isfinite(bel)
    out = {"truth_nominal": sel["nominal"]["bystander_living"]["truth"]["P_belief"]}
    for p_s in (0.93, 0.75, 0.5, 0.25, 0.1):
        out[f"belief_at_pS_{p_s}"] = float(np.interp(p_s, ps[ok], bel[ok]))
    return out


def figure(rm, sob, heads, out):
    plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
                         "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2,
                         "ytick.color": INK2, "text.color": INK, "font.size": 9, "axes.titlesize": 10,
                         "axes.titleweight": "bold", "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.9), constrained_layout=True,
                             gridspec_kw={"width_ratios": [1.25, 1.0, 1.05]})
    # (a) regime map
    ax = axes[0]
    j = np.log10(JND)
    norm = TwoSlopeNorm(vmin=-1.0, vcenter=0.0, vmax=1.0)
    m = ax.pcolormesh(rm["Si"], rm["t"], rm["log10R"], cmap=g0.DIVERGING, norm=norm, shading="auto",
                      rasterized=True)
    cs = ax.contour(rm["Si"], rm["t"], rm["log10R"], levels=[-j, j], colors=INK, linewidths=[0.9, 0.9],
                    linestyles=[(0, (3, 2))] * 2)
    ax.clabel(cs, fmt={-j: "JND", j: "JND"}, fontsize=7)
    ax.axvline(rm["Si_onset"], color=INK, lw=1.4)
    ax.text(rm["Si_onset"] * 1.06, 0.6, "acoustic onset\n(audible →)", fontsize=7.5, color=INK, va="bottom")
    ax.axvspan(rm["Si"].min(), rm["Si_onset"], color=SURFACE, alpha=0.6, lw=0, zorder=1.5)
    ax.text(rm["Si"].min() * 1.2, 40.0, "comparator not audible (S1):\nonly the right of the onset\nline is a "
            "silent-vs-audible pair", fontsize=7, color=INK2, va="top")
    for t_nom, lab in ((P0["L_own"] / P0["u_own_eff"], "own nose (nominal)"),
                       (P0["L_neighbour"] / P0["u_room"], "neighbour (nominal)")):
        ax.axhline(t_nom, color=INK, lw=0.9, ls=(0, (1, 1.5)), zorder=3)
        ax.text(rm["Si"].min() * 1.2, t_nom * 1.06, lab, fontsize=7.5, color=INK, va="bottom", zorder=3)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Silencer number of the audible release, Si = u₀/u_h")
    ax.set_ylabel("travel time to the nose (s)")
    ax.set_title("a  Regime map (equal mass, room air)", loc="left")
    cb = fig.colorbar(m, ax=ax, shrink=0.9, pad=0.01)
    cb.set_label("log₁₀ (C_silent / C_audible)")
    cb.ax.text(1.0, 1.02, "silent\ndeadlier", transform=cb.ax.transAxes, ha="center", va="bottom", fontsize=7,
               color="#9e2322")
    cb.ax.text(1.0, -0.02, "audible\nworse", transform=cb.ax.transAxes, ha="center", va="top", fontsize=7,
               color="#104281")
    # (b) Sobol first-order
    ax = axes[1]
    keys = sorted(sob["nb_conc"], key=lambda k: -sob["nb_conc"][k]["S1"])[:9]
    y = np.arange(len(keys))
    for off, tag, col, lab in ((0.2, "nb_conc", AUDIBLE_C, "as emitted"), (-0.2, "nb_mass", SILENT_C, "equal mass")):
        v = [max(sob[tag][k]["S1"], 0.0) for k in keys]
        lo = [max(sob[tag][k]["S1"], 0) - max(sob[tag][k]["CI90"][0], 0) for k in keys]
        hi = [max(sob[tag][k]["CI90"][1], 0) - max(sob[tag][k]["S1"], 0) for k in keys]
        ax.barh(y + off, v, 0.38, color=col, label=lab, zorder=2)
        ax.errorbar(v, y + off, xerr=[np.maximum(lo, 0), np.maximum(hi, 0)], fmt="none", ecolor=INK2,
                    elinewidth=0.8, capsize=2, zorder=3)
    ax.set_yticks(y, [SOBOL_INPUTS[k][0] for k in keys])
    ax.invert_yaxis()
    ax.set_xlabel("first-order Sobol index of log₁₀ R (neighbour)")
    ax.set_title("b  What decides the ratio", loc="left")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    # (c) layered headline
    ax = axes[2]
    names = [("nb_conc", "neighbour · as emitted"), ("nb_mass", "neighbour · equal mass"),
             ("own_conc", "own nose · as emitted"), ("own_mass", "own nose · equal mass"),
             ("nb_conc_denim", "neighbour · as emitted · denim")]
    y = np.arange(len(names))
    left = np.zeros(len(names))
    for key, col, lab in (("P_silent_perceptibly_worse", "#e34948", "silent perceptibly worse"),
                          ("P_indistinguishable", NEUTRAL_C, "indistinguishable (< JND)"),
                          ("P_audible_perceptibly_worse", SILENT_C, "audible perceptibly worse")):
        v = np.array([heads[n][key] for n, _ in names])
        ax.barh(y, v, 0.6, left=left, color=col, label=lab, zorder=2, edgecolor=SURFACE, linewidth=1.5)
        for yy, l0, vv in zip(y, left, v):
            if vv > 0.07:
                ax.text(l0 + vv / 2, yy, f"{vv:.2f}", ha="center", va="center", fontsize=7.5,
                        color=SURFACE if col != NEUTRAL_C else INK)
        left += v
    for yy, (n, _) in zip(y, names):
        ax.text(1.02, yy, f"P(R>1) = {heads[n]['P_SBD']:.2f}", va="center", fontsize=7.5, color=INK2)
    ax.set_yticks(y, [lab for _, lab in names])
    ax.invert_yaxis()
    ax.set_xlim(0, 1.32)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlabel("share of random silent/audible pairs")
    ax.set_title("c  Physics, then the nose", loc="left")
    ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.45, -0.13), ncol=2)
    fig.suptitle("Fig. 10 · Uncertainty and regimes: where a silent release could be deadlier, and how often a nose "
                 "could tell", x=0.01, ha="left", fontsize=10.5, fontweight="bold")
    fig.savefig(out, dpi=200)


def main():
    mc = g0.monte_carlo()
    rm = regime_map()
    outputs = {"nb_conc": "R_nb_conc_phi_inh_none", "nb_mass": "R_nb_mass_phi_inh_none",
               "own_conc": "R_own_conc_phi_inh_none", "own_mass": "R_own_mass_phi_inh_none",
               "nb_conc_denim": "R_nb_conc_phi_inh_denim"}
    heads = {k: layers(mc[v]) for k, v in outputs.items()}
    rng = np.random.default_rng(SEED)
    sob = {}
    for tag in ("nb_conc", "nb_mass", "own_conc"):
        y = np.log10(mc[outputs[tag]])
        sob[tag] = {}
        for k, (lab, lg) in SOBOL_INPUTS.items():
            x = np.log(mc[k]) if lg else mc[k]
            s, ci = sobol_first_order(x, y, rng=rng)
            sob[tag][k] = {"label": lab, "S1": s, "CI90": ci}
        sob[tag]["_sum_S1"] = float(sum(v["S1"] for v in sob[tag].values() if isinstance(v, dict)))
    wardrobe = {cl: layers(mc[f"R_nb_conc_phi_inh_{cl}"]) for cl in g0.CLOTHING}
    res = {"n_mc": int(mc["K_turb"].size), "JND_conc_ratio": JND, "regime_map": {
               "Si_onset": rm["Si_onset"], "Si_silent_ref": rm["Si_silent_ref"],
               "Si": rm["Si"].tolist(), "t": rm["t"].tolist(), "log10R": rm["log10R"].tolist()},
           "headline": heads, "wardrobe_nb_as_emitted": wardrobe, "sobol_first_order": sob,
           "memory_layer": memory_layer()}
    (ROOT / "uq").mkdir(exist_ok=True)
    (ROOT / "uq/results.json").write_text(json.dumps(res, indent=1))
    figure(rm, {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")} for k, v in sob.items()}, heads,
           ROOT / "figures/fig10_regime_uq.png")
    for k, v in heads.items():
        print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items()})
    for tag in sob:
        top = sorted(((v["S1"], v["label"]) for k, v in sob[tag].items() if isinstance(v, dict)), reverse=True)[:5]
        print(tag, "sum S1 %.2f" % sob[tag]["_sum_S1"], [(lab, round(s, 3)) for s, lab in top])
    print("Si_onset", round(rm["Si_onset"], 1), "Si_silent_ref", round(rm["Si_silent_ref"], 2))
    print("memory", res["memory_layer"])


if __name__ == "__main__":
    main()
