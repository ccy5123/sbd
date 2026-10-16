"""Fig. 6 - the sofa duet in side view: odorant on the releaser's mid-sagittal plane, silent vs audible.

Reads postProcessing/planes/<t>/midFarter.xy (raw cut-plane, cell values: x y z s T Ux Uy Uz) from
cfd/runs/sofa_{silent,audible}; colour = log10 of the summed odour activity value (OAV, gate0.model.oav), solid
contour = odour threshold (OAV = 1). Times are after release onset (t = 0.2 s in the branch cases).
With --recline DEG it reads sofa_rec<DEG>_{silent,audible}, draws the reclined releaser and writes
figures/figS_sofa_rec<DEG>_planes.png.
Usage: python3 fig_sofa_planes.py [runs_dir] [--recline DEG] [--times t1 t2 ...]
"""
import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Polygon, Rectangle

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gate0"))
sys.path.insert(0, str(ROOT / "cfd/geometry"))
import manikin
from model import load_params, nominal, oav

P = nominal(load_params())
OAV_PER_S = oav(1.0, P)  # OAV is linear in s
T_REL = 0.2
SURFACE, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
SEQ = LinearSegmentedColormap.from_list("warm_seq", ["#fcfcfb", "#fde9d6", "#fbc99e", "#f6a066", "#eb6834",
                                                     "#c84d1c", "#9a3712", "#6b250b"])


def load(case: Path, t: float):
    d = case / "postProcessing/planes"
    times = sorted((p for p in d.iterdir() if p.name.replace(".", "").isdigit()), key=lambda p: float(p.name))
    best = min(times, key=lambda p: abs(float(p.name) - (t + T_REL)))
    a = np.loadtxt(best / "midFarter.xy")
    return float(best.name) - T_REL, a[:, 0], a[:, 2], a[:, 3]


def silhouette(ax, recline=0.0):
    ax.add_patch(Rectangle((-0.25, 0.0), 0.55, manikin.SEAT_Z, fc="#c3c2b7", ec="none", zorder=3))
    ax.add_patch(Rectangle((-0.42, 0.0), 0.21, 0.95, fc="#c3c2b7", ec="none", zorder=3))
    for a, b, c in manikin.body(recline_deg=recline):
        ax.add_patch(Polygon([(a[0], a[2]), (b[0], b[2]), (c[0], c[2])], closed=True, fc="#9b9a95", ec="#9b9a95",
                             lw=0.3, alpha=0.75, zorder=4))


def main(runs: Path, times, recline: float = 0.0):
    prefix = "sofa" if not recline else f"sofa_rec{recline:g}"
    plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "font.size": 8.5,
                         "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2})
    fig, axes = plt.subplots(2, len(times), figsize=(2.6 * len(times) + 1.2, 6.4), sharex=True, sharey=True,
                             constrained_layout=True)
    levels = np.linspace(-1, 4, 21)
    cf = None
    for r, mode in enumerate(("silent", "audible")):
        case = runs / f"{prefix}_{mode}"
        for c, t in enumerate(times):
            ax = axes[r, c]
            if not (case / "postProcessing/planes").exists():
                ax.text(0.5, 0.5, "not run yet", transform=ax.transAxes, ha="center", color=INK2)
                continue
            tt, x, z, s = load(case, t)
            lo = np.log10(np.maximum(s * OAV_PER_S, 1e-3))
            tri = mtri.Triangulation(x, z)
            pts = np.c_[x, z][tri.triangles]
            tri.set_mask(np.max(np.linalg.norm(pts - np.roll(pts, 1, axis=1), axis=2), axis=1) > 0.12)
            cf = ax.tricontourf(tri, np.clip(lo, levels[0], levels[-1]), levels=levels, cmap=SEQ, zorder=1)
            ax.tricontour(tri, lo, levels=[0.0], colors=[INK], linewidths=0.9, zorder=2)
            silhouette(ax, recline)
            nose = manikin.nose_tip(recline)
            ax.plot(nose[0] + 0.012, nose[2], marker=">", ms=5, color=INK, zorder=6)
            ax.set_xlim(-0.6, 0.9); ax.set_ylim(0.0, 2.0); ax.set_aspect("equal")
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
            if r == 0:
                ax.set_title(f"t = {tt:.1f} s", loc="left", fontweight="bold")
            if c == 0:
                ax.set_ylabel(f"{mode.upper()}\nz (m)", color=INK, fontweight="bold")
            if r == 1:
                ax.set_xlabel("x, forward (m)")
    cb = fig.colorbar(cf, ax=axes, shrink=0.75, pad=0.02, ticks=range(-1, 5))
    cb.set_label("log₁₀ summed odour activity value (OAV)")
    cb.ax.axhline(0.0, color=INK, lw=1.2)
    cb.ax.text(2.6, 0.0, "threshold", transform=cb.ax.get_yaxis_transform(), va="center", fontsize=7.5)
    cb.ax.text(2.6, 3.6, "plausible\ndeniability\nexpires", transform=cb.ax.get_yaxis_transform(), va="center",
               fontsize=7.5, color=INK2)
    head = "Fig. 6 · Sofa duet" if not recline else f"Fig. S · Sofa duet, releaser reclined {recline:g}°"
    fig.suptitle(f"{head}, releaser's mid-plane: the same 92 mL, silent (2 s, 0.9 m/s) vs audible\n"
                 "(0.5 s, 41 m/s). Black contour: odour threshold (OAV = 1).", x=0.01, ha="left", fontsize=9.5,
                 fontweight="bold")
    out = ROOT / ("figures/fig6_sofa_duet_planes.png" if not recline else f"figures/figS_sofa_rec{recline:g}_planes.png")
    fig.savefig(out, dpi=200)
    print("wrote", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="?", default=str(ROOT / "cfd/runs"))
    ap.add_argument("--recline", type=float, default=0.0)
    ap.add_argument("--times", type=float, nargs="*", default=[1.0, 3.0, 8.0, 15.0])
    a = ap.parse_args()
    main(Path(a.runs), a.times, a.recline)
