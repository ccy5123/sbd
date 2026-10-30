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
Figure in FIGSTYLE v1.2 (paper, double column): (a) and (b) on top, (c) across the bottom.
Usage (repo root, figure venv, see HANDOFF): /root/figenv/bin/python uq/run_m7.py
  -> figures/regime_uq_paper.svg/.png, uq/results.json
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np
from matplotlib.colors import TwoSlopeNorm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gate0"))
sys.path.insert(0, str(ROOT / "acoustics"))
import run_gate0 as g0
from model import Release, phase1, ratio  # gate0 model
from regime import u_onset

sys.path.insert(0, str(ROOT))
from figstyle import *  # noqa: E402,F401,F403  (FIGSTYLE v1.2, verbatim)

P0 = g0.P0
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


PLOT_LABELS = {  # figure labels for SOBOL_INPUTS (the JSON keeps the SOBOL_INPUTS labels)
    "K_turb": "Eddy diffusivity " + var("K"), "u_room": "Room air speed", "L_neighbour": "Neighbour distance",
    "u_handoff": "Hand-off speed " + var("u", "h"), "P_th": "Sphincter onset pressure", "C_d": "Discharge coefficient",
    "g_reduced": "Buoyancy " + var("g") + "′", "T_insp": "Inhalation time",
    "V_s": "Silent: volume", "T_s": "Silent: duration", "d_s": "Silent: orifice",
    "V_l": "Audible: volume", "T_l": "Audible: duration", "d_l": "Audible: orifice",
}
SOBOL_SERIES = (("nb_conc", "As emitted"), ("nb_mass", "Equal mass"))  # colour, hatch follow the index
LAYERS = (("P_silent_perceptibly_worse", "Silent perceptibly stronger", 0.85),
          ("P_indistinguishable", "Indistinguishable (below the JND)", 0.5),
          ("P_audible_perceptibly_worse", "Silent perceptibly weaker", 0.15))  # CMAP_DIV position: sign of log10 R
HEAD_NAMES = (("nb_conc", "Neighbour, as emitted"), ("nb_mass", "Neighbour, equal mass"),
              ("own_conc", "Own nose, as emitted"), ("own_mass", "Own nose, equal mass"),
              ("nb_conc_denim", "Neighbour, as emitted, denim"))


