"""PLAN v4 E0-3: near-body source to the breathing zone, against Licina, Tian & Nazaroff 2017 (Build Environ 123:14,
doi 10.1016/j.buildenv.2017.06.037; values below from the authors' manuscript, eScholarship qt4xc5n6hr).

Experiment (their section 2, Fig. 1, Tables 1-2): chamber 4.6 m x 4.6 m, ~50 m^3, 100 % outdoor air at 2.3 /h
(115 m^3/h) through two ceiling diffusers, exhaust through a wall opening at 1.8 m; 21 C set point. Non-breathing
seated thermal manikin (100 W sensible, long trousers and T-shirt) on a chair in the centre, back to the exhaust wall.
Particles from a nebulizer (3.5 L/min) leave a perforated cylinder (open upwards) proximate to the groin at 0.5 m
height, at a constant rate for 10 min. Breathing-zone monitor at 1.1 m height, within 0.15 m of the mouth. Intake
fraction iF = Qb * int C_bz dt / released mass, Qb = 0.5 m^3/h. Groin, per mille: source-active 10 min 5.5, to 22 min
7.7, full 100 min 9.8 (heated); 0.05 / 0.1 / 1.2 with the manikin off. Well mixed, non-depositing: 0.74 / 4.2.

Model (the scene set-up of cfd/cases/sofa/make_case.py, so the check covers the model as used):
  - the project's seated manikin and chair (cfd/geometry/manikin.py), bare skin at 33 C as in the scenes (heated) or
    at room temperature (unheated); walls, floor and ceiling at 21 C; transient RANS k-omega SST, Boussinesq.
  - room x in [-2.0, 2.6] (exhaust wall at x = -2.0, the manikin's back towards it, as in their Fig. 1), y in
    [-2.3, 2.3], height 2.36 m (50 m^3).
  - supply: two ceiling patches (supply0, supply1) 0.6 m (x) x 0.4 m (y) centred at x = -0.53, y = +-1.2 (scaled
    from Fig. 1), 57.5 m^3/h each, straight down at 21 C [ASSUMPTION: diffuser throw and supply temperature not reported; the authors found
    iF within 5 % when they moved the manikin, so the plume, not the supply jets, dominates near the body].
  - exhaust: 0.3 m x 0.3 m wall opening centred at y = 0, z = 1.8 m, fixed pressure [ASSUMPTION: size].
  - source: a vertical tube (radius 1.2 cm) between the thighs 2 cm in front of the torso, its top face at
    z = 0.50 m, blowing 3.5 L/min of room-temperature air upwards with s = 1 for 600 s (nebulizer flow only; the
    dilution branches of their Fig. S1 are not quantified) [ASSUMPTION].
  - gas, no deposition (the odorant case); their deposition lowers the well-mixed full-period iF from 4.2 to 3.2.
  - one case: the flow develops for T_PRE s (no scalar), the source runs from T_PRE + 0.2 s for 600 s, and the run
    ends 22 min after the source starts; analyze_licina.py adds the well-mixed decay to 100 min.

Usage: python3 make_case.py <case_dir> [--unheated] [--t-pre 600]
"""
import argparse
import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_spec = importlib.util.spec_from_file_location("sofa_case", ROOT / "cfd/cases/sofa/make_case.py")
sofa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sofa)
w, pulse_table = sofa.w, sofa.pulse_table

H = 50.0 / 4.6**2                       # 2.363 m: 50 m^3 over the 4.6 m x 4.6 m floor
DOMAIN = ((-2.0, 2.6), (-2.3, 2.3), (0.0, round(H, 3)))
T_ROOM, T_SKIN = 21.0, 33.0
Q_SUPPLY = 115.0 / 3600                 # m^3/s, 2.3 /h
SUPPLY = [(-0.53, s * 1.2) for s in (-1, 1)]
SUPPLY_HALF = (0.30, 0.20)              # half sizes in x and y
EXHAUST = (0.0, 1.8, 0.15)              # y, z, half size
SRC = (0.06, 0.0, 0.50)                 # top of the source tube
R_SRC, L_SRC = 0.012, 0.03
Q_SRC = 3.5e-3 / 60                     # m^3/s, nebulizer flow
T_REL = 600.0                           # s, constant release
T_RUN = 22 * 60.0                       # s after the source starts (end of their unmixed period)
QB = 0.5 / 3600                         # m^3/s, breathing rate for iF
BZ = (0.12, 0.0, 1.10)                  # breathing-zone monitor: 1.1 m height, ~9 cm from the mouth
NOSE = (0.10, 0.0, 1.215)               # as the scene nose probes (2.5 cm in front of the nose tip)
STATIONARY = [(2.13, -1.94, 0.2), (-1.61, -1.91, 1.1), (-1.65, 1.85, 1.7)]  # their monitors 1-3 (Fig. 1)
EXH_PROBE = (-1.95, 0.0, 1.8)
WALLS = ("floor", "ceiling", "walls")
SOLIDS = ("body", "chair", "tube")


