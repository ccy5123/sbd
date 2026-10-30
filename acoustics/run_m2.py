"""M2: acoustic regime map (Fig. 3) and regime statistics over the release prior.

Figure in FIGSTYLE v1.2 (paper, double column): (a) regimes over flow rate and orifice diameter for a sofa neighbour
(0.6 m) in a 35 dB(A) living room; (b) minimum audible flow rate of an oscillating release for five backgrounds at
0.6 m and 3 m.
Usage (repo root, figure venv, see HANDOFF): /root/figenv/bin/python acoustics/run_m2.py
Writes: figures/acoustic_regimes_paper.svg/.png, acoustics/results.json
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gate0"))
sys.path.insert(0, str(ROOT / "acoustics"))
from model import load_params, nominal, prior_range  # noqa: E402
import regime as ac  # noqa: E402

sys.path.insert(0, str(ROOT))
from figstyle import *  # noqa: E402,F401,F403  (FIGSTYLE v1.2, verbatim)

# S1, S2, S3, audible (ordinal): CMAP_SEQ samples, light = silent, dark = audible
REG_COLORS = [matplotlib.colormaps[CMAP_SEQ](x) for x in (0.92, 0.66, 0.40, 0.14)]
BG_ORDER = ["library", "living", "office", "restaurant", "subway"]
BG_LABEL = {"library": "Library", "living": "Living room", "office": "Open-plan office",
            "restaurant": "Restaurant / café", "subway": "Subway car"}
REG_LABEL = {ac.S1: "No oscillation (physically silent)", ac.S2: "Oscillating, below hearing threshold",
             ac.S3: "Audible in quiet, masked here", ac.AUDIBLE: "Audible"}
DIST = ((0.6, "Sofa neighbour, 0.6 m"), (3.0, "Across the room, 3 m"))  # colour, marker follow the index
P = nominal(load_params())
NU = P["nu_gas"]
SEED = 20261015
PRIOR = {k: prior_range(load_params(), name)  # same as the Gate 0 release prior (params.yaml)
         for k, name in (("V", "V_passage"), ("T", "T_release"), ("d", "d_orifice"))}


def prior_samples(n=200000):
    rng = np.random.default_rng(SEED)
    lu = lambda lo, hi: np.exp(rng.uniform(np.log(lo), np.log(hi), n))  # noqa: E731
    V, T, d = lu(*PRIOR["V"]), lu(*PRIOR["T"]), lu(*PRIOR["d"])
    return V / T, d


def regime_map():
    apply_style("paper")
    Q = np.geomspace(5e-7, 2e-3, 300)            # 0.5 mL/s .. 2 L/s
    d = np.geomspace(1e-3, 1.5e-2, 240)
    QQ, DD = np.meshgrid(Q, d)
    fig, axes = new_figure("double", aspect=0.5, ncols=2)
    cmap = ListedColormap(REG_COLORS)
    q_label = var("Q")
    # (a) living room, sofa neighbour
    ax = axes[0]
    reg = ac.classify(QQ, DD, P, "living")
    ax.pcolormesh(Q * 1e6, d * 1e3, reg, cmap=cmap, vmin=-0.5, vmax=3.5, shading="auto", rasterized=True)
    re_lines = []
    for i, Re in enumerate((300, 1000, 3000, 10000)):
        dd = 4 * Q / (np.pi * NU * Re)
        m = (dd >= 1e-3) & (dd <= 1.5e-2)
        ax.plot(Q[m] * 1e6, dd[m] * 1e3, color=MUTED, lw=0.8, ls=LINESTYLES[(3, 1, 2, 0)[i]])
        re_lines.append((Re, Q[m] * 1e6, dd[m] * 1e3))
    qlo, qhi = PRIOR["V"][0] / PRIOR["T"][1] * 1e6, PRIOR["V"][1] / PRIOR["T"][0] * 1e6
    ax.add_patch(Rectangle((qlo, PRIOR["d"][0] * 1e3), qhi - qlo, (PRIOR["d"][1] - PRIOR["d"][0]) * 1e3,
                           fill=False, ec=INK, lw=0.8, ls=LINESTYLES[1]))
    allow_overlap(ax.text(0.6, PRIOR["d"][1] * 1e3 * 1.04, "Sampled releases\n(Suarez 1997 volumes)",
                          va="bottom", ha="left"))  # just above the top left of the dashed box
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(1, 15)
    ax.set_yticks([1, 2, 3, 5, 10])
    ax.set_yticklabels(["1", "2", "3", "5", "10"])
    ax.set_xlabel(axis_label("Volume flow rate " + q_label, "mL s-1"))
    ax.set_ylabel(axis_label("Effective orifice diameter " + var("d"), "mm"))
    # (b) minimum audible flow rate Q* per background (SPL depends on Q only, so each edge is a single number)
    ax = axes[1]
    Qf = np.geomspace(1e-7, 1e-1, 4000)
    ax.axvspan(qlo, qhi, color=MUTED, alpha=0.2, lw=0)
    allow_overlap(ax.text(np.sqrt(qlo * qhi), len(BG_ORDER) - 0.15, "Flow-rate range of\nthe sampled releases",
                          ha="center", va="center"))
    y = np.arange(len(BG_ORDER))[::-1]
    for i, (r, lab) in enumerate(DIST):
        qstar = []
        for bg in BG_ORDER:
            reg_b = ac.classify(Qf, np.full_like(Qf, 1e-4), P, bg, r=r)  # tiny d: always oscillating
            idx = np.where(reg_b == ac.AUDIBLE)[0]
            qstar.append(Qf[idx[0]] * 1e6 if idx.size else np.nan)
        ax.plot(qstar, y, ls="none", marker=MARKERS[i], color=PALETTE[i], label=lab, zorder=3)
        for qq, yy in zip(qstar, y):  # direct value labels beside each marker (on the grey band)
            allow_overlap(ax.text(qq, yy + (0.3 if i == 0 else -0.3), f"{qq:,.0f}", ha="center", va="center"))
    ax.set_yticks(y)
    ax.set_yticklabels([f"{BG_LABEL[b]}, {P['bg_' + b]:.0f} dB(A)" for b in BG_ORDER])
    ax.set_ylim(-0.6, len(BG_ORDER) + 0.2)
    ax.set_xscale("log")
    ax.set_xlim(1, 3e4)
    ax.set_xlabel(axis_label("Minimum audible flow rate " + r"$\mathit{Q}^{*}$", "mL s-1"))
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    fig.legend(handles=[Patch(fc=REG_COLORS[k], label=REG_LABEL[k]) for k in range(4)], loc="outside lower left",
               ncol=2)
    fig.legend(*ax.get_legend_handles_labels(), loc="outside lower right", ncol=1)
    # Reynolds-number labels along their lines, rotated to the on-screen slope (needs the final layout)
    fig.draw_without_rendering()
    ax = axes[0]
    for n, (Re, qq, dd) in enumerate(re_lines):  # start at d = 4.6 mm (first 3.2), half a decade apart, in the silent region
        if qq.size < 2:
            continue
        k = int(np.argmin(abs(dd - (3.2 if n == 0 else 4.6))))  # the longer first label starts lower
        p0, p1 = ax.transData.transform([(qq[0], dd[0]), (qq[-1], dd[-1])])
        ang = np.degrees(np.arctan2(p1[1] - p0[1], p1[0] - p0[0]))
        allow_overlap(ax.text(qq[k], dd[k] * 1.08, f"Re = {Re:,}" if n == 0 else f"{Re:,}", rotation=ang,
                              rotation_mode="anchor", ha="left", va="bottom", color=INK))
    panel_labels(axes)
    out = save_figure(fig, "acoustic_regimes_paper", outdir=ROOT / "figures")
    plt.close(fig)
    return out


def prior_stats():
    Q, d = prior_samples()
    out = {"u_onset_m_s": float(ac.u_onset(P)), "n": int(Q.size)}
    for bg in BG_ORDER:
        reg = ac.classify(Q, d, P, bg)
        out[bg] = {name: float(np.mean(reg == k)) for k, name in ((ac.S1, "S1"), (ac.S2, "S2"), (ac.S3, "S3"),
                                                                   (ac.AUDIBLE, "audible"))}
    reg_far = ac.classify(Q, d, P, None, r=3.0)
    out["quiet_3m"] = {"S2": float(np.mean(reg_far == ac.S2))}
    return out


if __name__ == "__main__":
    regime_map()
    stats = prior_stats()
    (ROOT / "acoustics" / "results.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=1))
