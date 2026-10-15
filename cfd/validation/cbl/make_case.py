"""Generate an OpenFOAM-13 case for the human convective-boundary-layer validation (M3b).

Simplified seated manikin (cfd/geometry/manikin.py) in a quiescent room, half model (symmetry plane y = 0).
Steady RANS k-omega SST, Boussinesq buoyancy (solver 'fluid'), skin at T_skin, walls/floor/ceiling at T_room.
Target: peak upward CBL velocity in front of the face (Licina et al. 2014: 0.24 m/s at 20 C -> 0.16 m/s at 26 C).

Usage: python3 make_case.py <case_dir> --troom 23 [--tskin 33] [--level medium]
"""
import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOMAIN = ((-0.7, 1.3), (0.0, 1.0), (0.0, 2.5))
LEVELS = {"coarse": (0.06, 2, 3), "medium": (0.05, 3, 3), "fine": (0.04, 3, 4)}  # background dx, region lvl, surf lvl

HEADER = "FoamFile\n{{\n    format ascii;\n    class {cls};\n    object {obj};\n}}\n"
WALLS = ("floor", "ceiling", "walls")


def w(path: Path, body: str, cls="dictionary", obj=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HEADER.format(cls=cls, obj=obj or path.name) + body)


def block_mesh(dx):
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
    walls    {{ type wall; faces ((0 4 7 3) (1 2 6 5) (3 7 6 2)); }}
    symmetry {{ type symmetryPlane; faces ((0 1 5 4)); }}
);
"""


def snappy(region_lvl, surf_lvl):
    return f"""castellatedMesh true;
