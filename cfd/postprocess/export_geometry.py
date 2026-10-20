"""Scene geometry for the 3D run viewer: the same primitives the OpenFOAM cases mesh (cfd/geometry/manikin.py and the
case generators), as compact JSON for a browser.

Each scene has a room box, solid objects (triangle soups, coordinates in integer millimetres), the trousers shell
(outer offset surfaces, shown translucent), nose probe points, the release point and its direction, and openings
(vent, supply slots, exhaust). Writes <out>/geometry.json.
Usage: python3 cfd/postprocess/export_geometry.py <out_dir>
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cfd/geometry"))
import manikin  # noqa: E402


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sofa_case = load("sofa_case", "cfd/cases/sofa/make_case.py")
stand_case = load("standing_case", "cfd/cases/standing/make_case.py")
elev_case = load("elevator_case", "cfd/cases/elevator/make_case.py")


def mm(tris):
    """Triangle soup -> flat list of integer millimetres."""
    a = np.round(np.asarray(tris, float).reshape(-1) * 1000.0).astype(int)
    return a.tolist()


def tube(p1, direction, radius, length):
    d = np.asarray(direction, float)
    d /= np.linalg.norm(d)
    p1 = np.asarray(p1, float)
    return manikin.cylinder(p1 - length * d, p1, radius, caps=True, n=24)


def box_room(domain):
    return [[a, b] for a, b in domain]


def sofa_scene(recline):
    dyf, dyn = sofa_case.DY_F, sofa_case.DY_N
    nf = manikin.nose_tip(recline)
    tr = []
    for dy, rec in ((dyf, recline), (dyn, 0.0)):
        tr += [mm(t) for t in manikin.trouser_parts("seated", sofa_case.GAP + sofa_case.FABRIC, dy=dy, recline_deg=rec)]
    return {
        "room": box_room(sofa_case.DOMAIN),
        "objects": [
            {"name": "releaser", "kind": "body", "tris": mm(manikin.body(dyf, recline))},
            {"name": "neighbour", "kind": "body", "tris": mm(manikin.body(dyn))},
            {"name": "sofa", "kind": "furniture", "tris": mm(manikin.sofa())},
            {"name": "nozzle", "kind": "nozzle", "tris": mm(tube(sofa_case.REL, sofa_case.REL_DIR, sofa_case.R_E, sofa_case.L_E))},
        ],
        "trousers": tr,
        "probes": {"releaser": [nf[0] + sofa_case.NOSE_X - manikin.NOSE[0], dyf, nf[2]],
                   "neighbour": [sofa_case.NOSE_X, dyn, sofa_case.NOSE_Z]},
        "release": {"point": list(sofa_case.REL), "dir": list(sofa_case.REL_DIR)},
        "openings": [{"name": "ceiling vent (pressure relief)", "box": [[1.6, 1.0, 2.58], [2.1, 1.5, 2.6]]}],
        "planes": {"noseHeight": {"axis": "z", "at": sofa_case.NOSE_Z}, "midFarter": {"axis": "y", "at": dyf}},
    }


def standing_scene():
    objs = [{"name": "culprit" if n == "C" else "neighbour", "kind": "body", "tris": mm(manikin.standing(x, y, f))}
            for n, (x, y, f) in manikin.PAIR.items()]
    objs.append({"name": "nozzle", "kind": "nozzle", "tris": mm(tube(stand_case.rel_point(), stand_case.REL_DIR, stand_case.R_E, stand_case.L_E))})
    tr = []
    for n, (x, y, f) in manikin.PAIR.items():
        tr += [mm(t) for t in manikin.trouser_parts("standing", sofa_case.GAP + sofa_case.FABRIC, dx=x, dy=y, facing=f)]
    openings = [{"name": f"supply slot {k} (ventilated case)", "box": [[lo[0], lo[1], 2.58], [hi[0], hi[1], 2.6]]}
                for k, (lo, hi, _) in stand_case.SLOTS.items()]
    ex = [[float(v) for v in s.strip("() ").split()] for s in stand_case.EXHAUST_BOX.split(") (")]
    openings.append({"name": "exhaust", "box": [[ex[0][0], ex[0][1], 2.58], [ex[1][0], ex[1][1], 2.6]]})
    return {
        "room": box_room(stand_case.DOMAIN),
        "objects": objs,
        "trousers": tr,
        "probes": {"releaser": list(stand_case.nose_probe("C")), "neighbour": list(stand_case.nose_probe("N"))},
        "release": {"point": stand_case.rel_point().tolist(), "dir": list(stand_case.REL_DIR)},
        "openings": openings,
        "planes": {"noseHeight": {"axis": "z", "at": float(manikin.STAND_NOSE[2])}, "midPlane": {"axis": "y", "at": 0.0}},
    }


def elevator_scene():
    cx, cy, cz = manikin.CAR
    objs = [{"name": n, "kind": "body", "tris": mm(manikin.standing(x, y))} for n, (x, y) in manikin.OCCUPANTS.items()]
    return {
        "room": [[0.0, cx], [-cy / 2, cy / 2], [0.0, cz]],
        "objects": objs,
        "trousers": [],
        "probes": {},
        "release": None,
        "openings": [],
        "planes": {},
    }


def main(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    scenes = {
        "sofa": {"label": "Sofa duet, upright", "geo": sofa_scene(0.0)},
        "sofa_rec4.5": {"label": "Sofa duet, releaser reclined 4.5 deg", "geo": sofa_scene(4.5)},
        "sofa_rec-10": {"label": "Sofa duet, releaser leaning forward 10 deg", "geo": sofa_scene(-10.0)},
        "standing": {"label": "Standing pair, face to face", "geo": standing_scene()},
        "elevator": {"label": "Elevator car, four occupants (supplement)", "geo": elevator_scene()},
    }
    (out / "geometry.json").write_text(json.dumps(scenes, separators=(",", ":")))
    print("wrote", out / "geometry.json", f"{(out / 'geometry.json').stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
