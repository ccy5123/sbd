"""Fig. 16: routing decides. For every CFD scene and nose, (a) the equal-mass ratio R = OAV_silent / OAV_audible
(expected worst breath, 92 mL each) and (b) the as-emitted perceptual split from uq/routing_headline.json (CFD route x
Gate 0 volume pairs). The Gate 0 neighbour result without routing is shown for comparison.
Usage (repo root): python3 uq/fig_routing.py -> figures/fig16_routing.png
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984"
SILENT_C, NEUTRAL_C, WORSE_C = "#2a78d6", "#c3c2b7", "#e34948"
R_FLOOR = 1e-3  # equal-mass ratios below this (silent cloud never arrives) are drawn at the axis edge


def main():
    d = json.loads((ROOT / "uq/routing_headline.json").read_text())
    rows = [s for s in d["scenes"] if "120 s" not in s["scene"]]
    labels = [f"{s['scene']} · {s['nose']}" for s in rows]
    g0 = json.loads((ROOT / "uq/results.json").read_text())
    plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
                         "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                         "text.color": INK, "font.size": 8.5, "axes.titlesize": 10, "axes.titleweight": "bold",
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 0.36 * len(rows) + 2.2), sharey=True,
                                   constrained_layout=True, gridspec_kw={"width_ratios": [1, 1.25]})
    y = np.arange(len(rows))
    # scene bands
    scene_of = [s["scene"] for s in rows]
    for i, sc in enumerate(scene_of):
        if i == 0 or sc != scene_of[i - 1]:
            j = i
            while j + 1 < len(rows) and scene_of[j + 1] == sc:
                j += 1
            if (len(set(scene_of[:i])) % 2) == 1:
                for ax in (ax1, ax2):
                    ax.axhspan(i - 0.5, j + 0.5, color="#f0efea", zorder=0, lw=0)
    # (a) equal-mass ratio
    r = np.array([s["R_equal_mass"] if s["R_equal_mass"] is not None else np.nan for s in rows], float)
    clipped = r < R_FLOOR
    ax1.axvline(1.0, color=INK, lw=0.9)
    ax1.axvspan(1 / 1.28, 1.28, color=NEUTRAL_C, alpha=0.5, lw=0)
    ax1.scatter(r[~clipped], y[~clipped], s=28, color=np.where(r[~clipped] > 1, WORSE_C, SILENT_C), zorder=3)
    ax1.scatter(np.full(clipped.sum(), R_FLOOR), y[clipped], s=36, marker="<", color=SILENT_C, zorder=3)
    for yy in y[clipped]:
        ax1.text(R_FLOOR * 1.5, yy, "silent not arrived in window", fontsize=7, color=SILENT_C, va="center")
    ax1.set_xscale("log")
    ax1.set_xlim(R_FLOOR * 0.6, 20)
    ax1.set_yticks(y, labels)
    ax1.invert_yaxis()
    ax1.set_xlabel("R at equal mass (silent / audible, worst breath)")
    ax1.set_title("a  Same gas, different route", loc="left")
    ax1.text(1.5, -0.75, "silent stronger →", fontsize=7.5, color=WORSE_C, va="bottom")
    ax1.text(0.65, -0.75, "← audible stronger", fontsize=7.5, color=SILENT_C, va="bottom", ha="right")
    # (b) as emitted, perceptual split
    left = np.zeros(len(rows))
    for key, col, lab in (("P_silent_perceptibly_worse", WORSE_C, "silent perceptibly stronger"),
                          ("P_indistinguishable", NEUTRAL_C, "indistinguishable (< JND)"),
                          ("P_audible_perceptibly_worse", SILENT_C, "audible perceptibly stronger")):
        v = np.array([s[key] for s in rows])
        ax2.barh(y, v, 0.62, left=left, color=col, label=lab, zorder=2, edgecolor=SURFACE, linewidth=1.2)
        for yy, l0, vv in zip(y, left, v):
            if vv > 0.09:
                ax2.text(l0 + vv / 2, yy, f"{vv:.2f}", ha="center", va="center", fontsize=7,
                         color=SURFACE if col != NEUTRAL_C else INK)
        left += v
    for yy, s in zip(y, rows):
        ax2.text(1.02, yy, f"{s['P_R_gt_1']:.2f}", va="center", fontsize=7.5, color=INK2)
    ax2.text(1.02, -0.75, "P(R>1)", fontsize=7.5, color=INK2, va="bottom")
    nb = g0["headline"]["nb_conc"]["P_SBD"] if "headline" in g0 else d["gate0_neighbour_P_R_gt_1"]
    ax2.axvline(nb, color=INK, lw=0.9, ls=(0, (2, 2)), zorder=3)
    ax2.text(nb + 0.01, -0.75, f"analytic model, no routing: {nb:.2f}", fontsize=7, color=INK, va="bottom")
    ax2.set_xlim(0, 1.15)
    ax2.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax2.set_xlabel("share of passages as emitted")
    ax2.set_title("b  As emitted: does a nose tell the difference?", loc="left")
    ax2.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.45, -0.07 * 14 / len(rows)),
               ncol=3)
    fig.suptitle("Fig. 16 · Routing decides: silent vs audible across scenes", x=0.01, ha="left",
                 fontsize=10.5, fontweight="bold")
    out = ROOT / "figures/fig16_routing.png"
    fig.savefig(out, dpi=200)
    print("wrote", out)


if __name__ == "__main__":
    main()
