"""Convert the ASCII STL files written by cfd/geometry/manikin.py to binary STL (FluidX3D reads binary only).
Coordinates stay in metres; the FluidX3D setup scales them to the lattice.
Usage: python3 cfd/lbm/stl_to_binary.py <in.stl> <out.stl>
"""
import struct
import sys


def convert(src, dst):
    tris, cur = [], []
    for line in open(src):
        w = line.split()
        if w and w[0] == "vertex":
            cur.append(tuple(map(float, w[1:4])))
            if len(cur) == 3:
                tris.append(cur)
                cur = []
    with open(dst, "wb") as f:
        f.write(b"\0" * 80)
        f.write(struct.pack("<I", len(tris)))
        for t in tris:
            f.write(struct.pack("<12fH", 0.0, 0.0, 0.0, *t[0], *t[1], *t[2], 0))
    return len(tris)


if __name__ == "__main__":
    print(convert(sys.argv[1], sys.argv[2]), "triangles")