def figure(rm, sob, heads):
    """Fig. 10 in FIGSTYLE v1.2 (paper, double column): (a) regime map and (b) Sobol indices on top, (c) layers below."""
    apply_style("paper")
    fig, axs = new_figure("double", aspect=0.78, nrows=2, ncols=2, gridspec_kw={"height_ratios": [1.45, 1]})
    gs = axs[1, 0].get_gridspec()
    for a in axs[1]:
        a.remove()
    axes = [axs[0, 0], axs[0, 1], fig.add_subplot(gs[1, :])]
    cmap = matplotlib.colormaps[CMAP_DIV]
    r_lab = var("R")
    # (a) regime map
    ax = axes[0]
    j = np.log10(JND)
    norm = TwoSlopeNorm(vmin=-1.0, vcenter=0.0, vmax=1.0)
    m = ax.pcolormesh(rm["Si"], rm["t"], rm["log10R"], cmap=CMAP_DIV, norm=norm, shading="auto", rasterized=True)
    cs = ax.contour(rm["Si"], rm["t"], rm["log10R"], levels=[-j, j], colors=INK, linewidths=0.8,
                    linestyles=[LINESTYLES[1]] * 2)
    ax.axvline(rm["Si_onset"], color=INK, lw=1.2)
    ax.axvspan(rm["Si"].min(), rm["Si_onset"], color=MUTED, alpha=0.3, lw=0, zorder=1.5)  # grey: not a pair
    for t_nom in (P0["L_own"] / P0["u_own_eff"], P0["L_neighbour"] / P0["u_room"]):
        ax.axhline(t_nom, color=INK, lw=0.8, ls=LINESTYLES[3], zorder=3)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(axis_label("Silencer number of the audible release, Si = " + var("u", "0") + "/" + var("u", "h")))
    ax.set_ylabel(axis_label("Travel time to the nose", "s"))
    cb = fig.colorbar(m, ax=ax, pad=0.02, ticks=[-1, -0.5, 0, 0.5, 1])
    cb.set_label("log$_{10}$ " + r_lab + " (positive: silent stronger)")
    # labels sit on the map (pale region, high contrast); placed after the layout so the JND label follows the line
    fig.draw_without_rendering()
    x0 = rm["Si"].min() * 1.15
    allow_overlap(ax.text(x0, 50.0, "Comparison release\nnot audible", va="top"))
    allow_overlap(ax.text(rm["Si_onset"] * 0.93, 0.62, "Acoustic\nonset", ha="right", va="bottom"))
    for t_nom, lab in ((P0["L_own"] / P0["u_own_eff"], "Releaser's nose (nominal)"),
                       (P0["L_neighbour"] / P0["u_room"], "Neighbour (nominal)")):
        allow_overlap(ax.text(x0, t_nom * 1.08, lab, va="bottom"))
    seg = max((p for lv, segs in zip(cs.levels, cs.allsegs) if lv > 0 for p in segs), key=len, default=None)
    if seg is not None and len(seg) > 1:  # "JND" along the longest stretch of the contour, rotated to its slope
        k = int(0.6 * len(seg))
        p0, p1 = ax.transData.transform([seg[k - 1], seg[min(k + 1, len(seg) - 1)]])
        ang = (np.degrees(np.arctan2(p1[1] - p0[1], p1[0] - p0[0])) + 90) % 180 - 90  # keep the text upright
        allow_overlap(ax.text(*seg[k], "JND", rotation=ang, rotation_mode="anchor", ha="center", va="bottom"))
    # (b) Sobol first-order
    ax = axes[1]
    keys = sorted(sob["nb_conc"], key=lambda k: -sob["nb_conc"][k]["S1"])[:9]
    y = np.arange(len(keys))
    for i, (tag, lab) in enumerate(SOBOL_SERIES):
        off = 0.2 if i == 0 else -0.2
        v = [max(sob[tag][k]["S1"], 0.0) for k in keys]
        lo = [max(sob[tag][k]["S1"], 0) - max(sob[tag][k]["CI90"][0], 0) for k in keys]
        hi = [max(sob[tag][k]["CI90"][1], 0) - max(sob[tag][k]["S1"], 0) for k in keys]
        ax.barh(y - off, v, 0.38, color=PALETTE[i], label=lab, hatch=None if i == 0 else "////",
                edgecolor="white", lw=0, zorder=2)
        ax.errorbar(v, y - off, xerr=[np.maximum(lo, 0), np.maximum(hi, 0)], fmt="none", ecolor=INK,
                    elinewidth=0.6, capsize=1.5, zorder=3)
    ax.set_yticks(y, [PLOT_LABELS[k] for k in keys])
    ax.invert_yaxis()
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel(axis_label("First-order Sobol index of log$_{10}$ " + r_lab))
    ax.legend(loc="lower right")
    # (c) layered headline
    ax = axes[2]
    y = np.arange(len(HEAD_NAMES))
    left = np.zeros(len(HEAD_NAMES))
    for key, lab, pos in LAYERS:
        v = np.array([heads[n][key] for n, _ in HEAD_NAMES])
        ax.barh(y, v, 0.62, left=left, color=cmap(pos), label=lab, zorder=2, edgecolor=INK, linewidth=0.5)
        for yy, l0, vv in zip(y, left, v):
            if vv > 0.07:  # value labels inside the bars
                allow_overlap(ax.text(l0 + vv / 2, yy, f"{vv:.2f}", ha="center", va="center"))
        left += v
    for yy, (n, _) in zip(y, HEAD_NAMES):
        ax.text(1.02, yy, var("P") + "(" + r_lab + f" > 1) = {heads[n]['P_SBD']:.2f}", va="center")
    ax.set_yticks(y, [lab for _, lab in HEAD_NAMES])
    ax.invert_yaxis()
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 1.17)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.spines["bottom"].set_bounds(0, 1)
    ax.set_xlabel(axis_label("Share of random silent/audible pairs"))
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.3), ncol=3)
    for ax, letter in zip(axes, "abc"):  # one call each: panel_labels takes an array or a single axes
        panel_labels(ax, start=letter)
    out = save_figure(fig, "regime_uq_paper", outdir=ROOT / "figures")
    plt.close(fig)
    return out


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
    figure(rm, {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")} for k, v in sob.items()}, heads)
    for k, v in heads.items():
        print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items()})
    for tag in sob:
        top = sorted(((v["S1"], v["label"]) for k, v in sob[tag].items() if isinstance(v, dict)), reverse=True)[:5]
        print(tag, f"sum S1 {sob[tag]['_sum_S1']:.2f}", [(lab, round(s, 3)) for s, lab in top])
    print("Si_onset", round(rm["Si_onset"], 1), "Si_silent_ref", round(rm["Si_silent_ref"], 2))
    print("memory", res["memory_layer"])


if __name__ == "__main__":
    main()
