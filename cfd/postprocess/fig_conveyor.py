"""Preview figure: 'The Conveyor Belt' - the human convective boundary layer on the mid-sagittal plane.

Serious data (steady RANS k-omega SST, room 23 C, skin 33 C, coarse mesh), ridiculous staging (plan section 13).
Input: postProcessing/midPlane/<time>/cutPlane.xy from
  foamPostProcess -func "cutPlaneSurface(funcName=midPlane, point=(0 0.003 0), normal=(0 1 0), fields=(U T),
                                         interpolate=false, surfaceFormat=raw)" -time <time>
Usage: python3 fig_conveyor.py <case_dir> <time> <out.png>
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Polygon

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cfd/geometry"))
import manikin  # noqa: E402

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984"
SEQ = LinearSegmentedColormap.from_list("blue_seq", ["#f4f8fd", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5",
                                                     "#256abf", "#1c5cab", "#104281", "#0d366b"])
STREAM = "#eb6834"


def load(case: Path, time: str):
    d = np.loadtxt(case / "postProcessing/midPlane" / time / "cutPlane.xy")
    return d[:, 0], d[:, 2], d[:, 3], d[:, 5], d[:, 6]  # x, z, Ux, Uz, T


def triangulation(x, z, max_edge=0.12):
    tri = mtri.Triangulation(x, z)
    p = np.c_[x, z][tri.triangles]
    edges = np.max(np.linalg.norm(p - np.roll(p, 1, axis=1), axis=2), axis=1)
    tri.set_mask(edges > max_edge)
    return tri


def silhouette(ax):
    for tris, fc, z in ((manikin.chair(), "#c3c2b7", 3), (manikin.body(), "#9b9a95", 4)):
        for a, b, c in tris:
            ax.add_patch(Polygon([(a[0], a[2]), (b[0], b[2]), (c[0], c[2])], closed=True, fc=fc, ec=fc, lw=0.3,
                                 zorder=z))


def integrate(fx, fz, start, dt=0.02, t_max=40.0, z_stop=manikin.NOSE[2]):
    """RK2 path of a massless parcel; returns path and arrival time at z_stop (None if it never gets there)."""
    p = np.array(start, float)
    path, t = [p.copy()], 0.0
    while t < t_max:
        u = np.array([fx(*p), fz(*p)], float)
        if np.any(~np.isfinite(u)):
            break
        mid = p + 0.5 * dt * u
        um = np.array([fx(*mid), fz(*mid)], float)
        if np.any(~np.isfinite(um)):
            break
        p = p + dt * um
        t += dt
        path.append(p.copy())
        if p[1] >= z_stop:
            return np.array(path), t
    return np.array(path), None


def main(case: Path, time: str, out: Path):
    x, z, ux, uz, T = load(case, time)
    tri = triangulation(x, z)
    umag = np.hypot(ux, uz)
    nose_z = manikin.NOSE[2]

    plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "font.size": 9,
                         "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2})
    fig, ax = plt.subplots(figsize=(7.6, 8.6))
    levels = np.linspace(0, 0.40, 17)
    cf = ax.tricontourf(tri, np.clip(umag, 0, 0.40), levels=levels, cmap=SEQ, zorder=1)
    t_room = 273.15 + 23.0
    ax.tricontour(tri, T - t_room, levels=[0.5, 2.0], colors=[MUTED, INK2], linewidths=[0.6, 0.9],
                  linestyles=["--", "-"], zorder=2)
    silhouette(ax)

    # 3-D parcel trajectories (OpenFOAM streamlinesPoints, forward, from seat-level seeds), projected on the side view
    tr_file = case / "postProcessing/seatParcels" / time / "tracks.xy"
    arrivals = []
    if tr_file.exists():
        d = np.loadtxt(tr_file)
        starts = np.where(d[:, 3] == 0)[0]
        for s0, e0 in zip(starts, list(starts[1:]) + [len(d)]):
            trk = d[s0:e0]
            k = np.where(trk[:, 2] >= nose_z)[0]
            stop = k[0] + 1 if k.size else len(trk)
            ax.plot(trk[:stop, 0], trk[:stop, 2], color=STREAM, lw=1.4, alpha=0.9, zorder=6, solid_capstyle="round")
            ax.plot(trk[0, 0], trk[0, 2], "o", ms=5, color=STREAM, mec=SURFACE, mew=1.2, zorder=7)
            if k.size:
                arrivals.append(float(trk[k[0], 3]))
                ax.plot(trk[k[0], 0], trk[k[0], 2], "o", ms=3.5, color=INK, zorder=7)
    nose = manikin.NOSE
    ax.plot(nose[0] + 0.012, nose[2], marker=">", ms=7, color=INK, zorder=8)
    ax.annotate("breathing zone\n(nose, 0.77 m above seat)", xy=(nose[0] + 0.02, nose[2]),
                xytext=(0.30, 1.40), fontsize=8, color=INK, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7))
    n_seed = len(starts) if tr_file.exists() else 0
    msg = (f"{len(arrivals)} of {n_seed} parcels released at seat level\nreach nose height in "
           f"{min(arrivals):.0f}–{max(arrivals):.0f} s" if arrivals else "no parcel reached nose height")
    ax.text(0.30, 1.78, msg, fontsize=8.5, color=INK, va="top", fontweight="bold")
    ax.text(0.30, 1.68, "orange: 3-D trajectories from seat-level seeds (●),\nprojected on the side view; "
            "black dot: arrival at nose height", fontsize=7.2, color=INK2, va="top")
    ax.set_xlim(-0.42, 0.72); ax.set_ylim(0.0, 1.85)
    ax.set_aspect("equal")
    ax.set_xlabel("x, forward (m)"); ax.set_ylabel("z, height above floor (m)")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    cb = fig.colorbar(cf, ax=ax, shrink=0.62, pad=0.12, ticks=[0, 0.05, 0.1, 0.16, 0.24, 0.3, 0.4])
    cb.set_label("air speed in the mid-sagittal plane, |U| (m/s)", labelpad=-62)
    cb.ax.axhspan(0.16, 0.24, xmin=0, xmax=1, fc="none", ec=INK, lw=1.0)
    cb.ax.text(1.9, 0.20, "Licina et al. 2014:\nthe conveyor belt\n(0.16–0.24 m/s)", transform=cb.ax.get_yaxis_transform(),
               fontsize=7.5, va="center", color=INK)
    cb.ax.text(1.9, 0.025, "still air\n(nobody suspects)", transform=cb.ax.get_yaxis_transform(), fontsize=7.5,
               va="center", color=INK2)
    cb.ax.text(1.9, 0.37, "express lane", transform=cb.ax.get_yaxis_transform(), fontsize=7.5, va="center",
               color=INK2)
    fig.suptitle("The Conveyor Belt", x=0.06, y=0.985, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.06, 0.953, "Human convective boundary layer of a seated adult, mid-sagittal plane. Room 23 °C, "
             "skin 33 °C.\nSteady RANS (k-ω SST), Boussinesq, 340 k cells. Thin/solid grey contours: +0.5 / +2 K "
             "above room air.\nPRELIMINARY (coarse mesh, validation in progress).", fontsize=7.8, color=INK2,
             va="top")
    fig.savefig(out, dpi=220, bbox_inches="tight")
    print("wrote", out, "arrival times (s):", [round(a, 1) for a in arrivals])


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]))
