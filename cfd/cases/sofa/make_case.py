"""Scenario A, 'sofa duet': two seated adults on a sofa in a quiescent living room; one releases.

Transient RANS k-omega SST, Boussinesq ('fluid' solver), skin 33 C, walls 23 C (same set-up as the M3b CBL runs).
Release = momentum-equivalent mass source (fvModel massSource) in a small sphere behind the farter's buttocks just
above the seat, directed down-and-back into the seat/backrest corner:
  physical release  : V over T through an orifice d  ->  Q0 = V/T, u0 = Q0/(pi d^2/4), M0 = u0 Q0
  equivalent source : sphere of radius r_s, area A_s = pi r_s^2;
                      audible (u0 > sqrt(M0/A_s)): u_eq = sqrt(M0/A_s), Q_eq = M0/u_eq  (momentum and odorant flux
                      conserved, the source fluid is pre-diluted by Q0/Q_eq with room air)
                      silent: Q_eq = Q0, u_eq = Q0/A_s
  buoyancy          : the flatus density deficit (median g' = 1.70 m/s^2, Suarez 1997 compositions) is represented
                      by an equivalent temperature excess dT = g'/(g beta), diluted like the scalar.
  odorant           : passive scalar s (s = 1 for undiluted flatus), scalarTransport with Sc_t = 0.7.
Nose probes 2.5 cm in front of each nose tip.
Pressure relief: a 0.5 m x 0.5 m ceiling vent (p_rgh = 0, inflow at room temperature) in the far corner, cut from the
ceiling patch by createPatch after meshing. A sealed Boussinesq room cannot take a net mass source (incompatible
pressure equation; two tests diverged, also with no temperature excess and with max Co 0.5), and a real room leaks.

Usage: python3 make_case.py <case_dir> --mode {precursor,silent,audible} [--V 9.2e-5 --T 2.0 --d 0.008]
       [--t-release 30 --t-end 60]   (branch cases mapped from the precursor use --t-release 1 --t-end 31)
"""
import argparse
import math
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DOMAIN = ((-1.0, 2.2), (-1.6, 1.6), (0.0, 2.6))
DY_F, DY_N = -0.30, 0.30
NOSE_X, NOSE_Z = 0.10, 1.215
REL = (-0.195, DY_F, 0.478)            # release point: behind the buttocks, 2.8 cm above the seat
REL_DIR = (-0.5, 0.0, -0.866)          # down and back, into the seat/backrest corner
R_SRC = 0.0075
VENT_BOX = "(1.6 1.0 2.5) (2.1 1.5 2.7)"  # ceiling faces with centres in this box become the vent patch
T_ROOM, T_SKIN = 23.0, 33.0
G_PRIME = 1.70                         # params.yaml source.g_reduced (median)
T_PRE, T_REL = 30.0, 30.0              # precursor length; release time
T_END = 60.0
HEADER = "FoamFile\n{{\n    format ascii;\n    class {cls};\n    object {obj};\n}}\n"
WALLS = ("floor", "ceiling", "walls")
BODIES = ("farter", "neighbour")


def w(path: Path, body: str, cls="dictionary", obj=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HEADER.format(cls=cls, obj=obj or path.name) + body)


def equivalent_source(V, T, d):
    Q0 = V / T
    A0 = math.pi * d**2 / 4
    u0 = Q0 / A0
    M0 = u0 * Q0
    A_s = math.pi * R_SRC**2
    u_eq = math.sqrt(M0 / A_s)
    if u_eq < Q0 / A_s:  # source sphere larger than the jet would be: no pre-dilution
        u_eq, Q_eq = Q0 / A_s, Q0
    else:
        Q_eq = M0 / u_eq
    return {"Q0": Q0, "u0": u0, "M0": M0, "u_eq": u_eq, "Q_eq": Q_eq, "dilution": Q_eq / Q0}


def block_mesh(dx=0.08):
    (x0, x1), (y0, y1), (z0, z1) = DOMAIN
    n = [max(1, round((b - a) / dx)) for a, b in DOMAIN]
    return f"""convertToMeters 1;
vertices ( ({x0} {y0} {z0}) ({x1} {y0} {z0}) ({x1} {y1} {z0}) ({x0} {y1} {z0})
           ({x0} {y0} {z1}) ({x1} {y0} {z1}) ({x1} {y1} {z1}) ({x0} {y1} {z1}) );
blocks ( hex (0 1 2 3 4 5 6 7) ({n[0]} {n[1]} {n[2]}) simpleGrading (1 1 1) );
boundary
(
    floor    {{ type wall; faces ((0 3 2 1)); }}
    ceiling  {{ type wall; faces ((4 5 6 7)); }}
    walls    {{ type wall; faces ((0 4 7 3) (1 2 6 5) (3 7 6 2) (0 1 5 4)); }}
);
"""


