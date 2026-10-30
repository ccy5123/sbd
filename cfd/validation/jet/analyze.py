"""Analyse the M3a jet runs: centreline decay constants, spreading rate, mesh convergence (GCI); Fig. 4a/4b.

Fits on 20 <= x/d <= 90 (the Dowling & Dimotakis / Hussein measurement window):
  U0/Uc = (x - x0)/(B_u d),   s0/sc = (x - x0)/(K_c d*)   (d* = d here: same density)
Spreading rate S = d r_1/2 / dx from radial velocity profiles at x/d = 40..90.

Usage: python3 analyze.py [runs_dir] [results_json] [--no-plot]
  -> writes results_json (default cfd/validation/jet/results.json) and figures/jet_validation_paper.{svg,png}
     (FIGSTYLE v1.2, paper, double); --no-plot skips the figure.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from figstyle import *  # noqa: E402,F401,F403  (FIGSTYLE v1.2, verbatim)

D, U0 = 0.01, 10.0
EXP = {"B_u": 5.8, "K_c": 5.11, "S": 0.094}  # Hussein et al. 1994; Dowling & Dimotakis 1990
CASES = [("jet_sst_coarse", "SST coarse"), ("jet_sst_medium", "SST medium"), ("jet_sst_fine", "SST fine"),
         ("jet_ke_medium", "k-ε medium"), ("jet_ke_pope_medium", "k-ε + round-jet C_ε1 medium")]


def read_field(path: Path):
    txt = path.read_text()
    m = re.search(r"internalField\s+nonuniform\s+List<(\w+)>\s*(\d+)\s*\(", txt)
    if not m:
        raise ValueError(f"cannot parse {path}")
    n = int(m.group(2))
    body = txt[m.end():]
    if m.group(1) == "vector":
        vals = re.findall(r"\(([^()]*)\)", body[: body.index("\n)\n") + 1] if "\n)\n" in body else body)[:n]
        return np.array([[float(v) for v in t.split()] for t in vals])
    end = body.index(")")
    return np.array(body[:end].split(), dtype=float)[:n]


def latest_time(case: Path):
    times = [p for p in case.iterdir() if p.is_dir() and re.fullmatch(r"[0-9.eE+-]+", p.name) and p.name != "0"]
    return max(times, key=lambda p: float(p.name)) if times else None


def load(case: Path):
    t = latest_time(case)
    if t is None or not (t / "C").exists():
        return None
    C, U, s = read_field(t / "C"), read_field(t / "U"), read_field(t / "s")
    r = np.hypot(C[:, 1], C[:, 2])
    return {"x": C[:, 0], "r": r, "u": U[:, 0], "s": s, "time": t.name}


def centreline(dat):
    x, r = dat["x"], dat["r"]
    xs = np.unique(np.round(x, 7))
    xc, uc, sc = [], [], []
    for xv in xs:
        m = np.isclose(x, xv, atol=1e-7)
        j = np.argmin(np.where(m, r, np.inf))
        xc.append(xv); uc.append(dat["u"][j]); sc.append(dat["s"][j])
    return np.array(xc), np.array(uc), np.array(sc)


def fit_decay(x, q, q0):
    m = (x / D >= 20) & (x / D <= 90)
    slope, icpt = np.polyfit(x[m] / D, q0 / q[m], 1)
    return 1.0 / slope, -icpt / slope  # constant, x0/d


def half_widths(dat, xc, uc):
    """Velocity half-width r_1/2 at x/d = 40..90."""
    rh = []
    xs = [40, 50, 60, 70, 80, 90]
    for xd in xs:
        j = np.argmin(abs(xc / D - xd))
        m = np.isclose(dat["x"], xc[j], atol=1e-7)
        r, u = dat["r"][m], dat["u"][m]
        o = np.argsort(r); r, u = r[o], u[o]
        half = 0.5 * uc[j]
        k = np.where(u < half)[0]
        if k.size == 0 or k[0] == 0:
            rh.append(np.nan); continue
        k = k[0]
        rh.append(np.interp(half, [u[k], u[k - 1]], [r[k], r[k - 1]]))
    return xs, rh


def spreading(dat, xc, uc):
    xs, rh = half_widths(dat, xc, uc)
    return float(np.polyfit(np.array(xs) * D, rh, 1)[0])


def gci(f1, f2, f3, r=2.0, Fs=1.25):
    """Roache GCI (fine-grid) from three systematically refined solutions f1 (fine), f2, f3 (coarse)."""
    e32, e21 = f3 - f2, f2 - f1
    if e21 == 0 or e32 / e21 <= 0:
        # oscillatory convergence: Roache GCI undefined; use U = 0.5 (max - min) (Stern et al. 2001, J Fluids Eng 123:793)
        u = 0.5 * (max(f1, f2, f3) - min(f1, f2, f3))
        return {"convergence": "oscillatory", "U_mesh": float(u), "U_mesh_rel_pct": float(100 * u / abs(f1))}
    p = np.log(abs(e32 / e21)) / np.log(r)
    ext = f1 + e21 / (r**p - 1)
    return {"convergence": "monotonic", "p": float(p), "GCI_fine": float(Fs * abs(e21 / f1) / (r**p - 1)),
            "extrapolated": float(ext)}


def main(runs: Path, out: Path = ROOT / "cfd/validation/jet/results.json", draw: bool = True):
    res, curves = {}, {}
    for name, label in CASES:
        dat = load(runs / name) if (runs / name).exists() else None
        if dat is None:
            continue
        xc, uc, sc = centreline(dat)
        B, x0u = fit_decay(xc, uc, U0)
        K, x0s = fit_decay(xc, sc, 1.0)
        S = spreading(dat, xc, uc)
        res[name] = {"label": label, "iteration": dat["time"], "B_u": float(B), "x0_u_over_d": float(x0u),
                     "K_c": float(K), "x0_s_over_d": float(x0s), "S": S,
                     "err_B_u_pct": 100 * (B / EXP["B_u"] - 1), "err_K_c_pct": 100 * (K / EXP["K_c"] - 1),
                     "err_S_pct": 100 * (S / EXP["S"] - 1)}
        xs, rh = half_widths(dat, xc, uc)
        curves[name] = (label, xc / D, U0 / uc, 1.0 / sc, np.array(xs), np.array(rh) / D)
    if all(c in res for c in ("jet_sst_fine", "jet_sst_medium", "jet_sst_coarse")):
        for q in ("B_u", "K_c", "S"):
            res[f"GCI_{q}"] = gci(res["jet_sst_fine"][q], res["jet_sst_medium"][q], res["jet_sst_coarse"][q])
    res["experiment"] = EXP
    out.write_text(json.dumps(res, indent=2))
    if draw:
        plot(curves, res)
    print(json.dumps(res, indent=1))


KE = r"$\mathit{k}$–$\mathit{\varepsilon}$"
STYLE = {  # case -> (display label, PALETTE / MARKERS / LINESTYLES index)
    "jet_sst_coarse": ("SST, coarse", 0), "jet_sst_medium": ("SST, medium", 1), "jet_sst_fine": ("SST, fine", 2),
    "jet_ke_medium": (KE + ", medium", 3),
    "jet_ke_pope_medium": (KE + ", medium, " + var("C", r"\varepsilon 1") + " = 1.6", 4)}


def plot(curves, res):
    apply_style("paper")
    fig, axes = new_figure("double", aspect=0.36, ncols=3)
    xd = np.linspace(0, 100, 200)
    xlab = axis_label(var("x") + "/" + var("d"))
    # (a, b) centreline velocity and scalar decay; experiment = correlation line (Hussein 1994; Dowling & Dimotakis 1990)
    for ax, idx, key, lab in ((axes[0], 2, "B_u", var("U", "0") + "/" + var("U", "c")),
                              (axes[1], 3, "K_c", var("s", "0") + "/" + var("s", "c"))):
        ax.axvspan(20, 90, color=MUTED, alpha=0.15, lw=0, zorder=0, label="Fit window")
        x0 = 4.0 if key == "B_u" else -3.7
        ax.plot(xd, (xd - x0) / EXP[key], color=INK, ls=(0, (5, 3)), label="Experiment", zorder=3)
        for name, c in curves.items():
            lbl, i = STYLE[name]
            ax.plot(c[1], c[idx], color=PALETTE[i], ls=LINESTYLES[i], marker=MARKERS[i],
                    markevery=(0.03 + 0.035 * i, 0.18), label=lbl)
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 22)
        ax.set_xlabel(xlab)
        ax.set_ylabel(axis_label(lab))
    # (c) spreading: velocity half-width with the fitted slope S, experiment slope drawn through the SST fine fit
    ax = axes[2]
    for name, c in curves.items():
        lbl, i = STYLE[name]
        ax.plot(c[4], c[5], color=PALETTE[i], ls=LINESTYLES[i], marker=MARKERS[i])
    if "jet_sst_fine" in curves:
        c = curves["jet_sst_fine"]
        xm, rm = np.mean(c[4]), np.mean(c[5])
        xe = np.array([35, 95])
        ax.plot(xe, rm + EXP["S"] * (xe - xm), color=INK, ls=(0, (5, 3)), zorder=3)
    ax.set_xlim(30, 100)
    ax.set_ylim(2, 12.5)
    ax.set_xlabel(xlab)
    ax.set_ylabel(axis_label(var("r", "1/2") + "/" + var("d")))
    handles, labels = axes[0].get_legend_handles_labels()
    order = sorted(range(len(labels)), key=lambda k: labels[k] == "Fit window")  # shaded window listed last
    fig.legend([handles[k] for k in order], [labels[k] for k in order], loc="outside lower center", ncol=4)
    panel_labels(axes)
    return save_figure(fig, "jet_validation_paper", outdir=ROOT / "figures")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--no-plot"]
    main(Path(args[0]) if args else ROOT / "cfd/runs",
         Path(args[1]) if len(args) > 1 else ROOT / "cfd/validation/jet/results.json",
         draw="--no-plot" not in sys.argv[1:])
