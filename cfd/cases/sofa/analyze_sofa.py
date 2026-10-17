"""Scenario A ('sofa duet') analysis: nose-probe time series of the silent and audible branches.

Reads postProcessing/noses/<start>/s from cfd/runs/sofa_{silent,audible} (probe 0 = the farter's own nose, probe 1 =
the neighbour's nose; both stages of the two-stage run are concatenated). s = 1 is undiluted flatus; OAV = summed odour
activity value of H2S + CH3SH + DMS (gate0.model.oav). Release starts at t = 0.2 s in both branches.

Metrics per nose: peak OAV, arrival time (first OAV >= 1), time above OAV 1, exposure integral, and the worst-breath
OAV (sinusoidal breathing, Wysocki 2006; mean and max over 24 breathing phases). R = silent / audible for each metric.
Writes cfd/cases/sofa/results.json and figures/fig5_sofa_duet_noses.png. With --recline DEG (posture sensitivity,
run_sofa.sh [runs_dir] DEG) it reads sofa_rec<DEG>_{silent,audible}, moves the releaser's breathing zone and head axis
with the reclined head, and writes results_rec<DEG>.json and figures/figS_sofa_rec<DEG>_noses.png. With --window W
only the first W s after release onset are used and the output names get a _W<W>s suffix (e.g. the 30 s direct pass of
runs later extended to 120 s by extend_window.sh).
Usage: python3 analyze_sofa.py [runs_dir] [--recline DEG]
"""
import argparse
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
from model import load_params, nominal, oav

P = nominal(load_params())
import importlib.util

_spec = importlib.util.spec_from_file_location("pmodel", ROOT / "perception/model.py")
pm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pm)

T_REL = 0.2
NOSE_X, HEAD_X, DY_F, DY_N = 0.10, 0.0, -0.30, 0.30  # probe x, head axis x, lateral seat positions (make_case.py)
NOSES = ("own nose (releaser)", "neighbour's nose")
sys.path.insert(0, str(ROOT / "cfd/geometry"))
import manikin


def zone_x(recline: float):
    """(breathing-zone x, head-axis x) for the releaser and the neighbour; only the releaser reclines."""
    shift = manikin.nose_tip(recline)[0] - manikin.NOSE[0]
    return ((NOSE_X + shift, HEAD_X + shift), (NOSE_X, HEAD_X))


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


def zone_series(case: Path, r_bz=0.05, r_head=0.25, recline: float = 0.0):
    """From the nose-height plane (every 0.5 s): mean s in the breathing zone (disc of radius r_bz around the probe
    point 2.5 cm in front of the nose) and max s within r_head of the head axis (catches a cloud passing behind)."""
    d = case / "postProcessing/planes"
    times = sorted((q for q in d.iterdir() if q.name.replace(".", "").isdigit()), key=lambda q: float(q.name))
    t, bz, ring = [], [], []
    for q in times:
        f = q / "noseHeight.xy"
        if not f.exists():
            continue
        a = np.loadtxt(f)
        t.append(float(q.name))
        row_bz, row_ring = [], []
        for y, (x_bz, x_head) in zip((DY_F, DY_N), zone_x(recline)):
            dist_bz = np.hypot(a[:, 0] - x_bz, a[:, 1] - y)
            dist_head = np.hypot(a[:, 0] - x_head, a[:, 1] - y)
            row_bz.append(a[dist_bz < r_bz, 3].mean())
            row_ring.append(a[dist_head < r_head, 3].max())
        bz.append(row_bz)
        ring.append(row_ring)
    return np.array(t), np.array(bz), np.array(ring)


def metrics(t, s):
    o = np.array([oav(x, P) for x in np.maximum(s, 0.0)])
    above = o >= 1.0
    dt = np.gradient(t)
    wb_mean, wb_max = breath_metrics(t, s)
    return {"peak_s": float(s.max()), "peak_OAV": float(o.max()), "t_peak_s": float(t[np.argmax(s)] - T_REL),
            "t_arrival_s": float(t[np.argmax(above)] - T_REL) if above.any() else None,
            "time_above_OAV1_s": float(np.sum(dt[above])), "exposure_s_dt": float(np.trapezoid(s, t)),
            "worst_breath_OAV_mean": oav(wb_mean, P), "worst_breath_OAV_max": oav(wb_max, P)}