snap            true;
addLayers       true;
geometry
{{
    body  {{ type triSurface; file "body.stl"; }}
    chair {{ type triSurface; file "chair.stl"; }}
    person {{ type box; min (-0.35 0 0); max (0.75 0.40 1.45); }}
    plume  {{ type box; min (-0.30 0 1.0); max (0.35 0.30 2.2); }}
    face   {{ type box; min (0.0 0 1.05); max (0.40 0.15 1.40); }}
}};
castellatedMeshControls
{{
    maxLocalCells 2000000;
    maxGlobalCells 6000000;
    minRefinementCells 10;
    maxLoadUnbalance 0.10;
    nCellsBetweenLevels 3;
    features ();
    refinementSurfaces
    {{
        body  {{ level ({surf_lvl} {surf_lvl}); patchInfo {{ type wall; }} }}
        chair {{ level (2 2); patchInfo {{ type wall; }} }}
    }}
    resolveFeatureAngle 30;
    refinementRegions
    {{
        person {{ mode inside; level {region_lvl}; }}
        plume  {{ mode inside; level {max(region_lvl - 1, 1)}; }}
        face   {{ mode inside; level {surf_lvl}; }}
    }}
    insidePoint (1.0 0.8 2.0);
    allowFreeStandingZoneFaces false;
}}
snapControls
{{
    nSmoothPatch 3;
    tolerance 2.0;
    nSolveIter 50;
    nRelaxIter 5;
}}
addLayersControls
{{
    relativeSizes true;
    layers {{ "body.*" {{ nSurfaceLayers 3; }} }}
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
meshQualityControls
{{
    #includeEtc "caseDicts/mesh/generation/meshQualityDict.cfg"
}}
mergeTolerance 1e-6;
"""


def fields(troom_k, tskin_k):
    k0, om0 = 1e-5, 0.1
    bc = lambda wall, body, chair, sym="type symmetryPlane;": (  # noqa: E731
        "boundaryField\n{\n" + "".join(f"    {p} {{ {wall} }}\n" for p in WALLS)
        + f"    body {{ {body} }}\n    chair {{ {chair} }}\n    symmetry {{ {sym} }}\n}}\n")
    out = {
        "U": ("volVectorField", "dimensions [0 1 -1 0 0 0 0];\ninternalField uniform (0 0 0);\n"
              + bc("type noSlip;", "type noSlip;", "type noSlip;")),
        "T": ("volScalarField", f"dimensions [0 0 0 1 0 0 0];\ninternalField uniform {troom_k};\n"
              + bc(f"type fixedValue; value uniform {troom_k};", f"type fixedValue; value uniform {tskin_k};",
                   "type zeroGradient;")),
        "p_rgh": ("volScalarField", "dimensions [1 -1 -2 0 0 0 0];\ninternalField uniform 0;\n"
                  + bc(*["type fixedFluxPressure; value uniform 0;"] * 3)),
        "p": ("volScalarField", "dimensions [1 -1 -2 0 0 0 0];\ninternalField uniform 0;\n"
              + bc(*["type calculated; value uniform 0;"] * 3)),
        "k": ("volScalarField", f"dimensions [0 2 -2 0 0 0 0];\ninternalField uniform {k0};\n"
              + bc(*[f"type kqRWallFunction; value uniform {k0};"] * 3)),
        "omega": ("volScalarField", f"dimensions [0 0 -1 0 0 0 0];\ninternalField uniform {om0};\n"
                  + bc(*[f"type omegaWallFunction; value uniform {om0};"] * 3)),
        "nut": ("volScalarField", "dimensions [0 2 -1 0 0 0 0];\ninternalField uniform 0;\n"
                + bc(*["type nutkWallFunction; value uniform 0;"] * 3)),
        "alphat": ("volScalarField", "dimensions [1 -1 -1 0 0 0 0];\ninternalField uniform 0;\n"
                   + bc(*["type compressible::alphatJayatillekeWallFunction; Prt 0.85; value uniform 0;"] * 3)),
    }
    return out


def make(case: Path, troom_c: float, tskin_c: float, level: str):
    troom, tskin = troom_c + 273.15, tskin_c + 273.15
    dx, rl, sl = LEVELS[level]
    geo = case / "constant/geometry"
    geo.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(HERE.parents[1] / "geometry/manikin.py"), str(geo)], check=True,
                   capture_output=True)
    w(case / "system/blockMeshDict", block_mesh(dx))
    w(case / "system/snappyHexMeshDict", snappy(rl, sl))
    for name, (cls, body) in fields(troom, tskin).items():
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
    equationOfState {{ rho0 {101325 * 0.02896 / (8.314 * troom):.5f}; T0 {troom}; beta {1 / troom:.6e}; }}
    thermodynamics {{ Cp 1006; hf 0; }}
    transport {{ mu 1.81e-05; Pr 0.71; }}
}}
""")
    w(case / "constant/momentumTransport", "simulationType RAS;\nRAS\n{\n    model kOmegaSST;\n    turbulence on;\n}\n")
    w(case / "system/controlDict", f"""solver fluid;
startFrom latestTime;
startTime 0;
stopAt endTime;
endTime 3000;
deltaT 1;
writeControl timeStep;
writeInterval 1000;
purgeWrite 1;
writeFormat binary;
writePrecision 8;
writeCompression off;
timeFormat general;
runTimeModifiable true;
functions
{{
    #includeFunc residuals(p_rgh, U, h, k, omega)
    #includeFunc graphUniform(funcName=faceLine, start=(0.06 0.001 1.215), end=(0.40 0.001 1.215), nPoints=200, fields=(U T), axis=x)
    #includeFunc graphUniform(funcName=noseColumn, start=(0.12 0.001 0.50), end=(0.12 0.001 1.60), nPoints=220, fields=(U T), axis=z)
    #includeFunc graphUniform(funcName=headTop, start=(-0.03 0.001 1.37), end=(-0.03 0.001 2.30), nPoints=200, fields=(U T), axis=z)
}}
""")
    w(case / "system/fvSchemes", """ddtSchemes { default steadyState; }
gradSchemes { default Gauss linear; }
divSchemes
{
    default none;
    div(phi,U) bounded Gauss linearUpwind grad(U);
    div(phi,h) bounded Gauss upwind;
    div(phi,k) bounded Gauss upwind;
    div(phi,omega) bounded Gauss upwind;
    div(phi,K) bounded Gauss linear;
    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear limited corrected 0.5; }
interpolationSchemes { default linear; }
snGradSchemes { default limited corrected 0.5; }
wallDist { method meshWave; }
""")
    w(case / "system/fvSolution", """solvers
{
    p_rgh { solver GAMG; smoother DIC; tolerance 1e-7; relTol 0.01; }
    "(U|h|k|omega)" { solver PBiCGStab; preconditioner DILU; tolerance 1e-7; relTol 0.1; }
}
PIMPLE
{
    momentumPredictor yes;
    nNonOrthogonalCorrectors 1;
    pRefCell 0;
    pRefValue 0;
}
relaxationFactors
{
    fields { p_rgh 0.7; }
    equations { U 0.3; h 0.5; "(k|omega)" 0.5; }
}
""")
    w(case / "system/decomposeParDict", "numberOfSubdomains 4;\nmethod scotch;\n")
    w(case / "system/meshQualityDict", "#includeEtc \"caseDicts/mesh/generation/meshQualityDict.cfg\"\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("--troom", type=float, default=23.0)
    ap.add_argument("--tskin", type=float, default=33.0)
    ap.add_argument("--level", default="medium", choices=LEVELS)
    a = ap.parse_args()
    make(Path(a.case), a.troom, a.tskin, a.level)
    print("written", a.case)
