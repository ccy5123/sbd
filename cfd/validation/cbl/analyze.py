"""Analyse the M3b CBL runs: peak upward velocity in front of the face vs room temperature (Licina et al. 2014).

Reads postProcessing/{faceLine,noseColumn,headTop}/<time>/line.xy from each transient cbl_t*_tr case (sampled every
0.5 s; statistics over the second half of the run). The steady cbl_t*_coarse runs did not converge and are skipped.
Writes cfd/validation/cbl/results.json and figures/fig4_cbl_validation.png.
Usage: python3 analyze.py [runs_dir]
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


def plot(res):
    SURFACE, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
    plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "font.size": 9,
                         "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold"})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.2), constrained_layout=True)
    a1.plot(list(LICINA), list(LICINA.values()), color=INK, lw=2, ls=(0, (5, 3)), marker="s", ms=7,
            label="Licina et al. 2014 (thermal manikin)")
    for level, col, mk in (("tr", "#2a78d6", "o"),):
        pts = sorted((v["T_room_C"], v["peak_Uz_face_mean"], v["peak_Uz_face_sd"]) for k, v in res.items()
                     if k.startswith("cbl") and v["level"] == level)
        if pts:
            t, m_, e = zip(*pts)
            a1.errorbar(t, m_, yerr=e, color=col, lw=1.6, marker=mk, ms=8, mec=SURFACE, mew=2, capsize=3,
                        label="CFD, transient RANS, coarse mesh (mean ± sd, 30–60 s)")
    a1.set_xlabel("room temperature (°C), skin 33 °C"); a1.set_ylabel("peak upward CBL velocity in front of face (m/s)")
    a1.set_ylim(0, 0.45); a1.set_xlim(19, 27)
    a1.set_title("a  Breathing-zone CBL peak velocity", loc="left")
    a1.legend(frameon=False, fontsize=8)
    for k, v in res.items():
        if k.startswith("cbl") and v["level"] == "tr":
            a2.plot((np.array(v["profile_x"]) - 0.06) * 100, v["profile_Uz"], lw=1.8,
                    color={20.0: "#104281", 23.0: "#2a78d6", 26.0: "#86b6ef"}.get(v["T_room_C"], INK2),
                    label=f"{v['T_room_C']:.0f} °C")
    a2.axhline(0, color=INK2, lw=0.6)
    a2.set_xlabel("distance in front of the face at nose height (cm)"); a2.set_ylabel("U_z (m/s)")
    a2.set_title("b  Time-mean vertical velocity profile at nose height", loc="left")
    a2.legend(frameon=False, fontsize=8, title="room")
    fig.suptitle("Fig. 4 (cont.) · Human convective boundary layer validation (simplified seated manikin, RANS k-ω SST)",
                 x=0.01, ha="left", fontsize=10, fontweight="bold")
    fig.savefig(ROOT / "figures/fig4_cbl_validation.png", dpi=200)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "cfd/runs")
