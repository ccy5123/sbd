"""M2: acoustic regime map (Fig. 3) and regime statistics over the release prior.

Usage (repo root):  python3 acoustics/run_m2.py
Writes: figures/fig3_acoustic_regimes.png, acoustics/results.json
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gate0"))
sys.path.insert(0, str(ROOT / "acoustics"))
from model import load_params, nominal  # noqa: E402
import regime as ac  # noqa: E402

INK, INK2, MUTED, SURFACE = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb"
REG_COLORS = ["#cde2fb", "#86b6ef", "#3987e5", "#104281"]  # S1, S2, S3, audible (ordinal)
BG_ORDER = ["library", "living", "office", "restaurant", "subway"]
BG_LABEL = {"library": "library", "living": "living room", "office": "open-plan office",
            "restaurant": "restaurant / café", "subway": "subway car"}
plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "text.color": INK, "font.size": 9, "axes.titlesize": 10, "axes.titleweight": "bold",
                     "axes.spines.top": False, "axes.spines.right": False})
P = nominal(load_params())
NU = P["nu_gas"]
SEED = 20261015
PRIOR = {"V": (1.7e-5, 3.75e-4), "T": (0.3, 5.0), "d": (1.0e-3, 1.5e-2)}  # same as Gate 0 release prior


def prior_samples(n=200000):
    rng = np.random.default_rng(SEED)
    lu = lambda lo, hi: np.exp(rng.uniform(np.log(lo), np.log(hi), n))  # noqa: E731
    V, T, d = lu(*PRIOR["V"]), lu(*PRIOR["T"]), lu(*PRIOR["d"])
    return V / T, d


def regime_map():
    Q = np.geomspace(1e-6, 2e-3, 300)            # 1 mL/s .. 2 L/s
    d = np.geomspace(1e-3, 1.5e-2, 240)
    QQ, DD = np.meshgrid(Q, d)
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.9), constrained_layout=True)
    cmap = ListedColormap(REG_COLORS)
    # (a) living room, sofa neighbour
    ax = axes[0]
    reg = ac.classify(QQ, DD, P, "living")
    ax.pcolormesh(Q * 1e6, d * 1e3, reg, cmap=cmap, vmin=-0.5, vmax=3.5, shading="auto", rasterized=True)
    for Re, ls in ((300, ":"), (1000, "--"), (3000, "-."), (10000, "-")):
        dd = 4 * Q / (np.pi * NU * Re)
        m = (dd >= 1e-3) & (dd <= 1.5e-2)
        ax.plot(Q[m] * 1e6, dd[m] * 1e3, color=INK2, lw=0.9, ls=ls)
        j = np.where(m)[0]
        if j.size:
            k = j[int(0.55 * j.size)]
            ax.text(Q[k] * 1e6, dd[k] * 1e3 * 1.06, f"Re {Re:,}", fontsize=7, color=INK2, rotation=33, ha="center")
    qs, ds = prior_samples(20000)
    ax.add_patch(Rectangle((PRIOR["V"][0] / PRIOR["T"][1] * 1e6, 1.0), (PRIOR["V"][1] / PRIOR["T"][0] -
                 PRIOR["V"][0] / PRIOR["T"][1]) * 1e6, 14.0, fill=False, ec=INK, lw=0.8, ls=(0, (4, 2))))
    ax.text(PRIOR["V"][0] / PRIOR["T"][1] * 1e6 * 1.1, 13.0, "release prior\n(Suarez 1997 volumes)", fontsize=7,
            color=INK, va="top")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("volume flow rate Q (mL/s)"); ax.set_ylabel("effective orifice diameter d (mm)")
    ax.set_title("a  Regimes for a sofa neighbour (0.6 m), living room 35 dB(A)", loc="left")
    ax.legend(handles=[Patch(fc=REG_COLORS[i], label=ac.LABELS[i]) for i in range(4)], loc="lower right",
              frameon=True, facecolor=SURFACE, edgecolor="none", fontsize=7.5)
    # (b) minimum audible flow rate Q* per background (SPL depends on Q only, so each edge is a single number)
    ax = axes[1]
    Qf = np.geomspace(1e-7, 1e-1, 4000)
    qlo, qhi = PRIOR["V"][0] / PRIOR["T"][1] * 1e6, PRIOR["V"][1] / PRIOR["T"][0] * 1e6
    ax.axvspan(qlo, qhi, color="#e4e3df", lw=0)
    ax.text(np.sqrt(qlo * qhi), len(BG_ORDER) - 0.35, "flow-rate range of the release prior", ha="center",
            fontsize=7.5, color=INK2)
    for r, col, lab in ((0.6, "#2a78d6", "sofa neighbour, 0.6 m"), (3.0, "#eb6834", "across the room, 3 m")):
        qstar = []
        for bg in BG_ORDER:
            reg_b = ac.classify(Qf, np.full_like(Qf, 1e-4), P, bg, r=r)  # tiny d: always oscillating
            idx = np.where(reg_b == ac.AUDIBLE)[0]
            qstar.append(Qf[idx[0]] * 1e6 if idx.size else np.nan)
        y = np.arange(len(BG_ORDER))[::-1]
        ax.plot(qstar, y, "o", ms=8, color=col, mec=SURFACE, mew=2, label=lab, zorder=3)
        for qq, yy in zip(qstar, y):
            ax.text(qq * 1.25, yy + (0.16 if r < 1 else -0.2), f"{qq:,.0f}", fontsize=7, color=INK2, va="center")
    ax.set_yticks(np.arange(len(BG_ORDER))[::-1])
    ax.set_yticklabels([f"{BG_LABEL[b]}  {P['bg_' + b]:.0f} dB(A)" for b in BG_ORDER])
    ax.set_ylim(-0.6, len(BG_ORDER) - 0.1)
    ax.set_xscale("log"); ax.set_xlim(1, 3e4)
    ax.set_xlabel("minimum audible flow rate Q* of an oscillating release (mL/s)")
    ax.set_title("b  Audible to the right of each dot; masked (S3) to the left", loc="left")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.tick_params(axis="y", length=0)
    axes[0].set_ylim(1, 15)
    axes[0].set_yticks([1, 2, 3, 5, 10, 15]); axes[0].set_yticklabels(["1", "2", "3", "5", "10", "15"])
    fig.suptitle(f"Fig. 3 · Acoustic regime map (onset P_th = {P['P_th']:.0f} Pa, f₀ = {P['f0_flatus']:.0f} Hz, "
                 f"{int(P['n_harm'])} harmonics)", x=0.01, ha="left", fontsize=10, fontweight="bold")
    fig.savefig(ROOT / "figures" / "fig3_acoustic_regimes.png", dpi=200)
    plt.close(fig)


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
