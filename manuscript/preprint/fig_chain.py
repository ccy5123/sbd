"""Fig. 2 of the preprint: the mechanistic chain from release to memory, with the quantity each stage hands on and
where each theorem acts. Pure drawing, no data.
Figure in FIGSTYLE v1.2 (paper, double column). Colour = part of the chain (physics, perception, memory), in PALETTE
order; box text sits on the boxes on purpose (allow_overlap), and a check below keeps every line inside its box.
Usage (repo root, figure venv, see HANDOFF): /root/figenv/bin/python manuscript/preprint/fig_chain.py
  -> figures/mechanism_chain_paper.svg/.png
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib.colors import to_rgba  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from figstyle import *  # noqa: E402,F401,F403  (FIGSTYLE v1.2, verbatim)

COLOR_MAP = {"phys": PALETTE[0], "perc": PALETTE[1], "mind": PALETTE[2]}

STAGES = [  # (title, detail, kind)
    ("Release", "volume " + var("V") + ",\nduration " + var("T") + ",\norifice " + var("d") + " → " + var("u", "0"),
     "phys"),
    ("Sound", "lip-reed onset\n" + var("u", "0") + " > " + var("u", "onset") + "\n≈ 42 " + unit("m s-1")
     + "\n85 % never\noscillate", "phys"),
    ("Near field", "momentum\npre-dilution\n" + var("D", "1") + " ≈ " + var(r"\beta") + " Si", "phys"),
    ("Transport", r"$\mathit{C} = \mathit{G} * \mathit{q}$" + "\n(linear)\nrouting by\nbody plumes,\nfurniture",
     "phys"),
    ("Nose", "worst breath\n" + r"$\mathit{I} = \mathit{k}\,\mathrm{OAV}_{\mathrm{b}}^{\,\mathit{n}}$", "perc"),
    ("Noticing", "heard (" + var("H") + ")\nor smelled\n(" + var("S") + ")?", "perc"),
    ("Memory", r"$\mathit{N} = \mathit{H} \cup \mathit{S}$:" + "\nonly noticed\npassages\ncount", "mind"),
]
NOTES = {  # stage index -> annotation under the box
    2: "the only\nexception to\nTheorem 1",
    3: "Theorems 1–2:\nno higher peak;\nrelease mode\nforgotten",
    4: "JND: ratio 1.28",
    6: "Theorem 3:\nevery\nremembered\nsilent passage\nstank",
}
SPANS = ((0, 3, "Physics: Sections 2.2–2.4, 4.1–4.4", "phys"),  # (first stage, last stage, label, kind)
         (4, 5, "Perception: Sections 4.5–4.6", "perc"),
         (6, 6, "Memory: 2.5, 4.7", "mind"))
W, H, Y0 = 0.9, 0.98, 0.76  # box width, height, bottom (data units; one stage per unit)
Y_BAR = Y0 + H + 0.13
SMALL = MEDIA["paper"]["small"]
PITCH = 1.3  # baseline-to-baseline distance in units of the font size


def stack(ax, x, y, text, size=SMALL, **kw):
    """Centred lines with their first baseline at data (x, y), one Text per line at a fixed pitch. (Multi-line Text
    in matplotlib 3.11 Agg raises lines with descenders, so the spacing came out uneven.)"""
    return [ax.annotate(line, (x, y), xytext=(0, -k * PITCH * size), textcoords="offset points", ha="center",
                        va="baseline", fontsize=size, annotation_clip=False, **kw)
            for k, line in enumerate(text.split("\n"))]


def figure():
    apply_style("paper")
    fig, ax = new_figure("double", aspect=0.3)
    ax.set_xlim(0, 7)
    ax.set_ylim(0.0, Y_BAR + 0.22)
    ax.axis("off")
    inside = []
    for i, (title, detail, kind) in enumerate(STAGES):
        x = i + (1 - W) / 2
        col = COLOR_MAP[kind]
        box = FancyBboxPatch((x, Y0), W, H, boxstyle="round,pad=0,rounding_size=0.05", fc=to_rgba(col, 0.15),
                             ec=col, lw=MEDIA["paper"]["line"])
        ax.add_patch(box)
        texts = stack(ax, x + W / 2, Y0 + H - 0.16, title, size=MEDIA["paper"]["base"], fontweight="bold")
        texts += stack(ax, x + W / 2, Y0 + H - 0.33, detail)
        allow_overlap(*texts)  # text written on its box on purpose
        inside += [(t, box) for t in texts]
        if i < len(STAGES) - 1:
            ax.add_patch(FancyArrowPatch((x + W, Y0 + H / 2), (x + 1, Y0 + H / 2), arrowstyle="->",
                                         mutation_scale=6, color=MUTED, lw=MEDIA["paper"]["axis"],
                                         shrinkA=0, shrinkB=0))
        if i in NOTES:
            stack(ax, x + W / 2, Y0 - 0.15, NOTES[i])
    for first, last, label, kind in SPANS:
        x0, x1 = first + (1 - W) / 2, last + (1 + W) / 2
        ax.plot([x0, x1], [Y_BAR, Y_BAR], color=COLOR_MAP[kind], lw=2 * MEDIA["paper"]["line"],
                solid_capstyle="butt")
        ax.text(x1 if first == last else (x0 + x1) / 2, Y_BAR + 0.06, label, ha="right" if first == last else "center",
                va="bottom")
    return fig, inside


def check_inside(fig, inside):
    """The overlap check exempts text on its box, so check here that every box text stays inside its box."""
    fig.draw_without_rendering()
    r = fig.canvas.get_renderer()
    bad = []
    for t, box in inside:
        tb, bb = t.get_window_extent(r), box.get_window_extent(r)
        if tb.x0 < bb.x0 or tb.x1 > bb.x1 or tb.y0 < bb.y0 or tb.y1 > bb.y1:
            bad.append(t.get_text().replace("\n", " / "))
    if bad:
        raise FigstyleLayoutError("text outside its box:\n  " + "\n  ".join(bad))


def main():
    fig, inside = figure()
    check_inside(fig, inside)
    out = save_figure(fig, "mechanism_chain_paper", outdir=ROOT / "figures")
    print("wrote", *out)


if __name__ == "__main__":
    main()
