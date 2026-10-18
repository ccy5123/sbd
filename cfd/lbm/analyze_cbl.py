"""FluidX3D feasibility test: seated-manikin CBL (same room and lines as the OpenFOAM M3b case) vs Licina et al. 2014.

Reads <run>/{faceLine,noseColumn,headTop}.csv written by the FluidX3D sbd setup (columns: t, then Uz, T per point)
and reports, over the averaging window, the peak of the time-mean upward velocity in front of the face, the mean and
sd of the instantaneous peaks (the statistic of the OpenFOAM M3b table), the time-mean peaks on the nose column and
above the head, and the comparison with Licina et al. 2014 and the OpenFOAM RANS (cfd/validation/cbl/results.json).
Usage: python3 cfd/lbm/analyze_cbl.py <run_dir> [t_avg_start] [t_end]
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
LICINA = {20.0: 0.24, 26.0: 0.16}  # mean CBL peak velocity in front of the seated manikin (clothed)
STARTS = {"faceLine": (0.06, 0.40), "noseColumn": (0.50, 1.60), "headTop": (1.37, 2.30)}


def load(run: Path, name: str, t0: float, t1: float):
    a = np.loadtxt(run / f"{name}.csv", delimiter=",")
    a = a[(a[:, 0] >= t0) & (a[:, 0] <= t1)]
    return a[:, 0], a[:, 1::2], a[:, 2::2]  # t, Uz, T


def main(run: Path, t0: float, t1: float):
    setup = dict(zip(*[iter((run / "cbl_setup.txt").read_text().split())] * 2))
    troom = float(setup["Troom"])
    out = {"run": run.name, "T_room_C": troom, "window_s": [t0, t1]}
    for name, (s0, s1) in STARTS.items():
        t, uz, T = load(run, name, t0, t1)
        s = np.linspace(s0, s1, uz.shape[1])
        mean = uz.mean(axis=0)
        k = int(np.argmax(mean))
        out[name] = {"n_samples": len(t), "peak_mean_Uz": float(mean[k]), "at": float(s[k]),
                     "inst_peak_mean": float(uz.max(axis=1).mean()), "inst_peak_sd": float(uz.max(axis=1).std())}
    lic = LICINA.get(troom, float(np.interp(troom, [20.0, 26.0], [0.24, 0.16])))
    rans = json.loads((ROOT / "cfd/validation/cbl/results.json").read_text()).get(f"cbl_t{int(troom)}_tr", {})
    f = out["faceLine"]
    out["licina"] = lic
    out["rans_inst_peak_mean"] = rans.get("peak_Uz_face_mean")
    out["bias_vs_licina_mean_profile"] = f["peak_mean_Uz"] / lic - 1.0
    out["bias_vs_licina_inst_peaks"] = f["inst_peak_mean"] / lic - 1.0
    print(json.dumps(out, indent=1))
    (run / "cbl_result.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1]), float(sys.argv[2]) if len(sys.argv) > 2 else 60.0,
         float(sys.argv[3]) if len(sys.argv) > 3 else 1e9)
