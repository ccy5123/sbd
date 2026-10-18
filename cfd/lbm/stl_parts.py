"""Split ASCII STL files into closed parts (connected components by shared vertices) and write each as binary STL.

FluidX3D voxelizes a mesh by ray parity, so where two closed primitives of one mesh overlap (seat block and backrest,
torso and thighs) the overlap counts as outside and becomes a sealed fluid pocket inside the solid. Voxelizing each
part separately and taking the union avoids this. Writes <out_dir>/<name>_NNN.stl and <out_dir>/<name>.parts (list).
Usage: python3 cfd/lbm/stl_parts.py <out_dir> <name> <in1.stl> [<in2.stl> ...]
"""
import struct
import sys
from pathlib import Path


def read_ascii(path):
    tris, cur = [], []
    for line in open(path):
        w = line.split()
        if w and w[0] == "vertex":
            cur.append(tuple(round(float(x), 7) for x in w[1:4]))
            if len(cur) == 3:
                tris.append(tuple(cur))
                cur = []
    return tris


def components(tris):
    parent = {}

    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for t in tris:
        for v in t[1:]:
            ra, rb = find(t[0]), find(v)
            if ra != rb:
                parent[rb] = ra
    groups = {}
    for t in tris:
        groups.setdefault(find(t[0]), []).append(t)
    return list(groups.values())


def write_binary(path, tris):
    with open(path, "wb") as f:
        f.write(b"\0" * 80)
        f.write(struct.pack("<I", len(tris)))
        for t in tris:
            f.write(struct.pack("<12fH", 0.0, 0.0, 0.0, *t[0], *t[1], *t[2], 0))


if __name__ == "__main__":
    out, name = Path(sys.argv[1]), sys.argv[2]
    tris = [t for p in sys.argv[3:] for t in read_ascii(p)]
    parts = components(tris)
    files = []
    for i, part in enumerate(parts):
        fn = f"{name}_{i:03d}.stl"
        write_binary(out / fn, part)
        files.append(fn)
    (out / f"{name}.parts").write_text("\n".join(files) + "\n")
    print(name, len(parts), "parts,", len(tris), "triangles")
