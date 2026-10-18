"""Reproduction check for the 10-minute reruns (HANDOFF item 2): compare a rerun's nose-probe series with the archived
one (cfd/probe_archive/nose_probes.tar.xz) over the archived window.

For each probe and field, the rerun is interpolated onto the archived times up to t_max. Reported: the archived peak,
the rerun peak, and max |rerun - archive| relative to the archived peak (s: scalar; T: temperature minus its initial
value; U: speed).
Usage: python3 cfd/postprocess/compare_probes.py <rerun_case> <archived_case> [t_max]
"""
import re
import sys
from pathlib import Path

import numpy as np


def read_probe(case: Path, field: str):
    """Concatenate postProcessing/noses/<start>/<field> over all start times; later files win on overlap."""
    d = case / "postProcessing/noses"
    parts = []
    for sub in sorted((p for p in d.iterdir() if re.fullmatch(r"[0-9.eE+-]+", p.name)), key=lambda p: float(p.name)):
        f = sub / field
        if f.exists():
            txt = f.read_text().replace("(", " ").replace(")", " ")
            rows = [list(map(float, ln.split())) for ln in txt.splitlines() if ln.strip() and not ln.startswith("#")]
            parts.append(np.array(rows))
    a = np.vstack(parts[::-1])
    _, idx = np.unique(a[:, 0], return_index=True)
    a = a[idx]
    t, v = a[:, 0], a[:, 1:]
    if field == "U":  # three components per probe -> speed
        v = np.linalg.norm(v.reshape(len(t), -1, 3), axis=2)
    if field == "T":
        v = v - v[0]
    return t, v


def main(new: Path, old: Path, t_max: float):
    ok = True
    for field in ("s", "T", "U"):
        t0, v0 = read_probe(old, field)
        t1, v1 = read_probe(new, field)
        m = (t0 <= min(t_max, t1[-1]))
        print(f"{field}: rerun reaches t = {t1[-1]:.2f} s, compared over [0, {t0[m][-1]:.2f}] s")
        for j in range(v0.shape[1]):
            ref = v0[m, j]
            got = np.interp(t0[m], t1, v1[:, j])
            peak = np.max(np.abs(ref))
            rel = np.max(np.abs(got - ref)) / peak if peak > 0 else float(np.max(np.abs(got)))
            flag = "" if rel < 0.05 else "  <-- differs"
            ok &= rel < 0.05 or peak == 0
            print(f"  probe {j}: archive peak {peak:.4g}, rerun peak {np.max(np.abs(got)):.4g}, max rel diff {rel:.3g}{flag}")
    print("REPRODUCED" if ok else "NOT REPRODUCED")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), float(sys.argv[3]) if len(sys.argv) > 3 else np.inf)