def snappy():
    rx, ry, rz = REL
    return f"""castellatedMesh true;
snap            true;
addLayers       true;
geometry
{{
    farter    {{ type triSurface; file "farter.stl"; }}
    neighbour {{ type triSurface; file "neighbour.stl"; }}
    sofa      {{ type triSurface; file "sofa.stl"; }}
    people    {{ type box; min (-0.45 -0.95 0); max (0.80 0.95 1.45); }}
    plumes    {{ type box; min (-0.35 -0.75 1.0); max (0.40 0.75 2.4); }}
    faces     {{ type box; min (0.0 -0.50 1.05); max (0.35 0.50 1.40); }}
    release   {{ type box; min ({rx - 0.06} {ry - 0.08} 0.45); max ({rx + 0.05} {ry + 0.08} {rz + 0.08}); }}
}};
castellatedMeshControls
{{
    maxLocalCells 3000000;
    maxGlobalCells 8000000;
    minRefinementCells 10;
    maxLoadUnbalance 0.10;
    nCellsBetweenLevels 3;
    features ();
    refinementSurfaces
    {{
        farter    {{ level (3 3); patchInfo {{ type wall; }} }}
        neighbour {{ level (3 3); patchInfo {{ type wall; }} }}
        sofa      {{ level (2 2); patchInfo {{ type wall; }} }}
    }}
    resolveFeatureAngle 30;
    refinementRegions
    {{
        people  {{ mode inside; level 2; }}
        plumes  {{ mode inside; level 1; }}
        faces   {{ mode inside; level 3; }}
        release {{ mode inside; level 4; }}
    }}
    insidePoint (1.5 1.2 2.0);
    allowFreeStandingZoneFaces false;
}}
snapControls {{ nSmoothPatch 3; tolerance 2.0; nSolveIter 50; nRelaxIter 5; }}
addLayersControls
{{
    relativeSizes true;
    layers {{ "(farter|neighbour).*" {{ nSurfaceLayers 3; }} }}
    expansionRatio 1.2;
    finalLayerThickness 0.5;
    minThickness 0.1;
    nGrow 0;
    featureAngle 120;
    slipFeatureAngle 30;
    nRelaxIter 3;
    nSmoothSurfaceNormals 1;
    nSmoothNormals 3;
    nSmoothThickness 10;
    maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3;
    minMedianAxisAngle 90;
    nBufferCellsNoExtrude 0;
    nLayerIter 50;
}}
meshQualityControls {{ #includeEtc "caseDicts/mesh/generation/meshQualityDict.cfg" }}
mergeTolerance 1e-6;
"""


