"""Figure 6 of the manuscript: the three path-traced snapshots of render_fig6.py side by side, with nose labels and a
cloud legend. FIGSTYLE v1.2, paper, double width.
Usage (figure venv): /root/figenv/bin/python manuscript/preprint/compose_fig6.py <render_dir>
Writes figures/clouds_routing_paper.svg/.png.
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

render = Path(sys.argv[1])
apply_style("paper")
CLOUD = {"OAV 1 (trained-panel threshold)": "#74C476", "OAV 20 (half of attentive observers notice)": "#006D2C"}
pts = {s: json.loads((render / f"points_px_{s}.json").read_text())["points"] for s in ("sofa", "elev")}
# (image, scene, header, labels: (text, point key, label offset in px))
PANELS = [
    ("cloud_sofa_A90.png", "sofa", "Sofa, audible (279 mL), 5 s",
     [("Releaser", "releaser_nose", (-430, -330)), ("Neighbour", "neighbour_nose", (330, -380))]),
    ("cloud_sofa_S50.png", "sofa", "Sofa, silent (122 mL), 15 s",
     [("Releaser", "releaser_nose", (-430, -330)), ("Neighbour", "neighbour_nose", (330, -380))]),
    ("cloud_elev_S50.png", "elev", "Lift, silent (122 mL), 16 s",
     [("Releaser", "releaser_nose", (330, 120)), ("Person behind", "behind_nose", (-390, 560))]),
]

fig, axes = new_figure("double", aspect=0.355, ncols=3)
tag = dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9)
pointer = dict(arrowstyle="-|>", color=INK, lw=0.6, shrinkA=0, shrinkB=2)
for ax, (img_name, scene, header, labels) in zip(axes, PANELS):
    img = plt.imread(render / img_name)
    # crop the white margin of the render (labels are shifted by the same offset)
    ink = np.where((img[..., :3] < 0.96).any(axis=2))
    y0, y1 = max(ink[0].min() - 20, 0), min(ink[0].max() + 20, img.shape[0])
    x0, x1 = max(ink[1].min() - 20, 0), min(ink[1].max() + 20, img.shape[1])
    img = img[y0:y1, x0:x1]
    h, w = img.shape[:2]
    ax.imshow(img)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xlabel(header)
    for text, key, (dx, dy) in labels:
        x, y = pts[scene][key]
        x, y = x - x0, y - y0
        at = (x + dx, y + dy)
        # arrow and text drawn separately, so the overlap check measures the text box only
        ax.annotate("", xy=(x, y), xytext=at, arrowprops=pointer, zorder=3)
        ax.text(*at, text, ha="center", va="center", bbox=tag, zorder=4)
    ax.set_xlim(0, w); ax.set_ylim(h, 0)
fig.legend([Patch(fc=c, ec="none") for c in CLOUD.values()], list(CLOUD), loc="outside lower center", ncol=2)
panel_labels(axes)
save_figure(fig, "clouds_routing_paper", outdir=str(ROOT / "figures"))
