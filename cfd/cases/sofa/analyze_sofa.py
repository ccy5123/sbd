"""Scenario A ('sofa duet') analysis: nose-probe time series of the silent and audible branches.

Reads postProcessing/noses/<start>/s from cfd/runs/sofa_{silent,audible} (probe 0 = the farter's own nose, probe 1 =
the neighbour's nose; both stages of the two-stage run are concatenated). s = 1 is undiluted flatus; OAV = summed odour
activity value of H2S + CH3SH + DMS (gate0.model.oav). Release starts at t = 0.2 s in both branches.

Metrics per nose: peak OAV, arrival time (first OAV >= 1), time above OAV 1, exposure integral, and the worst-breath
OAV (sinusoidal breathing, Wysocki 2006; mean and max over 24 breathing phases). R = silent / audible for each metric.
Writes cfd/cases/sofa/results.json and figures/fig5_sofa_duet_noses.png.
Usage: python3 analyze_sofa.py [runs_dir]
"""
import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gate0"))
from model import load_params, nominal, oav  # noqa: E402  (gate0 model)

P = nominal(load_params())
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("pmodel", ROOT / "perception/model.py")
pm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pm)

T_REL = 0.2
NOSES = ("own nose (releaser)", "neighbour's nose")


def read_probe(case: Path, field: str = "s"):
    """Concatenate postProcessing/noses/<start>/<field> over all start times; later files win on overlap."""
    parts = []
    d = case / "postProcessing/noses"
    for sub in sorted((p for p in d.iterdir() if re.fullmatch(r"[0-9.eE+-]+", p.name)), key=lambda p: float(p.name)):
        f = sub / field
        if f.exists():
            parts.append(np.atleast_2d(np.loadtxt(f, comments="#")))
    a = np.vstack(parts[::-1])  # later restarts first, so np.unique keeps their values on overlap
    _, idx = np.unique(a[:, 0], return_index=True)
    a = a[idx]
    return a[:, 0], a[:, 1:]


def breath_metrics(t, c, n_phase=24):
    """Worst-breath concentration over breathing phases (mean and max)."""
    tt = np.arange(t[0], t[-1], 0.01)
    cc = np.interp(tt, t, c)
    period = 60.0 / P["f_breath"]
    worst = [pm.worst_breath(tt, cc, pm.inspiratory_flow(tt, period, P["Ti_Ttot"], P["V_tidal"], phase=ph))
             for ph in np.linspace(0, 1, n_phase, endpoint=False)]
    return float(np.mean(worst)), float(np.max(worst))


def metrics(t, s):
    o = np.array([oav(x, P) for x in np.maximum(s, 0.0)])
    above = o >= 1.0
    dt = np.gradient(t)
    wb_mean, wb_max = breath_metrics(t, s)
    return {"peak_s": float(s.max()), "peak_OAV": float(o.max()), "t_peak_s": float(t[np.argmax(s)] - T_REL),
            "t_arrival_s": float(t[np.argmax(above)] - T_REL) if above.any() else None,
            "time_above_OAV1_s": float(np.sum(dt[above])), "exposure_s_dt": float(np.trapezoid(s, t)),
            "worst_breath_OAV_mean": oav(wb_mean, P), "worst_breath_OAV_max": oav(wb_max, P)}


def main(runs: Path):
    res, series = {}, {}
    for mode in ("silent", "audible"):
        case = runs / f"sofa_{mode}"
        if not (case / "postProcessing/noses").exists():
            print("missing", case)
            continue
        t, s = read_probe(case)
        series[mode] = (t, s)
        res[mode] = {NOSES[i]: metrics(t, s[:, i]) for i in range(2)}
    if len(res) == 2:
        res["R_silent_over_audible"] = {
            n: {k: (res["silent"][n][k] / res["audible"][n][k] if res["audible"][n][k] else None)
                for k in ("peak_OAV", "exposure_s_dt", "worst_breath_OAV_mean", "worst_breath_OAV_max")}
            for n in NOSES}
    (ROOT / "cfd/cases/sofa/results.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    plot(series)


def plot(series):
    SURFACE, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
    COL = {"silent": "#2a78d6", "audible": "#eb6834"}
    plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "font.size": 9,
                         "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold"})
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.0), sharey=True, constrained_layout=True)
    for i, ax in enumerate(axes):
        for mode, (t, s) in series.items():
            o = np.array([oav(x, P) for x in np.maximum(s[:, i], 0.0)])
            ax.plot(t - T_REL, np.maximum(o, 1e-3), color=COL[mode], lw=1.8,
                    label="silent (0.9 m/s, 2 s)" if mode == "silent" else "audible (41 m/s, 0.5 s)")
        ax.axhline(1.0, color=INK2, lw=0.8, ls=(0, (4, 3)))
        ax.text(0.98, 1.15, "odour threshold (OAV = 1)", transform=ax.get_yaxis_transform(), ha="right",
                fontsize=7.5, color=INK2)
        ax.set_yscale("log")
        ax.set_ylim(1e-2, None)
        ax.set_xlabel("time after release onset (s)")
        ax.set_title(f"{'ab'[i]}  {NOSES[i]}", loc="left")
    axes[0].set_ylabel("summed odour activity value at the nose")
    axes[0].legend(frameon=False, fontsize=8)
    fig.suptitle("Fig. 5 · Sofa duet: the same 92 mL, released silently or audibly (RANS, 23 °C room)",
                 x=0.01, ha="left", fontsize=10, fontweight="bold")
    fig.savefig(ROOT / "figures/fig5_sofa_duet_noses.png", dpi=200)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "cfd/runs")