def fields(src):
    troom, tskin = T_ROOM + 273.15, T_SKIN + 273.15
    k0, om0 = 1e-5, 0.1

    def bc(wall, body, sofa, vent):
        return ("boundaryField\n{\n" + "".join(f"    {p} {{ {wall} }}\n" for p in WALLS)
                + "".join(f"    {b} {{ {body} }}\n" for b in BODIES) + f"    sofa {{ {sofa} }}\n"
                + f"    vent {{ {vent} }}\n}}\n")

    def sources(spec):
        return f"sources\n{{\n    massSource {{ {spec} }}\n}}\n" if src else ""

    ue = src["u_eq"] if src else 0.0
    ux, uy, uz = (ue * c for c in REL_DIR)
    beta = 1.0 / troom
    dT_eq = G_PRIME / (9.81 * beta) / src["dilution"] if src else 0.0
    s_in = 1.0 / src["dilution"] if src else 0.0
    return {
        "U": ("volVectorField", "dimensions [0 1 -1 0 0 0 0];\ninternalField uniform (0 0 0);\n"
              + bc("type noSlip;", "type noSlip;", "type noSlip;",
                   "type pressureInletOutletVelocity; value uniform (0 0 0);")
              + sources(f"type uniformInletOutlet; uniformInletValue ({ux:.5g} {uy:.5g} {uz:.5g});")),
        "T": ("volScalarField", f"dimensions [0 0 0 1 0 0 0];\ninternalField uniform {troom};\n"
              + bc(f"type fixedValue; value uniform {troom};", f"type fixedValue; value uniform {tskin};",
                   "type zeroGradient;", f"type inletOutlet; inletValue uniform {troom}; value uniform {troom};")
              + sources(f"type uniformInletOutlet; uniformInletValue {troom + dT_eq:.4f};")),
        "s": ("volScalarField", "dimensions [0 0 0 0 0 0 0];\ninternalField uniform 0;\n"
              + bc("type zeroGradient;", "type zeroGradient;", "type zeroGradient;",
                   "type inletOutlet; inletValue uniform 0; value uniform 0;")
              + sources(f"type uniformInletOutlet; uniformInletValue {s_in:.6g};")),
        "p_rgh": ("volScalarField", "dimensions [1 -1 -2 0 0 0 0];\ninternalField uniform 0;\n"
                  + bc(*["type fixedFluxPressure; value uniform 0;"] * 3, "type fixedValue; value uniform 0;")),
        "p": ("volScalarField", "dimensions [1 -1 -2 0 0 0 0];\ninternalField uniform 0;\n"
              + bc(*["type calculated; value uniform 0;"] * 4)),
        "k": ("volScalarField", f"dimensions [0 2 -2 0 0 0 0];\ninternalField uniform {k0};\n"
              + bc(*[f"type kqRWallFunction; value uniform {k0};"] * 3,
                   f"type inletOutlet; inletValue uniform {k0}; value uniform {k0};")
              + sources("type turbulentIntensityKineticEnergy; intensity 0.05;")),
        "omega": ("volScalarField", f"dimensions [0 0 -1 0 0 0 0];\ninternalField uniform {om0};\n"
                  + bc(*[f"type omegaWallFunction; value uniform {om0};"] * 3,
                       f"type inletOutlet; inletValue uniform {om0}; value uniform {om0};")
                  + sources(f"type turbulentMixingLengthFrequency; mixingLength {0.07 * 2 * R_SRC:.5g};")),
        "nut": ("volScalarField", "dimensions [0 2 -1 0 0 0 0];\ninternalField uniform 0;\n"
                + bc(*["type nutkWallFunction; value uniform 0;"] * 3, "type calculated; value uniform 0;")),
        "alphat": ("volScalarField", "dimensions [1 -1 -1 0 0 0 0];\ninternalField uniform 0;\n"
                   + bc(*["type compressible::alphatJayatillekeWallFunction; Prt 0.85; value uniform 0;"] * 3,
                     "type calculated; value uniform 0;")),
    }


