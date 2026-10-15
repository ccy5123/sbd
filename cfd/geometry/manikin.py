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


def body(dy: float = 0.0):
    """Seated manikin centred at lateral offset dy (m)."""
    return _shift(_body(), dy=dy)


def _body():
    t = []
    t += cylinder((-0.07, 0, SEAT_Z + 0.01), (-0.07, 0, 1.05), 0.11, 0.17)       # torso (elliptic)
    t += ellipsoid((-0.07, 0, 1.05), (0.11, 0.19, 0.07))                          # shoulders cap
    t += cylinder((-0.05, 0, 1.03), (-0.05, 0, 1.16), 0.055)                      # neck
    t += ellipsoid((-0.03, 0, 1.24), (0.10, 0.08, 0.12))                          # head
    t += ellipsoid((0.065, 0, 1.215), (0.02, 0.015, 0.025))                       # nose
    for s in (-1, 1):
        t += cylinder((-0.10, s * 0.10, SEAT_Z + 0.08), (0.44, s * 0.10, SEAT_Z + 0.08), 0.08)  # thigh
        t += cylinder((0.45, s * 0.10, SEAT_Z + 0.06), (0.45, s * 0.10, 0.06), 0.055)        # lower leg
        t += box((0.38, s * 0.10 - 0.05, 0.0), (0.66, s * 0.10 + 0.05, 0.07))                # foot
        t += cylinder((-0.07, s * 0.21, 1.00), (-0.04, s * 0.22, 0.73), 0.045)               # upper arm
        t += cylinder((-0.04, s * 0.21, 0.73), (0.28, s * 0.14, 0.62), 0.04)                 # forearm
    return t


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


def write_scene(out: Path, dy_farter=-0.30, dy_neighbour=0.30):
    """Sofa duet: farter.stl, neighbour.stl, sofa.stl."""
    out.mkdir(parents=True, exist_ok=True)
    write_stl(out / "farter.stl", "farter", body(dy_farter))
    write_stl(out / "neighbour.stl", "neighbour", body(dy_neighbour))
    write_stl(out / "sofa.stl", "sofa", sofa())


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    write_stl(out / "body.stl", "body", body())
    write_stl(out / "chair.stl", "chair", chair())
    print("wrote", out / "body.stl", out / "chair.stl")