def write_tube(path: Path, manikin):
    """Source tube along +z ending at SRC; two solids: 'tube' (wall) and 'release' (top face)."""
    p1 = np.array(SRC)
    p0 = p1 - np.array([0.0, 0.0, L_SRC])
    tris = manikin.cylinder(p0, p1, R_SRC, caps=True, n=32)
    n_cap = 31  # cylinder() appends the p0 cap, then the p1 cap, n - 1 triangles each
    with open(path, "w") as fh:
        for name, tt in (("tube", tris[:-n_cap]), ("release", tris[-n_cap:])):
            fh.write(f"solid {name}\n")
            for a, b, c in tt:
                nrm = np.cross(np.subtract(b, a), np.subtract(c, a))
                if np.linalg.norm(nrm) < 1e-12:
                    continue
                nrm = nrm / np.linalg.norm(nrm)
                fh.write(f" facet normal {nrm[0]:.6e} {nrm[1]:.6e} {nrm[2]:.6e}\n  outer loop\n")
                fh.writelines(f"   vertex {q[0]:.6e} {q[1]:.6e} {q[2]:.6e}\n" for q in (a, b, c))
                fh.write("  endloop\n endfacet\n")
            fh.write(f"endsolid {name}\n")


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
    """Refinement as in the sofa scene: body surface level 3, people/plume/face regions 2/1/3, the source at the
    levels of the scene's emitter (tube 4, release face 5)."""
    sx, sy, sz = SRC
    return f"""castellatedMesh true;
snap            true;
addLayers       true;
geometry
{{
    body   {{ type triSurface; file "body.stl"; }}
    chair  {{ type triSurface; file "chair.stl"; }}
    source {{ type triSurface; file "source.stl"; regions {{ tube {{ name tube; }} release {{ name release; }} }} }}
    people {{ type box; min (-0.45 -0.45 0); max (0.80 0.45 1.45); }}
    plumes {{ type box; min (-0.35 -0.45 1.0); max (0.40 0.45 2.36); }}
    faces  {{ type box; min (0.0 -0.20 1.05); max (0.35 0.20 1.40); }}
    near   {{ type box; min ({sx - 0.04} -0.05 {sz - 0.06}); max ({sx + 0.06} 0.05 {sz + 0.06}); }}
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
        body   {{ level (3 3); patchInfo {{ type wall; }} }}
        chair  {{ level (2 2); patchInfo {{ type wall; }} }}
        source
        {{
            level (4 4);
            regions
            {{
                tube    {{ level (4 4); patchInfo {{ type wall; }} }}
                release {{ level (5 5); patchInfo {{ type patch; }} }}
            }}
        }}
    }}
    resolveFeatureAngle 30;
    refinementRegions
    {{
        people {{ mode inside; level 2; }}
        plumes {{ mode inside; level 1; }}
        faces  {{ mode inside; level 3; }}
        near   {{ mode inside; level 4; }}
    }}
    insidePoint (1.5 1.2 2.0);
    allowFreeStandingZoneFaces false;
}}
snapControls {{ nSmoothPatch 3; tolerance 2.0; nSolveIter 50; nRelaxIter 5; }}
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
meshQualityControls {{ #includeEtc "caseDicts/mesh/generation/meshQualityDict.cfg" }}
mergeTolerance 1e-6;
"""


def create_patch():
    """Supply patches cut from the ceiling and the exhaust from the walls (faces with centres in a box), as the
    sofa's ceiling vent."""
    (x0, _), _, (_, z1) = DOMAIN
    hx, hy = SUPPLY_HALF
    ey, ez, eh = EXHAUST
    boxes = [(f"supply{k}", f"({x - hx} {y - hy} {z1 - 0.1}) ({x + hx} {y + hy} {z1 + 0.1})", "ceiling")
             for k, (x, y) in enumerate(SUPPLY)]
    boxes.append(("exhaust", f"({x0 - 0.1} {ey - eh} {ez - eh}) ({x0 + 0.1} {ey + eh} {ez + eh})", "walls"))
    return "patches\n{\n" + "".join(f"""    {name}
    {{
        patchInfo {{ type patch; }}
        constructFrom zone;
        zone {{ type box; zoneType face; box {box}; zone {{ type patch; patch {parent}; }} }}
    }}
""" for name, box, parent in boxes) + "}\n"


