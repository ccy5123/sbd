"""Selection ('memory filter') analysis: Theorem 3 applied to the Gate 0 release population.

Each Monte Carlo passage is drawn from the Gate 0 priors (release V, T, d; environment; sphincter onset), with a
log-normal sulfur multiplier (params sulfur_sigma_ln, independent of volume: Suarez 1997 Table 3). For each passage:
  * heard: M2 classification (acoustics/regime.classify) at the neighbour's distance, per background noise;
  * smelled: inhalation-averaged OAV >= 1 at the neighbour's nose (bystander) or the emitter's own nose;
  * intensity I = OAV^n if smelled, else 0.
Observers: bystander (remembers heard or smelled), emitter (remembers all, classifies by oscillation), anosmic
(remembers heard only). Reported: silent-vs-audible statistics over all passages (truth) and over remembered ones.

Usage (repo root): python3 perception/run_selection.py -> figures/fig13_memory_filter.png, perception/selection.json
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gate0"))
sys.path.insert(0, str(ROOT / "acoustics"))
sys.path.insert(0, str(ROOT / "perception"))
import run_gate0 as g0
from model import oav, receptor
from regime import AUDIBLE, classify
from selection import compare, noticed

N_EVENTS = 20000
SEED = 20261016
BACKGROUNDS = ("library", "living", "restaurant", "subway")
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984"
SILENT_C, AUDIBLE_C, EMITTER_C, TRUTH_C = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984"


def simulate(n=N_EVENTS, seed=SEED):
    rng = np.random.default_rng(seed)
    P0 = g0.P0
    sig = P0["sulfur_sigma_ln"]
    rows = []
    for _ in range(n):
        p = dict(P0)
        for k, (lo, hi, lg) in g0.SAMPLED.items():
            p[k] = g0.logu(rng, lo, hi) if lg else rng.uniform(lo, hi)
        p["g_reduced"] = float(rng.choice(g0.G_RED_EMPIRICAL))
        p["u_audible"] = p["C_d"] * np.sqrt(2.0 * p["P_th"] / (p["rho_air"] * (1.0 - p["g_reduced"] / p["g"])))
        r = g0.draw_release(rng)
        m = float(np.exp(sig * rng.standard_normal() - 0.5 * sig**2))  # sulfur multiplier, mean 1
        Q = r.V / r.T
        row = {"V": r.V, "u0": r.u0, "osc": r.u0 >= p["u_audible"], "sulfur": m,
               "OAV_nb": m * oav(receptor(r, p, p["L_neighbour"], p["u_room"])["phi_inh"], p),
               "OAV_own": m * oav(receptor(r, p, p["L_own"], p["u_own_eff"])["phi_inh"], p)}
        for bg in BACKGROUNDS:
            row[f"heard_{bg}"] = bool(classify(Q, r.d, p, background=bg, r=p["L_neighbour"]) == AUDIBLE)
        rows.append(row)
    return {k: np.array([r[k] for r in rows]) for k in rows[0]}


def analyse(sim, n_stevens, scale=1.0):
    """Truth and remembered statistics for each observer; `scale` multiplies all OAVs (base-rate sweep)."""
    out = {}
    for nose in ("nb", "own"):
        o = scale * sim[f"OAV_{nose}"]
        sim[f"_S_{nose}"] = o >= 1.0
        sim[f"_I_{nose}"] = np.where(sim[f"_S_{nose}"], o**n_stevens, 0.0)
    S, I = sim["_S_nb"], sim["_I_nb"]
    for bg in BACKGROUNDS:
        heard = sim[f"heard_{bg}"]
        out[f"bystander_{bg}"] = {
            "truth": compare(~heard, I, S, np.ones_like(S)),
            "remembered": compare(~heard, I, S, noticed(heard, S, "bystander")),
            "anosmic": compare(~heard, I, S, noticed(heard, S, "anosmic")),
            "frac_osc_heard": float(heard[sim["osc"]].mean()),
            "P_smelled_given_heard": float(S[heard].mean()),
        }
    So, Io = sim["_S_own"], sim["_I_own"]
    out["emitter"] = {"truth": compare(~sim["osc"], Io, So, np.ones_like(So)),
                      "remembered": compare(~sim["osc"], Io, So, noticed(sim["osc"], So, "emitter"))}
    out["p_S_nb"] = float(S.mean())
    out["p_S_own"] = float(So.mean())
    return out


def sweep(sim, n_stevens, scales):
    rows = []
    for f in scales:
        a = analyse(sim, n_stevens, f)
        rows.append({"scale": float(f), "p_S_nb": a["p_S_nb"], "p_S_own": a["p_S_own"],
                     "belief_bystander": a["bystander_living"]["remembered"]["P_belief"],
                     "belief_truth_nb": a["bystander_living"]["truth"]["P_belief"],
                     "belief_emitter": a["emitter"]["remembered"]["P_belief"],
                     "gap_bystander": a["bystander_living"]["remembered"]["gap_P_smelly"],
                     "theory_gap": 1.0 - a["bystander_living"]["P_smelled_given_heard"]})
    return rows


def figure(base, rows, out):
    plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
                         "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2,
                         "ytick.color": INK2, "text.color": INK, "font.size": 9, "axes.titlesize": 10,
                         "axes.titleweight": "bold", "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.3), constrained_layout=True,
                             gridspec_kw={"width_ratios": [1.15, 1.1, 1.0]})
    # (a) P(smelly | mode): truth vs memory
    ax = axes[0]
    groups = [("neighbour's nose,\nall passages", base["bystander_living"]["truth"]),
              ("bystander's\nmemory", base["bystander_living"]["remembered"]),
              ("emitter's own nose,\nall = memory", base["emitter"]["remembered"])]
    x = np.arange(len(groups))
    w = 0.36
    for k, (key, col, lab) in enumerate((("P_smelly_silent", SILENT_C, "silent"),
                                         ("P_smelly_audible", AUDIBLE_C, "audible"))):
        vals = [g[1][key] for g in groups]
        bars = ax.bar(x + (k - 0.5) * (w + 0.02), vals, w, color=col, label=lab, zorder=2)
        for b_, v in zip(bars, vals):
            ax.text(b_.get_x() + b_.get_width() / 2, v + 0.02, f"{v:.2f}", ha="center", fontsize=8, color=INK)
    ax.set_xticks(x, [g[0] for g in groups])
    ax.set_ylim(0, 1.25)
    ax.set_ylabel("P(smelled | silent or audible)")
    ax.set_title("a  What memory keeps (living room)", loc="left")
    ax.legend(frameon=False, loc="upper center", ncol=2, fontsize=8)
    # (b) belief vs base rate
    ax = axes[1]
    ps = np.array([r["p_S_nb"] for r in rows])
    ax.plot(ps, [r["belief_bystander"] for r in rows], color=AUDIBLE_C, lw=2, label="bystander's memory")
    ax.plot(ps, [r["belief_truth_nb"] for r in rows], color=TRUTH_C, lw=1.6, ls=(0, (4, 2)),
            label="neighbour's nose, all passages")
    ax.plot([r["p_S_own"] for r in rows], [r["belief_emitter"] for r in rows], color=EMITTER_C, lw=2,
            label="emitter (own nose, all)")
    ax.axhline(0.5, color=MUTED, lw=0.8)
    ax.axvline(base["p_S_nb"], color=INK2, lw=0.7, ls=":")
    ax.text(base["p_S_nb"], 0.03, "Gate 0 nominal\n(puff centred\non the nose) ", fontsize=7.5, color=INK2,
            ha="right")
    ax.set_xscale("log")
    ax.set_xlim(1e-3, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("base rate: fraction of passages smelled at that nose")
    ax.set_ylabel("P(a silent passage seems stronger)")
    ax.set_title("b  Rarer stink, stronger belief", loc="left")
    ax.legend(frameon=False, fontsize=7.5, loc="lower left")
    # (c) masking
    ax = axes[2]
    bgs = list(BACKGROUNDS)
    y = np.arange(len(bgs))
    bel = [base[f"bystander_{b}"]["remembered"]["P_belief"] for b in bgs]
    heard = [base[f"bystander_{b}"]["frac_osc_heard"] for b in bgs]
    ax.barh(y + 0.19, bel, 0.36, color=AUDIBLE_C, label="belief, bystander's memory", zorder=2)
    ax.barh(y - 0.19, heard, 0.36, color=MUTED, label="oscillating releases still heard", zorder=2)
    for yy, v in zip(y + 0.19, bel):
        ax.text(v + 0.01, yy, f"{v:.2f}", va="center", fontsize=8)
    for yy, v in zip(y - 0.19, heard):
        ax.text(v + 0.01, yy, f"{v:.2f}", va="center", fontsize=8, color=INK2)
    ax.set_yticks(y, bgs)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.15)
    ax.set_xlabel("probability")
    ax.set_title("c  Masking noise", loc="left")
    ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=1)
    fig.suptitle("Fig. 13 · The memory filter: a silent passage is only remembered if it stank "
                 "(same passages, three observers)", x=0.01, ha="left", fontsize=10.5, fontweight="bold")
    fig.savefig(out, dpi=200)


def main():
    n = g0.P0["n_stevens"]
    sim = simulate()
    base = analyse(sim, n)
    rows = sweep(sim, n, np.geomspace(1e-5, 1e2, 43))
    out = {"n_events": N_EVENTS, "seed": SEED, "sulfur_sigma_ln": g0.P0["sulfur_sigma_ln"], "n_stevens": n,
           "nominal": base, "base_rate_sweep": rows}
    (ROOT / "perception/selection.json").write_text(json.dumps(out, indent=1))
    figure(base, rows, ROOT / "figures/fig13_memory_filter.png")
    b = base["bystander_living"]
    print(f"p_S neighbour {base['p_S_nb']:.3f}, own {base['p_S_own']:.3f}")
    for k in ("truth", "remembered", "anosmic"):
        print(k, {a: round(v, 3) if isinstance(v, float) else v for a, v in b[k].items()})
    print("emitter", {a: round(v, 3) if isinstance(v, float) else v for a, v in base["emitter"]["remembered"].items()})
    for bg in BACKGROUNDS:
        r = base[f"bystander_{bg}"]
        print(bg, f"belief {r['remembered']['P_belief']:.3f}, osc heard {r['frac_osc_heard']:.2f}")


if __name__ == "__main__":
    main()
