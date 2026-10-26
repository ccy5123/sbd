"""Figure 1 of the contest paper: the two path-traced snapshots (render_clouds.py) side by side, with speech bubbles,
nose values and a cloud legend. FIGSTYLE v1.2, paper, onehalf width.
FIGSTYLE override (user's choice, 26 Oct): the font is Batang, the body font of the contest guideline, not Arial.
Nose values: instantaneous OAV at each nose probe at the snapshot (series of the 3D viewer data, sofa_rec4.5 run).
Usage (figure venv): /root/figenv/bin/python compose_figure.py <render_dir> <out_dir>
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from figstyle import *  # noqa: E402,F401,F403  (FIGSTYLE v1.2, verbatim)
from matplotlib.patches import Patch  # noqa: E402

render, outdir = Path(sys.argv[1]), Path(sys.argv[2])
apply_style("paper")
mpl.rcParams["font.sans-serif"] = ["Batang"] + mpl.rcParams["font.sans-serif"]  # override: Batang (see docstring)
mpl.rcParams["mathtext.rm"] = mpl.rcParams["mathtext.sf"] = "Batang"

pts = json.loads((render / "points_px.json").read_text())["points"]
CLOUD = {"OAV 1 (훈련된 판정단의 탐지 역치)": "#74C476", "OAV 20 (주의하면 절반이 알아챔)": "#006D2C"}
PANELS = {
    "A90": {"header": "소리 나는 방귀 (A90, 279 mL)", "sound": "뿡!", "releaser": 3.8, "neighbour": 15.1,
            "say": ("neighbour", "윽!")},
    "S90": {"header": "조용한 방귀 (S90, 66 mL)", "sound": "……", "releaser": 22.3, "neighbour": 0.0,
            "say": ("releaser", "아무도 모르겠지?")},
}

fig, axes = new_figure("onehalf", aspect=0.54, ncols=2)
bubble = dict(boxstyle="round,pad=0.35", fc="white", ec=INK, lw=0.6)
for ax, (rel, p) in zip(axes, PANELS.items()):
    img = plt.imread(render / f"cloud_{rel}.png")
    ax.imshow(img)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xlabel(p["header"])
    h, w = img.shape[:2]
    rn, nn, rp = pts["releaser_nose"], pts["neighbour_nose"], pts["release"]
    # labels and their arrows are drawn separately (arrow first, text box on top), so the overlap check measures the
    # text boxes only (an Annotation's extent includes its arrow)
    def label(text, at, to, arrow, box, **kw):
        ax.annotate("", xy=to, xytext=at, arrowprops=arrow, zorder=3)
        ax.text(*at, text, ha="center", va="center", bbox=box, zorder=4, **kw)

    # nose values: to the left of the releaser and to the right of the neighbour, at head height
    tag = dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85)
    pointer = dict(arrowstyle="-|>", color=INK, lw=0.6, shrinkA=0, shrinkB=3)
    for who, xy, dx in (("releaser", rn, -430), ("neighbour", nn, 420)):
        lab = f"{'본인' if who == 'releaser' else '옆 사람'} 코\nOAV {p[who]:g}"
        label(lab, (xy[0] + dx, xy[1] - 60), xy, pointer, tag, fontsize=7)
    # the sound of the release, next to the release point
    ax.text(rp[0] - 330, rp[1] + 170, p["sound"], fontsize=12 if rel == "A90" else 10,
            ha="center", va="center", color=PALETTE[3] if rel == "A90" else MUTED, bbox=tag)
    # what one of them says, as a speech bubble from the head
    who, line = p["say"]
    head = rn if who == "releaser" else nn
    tail = dict(arrowstyle="wedge,tail_width=0.6", fc="white", ec=INK, lw=0.6, shrinkA=0, shrinkB=4)
    label(line, (head[0] + (-200 if who == "releaser" else 200), head[1] - 520), (head[0], head[1] - 70), tail, bubble,
          fontsize=7)
    ax.set_xlim(0, w); ax.set_ylim(h, 0)
fig.legend([Patch(fc=c, ec="none") for c in CLOUD.values()], list(CLOUD), loc="outside lower center", ncol=2)
panel_labels(axes)
save_figure(fig, "fig1_sbd_clouds_paper", outdir=outdir)
