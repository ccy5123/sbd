"""Scenario D', 'standing pair': two adults talking face to face (noses 1.0 m apart) in the 3.2 x 3.2 x 2.6 m room
of the sofa duet, nothing behind the culprit for 0.8 m; still air or office ceiling ventilation.

Purpose: the sofa and the elevator showed that what stands behind the culprit (backrest, wall, person) decides the
routing, and both were in still air. This scene fills the two empty cells of that table: open space behind, in still
air and in mixed (ventilated) air.

Same physics and release model as the sofa duet (cfd/cases/sofa/make_case.py): transient RANS k-omega SST,
Boussinesq, skin 33 C, walls 23 C; momentum-equivalent release inlet behind the culprit's buttocks, pointing down and
back (away from the neighbour); odorant = passive scalar s (s = 1 undiluted flatus), Sc_t = 0.7.

Ventilation ('--vent on'): one square ceiling diffuser at the room centre, above the gap between the two people,
discharging through four 0.06 m slots along the edges of a 0.32 m square.
  - Supply 21.2 L/s = EN 16798-1 Category II, low-polluting building: 7 L/s per person x 2 + 0.7 L/s per m2 x 10.24 m2
    (Olesen 2024, REHVA J. 06/2024, Tables 2-3); 2.9 air changes per hour.
  - Discharge: the vertical component carries the flow (0.34 m/s over 0.0624 m2); a horizontal component of 1.5 m/s
    along the ceiling, outward from each slot [ASSUMPTION: square-diffuser-like throw; not a manufacturer's diffuser].
  - Isothermal supply at room temperature [ASSUMPTION: ventilation only, no cooling load].
Both modes have the same mesh: with '--vent off' the slots are closed inlets (zero flow). A 0.30 m x 0.30 m ceiling
grille near a corner is the exhaust (p_rgh = 0) in both, i.e. also the pressure relief of the still room.

Usage: python3 make_case.py <case_dir> --mode {precursor,silent,audible} --vent {off,on}
       [--t-release 0.2 --t-end 60] [--V 9.2e-5 --T .. --d ..]
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

DOMAIN = ((0.0, 3.2), (-1.6, 1.6), (0.0, 2.6))
NAMES = tuple(manikin.PAIR)               # probe order: C (culprit), N (neighbour)
T_ROOM, T_SKIN = 23.0, 33.0
G_PRIME = 1.70
T_PRE = {"off": 30.0, "on": 90.0}         # precursor length: body plumes; plus the diffuser's room circulation
PROBE_DX = 0.025                          # probe 2.5 cm in front of the nose tip
EXHAUST_BOX = "(2.70 1.10 2.55) (3.00 1.40 2.65)"
Q_SUPPLY = 2 * 7e-3 + 0.7e-3 * 3.2 * 3.2  # m3/s, EN 16798-1 Cat. II
U_THROW = 1.5                             # m/s, horizontal discharge component [ASSUMPTION]
# diffuser slots on the ceiling (aligned with the 0.02 m level-2 grid): name -> (box lo, box hi, outward direction)
SLOTS = {"supply_xp": ((1.70, -0.16), (1.76, 0.16), (1, 0)), "supply_xm": ((1.44, -0.16), (1.50, 0.16), (-1, 0)),
         "supply_yp": ((1.50, 0.10), (1.70, 0.16), (0, 1)), "supply_ym": ((1.50, -0.16), (1.70, -0.10), (0, -1))}
SLOT_AREA = sum((hi[0] - lo[0]) * (hi[1] - lo[1]) for lo, hi, _ in SLOTS.values())
U_DOWN = Q_SUPPLY / SLOT_AREA


def rel_point():
    x, y, _ = manikin.PAIR["C"]
    return manikin.STAND_REL + np.array([x, y, 0.0])


def nose_probe(name):
    x, y, f = manikin.PAIR[name]
    n = manikin.STAND_NOSE
    return (x + f * (n[0] + PROBE_DX), y, n[2])


def write_emitter(path: Path):
    """Nozzle stub behind the culprit along REL_DIR; solids nozzle (wall) and release (end face)."""
    d = np.array(REL_DIR) / np.linalg.norm(REL_DIR)
    p1 = rel_point()
    tube = manikin.cylinder(p1 - L_E * d, p1, R_E, caps=True, n=32)
    n_cap = 31
    with open(path, "w") as fh:
        for name, tt in (("nozzle", tube[:-n_cap]), ("release", tube[-n_cap:])):
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


def snappy(trousers=()):
    geo = "".join(f'    {n} {{ type triSurface; file "{n}.stl"; }}\n' for n in NAMES)
    geo += "".join(f'    tro{k} {{ type triSurface; file "{f}"; }}\n' for k, f in enumerate(trousers))
    geo += '    emitter { type triSurface; file "emitter.stl"; regions { nozzle { name nozzle; } release { name release; } } }\n'
    boxes = ""
    for n in NAMES:
        x, y, z = nose_probe(n)
        f = manikin.PAIR[n][2]
        lo, hi = sorted((x - f * 0.08, x + f * 0.20))
        boxes += f"    face_{n} {{ type box; min ({lo:.3f} {y - 0.12:.3f} 1.47); max ({hi:.3f} {y + 0.12:.3f} 1.72); }}\n"
    rx, ry, rz = rel_point()
    boxes += f"    rel {{ type box; min ({rx - 0.06:.3f} {ry - 0.08:.3f} {rz - 0.10:.3f}); max ({rx + 0.05:.3f} {ry + 0.08:.3f} {rz + 0.06:.3f}); }}\n"
    surf = "".join(f"        {n} {{ level (3 3); patchInfo {{ type wall; }} }}\n" for n in NAMES)
    surf += ("        emitter\n        {\n            level (4 4);\n            regions\n            {\n"
             "                nozzle { level (4 4); patchInfo { type wall; } }\n"
             "                release { level (5 5); patchInfo { type patch; } }\n            }\n        }\n")
    reg = "".join(f"        face_{n} {{ mode inside; level 3; }}\n" for n in NAMES)
    reg += "".join(f"        tro{k} {{ mode inside; level 4; }}\n" for k in range(len(trousers)))
    return f"""castellatedMesh true;
