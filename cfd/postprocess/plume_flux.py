"""Momentum flux of the body's convective boundary layer where a release enters it, for the routing map (A1 of
manuscript/preprint/interface_plan.md section 9).

For each developed precursor field (time T, no release yet), horizontal cut planes at DZ above the release point are
sampled (foamPostProcess, cell values, VTK) and integrated over the upward-moving air in a square of half-width HALF
around the release point:
  Q_p = sum w A          (m^3/s, upward volume flux)
  m_p = sum w^2 A        (m^4/s^2, kinematic momentum flux; compare with the release's M0 = Q0 u0)
  B_p = sum g beta (T - T_room) w A   (m^4/s^3, buoyancy flux, for a Richardson number)
plus the peak upward speed. Faces inside bodies or furniture are not on the plane, so they drop out by themselves.
Usage (OpenFOAM environment): python3 cfd/postprocess/plume_flux.py <out.json> <name>=<case>:<x>,<y>,<z>[:<time>] ...
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

DZ = (0.05, 0.15, 0.30)  # m above the release point
HALF = 0.30              # m, half-width of the integration square
G, T_ROOM = 9.81, 296.15


def sample(case: Path, z_list, time):
    """Write cut planes at heights z_list for `time`; return {z: path of the VTK file}."""
    surf = "".join(f"        z{k} {{ type cutPlane; planeType pointAndNormal; point (0 0 {z:.4f}); normal (0 0 1); "
                   f"interpolate false; }}\n" for k, z in enumerate(z_list))
    d = case / "system/plumeFluxDict"
    d.write_text("FoamFile { format ascii; class dictionary; object plumeFluxDict; }\n"
                 "plumeFlux\n{\n    type surfaces;\n    libs (\"libsampling.so\");\n    surfaceFormat vtk;\n"
                 "    interpolationScheme cell;\n    fields (U T);\n    surfaces\n    {\n" + surf + "    }\n}\n")
    subprocess.run(["foamPostProcess", "-case", str(case), "-dict", "system/plumeFluxDict", "-time", str(time)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    out = case / "postProcessing/plumeFlux" / f"{time:g}"
    return {z: out / f"z{k}.vtk" for k, z in enumerate(z_list)}


def read_vtk_cells(path: Path):
    """Points, polygons (lists of point indices) and cell fields of a legacy ASCII VTK polydata surface."""
    tok = path.read_text().split()
    i = tok.index("POINTS")
    n = int(tok[i + 1])
    pts = np.array(tok[i + 3:i + 3 + 3 * n], float).reshape(-1, 3)
    j = tok.index("POLYGONS", i)
    npoly, size = int(tok[j + 1]), int(tok[j + 2])
    conn = np.array(tok[j + 3:j + 3 + size], int)
    polys, k = [], 0
    while k < size:
        m = conn[k]
        polys.append(conn[k + 1:k + 1 + m])
        k += m + 1
    fields = {}
    c = tok.index("CELL_DATA", j)
    k = tok.index("FIELD", c) + 3
    while k < len(tok) and len(fields) < 2:
        name, ncomp, nval = tok[k], int(tok[k + 1]), int(tok[k + 2])
        fields[name] = np.array(tok[k + 4:k + 4 + ncomp * nval], float).reshape(nval, ncomp)
        k += 4 + ncomp * nval
    return pts, polys, fields


def plane_fluxes(path: Path, x0, y0):
    pts, polys, f = read_vtk_cells(path)
    area = np.array([0.5 * abs(np.dot(pts[p, 0], np.roll(pts[p, 1], -1)) - np.dot(pts[p, 1], np.roll(pts[p, 0], -1)))
                     for p in polys])
    cen = np.array([pts[p].mean(axis=0) for p in polys])
    w, T = f["U"][:, 2], f["T"][:, 0]
    m = (np.abs(cen[:, 0] - x0) <= HALF) & (np.abs(cen[:, 1] - y0) <= HALF) & (w > 0)
    a, w, T = area[m], w[m], T[m]
    return {"Q_p": float(np.sum(w * a)), "m_p": float(np.sum(w**2 * a)),
            "B_p": float(np.sum(G / T_ROOM * (T - T_ROOM) * w * a)), "w_max": float(w.max()) if len(w) else 0.0,
            "area_up": float(a.sum())}


def main(out: Path, specs):
    res = {"DZ": DZ, "HALF": HALF, "cases": {}}
    for spec in specs:
        name, rest = spec.split("=", 1)
        parts = rest.split(":")
        case, (x0, y0, z0) = Path(parts[0]), map(float, parts[1].split(","))
        time = float(parts[2]) if len(parts) > 2 else 90.0
        files = sample(case, [z0 + dz for dz in DZ], time)
        res["cases"][name] = {"case": case.name, "release": [x0, y0, z0], "time": time,
                              "planes": {f"{dz:g}": plane_fluxes(files[z0 + dz], x0, y0) for dz in DZ}}
        print(name, {k: round(v["m_p"], 6) for k, v in res["cases"][name]["planes"].items()})
    out.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2:])
