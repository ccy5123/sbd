"""Generate an OpenFOAM-13 case for the free round-jet validation (M3a).

Axisymmetric 5-degree wedge, steady RANS (incompressibleFluid), passive scalar s (scalarTransport function, Sc_t = 0.7).
Nozzle d = 10 mm, U0 = 10 m/s (Re = 6.7e3), domain 100 d x 40 d, no-slip base wall, open (entraining) side boundary, outflow-only outlet.

Usage: python3 make_case.py <case_dir> --level {coarse,medium,fine} --model {kOmegaSST,kEpsilon,realizableKE}
"""
import argparse
import math
from pathlib import Path

D, U0, NU = 0.01, 10.0, 1.5e-5
# Base (x = 0, r > d/2) is a no-slip wall (jet issuing from a wall); the side boundary supplies entrained air
# (total pressure 0); the outlet is outflow-only (an open total-pressure outlet admitted a spurious reverse flow).
# A co-flow was tried first and rejected: over the 40 d domain its momentum flux rivals the jet's.
L, R = 100 * D, 40 * D
HALF = math.radians(2.5)
LEVELS = {"coarse": (150, 5, 45), "medium": (300, 10, 90), "fine": (600, 20, 180)}  # Nx, Nr(core), Nr(outer)

HEADER = """FoamFile
{{
    format      ascii;
    class       {cls};
    object      {obj};
}}
"""


def w(path: Path, cls: str, obj: str, body: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HEADER.format(cls=cls, obj=obj) + body)


def vertices():
    pts = []
    for x in (0.0, L):
        pts.append((x, 0.0, 0.0))
    for r in (D / 2, R):
        for x in (0.0, L):
            for sgn in (-1, 1):
                pts.append((x, r * math.cos(HALF), sgn * r * math.sin(HALF)))
    return pts
# index map: axis: 0 (x=0), 1 (x=L)
# r=D/2: x=0 -> 2(-z), 3(+z); x=L -> 4(-z), 5(+z)
# r=R  : x=0 -> 6(-z), 7(+z); x=L -> 8(-z), 9(+z)


def block_mesh(level):
    nx, nr1, nr2 = LEVELS[level]
    v = "\n".join(f"    ({x:.9g} {y:.9g} {z:.9g})" for x, y, z in vertices())
    return f"""convertToMeters 1;
vertices
(
{v}
);
blocks
(
    hex (0 1 4 2 0 1 5 3) ({nx} {nr1} 1) simpleGrading (8 1 1)
    hex (2 4 8 6 3 5 9 7) ({nx} {nr2} 1) simpleGrading (8 30 1)
);
boundary
(
    inlet   {{ type patch; faces ((0 2 3 0)); }}
    base    {{ type wall; faces ((2 6 7 3)); }}
    side    {{ type patch; faces ((6 8 9 7)); }}
    outlet  {{ type patch; faces ((1 1 5 4) (4 5 9 8)); }}
    front   {{ type wedge; faces ((0 1 4 2) (2 4 8 6)); }}
    back    {{ type wedge; faces ((0 3 5 1) (3 7 9 5)); }}
    axis    {{ type empty; faces ((0 1 1 0)); }}
);
"""


def field(name, cls, dims, internal, bcs):
    body = f"dimensions {dims};\ninternalField uniform {internal};\nboundaryField\n{{\n"
    for patch, spec in bcs.items():
        body += f"    {patch} {{ {spec} }}\n"
    body += '    "(front|back)" { type wedge; }\n    axis { type empty; }\n}\n'
    return body


