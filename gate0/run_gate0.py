"""Run the Gate 0 analysis: ratio maps, Monte Carlo P(SBD), rank sensitivity.

Usage:  python3 gate0/run_gate0.py      (from the repository root)
Writes: figures/gate0_ratio_map.png, figures/gate0_psbd.png, figures/gate0_sensitivity.png,
        gate0/results.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import Release, load_params, nominal, oav, prior_range, ratio, receptor, source_mole_fraction_ppb  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "params"))
from derive_from_suarez1997 import g_red as G_RED_EMPIRICAL  # noqa: E402  (16 subjects, Suarez 1997)

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)
SEED = 20261015

# --- style (reference palette, light surface) -------------------------------------------
INK, INK2, MUTED, SURFACE, GRID = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#e4e3df"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
DIVERGING = LinearSegmentedColormap.from_list(
    "blue_gray_red", ["#104281", "#2a78d6", "#86b6ef", "#f0efec", "#f2a3a2", "#e34948", "#9e2322"])
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "text.color": INK, "font.size": 9, "axes.titlesize": 10, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False,
})

P_RAW = load_params()
P0 = nominal(P_RAW)


def logu(rng, lo, hi, n=None):
    return np.exp(rng.uniform(np.log(lo), np.log(hi), n))


# --- 1. ratio maps ------------------------------------------------------------------------
REF_SILENT = Release(V=4.0e-5, T=2.0, d=6.0e-3)  # 40 mL over 2 s, Re ~ 250
V_LOUD = 1.0e-4                                   # loud comparator: 100 mL (larger volume)


def ratio_maps():
    T_sweep = np.geomspace(5.0, 0.08, 120)       # comparator duration -> Re sweep
    t_sweep = np.geomspace(0.5, 40.0, 100)        # travel time to the nose, s
    K_cases = [(1e-4, "quiescent CBL, K = 10⁻⁴ m²/s"), (1e-3, "room air, K = 10⁻³ m²/s")]
    u_adv = 0.1  # only enters the inhalation-averaging factor
    out = {}
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 7.0), sharex=True, sharey=True, constrained_layout=True)
    norm = TwoSlopeNorm(vmin=-1.5, vcenter=0.0, vmax=1.5)
    for i, basis in enumerate(("mass", "conc")):
        for j, (K, klabel) in enumerate(K_cases):
            p = {**P0, "K_turb": K}
            Re = np.empty(T_sweep.size)
            R = np.empty((t_sweep.size, T_sweep.size))
            for jj, T in enumerate(T_sweep):
                loud = Release(V=V_LOUD, T=T, d=6.0e-3)
                Re[jj] = loud.reynolds(p["nu_gas"])
                for ii, t in enumerate(t_sweep):
                    R[ii, jj] = ratio(REF_SILENT, loud, p, L=t * u_adv, u_adv=u_adv, basis=basis,
                                      metric="phi_inh")
            ax = axes[i, j]
            m = ax.pcolormesh(Re, t_sweep, np.log10(R), cmap=DIVERGING, norm=norm, shading="auto",
                              rasterized=True)
            cs = ax.contour(Re, t_sweep, np.log10(R), levels=[0.0], colors=INK, linewidths=1.6)
            ax.clabel(cs, fmt={0.0: "parity"}, fontsize=8)
            ax.set_xscale("log"); ax.set_yscale("log")
            for t_mark, lab in [(P0["L_own"] / P0["u_own_eff"], "own nose"),
                                (P0["L_neighbour"] / P0["u_room"], "neighbour")]:
                ax.axhline(t_mark, color=INK2, lw=0.8, ls=(0, (3, 3)))
                ax.text(Re[-1] * 0.92, t_mark * 1.07, lab, ha="right", va="bottom", fontsize=8, color=INK2)
            ax.set_title(f"{'Equal emitted mass' if basis == 'mass' else 'Equal source concentration'} · {klabel}",
                         loc="left", fontsize=9)
            if i == 1:
                ax.set_xlabel("Reynolds number of the audible comparator, Re = u₀d/ν")
            if j == 0:
                ax.set_ylabel("travel time to the nose (s)")
            out[f"{basis}_K{K:g}"] = {"Re": Re.tolist(), "t": t_sweep.tolist(), "log10R": np.log10(R).tolist()}
    cb = fig.colorbar(m, ax=axes, shrink=0.85, pad=0.02)
    cb.set_label("log₁₀ ( C_silent / C_audible )  at the nose, inhalation-averaged")
    cb.ax.text(1.0, 1.02, "silent is deadlier", transform=cb.ax.transAxes, ha="center", va="bottom", fontsize=8,
               color="#9e2322")
    cb.ax.text(1.0, -0.02, "loud is worse", transform=cb.ax.transAxes, ha="center", va="top", fontsize=8,
               color="#104281")
    fig.suptitle("Gate 0 · silent reference release (40 mL, 2 s, d = 6 mm, Re ≈ 250) vs a 100 mL audible release",
                 x=0.01, ha="left", fontsize=10, fontweight="bold")
    fig.savefig(FIG / "gate0_ratio_map.png", dpi=200)
    plt.close(fig)
    return out


# --- 2. Monte Carlo -----------------------------------------------------------------------
SAMPLED = {  # name: (low, high, log-uniform?)
    "u_handoff": (0.05, 0.25, False), "K_turb": (1e-4, 1.3e-2, True), "u_own_eff": (0.07, 0.16, False),
    "u_room": (0.03, 0.15, True), "L_own": (0.65, 0.85, False), "L_neighbour": (0.8, 1.4, False),
    "T_insp": (1.6, 2.7, False), "B_u": (5.8, 5.9, False),
    "K_c": (4.73, 5.2, False), "Gamma_sj": (2.74, 2.86, False), "C_puff": (2.54, 2.66, False),
    "alpha_th": (0.15, 0.35, False),
    "a_denim": (0.017, 0.25, True), "a_leggings": (0.16, 1.9, True), "a_chino": (0.02, 0.15, True), "V_skirt": (0.01, 0.06, True),
    "P_th": (*prior_range(P_RAW, "P_th"), True), "C_d": (0.6, 1.0, False),
}
RELEASE_PRIOR = {k: prior_range(P_RAW, name)                    # all log-uniform; ranges from params.yaml
                 for k, name in (("V", "V_passage"), ("T", "T_release"), ("d", "d_orifice"))}
CLOTHING = ("none", "skirt", "leggings", "chino", "denim")


def draw_release(rng):
    return Release(V=logu(rng, *RELEASE_PRIOR["V"]), T=logu(rng, *RELEASE_PRIOR["T"]),
                   d=logu(rng, *RELEASE_PRIOR["d"]))


def monte_carlo(n=20000):
    rng = np.random.default_rng(SEED)
    rows = []
    while len(rows) < n:
        p = dict(P0)
        for k, (lo, hi, lg) in SAMPLED.items():
            p[k] = logu(rng, lo, hi) if lg else rng.uniform(lo, hi)
        p["g_reduced"] = float(rng.choice(G_RED_EMPIRICAL))  # empirical flatus buoyancy (signed)
        # M2: a release is audible-type if it drives tissue oscillation (acoustics/regime.py u_onset)
        p["u_audible"] = p["C_d"] * np.sqrt(2.0 * p["P_th"] / (p["rho_air"] * (1.0 - p["g_reduced"] / p["g"])))
        silent = loud = None
        for _ in range(200):
            r = draw_release(rng)
            if r.u0 < p["u_audible"] and silent is None:
                silent = r
            elif r.u0 >= p["u_audible"] and loud is None:
                loud = r
            if silent and loud:
                break
        if not (silent and loud):
            continue
        row = {k: p[k] for k in SAMPLED}
        row["g_reduced"] = p["g_reduced"]
        row["u_audible"] = p["u_audible"]
        row.update({"V_s": silent.V, "T_s": silent.T, "d_s": silent.d, "u0_s": silent.u0,
                    "V_l": loud.V, "T_l": loud.T, "d_l": loud.d, "u0_l": loud.u0,
                    "Re_s": silent.reynolds(p["nu_gas"]), "Re_l": loud.reynolds(p["nu_gas"])})
        for who, L, u in (("own", p["L_own"], p["u_own_eff"]), ("nb", p["L_neighbour"], p["u_room"])):
            for cl in CLOTHING:
                rs = receptor(silent, p, L, u, cl)
                rl = receptor(loud, p, L, u, cl)
                for metric in ("phi_inst", "phi_inh"):
                    row[f"R_{who}_conc_{metric}_{cl}"] = rs[metric] / rl[metric]
                    row[f"R_{who}_mass_{metric}_{cl}"] = (rs[metric] / silent.V) / (rl[metric] / loud.V)
                if cl == "none":
                    for tag, rr in (("s", rs), ("l", rl)):
                        row[f"ta_{who}_{tag}"] = rr["t_travel"]
                        row[f"st_{who}_{tag}"] = rr["sigma_t"]
                        row[f"phi_{who}_{tag}"] = rr["phi_inst"]
                    row[f"OAV_{who}_silent"] = oav(rs["phi_inh"], p)
                    row[f"OAV_{who}_loud"] = oav(rl["phi_inh"], p)
                    row[f"Si_s"], row[f"Si_l"] = rs["Si"], rl["Si"]
        # jet aimed at the neighbour (sensitivity case, clothing none)
        rs = receptor(silent, p, p["L_neighbour"], p["u_room"], "none", jet_toward_receptor=True)
        rl = receptor(loud, p, p["L_neighbour"], p["u_room"], "none", jet_toward_receptor=True)
        row["R_nb_mass_phi_inh_none_aimed"] = (rs["phi_inh"] / silent.V) / (rl["phi_inh"] / loud.V)
        row["R_nb_conc_phi_inh_none_aimed"] = rs["phi_inh"] / rl["phi_inh"]
        rows.append(row)
    return {k: np.array([r[k] for r in rows]) for k in rows[0]}


def summarize(mc):
    def stats(x):
        lx = np.log10(x)
        rng = np.random.default_rng(SEED + 1)
        boot = [np.mean(rng.choice(x, x.size) > 1.0) for _ in range(400)]
        return {"P_SBD": float(np.mean(x > 1.0)), "P_R_gt_2": float(np.mean(x > 2.0)),
                "P_R_lt_half": float(np.mean(x < 0.5)), "P_SBD_95CI_bootstrap": [float(np.percentile(boot, 2.5)),
                                                                          float(np.percentile(boot, 97.5))],
                "median_ratio": float(10 ** np.median(lx)),
                "ratio_5_95": [float(10 ** np.percentile(lx, 5)), float(10 ** np.percentile(lx, 95))]}
    out = {}
    for key in mc:
        if key.startswith("R_"):
            out[key] = stats(mc[key])
    return out


def plot_psbd(summary, mc):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.8), constrained_layout=True,
                                   gridspec_kw={"width_ratios": [1.15, 1]})
    # (a) distributions, neighbour, inhaled, clothing none
    bins = np.linspace(-2.0, 2.0, 81)
    for basis, col, lab in (("mass", BLUE, "equal emitted mass"), ("conc", ORANGE, "equal source concentration")):
        x = np.log10(mc[f"R_nb_{basis}_phi_inh_none"])
        ax1.hist(x, bins=bins, histtype="step", lw=2.0, color=col,
                 label=f"{lab}: P(R>1) = {np.mean(x > 0):.2f}, P(R>2) = {np.mean(x > np.log10(2)):.2f}")
    ax1.axvline(0.0, color=INK, lw=1.0)
    ax1.axvspan(np.log10(2.0), 2.0, color="#f2a3a2", alpha=0.25, lw=0)
    ax1.axvspan(-2.0, np.log10(0.5), color="#86b6ef", alpha=0.25, lw=0)
    ymax = ax1.get_ylim()[1]
    ax1.text(1.15, ymax * 0.55, "silent noticeably\ndeadlier (R > 2)", fontsize=8, color=INK2, ha="center")
    ax1.text(-1.15, ymax * 0.55, "loud noticeably\nworse (R < ½)", fontsize=8, color=INK2, ha="center")
    ax1.set_xlabel("log₁₀ R,  R = C_silent / C_audible at the neighbour's nose")
    ax1.set_ylabel("Monte Carlo pairs")
    ax1.set_title("a  Neighbour, no clothing, inhalation-averaged", loc="left")
    ax1.legend(frameon=False, fontsize=8, loc="upper left")
    # (b) median ratio and 5-95 % range by wardrobe, nose and basis
    rows = []
    for cl in CLOTHING:
        for who in ("own", "nb"):
            for basis, col in (("mass", BLUE), ("conc", ORANGE)):
                rows.append((cl, who, basis, col, summary[f"R_{who}_{basis}_phi_inh_{cl}"]))
    y = []
    pos = 0.0
    for k in range(len(rows)):
        y.append(pos)
        pos -= 1.0 if k % 2 == 0 else 1.6
    for yy, (cl, who, basis, col, s) in zip(y, rows):
        lo, hi = s["ratio_5_95"]
        ax2.plot([lo, hi], [yy, yy], color=col, lw=2.0, solid_capstyle="round")
        ax2.plot(s["median_ratio"], yy, "o", ms=7, color=col, mec=SURFACE, mew=2)
        ax2.text(13.0, yy, f"P(R>2) = {s['P_R_gt_2']:.2f}", va="center", fontsize=7.5, color=INK2)
    ax2.set_yticks([(y[i] + y[i + 1]) / 2 for i in range(0, len(y), 2)])
    ax2.set_yticklabels([f"{r[0]} · {'own nose' if r[1] == 'own' else 'neighbour'}" for r in rows[::2]], fontsize=8)
    ax2.set_xscale("log"); ax2.set_xlim(0.1, 40)
    ax2.axvline(1.0, color=INK, lw=0.8)
    ax2.axvspan(2.0, 40, color="#f2a3a2", alpha=0.25, lw=0)
    ax2.axvspan(0.1, 0.5, color="#86b6ef", alpha=0.25, lw=0)
    ax2.set_xlabel("R = C_silent / C_audible (median and 5–95 % range)")
    ax2.set_title("b  By wardrobe and nose", loc="left")
    ax2.plot([], [], color=BLUE, lw=2, marker="o", label="equal emitted mass")
    ax2.plot([], [], color=ORANGE, lw=2, marker="o", label="equal source concentration")
    ax2.legend(frameon=False, fontsize=8, loc="lower left", bbox_to_anchor=(0.0, 1.06), ncol=2)
    ax2.tick_params(axis="y", length=0)
    fig.suptitle("Gate 0 Monte Carlo · random silent (S1) vs audible release pairs, n = %d" % mc["V_s"].size,
                 x=0.01, ha="left", fontsize=10, fontweight="bold")
    fig.savefig(FIG / "gate0_psbd.png", dpi=200)
    plt.close(fig)


def sensitivity(mc):
    target = np.log10(mc["R_nb_mass_phi_inh_none"])
    feats = {
        "log u₀ silent": np.log(mc["u0_s"]), "log u₀ audible": np.log(mc["u0_l"]),
        "log V audible / V silent": np.log(mc["V_l"] / mc["V_s"]), "log K (eddy diffusivity)": np.log(mc["K_turb"]),
        "u_handoff": mc["u_handoff"], "log u_room": np.log(mc["u_room"]), "L neighbour": mc["L_neighbour"],
        "log d silent": np.log(mc["d_s"]), "log d audible": np.log(mc["d_l"]), "g′ (buoyancy)": mc["g_reduced"],
        "K_c (jet constant)": mc["K_c"], "Γ (starting jet)": mc["Gamma_sj"], "T_insp": mc["T_insp"],
        "log u_onset (acoustic)": np.log(mc["u_audible"]),
    }
    rho = {k: float(spearmanr(v, target).statistic) for k, v in feats.items()}
    order = sorted(rho, key=lambda k: abs(rho[k]))
    fig, ax = plt.subplots(figsize=(6.4, 4.4), constrained_layout=True)
    vals = [rho[k] for k in order]
    ax.barh(range(len(order)), vals, color=[ORANGE if v > 0 else BLUE for v in vals], height=0.7,
            edgecolor=SURFACE, linewidth=2)
    ax.set_yticks(range(len(order))); ax.set_yticklabels(order, fontsize=8)
    ax.axvline(0, color=INK, lw=0.8)
    for i, v in enumerate(vals):
        ax.text(v + (0.02 if v >= 0 else -0.02), i, f"{v:+.2f}", va="center", ha="left" if v >= 0 else "right",
                fontsize=7.5, color=INK2)
    ax.set_xlim(-1, 1)
    ax.set_xlabel("Spearman ρ with log₁₀(C_silent/C_audible), neighbour, equal mass")
    ax.set_title("Gate 0 rank sensitivity (orange: raises the silent penalty)", loc="left")
    ax.tick_params(axis="y", length=0)
    fig.savefig(FIG / "gate0_sensitivity.png", dpi=200)
    plt.close(fig)
    return rho


def headline_numbers():
    p = P0
    x0 = {g: source_mole_fraction_ppb(p[f"c_{g}"], p["T_gas"]) for g in ("H2S", "CH3SH", "DMS")}
    oav0 = {g: x0[g] / p[g] for g in x0}
    D_star = sum(oav0.values())  # dilution needed to reach summed OAV = 1
    out = {"source_ppb": x0, "source_OAV": oav0, "dilution_to_threshold": D_star,
           "detectability_volume_m3_per_100mL": D_star * 1e-4}
    for name, rel in (("silent_ref", REF_SILENT), ("loud_ref", Release(V_LOUD, 0.5, 6e-3))):
        for who, L, u in (("own", p["L_own"], p["u_own_eff"]), ("nb", p["L_neighbour"], p["u_room"])):
            r = receptor(rel, p, L, u)
            out[f"{name}_{who}"] = {"Re": r["Re"], "u0": r["u0"], "Si": r["Si"], "D1": r["D1"],
                                    "regime": r["regime"], "x_h": r["x_h"], "t_travel": r["t_travel"],
                                    "D_total": r["D_total"], "OAV_inh": oav(r["phi_inh"], p)}
    return out


def main():
    print("ratio maps ...")
    ratio_maps()
    print("monte carlo ...")
    mc = monte_carlo()
    summary = summarize(mc)
    plot_psbd(summary, mc)
    rho = sensitivity(mc)
    results = {"seed": SEED, "n_mc": int(mc["V_s"].size), "headline": headline_numbers(),
               "P_SBD": summary, "spearman_nb_mass_inh": rho,
               "mc_medians": {k: float(np.median(v)) for k, v in mc.items() if not k.startswith("R_")}}
    with open(ROOT / "gate0" / "results.json", "w") as fh:
        json.dump(results, fh, indent=2, default=float)
    for k in sorted(summary):
        if "phi_inh" in k:
            s = summary[k]
            print(f"{k:40s} P(SBD)={s['P_SBD']:.3f} P(R>2)={s['P_R_gt_2']:.3f} P(R<.5)={s['P_R_lt_half']:.3f}  median R={s['median_ratio']:.2f}  5-95%={s['ratio_5_95']}")
    print("spearman:", {k: round(v, 2) for k, v in sorted(rho.items(), key=lambda kv: -abs(kv[1]))})


if __name__ == "__main__":
    main()
