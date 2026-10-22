"""Scenario C, 'elevator whodunit': four standing adults in a closed 630 kg elevator car, fan off; one releases.

Same physics and release model as the sofa duet (cfd/cases/sofa/make_case.py): transient RANS k-omega SST,
Boussinesq, skin 33 C, car walls 23 C; momentum-equivalent release inlet with the flatus density deficit carried as an
equivalent temperature excess; odorant = passive scalar s (s = 1 undiluted flatus), Sc_t = 0.7.
Geometry (cfd/geometry/manikin.py): car 1.10 m wide x 1.40 m deep x 2.10 m high; occupants FL, FR (front, next to the
door), BL, BR (back), all facing the door at x = 1.40 m. The car is mirror-symmetric about y = 0, so a culprit on the
left stands for both sides: two culprit positions (FL, BL) x two modes (silent, audible) cover all four occupants.
Both emitter stubs (behind FL and BL) are meshed in every case so that all branches share the precursor mesh; the
inactive one is a closed wall.
Pressure relief: a 0.20 m x 0.20 m opening at the ceiling centre [ASSUMPTION: stands for the car's ventilation
apertures; its size and position are not taken from a standard], p_rgh = 0, inflow at car temperature.

PLAN v4 supplement: --mode multi carries the sofa case's four representative releases (MULTI_RELEASES, 30 s apart,
scalars s1..s4, iso-surfaces for the viewer) and writes the segment 'schedule' that run_multi.sh steps through.

Usage: python3 make_case.py <case_dir> --mode {precursor,silent,audible,multi} [--culprit {FL,BL}]
       [--t-pre 30] [--t-release 0.2 --t-end 60] [--V 9.2e-5 --T .. --d ..]
"""
import argparse
import importlib.util
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "cfd/geometry"))
import manikin

_spec = importlib.util.spec_from_file_location("sofa_case", ROOT / "cfd/cases/sofa/make_case.py")
sofa_case = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sofa_case)  # shared release model of the sofa duet
L_E, R_E, REL_DIR = sofa_case.L_E, sofa_case.R_E, sofa_case.REL_DIR
equivalent_source, pulse_table, w = sofa_case.equivalent_source, sofa_case.pulse_table, sofa_case.w

CAR = manikin.CAR
NAMES = tuple(manikin.OCCUPANTS)
CULPRITS = ("FL", "BL")
T_ROOM, T_SKIN = 23.0, 33.0
G_PRIME = 1.70
T_PRE = 30.0
VENT_BOX = "(0.60 -0.10 2.05) (0.80 0.10 2.15)"
PROBE_DX = 0.025  # probe 2.5 cm in front of the nose tip


def rel_point(name):
    x, y = manikin.OCCUPANTS[name]
    return manikin.STAND_REL + np.array([x, y, 0.0])


def nose_probe(name):
    x, y = manikin.OCCUPANTS[name]
    n = manikin.STAND_NOSE
    return (x + n[0] + PROBE_DX, y, n[2])


def write_emitters(path: Path):
    """Nozzle stubs behind FL and BL along REL_DIR; solids nozzle_<C> (wall) and release_<C> (end face)."""
    d = np.array(REL_DIR) / np.linalg.norm(REL_DIR)
    n_cap = 31
    with open(path, "w") as fh:
        for c in CULPRITS:
            p1 = rel_point(c)
            tube = manikin.cylinder(p1 - L_E * d, p1, R_E, caps=True, n=32)
            for name, tt in ((f"nozzle_{c}", tube[:-n_cap]), (f"release_{c}", tube[-n_cap:])):
                fh.write(f"solid {name}\n")
                for a, b, cc in tt:
                    nrm = np.cross(np.subtract(b, a), np.subtract(cc, a))
                    if np.linalg.norm(nrm) < 1e-12:
                        continue
                    nrm = nrm / np.linalg.norm(nrm)
                    fh.write(f" facet normal {nrm[0]:.6e} {nrm[1]:.6e} {nrm[2]:.6e}\n  outer loop\n")
                    fh.writelines(f"   vertex {q[0]:.6e} {q[1]:.6e} {q[2]:.6e}\n" for q in (a, b, cc))
                    fh.write("  endloop\n endfacet\n")
                fh.write(f"endsolid {name}\n")