def main(runs: Path, recline: float = 0.0, window: float | None = None):
    res, series = {}, {}
    prefix = "sofa" if not recline else f"sofa_rec{recline:g}"
    for mode in ("silent", "audible"):
        case = runs / f"{prefix}_{mode}"
        if not (case / "postProcessing/noses").exists():
            print("missing", case)
            continue
        t, s = read_probe(case)
        tz, bz, ring = zone_series(case, recline=recline)
        if window is not None:
            k, kz = t <= T_REL + window + 1e-9, tz <= T_REL + window + 1e-9
            t, s, tz, bz, ring = t[k], s[k], tz[kz], bz[kz], ring[kz]
        res[mode] = {NOSES[i]: metrics(t, s[:, i]) for i in range(2)}
        series[mode] = (t, s, tz, bz)
        for i in range(2):
            res[mode][NOSES[i]].update({
                "bz_peak_OAV": oav(float(bz[:, i].max()), P),
                "bz_exposure_s_dt": float(np.trapezoid(bz[:, i], tz)),
                "head_ring_peak_OAV": oav(float(ring[:, i].max()), P),
                "t_head_ring_peak_s": float(tz[np.argmax(ring[:, i])] - T_REL)})
    if len(res) == 2:
        res["R_silent_over_audible"] = {
            n: {k: (res["silent"][n][k] / res["audible"][n][k] if res["audible"][n][k] else None)
                for k in ("peak_OAV", "exposure_s_dt", "worst_breath_OAV_mean", "worst_breath_OAV_max",
                          "bz_peak_OAV", "bz_exposure_s_dt", "head_ring_peak_OAV")}
            for n in NOSES}
    res["recline_deg"] = recline
    res["window_s"] = window if window is not None else float(max(series[m][0][-1] for m in series) - T_REL)
    tag = ("" if not recline else f"_rec{recline:g}") + ("" if window is None else f"_W{window:g}s")
    (ROOT / f"cfd/cases/sofa/results{tag}.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    plot(series, recline, tag)


def plot(series, recline: float = 0.0, tag: str = ""):
    SURFACE, INK2 = "#fcfcfb", "#52514e"
    COL = {"silent": "#2a78d6", "audible": "#eb6834"}
    plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "font.size": 9,
                         "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold"})
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6), sharey=True, constrained_layout=True)
    for i, ax in enumerate(axes):
        for mode, (t, s, tz, bz) in series.items():
            o = np.array([oav(x, P) for x in np.maximum(s[:, i], 0.0)])
            ob = np.array([oav(x, P) for x in np.maximum(bz[:, i], 0.0)])
            lab = "silent (0.9 m/s, 2 s)" if mode == "silent" else "audible (41 m/s, 0.5 s)"
            ax.plot(t - T_REL, np.maximum(o, 1e-3), color=COL[mode], lw=1.8, label=f"{lab}, probe")
            ax.plot(tz - T_REL, np.maximum(ob, 1e-3), color=COL[mode], lw=1.2, ls=(0, (3, 2)),
                    label=f"{lab}, breathing-zone mean (r = 5 cm)")
        ax.axhline(1.0, color=INK2, lw=0.8, ls=(0, (4, 3)))
        ax.text(0.98, 1.15, "odour threshold (OAV = 1)", transform=ax.get_yaxis_transform(), ha="right",
                fontsize=7.5, color=INK2)
        ax.set_yscale("log")
        ax.set_ylim(1e-2, 3.0)
        if "silent" in series:
            t, s, tz, bz = series["silent"]
            peak = oav(float(max(s[:, i].max(), bz[:, i].max(), 0.0)), P)
            if peak < 1e-2:
                ax.text(0.02, 0.95, f"silent: peak OAV {peak:.0e} (off scale)", transform=ax.transAxes, fontsize=7.5,
                        va="top", color=COL["silent"])
        ax.set_xlabel("time after release onset (s)")
        ax.set_title(f"{'ab'[i]}  {NOSES[i]}", loc="left")
    axes[0].set_ylabel("summed odour activity value at the nose")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=2, frameon=False, fontsize=8)
    title, out = ("Fig. 5 · Sofa duet: the same 92 mL, released silently or audibly (RANS, 23 °C room)",
                  "fig5_sofa_duet_noses.png")
    if recline:
        title = f"Fig. S · Sofa duet, releaser reclined {recline:g}° (back closed onto the backrest): same 92 mL"
        out = f"figS_sofa_rec{recline:g}_noses.png"
    if "_W" in tag:
        out = out.replace(".png", tag[tag.index("_W"):] + ".png")
    fig.suptitle(title, x=0.01, ha="left", fontsize=10, fontweight="bold")
    fig.savefig(ROOT / "figures" / out, dpi=200)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="?", default=str(ROOT / "cfd/runs"))
    ap.add_argument("--recline", type=float, default=0.0)
    ap.add_argument("--window", type=float, default=None, help="use only the first W s after release onset")
    a = ap.parse_args()
    main(Path(a.runs), a.recline, a.window)
