"""Plane snapshots and nose series of running cases for the 3D run viewer.

For each run, reads the sampled planes (postProcessing/planes/<t>/<plane>.xy: face centres, s or s1..sN, T, U) at
snapshot times after each release, rasterises each plane onto a 1 cm grid (nearest sample within 1.5 cm; farther
cells are inside a body or furniture and stay transparent) and writes colour PNGs:
  odour  log10 OAV of that release's scalar, transparent below OAV 0.01 (OAV = s x OAV of undiluted flatus)
  T      air temperature, 23-27 C
  U      speed |U|, 0-0.4 m/s
plus the nose probe series (OAV per release, both noses) and a manifest.json the page reads.
Usage: python3 cfd/postprocess/export_viewer.py <out_dir> <name>=<case_dir>:<scene>[:single] ...
  e.g. sofa_bare=/w/sbd-v4/cfd/runs/sofa_v4_multi:sofa  ref_silent=/w/sbd/cfd/runs/sofa_silent:sofa:single
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_multi as am  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402

K_OAV = am.an.oav(1.0, am.an.P)  # OAV of undiluted flatus (s = 1)
AFTER = (1, 2, 3, 5, 7, 10, 15, 20, 25, 30, 45, 60, 90, 120, 150)  # s after a release
FLOW_EVERY = 10.0  # s between temperature/speed snapshots
RES = 0.01  # m
CMAPS = {"odour": ("magma", -2.0, 3.0), "T": ("coolwarm", 23.0, 27.0), "U": ("viridis", 0.0, 0.4)}


def plane_times(case):
    d = case / "postProcessing/planes"
    return sorted((float(p.name), p) for p in d.iterdir() if re.fullmatch(r"[0-9.eE+-]+", p.name))


def read_plane(path):
    with open(path) as f:
        header = f.readline().lstrip("#").split()
    a = np.loadtxt(path, comments="#")
    return {h: a[:, i] for i, h in enumerate(header)}


def raster(cols, axis):
    u, v = ("face_x", "face_y") if axis == "z" else ("face_x", "face_z")
    pts = np.column_stack([cols[u], cols[v]])
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    gu = np.arange(lo[0], hi[0] + RES / 2, RES)
    gv = np.arange(lo[1], hi[1] + RES / 2, RES)
    GU, GV = np.meshgrid(gu, gv)
    dist, idx = cKDTree(pts).query(np.column_stack([GU.ravel(), GV.ravel()]))
    mask = (dist > 1.5 * RES).reshape(GU.shape)
    return idx.reshape(GU.shape), mask, [float(lo[0]), float(hi[0]), float(lo[1]), float(hi[1])]


def png(values, mask, field, path):
    cmap, vmin, vmax = CMAPS[field]
    x = np.clip((values - vmin) / (vmax - vmin), 0, 1)
    rgba = plt.get_cmap(cmap)(x)
    if field == "odour":
        rgba[..., 3] = np.where(values < vmin, 0.0, 0.9)
    rgba[mask, 3] = 0.0
    plt.imsave(path, rgba[::-1], origin="upper")  # row 0 = top (max v)


def export_run(out, name, case, scene, single):
    times = plane_times(case)
    tv = np.array([t for t, _ in times])
    if single:
        rels = [("92mL", 0.2, None)]
        window = 600.0
    else:
        plan, t0, gap, window = am.release_plan(case)
        rels = [(r[0], t0 + gap * k, k + 1) for k, r in enumerate(plan)]
    planes = sorted(p.stem for p in times[-1][1].glob("*.xy"))
    geo_axis = {p: ("z" if p == "noseHeight" else "y") for p in planes}
    grids = {}
    run_dir = out / name
    run_dir.mkdir(parents=True, exist_ok=True)
    snaps = []

    def snapshot(t_want, fields):
        k = int(np.argmin(np.abs(tv - t_want)))
        if abs(tv[k] - t_want) > 0.3:
            return None
        t, d = times[k]
        entry = {"t": t, "images": {}}
        for p in planes:
            cols = read_plane(d / f"{p}.xy")
            if p not in grids:
                grids[p] = raster(cols, geo_axis[p])
            idx, mask, ext = grids[p]
            for fname, col in fields:
                if fname == "odour":
                    with np.errstate(divide="ignore"):
                        val = np.log10(np.maximum(cols[col][idx], 1e-30) * K_OAV)
                elif fname == "T":
                    val = cols["T"][idx] - 273.15
                else:
                    val = np.sqrt(cols["U_x"] ** 2 + cols["U_y"] ** 2 + cols["U_z"] ** 2)[idx]
                fn = f"{p}_{fname}{col if fname == 'odour' else ''}_{t:g}.png"
                png(val, mask, fname, run_dir / fn)
                entry["images"][f"{p}|{fname}|{col if fname == 'odour' else ''}"] = fn
        return entry

    for rname, t_rel, k in rels:
        col = "s" if single else f"s{k}"
        for a in AFTER:
            if a > window or t_rel + a > tv[-1] + 0.3:
                continue
            e = snapshot(t_rel + a, [("odour", col)])
            if e:
                e.update({"release": rname, "after": a})
                snaps.append(e)
    t = FLOW_EVERY
    while t <= tv[-1] + 0.3:
        e = snapshot(t, [("T", ""), ("U", "")])
        if e:
            e.update({"release": None, "after": None})
            snaps.append(e)
        t += FLOW_EVERY
    # nose probe series, OAV per release, every 0.25 s
    series = {}
    for rname, t_rel, k in rels:
        col = "s" if single else f"s{k}"
        try:
            ts, s = am.an.read_probe(case, col)
        except Exception:
            continue
        m = ts >= t_rel
        grid = np.arange(t_rel, ts[-1], 0.25)
        if len(grid) < 2:
            continue
        series[rname] = {"t0": t_rel, "dt": 0.25,
                         "releaser": np.round(np.interp(grid, ts[m], s[m, 0]) * K_OAV, 4).tolist(),
                         "neighbour": np.round(np.interp(grid, ts[m], s[m, 1]) * K_OAV, 4).tolist()}
    ext = {p: grids[p][2] for p in grids}
    meta = {"name": name, "scene": scene, "single": single, "t_last": float(tv[-1]), "planes": planes,
            "plane_axis": geo_axis, "extent": ext, "releases": [{"name": r, "t_release": t} for r, t, _ in rels],
            "snapshots": snaps, "series": series}
    (run_dir / "run.json").write_text(json.dumps(meta, separators=(",", ":")))
    print(name, len(snaps), "snapshots,", sum(len(e["images"]) for e in snaps), "images, last t", tv[-1])
    return {"name": name, "scene": scene, "single": single, "t_last": float(tv[-1])}


def main(out, specs):
    out.mkdir(parents=True, exist_ok=True)
    runs = []
    for spec in specs:
        name, rest = spec.split("=", 1)
        parts = rest.split(":")
        runs.append(export_run(out, name, Path(parts[0]), parts[1], len(parts) > 2 and parts[2] == "single"))
    (out / "manifest.json").write_text(json.dumps({"runs": runs, "K_OAV": K_OAV, "cmaps": CMAPS}, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2:])
