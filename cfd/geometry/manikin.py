"""Simplified seated manikin and chair built from primitives (no scanned or copyrighted geometry).

Coordinates: x forward (face direction), y lateral, z up; seat surface at z = 0.45 m; mid-sagittal plane y = 0.
Seated eye height above the seat is ~0.78 m (ANSUR II p50 male 0.804 m, female 0.748 m).
Writes ASCII STL files: body.stl (heated skin surface) and chair.stl (adiabatic).

Usage: python3 manikin.py <out_dir>
"""
import sys
from pathlib import Path

import numpy as np

SEAT_Z = 0.45
NOSE = np.array([0.075, 0.0, 1.215])  # approximate nose tip, used for probes (seat-to-nose 0.765 m)


def _tri_grid(P):
    """Triangulate a structured (nu, nv, 3) point grid into triangles."""
    tris = []
    nu, nv, _ = P.shape
    for i in range(nu - 1):
        for j in range(nv - 1):
            a, b, c, d = P[i, j], P[i + 1, j], P[i + 1, j + 1], P[i, j + 1]
            tris += [(a, b, c), (a, c, d)]
    return tris


def ellipsoid(c, r, n=24):
    u = np.linspace(0, np.pi, n)
    v = np.linspace(0, 2 * np.pi, 2 * n)
    U, V = np.meshgrid(u, v, indexing="ij")
    P = np.stack([c[0] + r[0] * np.sin(U) * np.cos(V), c[1] + r[1] * np.sin(U) * np.sin(V),
                  c[2] + r[2] * np.cos(U)], axis=-1)
    return _tri_grid(P)


def cylinder(p0, p1, rx, ry=None, n=32, caps=True):
    """Elliptic cylinder from p0 to p1 (semi-axes rx, ry in a frame perpendicular to the axis)."""
    ry = rx if ry is None else ry
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    ax = p1 - p0
    ax /= np.linalg.norm(ax)
    ref = np.array([0, 0, 1.0]) if abs(ax[2]) < 0.9 else np.array([1.0, 0, 0])
    e1 = np.cross(ax, ref); e1 /= np.linalg.norm(e1)
    e2 = np.cross(ax, e1)
    if abs(ax[2]) > 0.9:  # vertical: make e1 = x, e2 = y so (rx, ry) map to (x, y)
        e1, e2 = np.array([1.0, 0, 0]), np.array([0, 1.0, 0])
    t = np.linspace(0, 2 * np.pi, n)
    ring = lambda p: p + rx * np.outer(np.cos(t), e1) + ry * np.outer(np.sin(t), e2)  # noqa: E731
    P = np.stack([ring(p0), ring(p1)])
    tris = _tri_grid(P)
    if caps:
        for p, rg, flip in ((p0, ring(p0), True), (p1, ring(p1), False)):
            for k in range(n - 1):
                tris.append((p, rg[k + 1], rg[k]) if flip else (p, rg[k], rg[k + 1]))
    return tris


def box(lo, hi):
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    v = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                  [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]])
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (1, 2, 6, 5), (0, 4, 7, 3)]
    tris = []
    for a, b, c, d in faces:
        tris += [(v[a], v[b], v[c]), (v[a], v[c], v[d])]
    return tris


def _shift(tris, dx=0.0, dy=0.0, dz=0.0):
    d = np.array([dx, dy, dz])
    return [tuple(np.asarray(p) + d for p in tri) for tri in tris]


HIP = np.array([-0.07, 0.0, SEAT_Z + 0.01])  # recline pivot: bottom of the torso axis


def _recline(tris, deg):
    """Rotate triangles backwards (top towards -x) by deg about the lateral axis through HIP."""
    if not deg:
        return tris
    a = np.radians(deg)
    R = np.array([[np.cos(a), 0.0, -np.sin(a)], [0.0, 1.0, 0.0], [np.sin(a), 0.0, np.cos(a)]])
    return [tuple(HIP + R @ (np.asarray(p) - HIP) for p in tri) for tri in tris]


def nose_tip(recline_deg: float = 0.0):
    """Nose tip of a manikin reclined by recline_deg (lateral offset 0)."""
    return _recline([(NOSE,)], recline_deg)[0][0]


def body(dy: float = 0.0, recline_deg: float = 0.0):
    """Seated manikin centred at lateral offset dy (m); the upper body (torso, head, arms) reclined by recline_deg
    about the hip, so the back closes onto the backrest while the pelvis and legs stay put."""
    return _shift(_body(recline_deg), dy=dy)


