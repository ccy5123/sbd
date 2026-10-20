"""3D odour clouds for the run viewer: the iso-surfaces the multi-release cases write (postProcessing/isoSurfaces/<t>/
s<k>_<level>.vtk, legacy ASCII polydata; levels OAV 0.1 / 1 / 20, see ISO_LEVELS in cfd/cases/sofa/make_case.py).

For each release, picks frames at AFTER s after the release, fan-triangulates the polygons and decimates them by vertex
clustering (cell H[level]). Writes one gzip-compressed binary per release, <out>/<name>/iso_<release>.bin: for each
frame and level, vertices as int16 mm (padded to 4 bytes) then triangle indices delta-coded as int32. The block layout
(offset, vertex and triangle counts) goes into <out>/<name>/run.json under "iso", so run export_viewer.py first.
Usage: python3 cfd/postprocess/export_iso.py <out_dir> <name>=<case_dir> ...
"""
import gzip
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_multi as am  # noqa: E402

H = {"oav0.1": 0.03, "oav1": 0.025, "oav20": 0.015}  # m, clustering cell per level
AFTER = (1, 2, 3, 4, 5, 7, 10, 15, 20, 25, 30, 40, 50, 60, 75, 90, 120, 150)  # s after a release


def read_vtk(path):
    tok = path.read_text().split()
    i = tok.index("POINTS")
    n = int(tok[i + 1])
    pts = np.array(tok[i + 3:i + 3 + 3 * n], float).reshape(-1, 3)
    if n == 0 or "POLYGONS" not in tok:
        return pts, np.zeros((0, 3), int)
    j = tok.index("POLYGONS", i)
    size = int(tok[j + 2])
    conn = np.array(tok[j + 3:j + 3 + size], int)
    tris, k = [], 0
    while k < size:
        m = conn[k]
        poly = conn[k + 1:k + 1 + m]
        tris += [(poly[0], poly[q], poly[q + 1]) for q in range(1, m - 1)]
        k += m + 1
    return pts, np.array(tris, int).reshape(-1, 3)


def decimate(pts, tris, h):
    if len(tris) == 0:
        return np.zeros((0, 3)), np.zeros((0, 3), int)
    key = np.floor(pts / h).astype(np.int64)
    _, inv = np.unique(key, axis=0, return_inverse=True)
    inv = inv.ravel()
    nc = inv.max() + 1
    cen = np.column_stack([np.bincount(inv, pts[:, d], nc) for d in range(3)]) / np.bincount(inv, minlength=nc)[:, None]
    t = inv[tris]
    t = t[(t[:, 0] != t[:, 1]) & (t[:, 1] != t[:, 2]) & (t[:, 0] != t[:, 2])]
    _, first = np.unique(np.sort(t, axis=1), axis=0, return_index=True)
    t = t[np.sort(first)]
    used, t = np.unique(t, return_inverse=True)
    return cen[used], t.reshape(-1, 3)


def block(v, t):
    vb = np.round(v * 1000).astype("<i2").tobytes()
    vb += b"\0" * (-len(vb) % 4)
    return vb + np.diff(np.concatenate([[0], t.ravel()])).astype("<i4").tobytes()


def export_run(out, name, case):
    d = case / "postProcessing/isoSurfaces"
    times = sorted((float(p.name), p) for p in d.iterdir() if re.fullmatch(r"[0-9.eE+-]+", p.name))
    tv = np.array([t for t, _ in times])
    plan, t0, gap, window = am.release_plan(case)
    run_dir = out / name
    run_dir.mkdir(parents=True, exist_ok=True)
    index = []
    for k, r in enumerate(plan):
        rname, t_rel, sc = r[0], t0 + gap * k, f"s{k + 1}"
        buf, frames = bytearray(), []
        for a in AFTER:
            if a > window:
                continue
            j = int(np.argmin(np.abs(tv - (t_rel + a))))
            if abs(tv[j] - (t_rel + a)) >= 0.5:
                continue
            surf = {}
            for lev, h in H.items():
                f = times[j][1] / f"{sc}_{lev}.vtk"
                if f.exists():
                    v, t = decimate(*read_vtk(f), h)
                    if len(t):
                        surf[lev] = [len(buf), len(v), len(t)]
                        buf += block(v, t)
            frames.append({"after": a, "t": times[j][0], "surf": surf})
        if not any(fr["surf"] for fr in frames):
            continue
        fn = f"iso_{rname}.bin"
        (run_dir / fn).write_bytes(gzip.compress(bytes(buf), 9))
        index.append({"release": rname, "t_release": t_rel, "file": fn, "frames": frames})
        print(name, rname, len(frames), "frames", f"{len(buf) / 1e6:.1f} MB raw,",
              f"{(run_dir / fn).stat().st_size / 1e6:.1f} MB gz")
    meta_f = run_dir / "run.json"
    meta = json.loads(meta_f.read_text())
    meta["iso"] = index
    meta["iso_levels"] = list(H)
    meta_f.write_text(json.dumps(meta, separators=(",", ":")))


def main(out, specs):
    for spec in specs:
        name, case = spec.split("=", 1)
        if (Path(case) / "postProcessing/isoSurfaces").is_dir():
            export_run(out, name, Path(case))
        else:
            print(name, "no iso-surfaces yet")


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2:])
