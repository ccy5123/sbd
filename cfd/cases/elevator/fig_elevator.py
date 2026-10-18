"""Fig. 15: the elevator whodunit (scenario C), from cfd/cases/elevator/results.json.
(a, b) Expected worst-breath OAV (trained-panel thresholds) at each occupant's nose within 60 s, silent vs audible,
       for a front-row and a back-row culprit; lines mark the trained-panel threshold (OAV 1) and the attentive
       population threshold (OAV 20).
(c)    Probability that onlookers identify the culprit from who reacted, for two observers and two culprit
       behaviours; the bar label is the probability that no one reacts at all. Chance is 0.25.
Usage (repo root): python3 cfd/cases/elevator/fig_elevator.py -> figures/fig15_elevator.png
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984"
MODE_C = {"silent": "#2a78d6", "audible": "#eb6834"}
ROLES = {"FL": {"FL": "culprit", "FR": "beside", "BL": "behind", "BR": "diagonal\nbehind"},
         "BL": {"BL": "culprit", "BR": "beside", "FL": "in front", "FR": "diagonal\nin front"}}
POP = 1 / 0.05  # attentive population threshold in trained-panel OAV (params thr_scale_typ)


def panel_noses(ax, res, culprit, title):
    names = list(ROLES[culprit])
    x = np.arange(len(names))
    for k, mode in enumerate(("silent", "audible")):
        v = [max(res["branches"][f"{culprit}_{mode}"][n]["worst_breath_OAV_mean"], 1e-3) for n in names]
        ax.bar(x + (k - 0.5) * 0.38, v, width=0.36, color=MODE_C[mode], edgecolor=SURFACE, linewidth=2, label=mode)
    ax.set_yscale("log")
    ax.set_ylim(0.1, 100)
    for y, lab in ((1, "trained-panel threshold"), (POP, "untrained, attentive")):
        ax.axhline(y, color=MUTED, lw=1, ls="--")
        ax.text(len(names) - 0.55, y * 1.08, lab, ha="right", va="bottom", fontsize=7.5, color=INK2,
                bbox={"fc": SURFACE, "ec": "none", "pad": 1.0}, zorder=5)
    ax.set_xticks(x, [ROLES[culprit][n] for n in names])
    ax.set_ylabel("worst-breath OAV within 60 s")
    ax.set_title(title, loc="left")


def panel_attribution(ax, res):
    combos = [("attentive, Amoore thresholds", "stays still", "attentive,\nculprit still"),
              ("attentive, Amoore thresholds", "acts along", "attentive,\nculprit acts"),
              ("distracted (everyday)", "stays still", "distracted,\nculprit still"),
              ("distracted (everyday)", "acts along", "distracted,\nculprit acts")]
    x = np.arange(len(combos))
    for k, mode in enumerate(("silent", "audible")):
        for i, (obs, beh, _) in enumerate(combos):
            a = res["attribution"].get(f"{mode} | {obs} | culprit {beh}")
            if a is None:
                continue
            xi = i + (k - 0.5) * 0.38
            ax.bar(xi, a["P_correct"], width=0.36, color=MODE_C[mode], edgecolor=SURFACE, linewidth=2,
                   label=mode if i == 0 else None)
            ax.text(xi, a["P_correct"] + 0.02, f"{100 * a['P_no_one_reacts']:.0f}%", ha="center", va="bottom",
                    fontsize=7, color=INK2)
    ax.axhline(0.25, color=MUTED, lw=1, ls="--")
    ax.text(-0.45, 0.26, "chance", ha="left", va="bottom", fontsize=7.5, color=INK2,
            bbox={"fc": SURFACE, "ec": "none", "pad": 1.0}, zorder=5)
    ax.set_ylim(0, 1)
    ax.set_xticks(x, [c[2] for c in combos], fontsize=8)
    ax.set_ylabel("P(culprit identified)")
    ax.set_title("c  can the others tell? (label: no one reacts)", loc="left")


def main():
    res = json.loads((ROOT / "cfd/cases/elevator/results.json").read_text())
    plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
                         "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2,
                         "ytick.color": INK2, "text.color": INK, "font.size": 9, "axes.titlesize": 10,
                         "axes.titleweight": "bold", "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(14.0, 4.4), constrained_layout=True,
                             gridspec_kw={"width_ratios": [1, 1, 1.15]})
    panel_noses(axes[0], res, "FL", "a  culprit in the front row")
    panel_noses(axes[1], res, "BL", "b  culprit in the back row")
    panel_attribution(axes[2], res)
    axes[0].legend(loc="upper left", frameon=False)
    fig.suptitle("Fig. 15 · Elevator whodunit: four standing occupants, 630 kg car, fan off", x=0.01, ha="left",
                 fontweight="bold", fontsize=11)
    out = ROOT / "figures/fig15_elevator.png"
    fig.savefig(out, dpi=200)
    print("wrote", out)


if __name__ == "__main__":
    main()