def fields(t_rel, heated):
    troom, tskin = T_ROOM + 273.15, (T_SKIN if heated else T_ROOM) + 273.15
    k0, om0 = 1e-5, 0.1
    k_in = 1.5 * (0.05 * 0.1) ** 2
    om_in = np.sqrt(k_in) / (0.09**0.25 * 0.07 * 0.3)

    def bc(wall, body, solid, supply, exhaust, release):
        return ("boundaryField\n{\n" + "".join(f"    {p} {{ {wall} }}\n" for p in WALLS)
                + f"    body {{ {body} }}\n    chair {{ {solid} }}\n    tube {{ {solid} }}\n"
                + "".join(f"    supply{k} {{ {supply} }}\n" for k in range(len(SUPPLY)))
                + f"    exhaust {{ {exhaust} }}\n    release {{ {release} }}\n}}\n")

    q_tab = pulse_table(t_rel, T_REL, Q_SRC, conserve=True)
    s_tab = pulse_table(t_rel, T_REL, 1.0)
    return {
        "U": ("volVectorField", "dimensions [0 1 -1 0 0 0 0];\ninternalField uniform (0 0 0);\n"
              + bc("type noSlip;", "type noSlip;", "type noSlip;",
                   f"type flowRateInletVelocity; volumetricFlowRate constant {Q_SUPPLY / len(SUPPLY):.6g}; value uniform (0 0 0);",
                   "type pressureInletOutletVelocity; value uniform (0 0 0);",
                   f"type flowRateInletVelocity; volumetricFlowRate {q_tab}; value uniform (0 0 0);")),
        "T": ("volScalarField", f"dimensions [0 0 0 1 0 0 0];\ninternalField uniform {troom};\n"
              + bc(f"type fixedValue; value uniform {troom};", f"type fixedValue; value uniform {tskin};",
                   "type zeroGradient;", f"type fixedValue; value uniform {troom};",
                   f"type inletOutlet; inletValue uniform {troom}; value uniform {troom};",
                   f"type fixedValue; value uniform {troom};")),
        "s": ("volScalarField", "dimensions [0 0 0 0 0 0 0];\ninternalField uniform 0;\n"
              + bc(*["type zeroGradient;"] * 3, "type fixedValue; value uniform 0;",
                   "type inletOutlet; inletValue uniform 0; value uniform 0;",
                   f"type uniformFixedValue; uniformValue {s_tab}; value uniform 0;")),
        "p_rgh": ("volScalarField", "dimensions [1 -1 -2 0 0 0 0];\ninternalField uniform 0;\n"
                  + bc(*["type fixedFluxPressure; value uniform 0;"] * 4, "type fixedValue; value uniform 0;",
                       "type fixedFluxPressure; value uniform 0;")),
        "p": ("volScalarField", "dimensions [1 -1 -2 0 0 0 0];\ninternalField uniform 0;\n"
              + bc(*["type calculated; value uniform 0;"] * 6)),
        "k": ("volScalarField", f"dimensions [0 2 -2 0 0 0 0];\ninternalField uniform {k0};\n"
              + bc(*[f"type kqRWallFunction; value uniform {k0};"] * 3, f"type fixedValue; value uniform {k_in:.6g};",
                   f"type inletOutlet; inletValue uniform {k0}; value uniform {k0};",
                   f"type fixedValue; value uniform {k_in:.6g};")),
        "omega": ("volScalarField", f"dimensions [0 0 -1 0 0 0 0];\ninternalField uniform {om0};\n"
                  + bc(*[f"type omegaWallFunction; value uniform {om0};"] * 3,
                       f"type fixedValue; value uniform {om_in:.6g};",
                       f"type inletOutlet; inletValue uniform {om0}; value uniform {om0};",
                       f"type fixedValue; value uniform {om_in:.6g};")),
        "nut": ("volScalarField", "dimensions [0 2 -1 0 0 0 0];\ninternalField uniform 0;\n"
                + bc(*["type nutkWallFunction; value uniform 0;"] * 3, *["type calculated; value uniform 0;"] * 3)),
        "alphat": ("volScalarField", "dimensions [1 -1 -1 0 0 0 0];\ninternalField uniform 0;\n"
                   + bc(*["type compressible::alphatJayatillekeWallFunction; Prt 0.85; value uniform 0;"] * 3,
                        *["type calculated; value uniform 0;"] * 3)),
    }


