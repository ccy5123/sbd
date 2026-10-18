"""PLAN v4 E0-5: frozen-flow vs coupled nose probes (same nose points, same branch time axis).

Reads postProcessing/noses/<start>/s from both cases (later restarts win), and for each nose and window reports the
peak and time-mean s and the worst-breath OAV (perception/pm via cfd/cases/sofa/analyze_sofa.breath_metrics), with the
frozen/coupled ratio. Only times reached by both runs are compared.
Usage: python3 cfd/frozen/compare_frozen.py <frozen_case> <coupled_case> [release_time=0.2]
"""
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cfd/cases/sofa"))
import analyze_sofa as an  # noqa: E402  (read_probe, breath_metrics, OAV scale)


def series(case: Path):
    t, c = an.read_probe(case, "s")
    return t, c


def main(frozen: Path, coupled: Path, t_rel: float):
    tf, cf = series(frozen)
    tc, cc = series(coupled)
    t_max = min(tf[-1], tc[-1])
    print(f"compared up to t = {t_max:.1f} s (release at {t_rel} s)")
    for j, nose in enumerate(("releaser", "neighbour")):
        for w in (30, 60, 120, 300, 600):
            if t_rel + w > t_max + 1e-6 and w != 30:
                continue
            out = []
            for t, c in ((tf, cf), (tc, cc)):
                m = (t >= t_rel) & (t <= min(t_rel + w, t_max))
                tt, x = t[m], c[m, j]
                wb_mean, wb_max = an.breath_metrics(tt, x)
                out.append((float(x.max()), float(np.trapz(x, tt) / (tt[-1] - tt[0])), wb_mean))
            r = [a / b if b > 0 else float("nan") for a, b in zip(out[0], out[1])]
            print(f"{nose:9s} {w:3d} s | frozen peak {out[0][0]:.3g} mean {out[0][1]:.3g} worst-breath {out[0][2]:.3g}"
                  f" | coupled peak {out[1][0]:.3g} mean {out[1][1]:.3g} worst-breath {out[1][2]:.3g}"
                  f" | ratio {r[0]:.2f} / {r[1]:.2f} / {r[2]:.2f}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), float(sys.argv[3]) if len(sys.argv) > 3 else 0.2)