def make(case: Path, level: str, model: str, c1: float | None = None):
    k_in = 1.5 * (0.05 * U0) ** 2
    l_in = 0.07 * D
    om_in = math.sqrt(k_in) / (0.09 ** 0.25 * l_in)
    eps_in = 0.09 ** 0.75 * k_in ** 1.5 / l_in
    k_amb, om_amb = 1e-6, 1.0
    eps_amb = 0.09 * k_amb * om_amb
    openU = "type pressureInletOutletVelocity; value uniform (0 0 0);"
    w(case / "system/blockMeshDict", "dictionary", "blockMeshDict", block_mesh(level))
    w(case / "0/U", "volVectorField", "U", field("U", "volVectorField", "[0 1 -1 0 0 0 0]", "(0 0 0)", {
        "inlet": f"type fixedValue; value uniform ({U0} 0 0);", "base": "type noSlip;",
        "side": openU, "outlet": "type inletOutlet; inletValue uniform (0 0 0); value uniform (0 0 0);"}))
    w(case / "0/p", "volScalarField", "p", field("p", "volScalarField", "[0 2 -2 0 0 0 0]", 0, {
        "inlet": "type zeroGradient;", "base": "type zeroGradient;",
        "side": "type totalPressure; p0 uniform 0;", "outlet": "type fixedValue; value uniform 0;"}))
    w(case / "0/s", "volScalarField", "s", field("s", "volScalarField", "[0 0 0 0 0 0 0]", 0, {
        "inlet": "type fixedValue; value uniform 1;", "base": "type zeroGradient;",
        **{p: "type inletOutlet; inletValue uniform 0; value uniform 0;" for p in ("side", "outlet")}}))
    turb = {"k": ("[0 2 -2 0 0 0 0]", k_in, k_amb), "omega": ("[0 0 -1 0 0 0 0]", om_in, om_amb),
            "epsilon": ("[0 2 -3 0 0 0 0]", eps_in, eps_amb)}
    for name, (dims, vin, vamb) in turb.items():
        w(case / f"0/{name}", "volScalarField", name, field(name, "volScalarField", dims, vamb, {
            "inlet": f"type fixedValue; value uniform {vin:.6g};",
            "base": {"k": "type kqRWallFunction;", "omega": "type omegaWallFunction;",
                     "epsilon": "type epsilonWallFunction;"}[name] + f" value uniform {vamb:.6g};",
            **{p: f"type inletOutlet; inletValue uniform {vamb:.6g}; value uniform {vamb:.6g};"
               for p in ("side", "outlet")}}))
    w(case / "0/nut", "volScalarField", "nut", field("nut", "volScalarField", "[0 2 -1 0 0 0 0]", 0, {
        **{p: "type calculated; value uniform 0;" for p in ("inlet", "side", "outlet")},
        "base": "type nutkWallFunction; value uniform 0;"}))
    w(case / "constant/physicalProperties", "dictionary", "physicalProperties",
      f"viscosityModel constant;\nnu {NU};\n")
    w(case / "constant/momentumTransport", "dictionary", "momentumTransport",
      f"simulationType RAS;\nRAS\n{{\n    model {model};\n    turbulence on;\n    viscosityModel Newtonian;\n"
      + (f"    {model}Coeffs {{ Cmu 0.09; C1 {c1}; C2 1.92; C3 0; sigmak 1.0; sigmaEps 1.3; }}\n" if c1 else "")
      + "}\n")
    w(case / "system/controlDict", "dictionary", "controlDict", """solver incompressibleFluid;
startFrom latestTime;
startTime 0;
stopAt endTime;
endTime 6000;
deltaT 1;
writeControl timeStep;
writeInterval 6000;
purgeWrite 1;
writeFormat ascii;
writePrecision 8;
writeCompression off;
timeFormat general;
runTimeModifiable true;
functions
{
    #includeFunc scalarTransport(s, diffusivity=viscosity, alphal=1.428571, alphat=1.428571)
    #includeFunc residuals(p, U, k, omega, epsilon, s)
}
""")
    w(case / "system/fvSchemes", "dictionary", "fvSchemes", """ddtSchemes { default steadyState; }
gradSchemes { default Gauss linear; }
divSchemes
{
    default none;
    div(phi,U) bounded Gauss linearUpwind grad(U);
    div(phi,k) bounded Gauss limitedLinear 1;
    div(phi,omega) bounded Gauss limitedLinear 1;
    div(phi,epsilon) bounded Gauss limitedLinear 1;
    div(phi,s) bounded Gauss limitedLinear01 1;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes { default corrected; }
wallDist { method meshWave; }
""")
    w(case / "system/fvSolution", "dictionary", "fvSolution", """solvers
{
    p { solver GAMG; tolerance 1e-7; relTol 0.05; smoother GaussSeidel; }
    "(U|k|omega|epsilon|s)" { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-8; relTol 0.05; }
}
SIMPLE
{
    nNonOrthogonalCorrectors 0;
    consistent yes;
    residualControl { p 1e-5; U 1e-6; "(k|omega|epsilon)" 1e-6; }
}
relaxationFactors { equations { U 0.7; ".*" 0.7; } }
""")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("--level", default="medium", choices=LEVELS)
    ap.add_argument("--model", default="kOmegaSST")
    ap.add_argument("--c1", type=float, default=None, help="k-epsilon C1 (round-jet correction, e.g. 1.6)")
    a = ap.parse_args()
    make(Path(a.case), a.level, a.model, a.c1)
    print("written", a.case, a.level, a.model)