def make(case: Path, heated: bool = True, t_pre: float = 600.0):
    troom = T_ROOM + 273.15
    rho0 = 101325 * 0.02896 / (8.314 * troom)
    t_rel = t_pre + 0.2
    t_end = t_rel + T_RUN
    geo = case / "constant/geometry"
    geo.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ROOT / "cfd/geometry"))
    import manikin
    manikin.write_stl(geo / "body.stl", "body", manikin.body())
    manikin.write_stl(geo / "chair.stl", "chair", manikin.chair())
    write_tube(geo / "source.stl", manikin)
    w(case / "system/blockMeshDict", block_mesh())
    w(case / "system/snappyHexMeshDict", snappy())
    w(case / "system/createPatchDict", create_patch())
    for name, (cls, body) in fields(t_rel, heated).items():
        w(case / "0" / name, body, cls)
    w(case / "constant/g", "dimensions [0 1 -2 0 0 0 0];\nvalue (0 0 -9.81);\n", "uniformDimensionedVectorField", "g")
    w(case / "constant/physicalProperties", f"""thermoType
{{
    type heRhoThermo; mixture pureMixture; transport const; thermo hConst;
    equationOfState Boussinesq; specie specie; energy sensibleInternalEnergy;
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
    pts = " ".join(f"({x} {y} {z})" for x, y, z in [BZ, NOSE, EXH_PROBE] + STATIONARY)
    (case / "probes.txt").write_text("bz nose exhaust stationary1 stationary2 stationary3\n")
    (case / "release.txt").write_text(f"t_release {t_rel}\nT_release {T_REL}\nQ_src {Q_SRC}\nt_end {t_end}\n"
                                      f"heated {int(heated)}\n")
    # maxDeltaT 0.2 s: the source face (2.5 mm cells, 0.13 m/s) keeps Co <= 5 at about 0.1 s anyway
    w(case / "system/controlDict", f"""solver fluid;
startFrom latestTime;
startTime 0;
stopAt endTime;
endTime {t_end:.6g};
deltaT 0.01;
adjustTimeStep yes;
maxCo 5;
maxDeltaT 0.2;
writeControl adjustableRunTime;
writeInterval 60;
purgeWrite 3;
writeFormat binary;
writePrecision 8;
writeCompression off;
timeFormat general;
runTimeModifiable true;
functions
{{
    #includeFunc scalarTransport(s, diffusivity=viscosity, alphal=1.428571, alphat=1.428571)
    #includeFunc probes(funcName=monitors, points=({pts}), fields=(s T U))
    #includeFunc residuals(p_rgh, U, e, k, omega, s)
    roomMean
    {{
        type            volFieldValue;
        libs            ("libfieldFunctionObjects.so");
        writeControl    timeStep;
        writeInterval   1;
        writeFields     false;
        cellZone        all;
        operation       volAverage;
        fields          (s T);
    }}
    exhaustFlux
    {{
        type            surfaceFieldValue;
        libs            ("libfieldFunctionObjects.so");
        writeControl    timeStep;
        writeInterval   1;
        writeFields     false;
        patch           exhaust;
        operation       sum;
        fields          (phi);
    }}
    bodyHeat
    {{
        type            wallHeatFlux;
        libs            ("libfluidThermoMomentumTransportModels.so");
        writeControl    adjustableRunTime;
        writeInterval   60;
        patches         (body);
    }}
    planes
    {{
        type            surfaces;
        libs            ("libsampling.so");
        writeControl    adjustableRunTime;
        writeInterval   10;
        surfaceFormat   raw;
        interpolationScheme cell;
        interpolate     false;
        fields          (s T U);
        surfaces
        {{
            mid  {{ type cutPlane; planeType pointAndNormal; point (0 0 0); normal (0 1 0); interpolate false; }}
            bz   {{ type cutPlane; planeType pointAndNormal; point (0 0 {BZ[2]}); normal (0 0 1); interpolate false; }}
        }}
    }}
}}
""")
    # schemes and solvers as the sofa scene
    w(case / "system/fvSchemes", """ddtSchemes { default Euler; }
gradSchemes { default Gauss linear; }
divSchemes
{
    default none;
    div(phi,U) Gauss linearUpwind grad(U);
    div(phi,e) Gauss upwind;
    div(phi,(p|rho)) Gauss linear;
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
    "(U|e|k|omega|s).*" { solver PBiCGStab; preconditioner DILU; tolerance 1e-8; relTol 0; }
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
    return t_rel, t_end


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("--unheated", action="store_true", help="manikin off: skin at room temperature")
    ap.add_argument("--t-pre", type=float, default=600.0, help="flow development before the source starts (s)")
    a = ap.parse_args()
    t_rel, t_end = make(Path(a.case), not a.unheated, a.t_pre)
    print("written", a.case, "heated" if not a.unheated else "unheated", f"source {t_rel:g}-{t_rel + T_REL:g} s,",
          f"end {t_end:g} s")
