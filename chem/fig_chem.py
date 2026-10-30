"""Fig. 14: the chemistry of the passage.
(a) Share of the summed odour activity value carried by H2S, methanethiol and DMS, for two measured compositions
    (Suarez 1998, Tangerman 2009) under three threshold sets (chem/odorants.py).
(b) Reduced gravity of the 16 measured compositions (Suarez 1997) against their CO2 content, at 37 C (dry basis) and
    after cooling to room temperature (chem/buoyancy.py). Water saturation shifts the 37 C values by -0.04 to +0.29 m/s2
    (stated in the caption, not drawn).
Figure in FIGSTYLE v1.2 (paper, double column). Gases take PALETTE[0:3]; the two temperatures in (b) take the next
two slots (PALETTE[3], vermilion = 37 C; PALETTE[4], sky blue = cooled) so that no colour means two things.
Usage (repo root, figure venv, see HANDOFF): /root/figenv/bin/python chem/fig_chem.py
  -> figures/chemistry_paper.svg/.png
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from figstyle import *  # noqa: E402,F401,F403  (FIGSTYLE v1.2, verbatim)

sys.path.insert(0, str(ROOT / "chem"))
from buoyancy import CASES, per_passage  # noqa: E402
from odorants import COMPOSITION, GASES, THRESHOLDS, oavs  # noqa: E402

GAS_C = {"H2S": PALETTE[0], "MeSH": PALETTE[1], "DMS": PALETTE[2]}
GAS_TEXT = {"H2S": "white", "MeSH": INK, "DMS": INK}  # value labels: the higher-contrast of white / black per fill
GAS_LABEL = {"H2S": "H$_2$S", "MeSH": "Methanethiol", "DMS": "Dimethyl sulfide"}
N = r"$\mathit{n}$"
ROWS = [(f"Suarez 1998, {N} = 87", "all (n = 87)"), (f"Tangerman 2009, {N} = 28", "Tangerman 2009 (n = 28)")]
THR_LABEL = {"trained panel (Nagata 2003)": "trained panel",
             "population (Amoore & Hautala 1983; DMS: Wilby 1969)": "population",
             "lowest literature (Tangerman 2009)": "lowest reported"}
SMALL = MEDIA["paper"]["small"]


def panel_shares(ax):
    labels, y = [], 0
    for clabel, ckey in ROWS:
        for tkey, tlabel in THR_LABEL.items():
            o = oavs(COMPOSITION[ckey], THRESHOLDS[tkey])
            tot = sum(o.values())
            left = 0.0
            for g in GASES:
                w = 100 * o[g] / tot
                ax.barh(y, w, left=left, height=0.62, color=GAS_C[g], edgecolor="white",
                        linewidth=MEDIA["paper"]["axis"], label=GAS_LABEL[g] if y == 0 else None)
                if w >= 12:
                    allow_overlap(ax.text(left + w / 2, y, f"{w:.0f} %", ha="center", va="center", fontsize=SMALL,
                                          color=GAS_TEXT[g], fontweight="bold"))
                left += w
            labels.append(f"{clabel}\n{tlabel} thresholds")
            y += 1
        y += 0.4
    ys = [0, 1, 2, 3.4, 4.4, 5.4]
    ax.set_yticks(ys, labels)
    ax.set_ylim(5.4 + 0.5, -0.5)  # inverted: first composition on top
    ax.set_xlim(0, 100)
    ax.set_xlabel(axis_label("Share of the summed odour activity value", "%"))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)


def panel_buoyancy(ax):
    dry = per_passage(CASES["dry"])
    ax.axhline(0, color=MUTED, lw=MEDIA["paper"]["axis"], zorder=0)
    ax.text(5.5, 0.1, "Rises ↑", ha="left", va="bottom")
    ax.text(5.5, -0.1, "Sinks ↓", ha="left", va="top")
    ax.set_xlim(4, 66)
    ax.plot(dry["co2"], dry["g_red"], ls="none", marker=MARKERS[3], color=PALETTE[3], label="At 37 °C")
    ax.plot(dry["co2"], dry["cooled"], ls="none", marker=MARKERS[4], color=PALETTE[4],
            label="Cooled to room temperature")
    ax.set_xlabel(axis_label("CO$_2$ in the passage", "% of dry gas"))
    ax.set_ylabel(axis_label(r"Reduced gravity $\mathit{g}'$", "m s-2"))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)


def main():
    apply_style("paper")
    fig, axes = new_figure("double", aspect=0.42, ncols=2, gridspec_kw={"width_ratios": [1.15, 1]})
    panel_shares(axes[0])
    panel_buoyancy(axes[1])
    panel_labels(axes)
    out = save_figure(fig, "chemistry_paper", outdir=ROOT / "figures")
    print("wrote", *out)


if __name__ == "__main__":
    main()