def _body(recline_deg: float = 0.0):
    t = []
    t += cylinder((-0.07, 0, SEAT_Z + 0.01), (-0.07, 0, 1.05), 0.11, 0.17)       # torso (elliptic)
    t += ellipsoid((-0.07, 0, 1.05), (0.11, 0.19, 0.07))                          # shoulders cap
    t += cylinder((-0.05, 0, 1.03), (-0.05, 0, 1.16), 0.055)                      # neck
    t += ellipsoid((-0.03, 0, 1.24), (0.10, 0.08, 0.12))                          # head
    t += ellipsoid((0.065, 0, 1.215), (0.02, 0.015, 0.025))                       # nose
    for s in (-1, 1):
        t += cylinder((-0.07, s * 0.21, 1.00), (-0.04, s * 0.22, 0.73), 0.045)               # upper arm
        t += cylinder((-0.04, s * 0.21, 0.73), (0.28, s * 0.14, 0.62), 0.04)                 # forearm
    t = _recline(t, recline_deg)
    for s in (-1, 1):
        t += cylinder((-0.10, s * 0.10, SEAT_Z + 0.08), (0.44, s * 0.10, SEAT_Z + 0.08), 0.08)  # thigh
        t += cylinder((0.45, s * 0.10, SEAT_Z + 0.06), (0.45, s * 0.10, 0.06), 0.055)        # lower leg
        t += box((0.38, s * 0.10 - 0.05, 0.0), (0.66, s * 0.10 + 0.05, 0.07))                # foot
    return t


STAND_NOSE = np.array([0.075, 0.0, 1.59])  # standing nose tip (stature ~1.69 m, mean of ANSUR II p50 male/female)
STAND_REL = np.array([-0.195, 0.0, 0.83])  # release point behind the buttocks, as on the sofa relative to the torso


def standing(dx: float = 0.0, dy: float = 0.0, facing: int = 1):
    """Standing manikin facing +x (facing = 1) or -x (facing = -1), centred at (dx, dy). Same torso, head and nose
    primitives as the seated one, raised by 0.375 m (nose at 1.59 m); straight legs, arms hanging at the sides.
    The body is mirror-symmetric about its own y = 0, so facing -x is the x-mirror (vertex order reversed)."""
    t = _standing()
    if facing < 0:
        t = [tuple((-p[0], p[1], p[2]) for p in tri[::-1]) for tri in t]
    return _shift(t, dx=dx, dy=dy)


def _standing():
    t = []
    t += cylinder((-0.07, 0, 0.80), (-0.07, 0, 1.425), 0.11, 0.17)               # torso incl. pelvis (elliptic)
    t += ellipsoid((-0.07, 0, 1.425), (0.11, 0.19, 0.07))                         # shoulders cap
    t += cylinder((-0.05, 0, 1.405), (-0.05, 0, 1.535), 0.055)                    # neck
    t += ellipsoid((-0.03, 0, 1.615), (0.10, 0.08, 0.12))                         # head
    t += ellipsoid((0.065, 0, 1.59), (0.02, 0.015, 0.025))                        # nose
    for s in (-1, 1):
        t += cylinder((-0.07, s * 0.20, 1.37), (-0.05, s * 0.20, 0.78), 0.045)   # arm, hanging
        t += cylinder((-0.05, s * 0.10, 0.88), (-0.03, s * 0.10, 0.07), 0.065)   # leg
        t += box((-0.08, s * 0.10 - 0.05, 0.0), (0.18, s * 0.10 + 0.05, 0.07))   # foot
    return t


def trouser_parts(posture: str, o: float, dx: float = 0.0, dy: float = 0.0, recline_deg: float = 0.0, facing: int = 1):
    """Long trousers as offset surfaces: the lower-body primitives they cover, inflated by o (m). posture 'seated'
    (pelvis section of the torso from the seat to the waist, thighs, lower legs) or 'standing' (pelvis section, legs).
    Returns one closed surface per primitive; the CFD case takes the union of the parts inflated by the air gap and
    by gap + fabric thickness, and makes the shell between them a porous zone."""
    if posture == "seated":
        parts = [_recline(cylinder((-0.07, 0, SEAT_Z + 0.01 - o), (-0.07, 0, SEAT_Z + 0.22), 0.11 + o, 0.17 + o),
                          recline_deg)]
        for s in (-1, 1):
            parts.append(cylinder((-0.10 - o, s * 0.10, SEAT_Z + 0.08), (0.44 + o, s * 0.10, SEAT_Z + 0.08), 0.08 + o))
            parts.append(cylinder((0.45, s * 0.10, SEAT_Z + 0.06 + o), (0.45, s * 0.10, 0.07), 0.055 + o))
    elif posture == "standing":
        parts = [cylinder((-0.07, 0, 0.80 - o), (-0.07, 0, 1.02), 0.11 + o, 0.17 + o)]
        for s in (-1, 1):
            parts.append(cylinder((-0.05, s * 0.10, 0.88), (-0.03, s * 0.10, 0.07), 0.065 + o))
    else:
        raise ValueError(posture)
    if facing < 0:
        parts = [[tuple((-p[0], p[1], p[2]) for p in tri[::-1]) for tri in t] for t in parts]
    return [_shift(t, dx=dx, dy=dy) for t in parts]


