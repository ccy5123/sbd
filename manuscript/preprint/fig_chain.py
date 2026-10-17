"""Fig. 2 of the preprint: the mechanistic chain from release to memory, with the quantity each stage hands on and
where each theorem acts. Pure drawing, no data.
Usage (repo root): python3 manuscript/preprint/fig_chain.py -> manuscript/preprint/figs/fig2_chain.png
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984"
PHYS, PERC, MIND = "#e4eefb", "#fde9d6", "#e3f4ec"  # stage tints: physics, perception, memory
EDGE = {"phys": "#2a78d6", "perc": "#eb6834", "mind": "#1baf7a"}

STAGES = [  # (title, detail, kind)
    ("Release", "volume $V$, duration $T$,\norifice $d$ → $u_0$", "phys"),
    ("Sound", "lip-reed onset\n$u_0 > u_\\mathrm{onset}$ ≈ 30 m/s\n79 % never oscillate", "phys"),
    ("Near field", "momentum\npre-dilution\n$D_1 \\approx \\beta\\,\\mathrm{Si}$", "phys"),
    ("Transport", "$C = G * q$ (linear)\nrouting by body\nplumes, furniture", "phys"),
    ("Nose", "worst breath\n$I = k\\,\\mathrm{OAV}_b^{\\,n}$", "perc"),
    ("Noticing", "heard ($H$)\nor smelled ($S$)?", "perc"),
    ("Memory", "$N = H \\cup S$:\nonly noticed\npassages count", "mind"),
]
NOTES = {  # stage index -> annotation under the box
    2: "the only exception\nto Theorem 1",
    3: "Theorems 1–2: no\nhigher peak; release\nmode forgotten",
    4: "JND: ratio 1.28",
    6: "Theorem 3: every\nremembered silent\npassage stank",
}


def main():
    plt.rcParams.update({"figure.facecolor": SURFACE, "savefig.facecolor": SURFACE, "font.size": 9, "text.color": INK})
    fig, ax = plt.subplots(figsize=(12.5, 3.2))
    ax.set_xlim(0, 7)
    ax.set_ylim(0.55, 3.15)
    ax.axis("off")
    w, h, y0 = 0.86, 1.25, 1.35
    fill = {"phys": PHYS, "perc": PERC, "mind": MIND}
    for i, (title, detail, kind) in enumerate(STAGES):
        x = i + 0.07
        ax.add_patch(FancyBboxPatch((x, y0), w, h, boxstyle="round,pad=0.02,rounding_size=0.06", fc=fill[kind],
                                    ec=EDGE[kind], lw=1.4))
        ax.text(x + w / 2, y0 + h - 0.2, title, ha="center", va="center", fontsize=10, fontweight="bold")
        ax.text(x + w / 2, y0 + h / 2 - 0.12, detail, ha="center", va="center", fontsize=7.4, color=INK2,
                linespacing=1.25)
        if i < len(STAGES) - 1:
            ax.add_patch(FancyArrowPatch((x + w + 0.005, y0 + h / 2), (x + 1 - 0.005, y0 + h / 2),
                                         arrowstyle="-|>", mutation_scale=11, color=MUTED, lw=1.2))
        if i in NOTES:
            ax.text(x + w / 2, y0 - 0.12, NOTES[i], ha="center", va="top", fontsize=7.2, color=INK2,
                    style="italic", linespacing=1.2)
    for x0, x1, label, kind in ((0.07, 3.93, "physics: Sections 2.2–2.4, 4.1–4.4, 4.6", "phys"),
                                (4.07, 5.93, "perception: Section 4.5", "perc"),
                                (6.07, 6.93, "memory: 2.5, 4.7", "mind")):
        ax.plot([x0, x1], [2.86, 2.86], color=EDGE[kind], lw=2.2, solid_capstyle="butt")
        ax.text((x0 + x1) / 2, 2.97, label, ha="center", va="bottom", fontsize=8, color=EDGE[kind])
    out = ROOT / "manuscript/preprint/figs/fig2_chain.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=200, bbox_inches="tight", pad_inches=0.05)
    print("wrote", out)


if __name__ == "__main__":
    main()
