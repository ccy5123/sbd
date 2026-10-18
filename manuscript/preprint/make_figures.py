"""Manuscript versions of the figures: the analysis scripts' own "Fig. N ·" titles are dropped (LaTeX numbers and
captions the figures), everything else is unchanged.

Each figure script is run unmodified with matplotlib's Figure.suptitle patched to a no-op and Figure.savefig redirected
into manuscript/preprint/figs/ (same file name). Scripts are deterministic (fixed seeds), so the result files they
also write are reproduced unchanged.
Usage (repo root): python3 manuscript/preprint/make_figures.py [script ...]
"""
import runpy
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib.figure import Figure

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "manuscript/preprint/figs"
SCRIPTS = {  # script -> argv
    "acoustics/run_m2.py": [],
    "cfd/validation/jet/analyze.py": [],
    "cfd/validation/cbl/analyze.py": [],
    "cfd/cases/sofa/analyze_sofa.py": [],
    "cfd/cases/sofa/fig_sofa_planes.py": [],
    "uq/run_m7.py": [],
    "perception/run_selection.py": [],
    "culture/make_map.py": [],
    "chem/fig_chem.py": [],
    "cfd/cases/elevator/fig_elevator.py": [],
}
_save = Figure.savefig


def _savefig(self, fname, *args, **kwargs):
    return _save(self, OUT / Path(str(fname)).name, *args, **kwargs)


def main(selected):
    OUT.mkdir(exist_ok=True)
    Figure.suptitle = lambda self, *a, **k: None
    Figure.savefig = _savefig
    for script in selected or SCRIPTS:
        path = ROOT / script
        sys.argv = [str(path), *SCRIPTS.get(script, [])]
        sys.path.insert(0, str(path.parent))
        print("running", script, flush=True)
        runpy.run_path(str(path), run_name="__main__")
        sys.path.pop(0)
    print("figures in", OUT)


if __name__ == "__main__":
    main(sys.argv[1:])