def block_mesh(dx=0.07):
    X, Y, Z = CAR
    n = [max(1, round(L / dx)) for L in (X, Y, Z)]
    y0, y1 = -Y / 2, Y / 2
    return f"""convertToMeters 1;
vertices ( (0 {y0} 0) ({X} {y0} 0) ({X} {y1} 0) (0 {y1} 0)
           (0 {y0} {Z}) ({X} {y0} {Z}) ({X} {y1} {Z}) (0 {y1} {Z}) );
blocks ( hex (0 1 2 3 4 5 6 7) ({n[0]} {n[1]} {n[2]}) simpleGrading (1 1 1) );
boundary
(
    floor    {{ type wall; faces ((0 3 2 1)); }}
    ceiling  {{ type wall; faces ((4 5 6 7)); }}
    walls    {{ type wall; faces ((0 4 7 3) (1 2 6 5) (3 7 6 2) (0 1 5 4)); }}
);
"""


def snappy():
    geo = "".join(f'    {n} {{ type triSurface; file "{n}.stl"; }}\n' for n in NAMES)
    regions = " ".join(f"nozzle_{c} {{ name nozzle_{c}; }} release_{c} {{ name release_{c}; }}" for c in CULPRITS)
    geo += f'    emitter {{ type triSurface; file "emitter.stl"; regions {{ {regions} }} }}\n'
    boxes = ""
    for n in NAMES:
        x, y, z = nose_probe(n)
        boxes += f"    face_{n} {{ type box; min ({x - 0.08:.3f} {y - 0.12:.3f} 1.47); max ({x + 0.20:.3f} {y + 0.12:.3f} 1.72); }}\n"
    for c in CULPRITS:
        rx, ry, rz = rel_point(c)
        boxes += f"    rel_{c} {{ type box; min ({rx - 0.06:.3f} {ry - 0.08:.3f} {rz - 0.10:.3f}); max ({rx + 0.05:.3f} {ry + 0.08:.3f} {rz + 0.06:.3f}); }}\n"
    surf = "".join(f"        {n} {{ level (3 3); patchInfo {{ type wall; }} }}\n" for n in NAMES)
    surf += ("        emitter\n        {\n            level (4 4);\n            regions\n            {\n"
             + "".join(f"                nozzle_{c} {{ level (4 4); patchInfo {{ type wall; }} }}\n"
                       f"                release_{c} {{ level (5 5); patchInfo {{ type patch; }} }}\n" for c in CULPRITS)
             + "            }\n        }\n")
    reg = "".join(f"        face_{n} {{ mode inside; level 3; }}\n" for n in NAMES)
    reg += "".join(f"        rel_{c} {{ mode inside; level 4; }}\n" for c in CULPRITS)
    return f"""castellatedMesh true;
snap            true;
addLayers       true;
geometry
{{
{geo}    people {{ type box; min (0.0 -0.55 0.0); max (1.40 0.55 1.80); }}
{boxes}}};
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
{surf}    }}
    resolveFeatureAngle 30;
    refinementRegions
    {{
        people {{ mode inside; level 1; }}
{reg}    }}
    insidePoint (1.30 0.0 2.0);
    allowFreeStandingZoneFaces false;
}}
snapControls {{ nSmoothPatch 3; tolerance 2.0; nSolveIter 50; nRelaxIter 5; }}
addLayersControls
{{
    relativeSizes true;
    layers {{ "(FL|FR|BL|BR).*" {{ nSurfaceLayers 3; }} }}
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


def fields(src, culprit, t_rel, T, multi=None):
    troom, tskin = T_ROOM + 273.15, T_SKIN + 273.15
    k0, om0 = 1e-5, 0.1
    beta = 1.0 / troom
    if multi:  # [(src, t_rel, T), ...]: one inlet carrying all pulses, one scalar per release (as the sofa case)
        mpt = sofa_case.multi_pulse_table
        q_tab = mpt([(tr, Tk, sk["Q_eq"], True) for sk, tr, Tk in multi])
        t_tab = mpt([(tr, Tk, G_PRIME / (9.81 * beta) / sk["dilution"], False) for sk, tr, Tk in multi], troom)
        s_tab = "constant 0"
        k_in = 1.5 * (0.05 * max(sk["u_eq"] for sk, _, _ in multi)) ** 2
        om_in = math.sqrt(k_in) / (0.09**0.25 * 0.07 * 2 * R_E)
        src = multi[0][0]  # marks the culprit's release face as an inlet below
    elif src:
        dT_eq = G_PRIME / (9.81 * beta) / src["dilution"]
        q_tab = pulse_table(t_rel, T, src["Q_eq"], conserve=True)
        t_tab = pulse_table(t_rel, T, dT_eq, troom)
        s_tab = pulse_table(t_rel, T, 1.0 / src["dilution"])
        k_in = 1.5 * (0.05 * src["u_eq"]) ** 2
        om_in = math.sqrt(k_in) / (0.09**0.25 * 0.07 * 2 * R_E)

    def bc(wall, body, vent, nozzle, active, idle):
        """wall: car walls; body: occupants; nozzle: emitter stubs (walls); active / idle: the culprit's release
        face / the other release face (zero inflow, as the sofa precursor's release)."""
        out = "boundaryField\n{\n" + "".join(f"    {p} {{ {wall} }}\n" for p in ("floor", "ceiling", "walls"))
        out += "".join(f"    {n} {{ {body} }}\n" for n in NAMES)
        out += "".join(f"    nozzle_{c} {{ {nozzle} }}\n" for c in CULPRITS)
        out += "".join(f"    release_{c} {{ {active if (src and c == culprit) else idle} }}\n" for c in CULPRITS)
        return out + f"    vent {{ {vent} }}\n}}\n"

    idle = {"U": "type flowRateInletVelocity; volumetricFlowRate constant 0; value uniform (0 0 0);",
            "T": f"type uniformFixedValue; uniformValue constant {troom}; value uniform {troom};",
            "s": "type uniformFixedValue; uniformValue constant 0; value uniform 0;",
            "k": f"type fixedValue; value uniform {k0};", "omega": f"type fixedValue; value uniform {om0};"}
    act = dict(idle)
    if src:
        act = {"U": f"type flowRateInletVelocity; volumetricFlowRate {q_tab}; value uniform (0 0 0);",
               "T": f"type uniformFixedValue; uniformValue {t_tab}; value uniform {troom};",
               "s": f"type uniformFixedValue; uniformValue {s_tab}; value uniform 0;",
               "k": f"type fixedValue; value uniform {k_in:.6g};",
               "omega": f"type fixedValue; value uniform {om_in:.6g};"}
    calc0 = "type calculated; value uniform 0;"
    vent_k = f"type inletOutlet; inletValue uniform {k0}; value uniform {k0};"
    vent_om = f"type inletOutlet; inletValue uniform {om0}; value uniform {om0};"
    kw, omw = f"type kqRWallFunction; value uniform {k0};", f"type omegaWallFunction; value uniform {om0};"
    nutw = "type nutkWallFunction; value uniform 0;"
    alw = "type compressible::alphatJayatillekeWallFunction; Prt 0.85; value uniform 0;"

    def scalar(active):
        return ("volScalarField", "dimensions [0 0 0 0 0 0 0];\ninternalField uniform 0;\n"
                + bc("type zeroGradient;", "type zeroGradient;", "type inletOutlet; inletValue uniform 0; value uniform 0;",
                     "type zeroGradient;", active, idle["s"]))

    if multi:
        out = {f"s{k}": scalar(f"type uniformFixedValue; uniformValue "
                                f"{sofa_case.multi_pulse_table([(tr, Tk, 1.0 / sk['dilution'], False)])}; value uniform 0;")
               for k, (sk, tr, Tk) in enumerate(multi, 1)}
    else:
        out = {"s": scalar(act["s"])}
    return out | {
        "U": ("volVectorField", "dimensions [0 1 -1 0 0 0 0];\ninternalField uniform (0 0 0);\n"
              + bc("type noSlip;", "type noSlip;", "type pressureInletOutletVelocity; value uniform (0 0 0);",
                   "type noSlip;", act["U"], idle["U"])),
        "T": ("volScalarField", f"dimensions [0 0 0 1 0 0 0];\ninternalField uniform {troom};\n"
              + bc(f"type fixedValue; value uniform {troom};", f"type fixedValue; value uniform {tskin};",
                   f"type inletOutlet; inletValue uniform {troom}; value uniform {troom};", "type zeroGradient;",
                   act["T"], idle["T"])),
        "p_rgh": ("volScalarField", "dimensions [1 -1 -2 0 0 0 0];\ninternalField uniform 0;\n"
                  + bc("type fixedFluxPressure; value uniform 0;", "type fixedFluxPressure; value uniform 0;",
                       "type fixedValue; value uniform 0;", *["type fixedFluxPressure; value uniform 0;"] * 3)),
        "p": ("volScalarField", "dimensions [1 -1 -2 0 0 0 0];\ninternalField uniform 0;\n" + bc(*[calc0] * 6)),
        "k": ("volScalarField", f"dimensions [0 2 -2 0 0 0 0];\ninternalField uniform {k0};\n"
              + bc(kw, kw, vent_k, kw, act["k"], idle["k"])),
        "omega": ("volScalarField", f"dimensions [0 0 -1 0 0 0 0];\ninternalField uniform {om0};\n"
                  + bc(omw, omw, vent_om, omw, act["omega"], idle["omega"])),
        "nut": ("volScalarField", "dimensions [0 2 -1 0 0 0 0];\ninternalField uniform 0;\n"
                + bc(nutw, nutw, calc0, nutw, calc0, calc0)),
        "alphat": ("volScalarField", "dimensions [1 -1 -1 0 0 0 0];\ninternalField uniform 0;\n"
                   + bc(alw, alw, calc0, alw, calc0, calc0)),
    }


def make(case: Path, mode: str, culprit: str, V: float, T: float, d: float, t_rel: float, t_end: float,
         t_pre: float = None):
    troom = T_ROOM + 273.15
    rho0 = 101325 * 0.02896 / (8.314 * troom)
    multi = None
    if mode == "multi":  # PLAN v4 E2' (supplement): the sofa case's four releases, 30 s apart, scalars s1..s4
        multi = [(equivalent_source(Vk, Tk, dk), t_rel + sofa_case.MULTI_GAP * i, Tk)
                 for i, (_, Vk, Tk, dk) in enumerate(sofa_case.MULTI_RELEASES)]
        t_end = multi[-1][1] + sofa_case.MULTI_WINDOW
    src = equivalent_source(V, T, d) if mode not in ("precursor", "multi") else None
    geo = case / "constant/geometry"
    manikin.write_elevator(geo)
    write_emitters(geo / "emitter.stl")
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
    for name, (cls, body) in fields(src, culprit, t_rel, T, multi).items():
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
    probes = " ".join("({:.4f} {:.4f} {:.4f})".format(*nose_probe(n)) for n in NAMES)
    scalars = ["s"]
    if multi:  # segment schedule for run_multi.sh (as in the sofa case)
        sched, t_prev = [], 0.0
        for sk, tr, Tk in multi:
            if tr - 0.05 > t_prev:
                sched.append((tr - 0.05, 0.1))
            t_prev = tr + Tk + 0.3
            sched.append((t_prev, min(0.01, 4 * 0.0025 / sk["u_eq"])))
        sched.append((t_end, 0.1))
        (case / "schedule").write_text("".join(f"{te:.6g} {dt:.4g}\n" for te, dt in sched))
        end, max_dt, write_int = sched[0][0], sched[0][1], 5
        scalars = [f"s{k}" for k in range(1, len(multi) + 1)]
    elif src:
        end = min(t_end, math.ceil(t_rel + T + 0.3))
        max_dt = min(0.01, 4 * 0.0025 / src["u_eq"])
        write_int = 1
    else:
        end, max_dt, write_int = (t_pre if t_pre else T_PRE), 0.1, 5
    sc = " ".join(scalars)
    st = "".join(f"    #includeFunc scalarTransport({s}, diffusivity=viscosity, alphal=1.428571, alphat=1.428571)\n"
                 for s in scalars)
    iso = sofa_case.iso_block(scalars) if multi else ""
    nose_z = manikin.STAND_NOSE[2]
    w(case / "system/controlDict", f"""solver fluid;
startFrom latestTime;
startTime 0;
stopAt endTime;
endTime {end};
deltaT 0.01;
adjustTimeStep yes;
maxCo 5;
maxDeltaT {max_dt:.4g};
writeControl adjustableRunTime;
writeInterval {write_int};
purgeWrite 0;
writeFormat binary;
writePrecision 8;
writeCompression off;
timeFormat general;
runTimeModifiable true;
functions
{{
{st}    #includeFunc probes(funcName=noses, points=({probes}), fields=({sc} T U))
    #includeFunc residuals(p_rgh, U, e, k, omega, {", ".join(scalars)})
{iso}    planes
    {{
        type            surfaces;
        libs            ("libsampling.so");
        writeControl    adjustableRunTime;
        writeInterval   0.5;
        surfaceFormat   raw;
        interpolationScheme cell;
        interpolate     false;
        fields          ({sc} T U);
        surfaces
        {{
            midLeft    {{ type cutPlane; planeType pointAndNormal; point (0 -0.27 0); normal (0 1 0); interpolate false; }}
            noseHeight {{ type cutPlane; planeType pointAndNormal; point (0 0 {nose_z}); normal (0 0 1); interpolate false; }}
        }}
    }}
}}
""")
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
    div(phi,s1) Gauss limitedLinear01 1;
    div(phi,s2) Gauss limitedLinear01 1;
    div(phi,s3) Gauss limitedLinear01 1;
    div(phi,s4) Gauss limitedLinear01 1;
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
    return src


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("--mode", choices=("precursor", "silent", "audible", "multi"), required=True)
    ap.add_argument("--culprit", choices=CULPRITS, default="FL")
    ap.add_argument("--t-pre", type=float, default=None, help="precursor length (s); default 30")
    ap.add_argument("--turbulence", choices=("rans",), default="rans", help="run_multi.sh passes this; RANS only")
    ap.add_argument("--V", type=float, default=9.2e-5, help="released volume (m^3); median per passage")
    ap.add_argument("--T", type=float, default=None, help="release duration (s)")
    ap.add_argument("--d", type=float, default=None, help="effective orifice diameter (m)")
    ap.add_argument("--t-release", type=float, default=0.2, help="release start time (s)")
    ap.add_argument("--t-end", type=float, default=60.0, help="end time (s)")
    a = ap.parse_args()
    # defaults as in the sofa duet: silent = 92 mL over 2 s through 8 mm; audible = 92 mL over 0.5 s through 2.4 mm
    T = a.T if a.T is not None else (2.0 if a.mode != "audible" else 0.5)
    d = a.d if a.d is not None else (0.008 if a.mode != "audible" else 0.0024)
    src = make(Path(a.case), a.mode, a.culprit, a.V, T, d, a.t_release, a.t_end, a.t_pre)
    if src:
        src["stage1_end"] = min(a.t_end, math.ceil(a.t_release + T + 0.3))
    print("written", a.case, a.mode, a.culprit, {k: round(v, 5) for k, v in (src or {}).items()})
