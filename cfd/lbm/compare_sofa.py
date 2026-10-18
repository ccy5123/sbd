"""FluidX3D feasibility test: sofa duet nose probes (LBM-LES) vs the archived OpenFOAM RANS series.

LBM: <run>/probes.csv (t from the start of the precursor; release at t_pre + 0.2 s) and scalar_mass.csv (released
scalar volume after the pulse vs the nominal V; the LBM series is rescaled by nominal/injected so both carry the same
odorant amount). RANS: cfd/runs/<case>/postProcessing/noses (extract cfd/probe_archive/nose_probes.tar.xz first;
probe 0 = releaser, probe 1 = neighbour; t from the branch start, release at 0.2 s).
Reports per nose and window (30, 60, 120 s after release): peak s, time-mean s, and the first time s exceeds 1e-6
(about OAV 0.14 for undiluted flatus at OAV 1.4e5).
Usage: python3 cfd/lbm/compare_sofa.py <lbm_run> <rans_case_dir> [t_pre]
"""
import re
import sys
from pathlib import Path

import numpy as np


def rans_probe(case: Path):
    d = case / "postProcessing/noses"
    parts = []
    for sub in sorted((p for p in d.iterdir() if re.fullmatch(r"[0-9.eE+-]+", p.name)), key=lambda p: float(p.name)):
        if (sub / "s").exists():
            parts.append(np.atleast_2d(np.loadtxt(sub / "s", comments="#")))
    a = np.vstack(parts[::-1])
    _, idx = np.unique(a[:, 0], return_index=True)
    a = a[idx]
    return a[:, 0] - 0.2, a[:, 1:]  # time since release


def lbm_probe(run: Path, t_pre: float):
    a = np.genfromtxt(run / "probes.csv", delimiter=",", names=True)
    scale = 1.0
    m = run / "scalar_mass.csv"
    if m.exists():
        w = m.read_text().split("\n")[0].split()
        scale = float(w[5]) / float(w[3])  # expected / injected
    t = a["t"] - (t_pre + 0.2)
    return t, np.column_stack([a["farter_C"], a["neighbour_C"]]) * scale, scale


def stats(t, c, w):
    m = (t >= 0) & (t <= w)
    if not m.any():
        return None
    tt, cc = t[m], c[m]
    over = np.nonzero(cc > 1e-6)[0]
    return {"peak": float(cc.max()), "mean": float(np.trapz(cc, tt) / (tt[-1] - tt[0])), "t_first": float(tt[over[0]]) if len(over) else None,
            "t_max": float(tt[-1])}


def main(run: Path, rans: Path, t_pre: float):
    tl, cl, scale = lbm_probe(run, t_pre)
    tr, cr = rans_probe(rans)
    print(f"LBM injected-volume rescale factor: {scale:.3f}")
    for j, nose in enumerate(("releaser", "neighbour")):
        for w in (30, 60, 120):
            sl, sr = stats(tl, cl[:, j], w), stats(tr, cr[:, j], w)
            fmt = lambda s: "n/a" if s is None else f"peak {s['peak']:.3g}  mean {s['mean']:.3g}  first>1e-6 {s['t_first']}  (to {s['t_max']:.0f} s)"  # noqa: E731
            print(f"{nose:9s} {w:3d} s | LBM {fmt(sl)}\n{'':9s}       | RANS {fmt(sr)}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), float(sys.argv[3]) if len(sys.argv) > 3 else 30.0)