def write_trousers(out: Path, name: str, posture: str, gap: float, thickness: float, **kw):
    """Write <name>_in_<k>.stl (inflated by gap) and <name>_out_<k>.stl (gap + thickness); returns both name lists."""
    names = {"in": [], "out": []}
    for side, o in (("in", gap), ("out", gap + thickness)):
        for k, t in enumerate(trouser_parts(posture, o, **kw)):
            fn = f"{name}_{side}_{k}.stl"
            # reversed winding: the primitives' triangles face inwards, and createZones' insideSurface uses the normals
            write_stl(out / fn, f"{name}_{side}_{k}", [tri[::-1] for tri in t])
            names[side].append(fn)
    return names["in"], names["out"]


# Elevator car, rated load 630 kg / 8 persons: inside 1.10 m wide x 1.40 m deep (KONE MonoSpace planning guide;
# 1.54 m2 <= EN 81-20 Table 6 maximum 1.66 m2), car height 2.10 m (the lower of the offered 2.10 / 2.20 m).
# x = depth (door at x = CAR[0]), y = width, z = height. Four occupants in a 2 x 2 grid, all facing the door.
CAR = (1.40, 1.10, 2.10)
OCCUPANTS = {"FL": (0.95, -0.27), "FR": (0.95, 0.27), "BL": (0.45, -0.27), "BR": (0.45, 0.27)}


def write_elevator(out: Path):
    """Elevator whodunit: one STL per occupant (FL, FR, BL, BR = front/back, left/right)."""
    out.mkdir(parents=True, exist_ok=True)
    for name, (x, y) in OCCUPANTS.items():
        write_stl(out / f"{name}.stl", name, standing(x, y))


# Standing pair (scenario D'): two people talking face to face, noses 1.0 m apart, in the sofa room
# (3.2 x 3.2 x 2.6 m, x in [0, 3.2], y in [-1.6, 1.6]); about 0.8 m of open floor behind each back.
# culprit C faces +x, neighbour N faces -x; (x centre, y, facing).
PAIR = {"C": (1.1 - STAND_NOSE[0], 0.0, 1), "N": (2.1 + STAND_NOSE[0], 0.0, -1)}


def write_pair(out: Path):
    """Standing pair: C.stl (culprit), N.stl (neighbour)."""
    out.mkdir(parents=True, exist_ok=True)
    for name, (x, y, f) in PAIR.items():
        write_stl(out / f"{name}.stl", name, standing(x, y, f))


def sofa(half_width=0.85):
    """Two-seat sofa: seat block, backrest and armrests (seat surface at SEAT_Z)."""
    hw = half_width
    t = box((-0.25, -hw, 0.0), (0.30, hw, SEAT_Z))                    # seat block
    t += box((-0.42, -hw - 0.15, 0.0), (-0.21, hw + 0.15, 0.95))      # backrest
    for s_ in (-1, 1):
        lo, hi = sorted((s_ * (hw - 0.02), s_ * (hw + 0.15)))  # overlap the seat: no coincident faces
        t += box((-0.25, lo, 0.0), (0.30, hi, 0.65))                  # armrest
    return t


def chair():
    return box((-0.22, -0.25, 0.0), (0.25, 0.25, SEAT_Z)) + box((-0.29, -0.25, SEAT_Z), (-0.21, 0.25, 1.0))


def write_stl(path, name, tris):
    with open(path, "w") as fh:
        fh.write(f"solid {name}\n")
        for a, b, c in tris:
            n = np.cross(np.subtract(b, a), np.subtract(c, a))
            nn = np.linalg.norm(n)
            if nn < 1e-12:  # drop degenerate (pole / seam) triangles
                continue
            n = n / nn
            fh.write(f" facet normal {n[0]:.6e} {n[1]:.6e} {n[2]:.6e}\n  outer loop\n")
            for p in (a, b, c):
                fh.write(f"   vertex {p[0]:.6e} {p[1]:.6e} {p[2]:.6e}\n")
            fh.write("  endloop\n endfacet\n")
        fh.write(f"endsolid {name}\n")


def write_scene(out: Path, dy_farter=-0.30, dy_neighbour=0.30, recline_farter=0.0):
    """Sofa duet: farter.stl, neighbour.stl, sofa.stl. recline_farter (deg) reclines the releaser only."""
    out.mkdir(parents=True, exist_ok=True)
    write_stl(out / "farter.stl", "farter", body(dy_farter, recline_farter))
    write_stl(out / "neighbour.stl", "neighbour", body(dy_neighbour))
    write_stl(out / "sofa.stl", "sofa", sofa())


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    write_stl(out / "body.stl", "body", body())
    write_stl(out / "chair.stl", "chair", chair())
    print("wrote", out / "body.stl", out / "chair.stl")
