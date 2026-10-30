"""Analyse the M3b CBL runs: peak upward velocity in front of the face vs room temperature (Licina et al. 2014).

Reads postProcessing/{faceLine,noseColumn,headTop}/<time>/line.xy from each transient cbl_t*_tr case (sampled every
0.5 s; statistics over the second half of the run). The steady cbl_t*_coarse runs did not converge and are skipped.
Writes cfd/validation/cbl/results.json and figures/cbl_validation_paper.{svg,png} (FIGSTYLE v1.2, paper, double).
Usage: python3 analyze.py [runs_dir]
       python3 analyze.py --from-json   (redraw the figure from the committed results.json; no analysis, no write)
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from figstyle import *  # noqa: E402,F401,F403  (FIGSTYLE v1.2, verbatim)

LICINA = {20.0: 0.24, 26.0: 0.16}  # CBL mean peak velocity in front of the seated manikin (Licina et al. 2014)


def line_samples(case: Path, func: str, it_min: float):
    """All samples of a graphUniform line with iteration >= it_min (sampled every 100 iterations)."""
    d = case / "postProcessing" / func
    if not d.exists():
        return []
    times = sorted((p for p in d.iterdir() if re.fullmatch(r"[0-9.eE+-]+", p.name)), key=lambda p: float(p.name))
    out = []
    for t in times:
        if float(t.name) >= it_min and (t / "line.xy").exists():
            data = np.loadtxt(t / "line.xy")
            out.append({"it": float(t.name), "s": data[:, 0], "U": data[:, 1:4], "T": data[:, 4]})
    return out


def peak_stats(samples, comp=2):
    peaks = np.array([np.max(x["U"][:, comp]) for x in samples])
    return float(np.mean(peaks)), float(np.std(peaks)), len(peaks)


def main(runs: Path):
    res = {}
    for case in sorted(runs.glob("cbl_t*_tr")):
        m = re.match(r"cbl_t(\d+)_(\w+)", case.name)
        face_all = line_samples(case, "faceLine", 1.0)
        if not face_all:
            continue
        it_last = face_all[-1]["it"]
        # statistically steady window: second half of the run (30-60 s of physical time)
        face = [x for x in face_all if x["it"] >= 0.5 * it_last] or face_all[-1:]
        mean, sd, n = peak_stats(face)
        col = line_samples(case, "noseColumn", 0.5 * it_last)
        top = line_samples(case, "headTop", 0.5 * it_last)
        prof = np.mean([x["U"][:, 2] for x in face], axis=0)
        res[case.name] = {"T_room_C": float(m.group(1)), "level": m.group(2), "last_time_s": it_last,
                          "n_samples": n, "peak_Uz_face_mean": mean, "peak_Uz_face_sd": sd,
                          "peak_dist_from_face_m": float(face[0]["s"][int(np.argmax(prof))] - 0.06),
                          "peak_Uz_noseColumn_mean": peak_stats(col)[0] if col else None,
                          "peak_Uz_above_head_mean": peak_stats(top)[0] if top else None,
                          "profile_x": face[0]["s"].tolist(), "profile_Uz": prof.tolist()}
    res["licina2014"] = {str(k): v for k, v in LICINA.items()}
    (ROOT / "cfd/validation/cbl/results.json").write_text(json.dumps(res, indent=1))
    plot(res)
    for k, v in res.items():
        if k.startswith("cbl"):
            print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items() if not a.startswith("profile")})


TEMP_COLOR = {20.0: PALETTE[0], 23.0: PALETTE[1], 26.0: PALETTE[2]}  # room temperature -> colour, marker, line
TEMP_IDX = {20.0: 0, 23.0: 1, 26.0: 2}


def plot(res):
    apply_style("paper")
    fig, axes = new_figure("double", aspect=0.36, ncols=2)
    a1, a2 = axes
    cases = sorted((v for k, v in res.items() if k.startswith("cbl") and v["level"] == "tr"),
                   key=lambda v: v["T_room_C"])
    # (a) peak upward velocity in front of the face vs room temperature
    a1.plot(list(LICINA), list(LICINA.values()), color=INK, ls=(0, (5, 3)), marker="s",
            markerfacecolor="white", label="Licina et al. (2014)")
    a1.plot([v["T_room_C"] for v in cases], [v["peak_Uz_face_mean"] for v in cases], color=MUTED, lw=0.6,
            zorder=1)
    for v in cases:
        i = TEMP_IDX[v["T_room_C"]]
        a1.errorbar(v["T_room_C"], v["peak_Uz_face_mean"], yerr=v["peak_Uz_face_sd"], color=TEMP_COLOR[v["T_room_C"]],
                    marker=MARKERS[i], ls="none", zorder=3)
    a1.text(0.03, 0.04, "Skin 33 °C; CFD mean ± sd over 30–60 s", transform=a1.transAxes, ha="left", va="bottom")
    a1.set_xlim(19, 27)
    a1.set_ylim(0, 0.45)
    a1.set_xlabel(axis_label("Room temperature", "°C"))
    a1.set_ylabel(axis_label("Peak " + var("U", "z") + " in front of the face", "m s-1"))
    # (b) time-mean vertical velocity profile at nose height
    a2.axhline(0, color=MUTED, lw=0.6, zorder=0)
    for v in cases:
        i = TEMP_IDX[v["T_room_C"]]
        a2.plot((np.array(v["profile_x"]) - 0.06) * 100, v["profile_Uz"], color=TEMP_COLOR[v["T_room_C"]],
                ls=LINESTYLES[i], marker=MARKERS[i], markevery=(0.04 + 0.05 * i, 0.16),
                label=f"CFD, room {v['T_room_C']:.0f} °C")
    a2.set_xlim(0, 35)
    a2.set_ylim(-0.05, 0.45)
    a2.set_xlabel(axis_label("Distance in front of the face at nose height", "cm"))
    a2.set_ylabel(axis_label("Time-mean " + var("U", "z"), "m s-1"))
    handles, labels = [], []
    for ax in (a1, a2):
        h, l = ax.get_legend_handles_labels()
        handles += h; labels += l
    fig.legend(handles, labels, loc="outside lower center", ncol=4)
    panel_labels(axes)
    return save_figure(fig, "cbl_validation_paper", outdir=ROOT / "figures")


if __name__ == "__main__":
    if "--from-json" in sys.argv[1:]:  # redraw only: read the committed results, never rewrite them
        plot(json.loads((ROOT / "cfd/validation/cbl/results.json").read_text()))
    else:
        main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "cfd/runs")
