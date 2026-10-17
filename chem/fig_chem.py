"""Fig. 14: the chemistry of the passage.
(a) Share of the summed odour activity value carried by H2S, methanethiol and DMS, for two measured compositions
    (Suarez 1998, Tangerman 2009) under three threshold sets (chem/odorants.py).
(b) Reduced gravity of the 16 measured compositions (Suarez 1997) against their CO2 content, at 37 C (dry basis) and
    after cooling to room temperature (chem/buoyancy.py). Water saturation shifts the 37 C values by -0.04 to +0.29 m/s2
    (stated in the caption, not drawn).
Usage (repo root): python3 chem/fig_chem.py -> figures/fig14_chemistry.png
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "chem"))
from buoyancy import CASES, per_passage
from odorants import COMPOSITION, GASES, THRESHOLDS, oavs

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984"
GAS_C = {"H2S": "#2a78d6", "MeSH": "#eb6834", "DMS": "#1baf7a"}  # categorical slots 1-3, fixed order
GAS_LABEL = {"H2S": "H$_2$S", "MeSH": "methanethiol", "DMS": "dimethyl sulfide"}
ROWS = [("Suarez 1998, n = 87", "all (n = 87)"), ("Tangerman 2009, n = 28", "Tangerman 2009 (n = 28)")]
THR_LABEL = {"trained panel (Nagata 2003)": "trained panel",
             "population (Amoore & Hautala 1983; DMS: Wilby 1969)": "population",
             "lowest literature (Tangerman 2009)": "lowest reported"}


def panel_shares(ax):
    labels, y = [], 0
    for clabel, ckey in ROWS:
        for tkey, tlabel in THR_LABEL.items():
            o = oavs(COMPOSITION[ckey], THRESHOLDS[tkey])
            tot = sum(o.values())
            left = 0.0
            for g in GASES:
                w = 100 * o[g] / tot
                ax.barh(y, w, left=left, height=0.62, color=GAS_C[g], edgecolor=SURFACE, linewidth=2,
                        label=GAS_LABEL[g] if y == 0 else None)
                if w >= 12:
                    ax.text(left + w / 2, y, f"{w:.0f} %", ha="center", va="center", fontsize=8, color="white",
                            fontweight="bold")
                left += w
            labels.append(f"{clabel}\n{tlabel} thresholds")
            y += 1
        y += 0.4
    ys = [0, 1, 2, 3.4, 4.4, 5.4]
    ax.set_yticks(ys, labels, fontsize=7.6)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("share of the summed odour activity value (%)")
    ax.set_title("a  which molecule carries the odour", loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3, frameon=False, fontsize=8)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)


def panel_buoyancy(ax):
    dry = per_passage(CASES["dry"])
    ax.axhline(0, color=MUTED, lw=1)
    ax.text(5.5, 0.1, "rises ↑", color=INK2, fontsize=8, ha="left", va="bottom")
    ax.text(5.5, -0.1, "sinks ↓", color=INK2, fontsize=8, ha="left", va="top")
    ax.set_xlim(4, 66)
    ax.plot(dry["co2"], dry["g_red"], "o", ms=8, color=INK, mec=SURFACE, mew=2, label="at 37 °C")
    ax.plot(dry["co2"], dry["cooled"], "o", ms=8, mfc=SURFACE, mec=INK2, mew=1.6, label="cooled to room temperature")
    ax.set_xlabel("CO$_2$ in the passage (% of dry gas)")
    ax.set_ylabel("reduced gravity $g'$ (m s$^{-2}$)")
    ax.set_title("b  what makes a passage rise or sink", loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False, fontsize=8)
    ax.grid(axis="y", color="#e6e5e1", lw=0.8)
    ax.set_axisbelow(True)


def main():
    plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
                         "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2,
                         "ytick.color": INK2, "text.color": INK, "font.size": 9, "axes.titlesize": 10,
                         "axes.titleweight": "bold", "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.4), constrained_layout=True, gridspec_kw={"width_ratios": [1.15, 1]})
    panel_shares(axes[0])
    panel_buoyancy(axes[1])
    fig.suptitle("Fig. 14 · The chemistry of the passage", x=0.01, ha="left", fontweight="bold", fontsize=11)
    out = ROOT / "figures/fig14_chemistry.png"
    fig.savefig(out, dpi=200)
    print("wrote", out)


if __name__ == "__main__":
    main()