snap            true;
addLayers       true;
geometry
{{
{geo}    people {{ type box; min (0.55 -0.55 0.0); max (2.65 0.55 1.80); }}
    diffuser {{ type box; min (1.30 -0.30 2.44); max (1.90 0.30 2.65); }}
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
        diffuser {{ mode inside; level 2; }}
{reg}        rel {{ mode inside; level 4; }}
    }}
    insidePoint (3.0 -1.4 2.0);
    allowFreeStandingZoneFaces false;
}}
snapControls {{ nSmoothPatch 3; tolerance 2.0; nSolveIter 50; nRelaxIter 5; }}
addLayersControls
{{
    relativeSizes true;
    layers {{ "(C|N)" {{ nSurfaceLayers 3; }} }}
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
    zones = f"""    exhaust
    {{
        patchInfo {{ type patch; }}
        constructFrom zone;
        zone {{ type box; zoneType face; box {EXHAUST_BOX}; zone {{ type patch; patch ceiling; }} }}
    }}
"""
    for name, (lo, hi, _) in SLOTS.items():
        zones += f"""    {name}
    {{
        patchInfo {{ type patch; }}
        constructFrom zone;
        zone {{ type box; zoneType face; box ({lo[0]} {lo[1]} 2.55) ({hi[0]} {hi[1]} 2.65); zone {{ type patch; patch ceiling; }} }}
    }}
"""
    return "patches\n{\n" + zones + "}\n"


def fields(src, vent, t_rel, T, multi=None):
    troom, tskin = T_ROOM + 273.15, T_SKIN + 273.15
    k0, om0 = 1e-5, 0.1
    beta = 1.0 / troom
    if multi:  # [(src, t_rel, T), ...]: one inlet carrying all pulses, one scalar per release (sofa_case.fields)
        mpt = sofa_case.multi_pulse_table
        q_tab = mpt([(tr, Tk, sk["Q_eq"], True) for sk, tr, Tk in multi])
        t_tab = mpt([(tr, Tk, G_PRIME / (9.81 * beta) / sk["dilution"], False) for sk, tr, Tk in multi], troom)
        s_tab = "constant 0"
        k_in = 1.5 * (0.05 * max(sk["u_eq"] for sk, _, _ in multi)) ** 2
        om_in = math.sqrt(k_in) / (0.09**0.25 * 0.07 * 2 * R_E)
        src = multi[0][0]  # marks the release patch as an inlet below
    elif src:
        dT_eq = G_PRIME / (9.81 * beta) / src["dilution"]
        q_tab = pulse_table(t_rel, T, src["Q_eq"], conserve=True)
        t_tab = pulse_table(t_rel, T, dT_eq, troom)
        s_tab = pulse_table(t_rel, T, 1.0 / src["dilution"])
        k_in = 1.5 * (0.05 * src["u_eq"]) ** 2
        om_in = math.sqrt(k_in) / (0.09**0.25 * 0.07 * 2 * R_E)
    # supply: 10 % intensity of the discharge speed, length scale 0.07 x slot hydraulic diameter (~0.1 m)
    u_dis = math.hypot(U_THROW, U_DOWN)
    k_sup = 1.5 * (0.10 * u_dis) ** 2
    om_sup = math.sqrt(k_sup) / (0.09**0.25 * 0.07 * 0.10)

    closed = {"U": "type flowRateInletVelocity; volumetricFlowRate constant 0; value uniform (0 0 0);",
              "T": f"type uniformFixedValue; uniformValue constant {troom}; value uniform {troom};",
              "s": "type uniformFixedValue; uniformValue constant 0; value uniform 0;",
              "k": f"type fixedValue; value uniform {k0};", "omega": f"type fixedValue; value uniform {om0};",
              "p_rgh": "type fixedFluxPressure; value uniform 0;"}

    def supply(direction):
        if vent != "on":
            return closed
        ux, uy = (U_THROW * c for c in direction)
        return {"U": f"type fixedValue; value uniform ({ux:.4f} {uy:.4f} {-U_DOWN:.4f});",
                "T": f"type fixedValue; value uniform {troom};", "s": "type fixedValue; value uniform 0;",
                "k": f"type fixedValue; value uniform {k_sup:.6g};", "omega": f"type fixedValue; value uniform {om_sup:.6g};",
                "p_rgh": "type fixedFluxPressure; value uniform 0;"}

    rel = dict(closed)
    if src:
        rel.update({"U": f"type flowRateInletVelocity; volumetricFlowRate {q_tab}; value uniform (0 0 0);",
                    "T": f"type uniformFixedValue; uniformValue {t_tab}; value uniform {troom};",
                    "s": f"type uniformFixedValue; uniformValue {s_tab}; value uniform 0;",
                    "k": f"type fixedValue; value uniform {k_in:.6g};",
                    "omega": f"type fixedValue; value uniform {om_in:.6g};"})
    kw, omw = f"type kqRWallFunction; value uniform {k0};", f"type omegaWallFunction; value uniform {om0};"
    nutw = "type nutkWallFunction; value uniform 0;"
    alw = "type compressible::alphatJayatillekeWallFunction; Prt 0.85; value uniform 0;"
    calc0 = "type calculated; value uniform 0;"
    fff = "type fixedFluxPressure; value uniform 0;"
    walls = {"U": "type noSlip;", "T": f"type fixedValue; value uniform {troom};", "s": "type zeroGradient;",
             "k": kw, "omega": omw, "nut": nutw, "alphat": alw, "p_rgh": fff, "p": calc0}
    bodies = dict(walls, T=f"type fixedValue; value uniform {tskin};")
    nozzle = dict(walls, T="type zeroGradient;")
    exhaust = {"U": "type pressureInletOutletVelocity; value uniform (0 0 0);",
               "T": f"type inletOutlet; inletValue uniform {troom}; value uniform {troom};",
               "s": "type inletOutlet; inletValue uniform 0; value uniform 0;",
               "k": f"type inletOutlet; inletValue uniform {k0}; value uniform {k0};",
               "omega": f"type inletOutlet; inletValue uniform {om0}; value uniform {om0};",
               "nut": calc0, "alphat": calc0, "p_rgh": "type fixedValue; value uniform 0;", "p": calc0}
    for d in (rel, closed):
        d.setdefault("nut", calc0), d.setdefault("alphat", calc0), d.setdefault("p", calc0)
    patches = {p: walls for p in ("floor", "ceiling", "walls")}
    patches.update({n: bodies for n in NAMES})
    patches.update({"nozzle": nozzle, "release": rel, "exhaust": exhaust})
    for name, (_, _, direction) in SLOTS.items():
        s = dict(supply(direction))
        s.setdefault("nut", calc0), s.setdefault("alphat", calc0), s.setdefault("p", calc0)
        patches[name] = s

    scalars = ["s"]
    if multi:
        scalars = [f"s{k}" for k in range(1, len(multi) + 1)]
        for p, v in patches.items():
            v = patches[p] = dict(v)
            for k, sc in enumerate(scalars):
                v[sc] = v["s"]
                if p == "release":
                    sk, tr, Tk = multi[k]
                    v[sc] = (f"type uniformFixedValue; uniformValue "
                             f"{sofa_case.multi_pulse_table([(tr, Tk, 1.0 / sk['dilution'], False)])}; value uniform 0;")

    def bf(field):
        return "boundaryField\n{\n" + "".join(f"    {p} {{ {v[field]} }}\n" for p, v in patches.items()) + "}\n"

    if multi:
        out = {sc: ("volScalarField", "dimensions [0 0 0 0 0 0 0];\ninternalField uniform 0;\n" + bf(sc)) for sc in scalars}
    else:
        out = {"s": ("volScalarField", "dimensions [0 0 0 0 0 0 0];\ninternalField uniform 0;\n" + bf("s"))}
    return out | {
        "U": ("volVectorField", "dimensions [0 1 -1 0 0 0 0];\ninternalField uniform (0 0 0);\n" + bf("U")),
        "T": ("volScalarField", f"dimensions [0 0 0 1 0 0 0];\ninternalField uniform {troom};\n" + bf("T")),
        "p_rgh": ("volScalarField", "dimensions [1 -1 -2 0 0 0 0];\ninternalField uniform 0;\n" + bf("p_rgh")),
        "p": ("volScalarField", "dimensions [1 -1 -2 0 0 0 0];\ninternalField uniform 0;\n" + bf("p")),
        "k": ("volScalarField", f"dimensions [0 2 -2 0 0 0 0];\ninternalField uniform {k0};\n" + bf("k")),
        "omega": ("volScalarField", f"dimensions [0 0 -1 0 0 0 0];\ninternalField uniform {om0};\n" + bf("omega")),
        "nut": ("volScalarField", "dimensions [0 2 -1 0 0 0 0];\ninternalField uniform 0;\n" + bf("nut")),
        "alphat": ("volScalarField", "dimensions [1 -1 -1 0 0 0 0];\ninternalField uniform 0;\n" + bf("alphat")),
    }


def make(case: Path, mode: str, vent: str, V: float, T: float, d: float, t_rel: float, t_end: float,
         clothing: str = "bare", a_fabric: float = 0.030, t_pre: float = None):
    troom = T_ROOM + 273.15
    rho0 = 101325 * 0.02896 / (8.314 * troom)
    multi = None
    if mode == "multi":  # PLAN v4 E2': the sofa case's four representative releases, 30 s apart, scalars s1..s4
        multi = [(equivalent_source(Vk, Tk, dk), t_rel + sofa_case.MULTI_GAP * i, Tk)
                 for i, (_, Vk, Tk, dk) in enumerate(sofa_case.MULTI_RELEASES)]
        t_end = multi[-1][1] + sofa_case.MULTI_WINDOW
    src = equivalent_source(V, T, d) if mode not in ("precursor", "multi") else None
    geo = case / "constant/geometry"
    manikin.write_pair(geo)
    write_emitter(geo / "emitter.stl")
    inner, outer = [], []
    if clothing == "trousers":
        for n, (x, y, f) in manikin.PAIR.items():
            i, o = manikin.write_trousers(geo, f"tr{n}", "standing", sofa_case.GAP, sofa_case.FABRIC, dx=x, dy=y, facing=f)
            inner += i; outer += o
    w(case / "system/blockMeshDict", block_mesh())
    w(case / "system/snappyHexMeshDict", snappy(outer))
    w(case / "system/createPatchDict", create_patch())
    for name, (cls, body) in fields(src, vent, t_rel, T, multi).items():
        w(case / "0" / name, body, cls)
    (case / "constant/fvModels").unlink(missing_ok=True)
    (case / "system/createZonesDict").unlink(missing_ok=True)
    if clothing == "trousers":
        zones, fvm = sofa_case.trousers_dicts(inner, outer, a_fabric)
        w(case / "system/createZonesDict", zones)
        w(case / "constant/fvModels", fvm)
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
        end, max_dt, write_int = (t_pre if t_pre else T_PRE[vent]), 0.1, 15
    sc = " ".join(scalars)
    st = "".join(f"    #includeFunc scalarTransport({s}, diffusivity=viscosity, alphal=1.428571, alphat=1.428571)\n" for s in scalars)
    nose_z = manikin.STAND_NOSE[2]
    iso = sofa_case.iso_block(scalars) if multi else ""
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
    #includeFunc patchFlowRate(patch=exhaust)
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
            midPlane   {{ type cutPlane; planeType pointAndNormal; point (0 0 0); normal (0 1 0); interpolate false; }}
            noseHeight {{ type cutPlane; planeType pointAndNormal; point (0 0 {nose_z}); normal (0 0 1); interpolate false; }}
        }}
    }}
}}
""")
    # numerics identical to the elevator and sofa cases
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
    "(U|e|k|omega|s[0-9]*).*" { solver PBiCGStab; preconditioner DILU; tolerance 1e-8; relTol 0; }
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
    ap.add_argument("--vent", choices=("off", "on"), required=True)
    ap.add_argument("--clothing", choices=("bare", "trousers"), default="bare", help="long trousers on both occupants")
    ap.add_argument("--fabric-a", type=float, default=0.030, help="fabric air permeability at 100 Pa (m/s); denim")
    ap.add_argument("--t-pre", type=float, default=None, help="precursor length (s); default 30 (still) / 90 (vent)")
    ap.add_argument("--V", type=float, default=9.2e-5, help="released volume (m^3); median per passage")
    ap.add_argument("--T", type=float, default=None, help="release duration (s)")
    ap.add_argument("--d", type=float, default=None, help="effective orifice diameter (m)")
    ap.add_argument("--t-release", type=float, default=0.2, help="release start time (s)")
    ap.add_argument("--t-end", type=float, default=60.0, help="end time (s)")
    ap.add_argument("--turbulence", choices=("rans",), default="rans",
                    help="run_multi.sh passes this; the standing LES branch (PLAN v4 E4) is not set up yet")
    a = ap.parse_args()
    # defaults as in the sofa duet: silent = 92 mL over 2 s through 8 mm; audible = 92 mL over 0.5 s through 2.4 mm
    T = a.T if a.T is not None else (2.0 if a.mode != "audible" else 0.5)
    d = a.d if a.d is not None else (0.008 if a.mode != "audible" else 0.0024)
    src = make(Path(a.case), a.mode, a.vent, a.V, T, d, a.t_release, a.t_end, a.clothing, a.fabric_a, a.t_pre)
    print("written", a.case, a.mode, a.vent, f"supply {1e3 * Q_SUPPLY:.1f} L/s, down {U_DOWN:.3f} m/s",
          {k: round(v, 5) for k, v in (src or {}).items()})
