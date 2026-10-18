"""PLAN v4 E3: frozen-flow transport of the odour scalar after the coupled release phase.

Builds a case that transports s from a coupled branch at t_src to t_end on a frozen background flow, without solving
the flow (OpenFOAM 13 'functions' solver with subSolver 'fluid'): mesh, constant/ and system/ come from the branch;
the flow fields (U, phi, nut, alphat, p, p_rgh, T, rho, k, omega) from the background case at t_bg; s (and its
boundary conditions) from the branch at t_src. Diffusivity and nose probes as in the branch (scalarTransport with
alphal = alphat = 1/0.7). Both source cases must be reconstructed at the requested times.
Usage: python3 cfd/frozen/make_frozen.py <out> --bg <case> --t-bg 30 --src <case> --t-src 3 [--t-end 600]
       [--dt 0.02] [--write 60]
"""
import argparse
import re
import shutil
from pathlib import Path

FLOW = ("U", "phi", "nut", "alphat", "p", "p_rgh", "T", "rho", "k", "omega")


def tname(t: float) -> str:
    return f"{t:g}"


def make(out: Path, bg: Path, t_bg: float, src: Path, t_src: float, t_end: float, dt: float, write: float):
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    shutil.copytree(src / "constant", out / "constant")
    shutil.copytree(src / "system", out / "system")
    tdir = out / tname(t_src)
    tdir.mkdir()
    for f in FLOW:
        p = bg / tname(t_bg) / f
        if p.exists():
            shutil.copy(p, tdir / f)
    shutil.copy(src / tname(t_src) / "s", tdir / "s")
    cd = (src / "system/controlDict").read_text()
    funcs = re.findall(r"^\s*#includeFunc\s+(?:scalarTransport|probes)\(.*\)\s*$", cd, flags=re.M)
    if len(funcs) != 2:
        raise SystemExit(f"expected scalarTransport and probes in {src}/system/controlDict, found {funcs}")
    (out / "system/controlDict").write_text(f"""FoamFile
{{
    format ascii;
    class dictionary;
    object controlDict;
}}
solver          functions;
subSolver       fluid;
subSolverTime   {tname(t_src)};
startFrom       startTime;
startTime       {tname(t_src)};
stopAt          endTime;
endTime         {tname(t_end)};
deltaT          {dt:g};
writeControl    runTime;
writeInterval   {write:g};
purgeWrite      2;
writeFormat     binary;
writePrecision  8;
timeFormat      general;
timePrecision   8;
runTimeModifiable false;
functions
{{
{chr(10).join(funcs)}
}}
""")
    print("written", out, "frozen flow from", bg, tname(t_bg), "| s from", src, tname(t_src))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--bg", required=True)
    ap.add_argument("--t-bg", type=float, required=True)
    ap.add_argument("--src", required=True)
    ap.add_argument("--t-src", type=float, required=True)
    ap.add_argument("--t-end", type=float, default=600.0)
    ap.add_argument("--dt", type=float, default=0.02)
    ap.add_argument("--write", type=float, default=60.0)
    a = ap.parse_args()
    make(Path(a.out), Path(a.bg), a.t_bg, Path(a.src), a.t_src, a.t_end, a.dt, a.write)