def make(case: Path, mode: str, V: float, T: float, d: float, t_rel: float = T_REL, t_end: float = T_END):
    troom = T_ROOM + 273.15
    rho0 = 101325 * 0.02896 / (8.314 * troom)
    src = equivalent_source(V, T, d) if mode != "precursor" else None
    geo = case / "constant/geometry"
    geo.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ROOT / "cfd/geometry"))
    import manikin
    manikin.write_scene(geo, DY_F, DY_N)
    w(case / "system/blockMeshDict", block_mesh())
    w(case / "system/snappyHexMeshDict", snappy())
    w(case / "system/createPatchDict", f"""patches
{{
    vent
    {{
        patchInfo {{ type patch; }}
        constructFrom zone;
        zone {{ type box; zoneType face; box {VENT_BOX}; zone {{ type patch; patch ceiling; }} }}
    }}
}}
""")
    for name, (cls, body) in fields(src).items():
        w(case / "0" / name, body, cls)
    w(case / "constant/g", "dimensions [0 1 -2 0 0 0 0];\nvalue (0 0 -9.81);\n", "uniformDimensionedVectorField", "g")
    w(case / "constant/physicalProperties", f"""thermoType
{{
    type heRhoThermo; mixture pureMixture; transport const; thermo hConst;
    equationOfState Boussinesq; specie specie; energy sensibleEnthalpy;
}}
mixture
{{
    specie {{ molWeight 28.96; }}
    equationOfState {{ rho0 {rho0:.5f}; T0 {troom}; beta {1 / troom:.6e}; }}
    thermodynamics {{ Cp 1006; hf 0; }}
    transport {{ mu 1.81e-05; Pr 0.71; }}
}}
""")
    w(case / "constant/momentumTransport", "simulationType RAS;\nRAS\n{\n    model kOmegaSST;\n    turbulence on;\n}\n")
    if src:
        w(case / "constant/fvModels", f"""massSource
{{
    type            massSource;
    cellZone        {{ type sphere; zoneType cell; centre ({REL[0]} {REL[1]} {REL[2]}); radius {R_SRC}; }}
    massFlowRate
    {{
        type        scale;
        scale       squarePulse;
        start       {t_rel};
        duration    {T};
        value       {rho0 * src['Q_eq']:.6g};
    }}
}}
""")
    nose_f, nose_n = f"({NOSE_X} {DY_F} {NOSE_Z})", f"({NOSE_X} {DY_N} {NOSE_Z})"
    end = T_PRE if mode == "precursor" else t_end
    w(case / "system/controlDict", f"""solver fluid;
startFrom latestTime;
startTime 0;
stopAt endTime;
endTime {end};
deltaT 0.01;
adjustTimeStep yes;
maxCo 5;
maxDeltaT 0.1;
writeControl adjustableRunTime;
writeInterval 5;
purgeWrite 0;
writeFormat binary;
writePrecision 8;
writeCompression off;
timeFormat general;
runTimeModifiable true;
functions
{{
    #includeFunc scalarTransport(s, diffusivity=viscosity, alphal=1.428571, alphat=1.428571)
    #includeFunc probes(funcName=noses, points=({nose_f} {nose_n}), fields=(s T U))
    #includeFunc residuals(p_rgh, U, h, k, omega, s)
}}
""")
    w(case / "system/fvSchemes", """ddtSchemes { default Euler; }
gradSchemes { default Gauss linear; }
divSchemes
{
    default none;
    div(phi,U) Gauss linearUpwind grad(U);
    div(phi,h) Gauss upwind;
    div(phi,k) Gauss upwind;
    div(phi,omega) Gauss upwind;
    div(phi,K) Gauss linear;
    div(phi,s) Gauss limitedLinear01 1;
    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear limited corrected 0.5; }
interpolationSchemes { default linear; }
snGradSchemes { default limited corrected 0.5; }
wallDist { method meshWave; }
""")
    w(case / "system/fvSolution", """solvers
{
    "p_rgh.*" { solver GAMG; smoother DIC; tolerance 1e-7; relTol 0.01; }
    p_rghFinal { solver GAMG; smoother DIC; tolerance 1e-7; relTol 0; }
    "(U|h|k|omega|s).*" { solver PBiCGStab; preconditioner DILU; tolerance 1e-8; relTol 0; }
    "rho.*" { solver diagonal; }
}
PIMPLE
{
    momentumPredictor yes;
    nOuterCorrectors 2;
    nCorrectors 2;
    nNonOrthogonalCorrectors 1;
    pRefCell 0;
    pRefValue 0;
}
""")
    w(case / "system/decomposeParDict", "numberOfSubdomains 4;\nmethod scotch;\n")
    w(case / "system/meshQualityDict", "#includeEtc \"caseDicts/mesh/generation/meshQualityDict.cfg\"\n")
    return src


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("--mode", choices=("precursor", "silent", "audible"), required=True)
    ap.add_argument("--V", type=float, default=9.2e-5, help="released volume (m^3); median per passage")
    ap.add_argument("--T", type=float, default=None, help="release duration (s)")
    ap.add_argument("--d", type=float, default=None, help="effective orifice diameter (m)")
    ap.add_argument("--t-release", type=float, default=T_REL, help="release start time (s)")
    ap.add_argument("--t-end", type=float, default=T_END, help="end time (s)")
    a = ap.parse_args()
    # defaults: silent = 92 mL over 2 s through 8 mm (u0 0.9 m/s, below acoustic onset);
    #           audible = 92 mL over 0.5 s through 2.4 mm (u0 41 m/s, above onset ~30 m/s)
    T = a.T if a.T is not None else (2.0 if a.mode != "audible" else 0.5)
    d = a.d if a.d is not None else (0.008 if a.mode != "audible" else 0.0024)
    src = make(Path(a.case), a.mode, a.V, T, d, a.t_release, a.t_end)
    print("written", a.case, a.mode, {k: round(v, 5) for k, v in (src or {}).items()})
