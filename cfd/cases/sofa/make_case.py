"""Scenario A, 'sofa duet': two seated adults on a sofa in a quiescent living room; one releases.

Transient RANS k-omega SST, Boussinesq ('fluid' solver), skin 33 C, walls 23 C (same set-up as the M3b CBL runs).
Release = momentum-equivalent inlet: a 3 cm long, 1 cm radius nozzle stub behind the farter's buttocks, its end face
(patch 'release') pointing down and back into the seat/backrest corner, 2.8 cm above the seat:
  physical release  : V over T through an orifice d  ->  Q0 = V/T, u0 = Q0/(pi d^2/4), M0 = u0 Q0
  equivalent inlet  : area A_e = pi r_e^2;
                      audible (u0 > sqrt(M0/A_e)): u_eq = sqrt(M0/A_e), Q_eq = M0/u_eq  (momentum and odorant flux
                      conserved, the inlet fluid is pre-diluted by Q0/Q_eq with room air)
                      silent: Q_eq = Q0, u_eq = Q0/A_e
                      the pulse has 0.03 s linear ramps (volume preserved)
  buoyancy          : the flatus density deficit (median g' = 1.70 m/s^2, Suarez 1997 compositions) is represented
                      by an equivalent temperature excess dT = g'/(g beta), diluted like the scalar.
  odorant           : passive scalar s (s = 1 for undiluted flatus), scalarTransport with Sc_t = 0.7.
Nose probes 2.5 cm in front of each nose tip.
Pressure relief: a 0.5 m x 0.5 m ceiling vent (p_rgh = 0, inflow at room temperature) in the far corner, cut from the
ceiling patch by createPatch after meshing. A sealed Boussinesq room cannot take a net volume inflow, and a real room
leaks.
Energy: sensibleInternalEnergy. OpenFOAM's Boussinesq equation of state puts h = p/rho(T) into the enthalpy, so with
sensibleEnthalpy every pressure change shifts T and rho; with an open vent that expansion leaves through the vent and
changes the pressure again. An isothermal room at rest blew up within 3 steps with h and stays at rest (mean Co 1e-9)
with e. The closed CBL validation rooms (pressure pinned by the reference cell) are not affected.
History: a volumetric massSource (sphere, r = 7.5 mm and 2 cm) diverged within 5-12 time steps with a growing
domain-mean Courant number, with or without the vent; the same mesh without the source was stable. The release is
therefore a boundary inlet.

Usage: python3 make_case.py <case_dir> --mode {precursor,silent,audible} [--V 9.2e-5 --T 2.0 --d 0.008]
       [--t-release 30 --t-end 60]   (branch cases mapped from the precursor use --t-release 1 --t-end 31)
"""
import argparse
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DOMAIN = ((-1.0, 2.2), (-1.6, 1.6), (0.0, 2.6))
DY_F, DY_N = -0.30, 0.30
NOSE_X, NOSE_Z = 0.10, 1.215
REL = (-0.195, DY_F, 0.478)            # release point: behind the buttocks, 2.8 cm above the seat
REL_DIR = (-0.5, 0.0, -0.866)          # down and back, into the seat/backrest corner
R_E, L_E = 0.01, 0.03                  # nozzle radius and length; the release face is meshed at level 5 (2.5 mm)
RAMP = 0.03                            # s, linear ramp at both ends of the pulse
VENT_BOX = "(1.6 1.0 2.5) (2.1 1.5 2.7)"  # ceiling faces with centres in this box become the vent patch
T_ROOM, T_SKIN = 23.0, 33.0
GAP, FABRIC = 0.02, 0.01               # trousers: air gap between skin and fabric (holds the release point, 1.5 cm behind
                                       # the back) and the modelled fabric thickness (2 cells at level 4)
DP_FABRIC = 100.0                      # Pa, EN ISO 9237 test pressure (params.yaml clothing.dp_ref_fabric)
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
    A_s = math.pi * R_E**2
    u_eq = math.sqrt(M0 / A_s)
    if u_eq < Q0 / A_s:  # inlet larger than the jet would be: no pre-dilution
        u_eq, Q_eq = Q0 / A_s, Q0
    else:
        Q_eq = M0 / u_eq
    return {"Q0": Q0, "u0": u0, "M0": M0, "u_eq": u_eq, "Q_eq": Q_eq, "dilution": Q_eq / Q0}


def write_emitter(path: Path, manikin):
    """Nozzle stub along REL_DIR ending at REL; two STL solids: 'nozzle' (wall) and 'release' (end face)."""
    import numpy as np
    d = np.array(REL_DIR) / np.linalg.norm(REL_DIR)
    p1 = np.array(REL)
    p0 = p1 - L_E * d
    tube = manikin.cylinder(p0, p1, R_E, caps=True, n=32)
    n_cap = 31  # cylinder() appends the p0 cap, then the p1 cap, n - 1 triangles each
    tris = {"nozzle": tube[:-n_cap], "release": tube[-n_cap:]}
    with open(path, "w") as fh:
        for name, tt in tris.items():
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


def pulse_table(t_rel, T, value, base=0.0, conserve=False):
    """Function1 table: base -> base + value over [t_rel, t_rel + T] with linear ramps. conserve=True scales the
    plateau so that the integral equals value * T (flow rate); intensive quantities (T, s) keep the plateau value."""
    v = value * T / (T - RAMP) if conserve else value
    pts = [(0.0, base), (t_rel, base), (t_rel + RAMP, base + v), (t_rel + T - RAMP, base + v), (t_rel + T, base),
           (t_rel + T + 1e4, base)]
    return "table (" + " ".join(f"({t:.6g} {y:.8g})" for t, y in pts) + ")"


def multi_pulse_table(pulses, base=0.0):
    """Function1 table of non-overlapping pulses [(t_rel, T, value, conserve), ...] on a common base value."""
    pts = [(0.0, base)]
    for t_rel, T, value, conserve in sorted(pulses):
        v = value * T / (T - RAMP) if conserve else value
        pts += [(t_rel, base), (t_rel + RAMP, base + v), (t_rel + T - RAMP, base + v), (t_rel + T, base)]
    pts.append((pts[-1][0] + 1e4, base))
    return "table (" + " ".join(f"({t:.6g} {y:.8g})" for t, y in pts) + ")"


# PLAN v4 E2': four releases in one run, one scalar each (s1..s4), 30 s apart, strongest first; representative
# passages at the 50th/90th percentile of the exit momentum flux M0 within each class (Gate 0 priors, onset 41.9 m/s)
MULTI_RELEASES = [  # (name, V m^3, T s, d m)
    ("A90", 278.8e-6, 0.34, 2.54e-3),
    ("A50", 86.2e-6, 0.42, 1.67e-3),
    ("S90", 66.4e-6, 0.65, 2.45e-3),
    ("S50", 122.1e-6, 4.76, 3.06e-3),
]
MULTI_GAP, MULTI_WINDOW = 30.0, 150.0


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
    rx, ry, rz = REL
    tro_geo = "".join(f'    tro{k} {{ type triSurface; file "{f}"; }}\n' for k, f in enumerate(trousers))
    tro_ref = "".join(f"        tro{k} {{ mode inside; level 4; }}\n" for k in range(len(trousers)))
    return f"""castellatedMesh true;
snap            true;
addLayers       true;
geometry
{{
    farter    {{ type triSurface; file "farter.stl"; }}
    neighbour {{ type triSurface; file "neighbour.stl"; }}
    sofa      {{ type triSurface; file "sofa.stl"; }}
    emitter   {{ type triSurface; file "emitter.stl"; regions {{ nozzle {{ name nozzle; }} release {{ name release; }} }} }}
    people    {{ type box; min (-0.45 -0.95 0); max (0.80 0.95 1.45); }}
    plumes    {{ type box; min (-0.35 -0.75 1.0); max (0.40 0.75 2.4); }}
    faces     {{ type box; min (0.0 -0.50 1.05); max (0.35 0.50 1.40); }}
    release   {{ type box; min ({rx - 0.06} {ry - 0.08} 0.45); max ({rx + 0.05} {ry + 0.08} {rz + 0.08}); }}
{tro_geo}}};
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
        emitter
        {{
            level (4 4);
            regions
            {{
                nozzle  {{ level (4 4); patchInfo {{ type wall; }} }}
                release {{ level (5 5); patchInfo {{ type patch; }} }}
            }}
        }}
    }}
    resolveFeatureAngle 30;
    refinementRegions
    {{
        people  {{ mode inside; level 2; }}
        plumes  {{ mode inside; level 1; }}
        faces   {{ mode inside; level 3; }}
        release {{ mode inside; level 4; }}
{tro_ref}    }}
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


def fields(src, t_rel=T_REL, T=1.0, multi=None):
    troom, tskin = T_ROOM + 273.15, T_SKIN + 273.15
    k0, om0 = 1e-5, 0.1

    def bc(wall, body, sofa, vent, release):
        """Boundary conditions; the nozzle stub takes the sofa (furniture) condition."""
        return ("boundaryField\n{\n" + "".join(f"    {p} {{ {wall} }}\n" for p in WALLS)
                + "".join(f"    {b} {{ {body} }}\n" for b in BODIES) + f"    sofa {{ {sofa} }}\n"
                + f"    nozzle {{ {sofa} }}\n    vent {{ {vent} }}\n    release {{ {release} }}\n}}\n")

    beta = 1.0 / troom
    if multi:  # [(src, t_rel, T), ...]
        q_tab = multi_pulse_table([(tr, Tk, sk["Q_eq"], True) for sk, tr, Tk in multi])
        t_tab = multi_pulse_table([(tr, Tk, G_PRIME / (9.81 * beta) / sk["dilution"], False) for sk, tr, Tk in multi], troom)
        u_max = max(sk["u_eq"] for sk, _, _ in multi)
        k_in = 1.5 * (0.05 * u_max) ** 2
        om_in = math.sqrt(k_in) / (0.09**0.25 * 0.07 * 2 * R_E)
        s_tab = "constant 0"
    elif src:
        dT_eq = G_PRIME / (9.81 * beta) / src["dilution"]
        q_tab = pulse_table(t_rel, T, src["Q_eq"], conserve=True)
        t_tab = pulse_table(t_rel, T, dT_eq, troom)
        s_tab = pulse_table(t_rel, T, 1.0 / src["dilution"])
        k_in = 1.5 * (0.05 * src["u_eq"]) ** 2
        om_in = math.sqrt(k_in) / (0.09**0.25 * 0.07 * 2 * R_E)
    else:
        q_tab, t_tab, s_tab, k_in, om_in = "constant 0", f"constant {troom}", "constant 0", k0, om0
    out = {
        "U": ("volVectorField", "dimensions [0 1 -1 0 0 0 0];\ninternalField uniform (0 0 0);\n"
              + bc("type noSlip;", "type noSlip;", "type noSlip;",
                   "type pressureInletOutletVelocity; value uniform (0 0 0);",
                   f"type flowRateInletVelocity; volumetricFlowRate {q_tab}; value uniform (0 0 0);")),
        "T": ("volScalarField", f"dimensions [0 0 0 1 0 0 0];\ninternalField uniform {troom};\n"
              + bc(f"type fixedValue; value uniform {troom};", f"type fixedValue; value uniform {tskin};",
                   "type zeroGradient;", f"type inletOutlet; inletValue uniform {troom}; value uniform {troom};",
                   f"type uniformFixedValue; uniformValue {t_tab}; value uniform {troom};")),
        "s": ("volScalarField", "dimensions [0 0 0 0 0 0 0];\ninternalField uniform 0;\n"
              + bc("type zeroGradient;", "type zeroGradient;", "type zeroGradient;",
                   "type inletOutlet; inletValue uniform 0; value uniform 0;",
                   f"type uniformFixedValue; uniformValue {s_tab}; value uniform 0;")),
        "p_rgh": ("volScalarField", "dimensions [1 -1 -2 0 0 0 0];\ninternalField uniform 0;\n"
                  + bc(*["type fixedFluxPressure; value uniform 0;"] * 3, "type fixedValue; value uniform 0;",
                       "type fixedFluxPressure; value uniform 0;")),
        "p": ("volScalarField", "dimensions [1 -1 -2 0 0 0 0];\ninternalField uniform 0;\n"
              + bc(*["type calculated; value uniform 0;"] * 5)),
        "k": ("volScalarField", f"dimensions [0 2 -2 0 0 0 0];\ninternalField uniform {k0};\n"
              + bc(*[f"type kqRWallFunction; value uniform {k0};"] * 3,
                   f"type inletOutlet; inletValue uniform {k0}; value uniform {k0};",
                   f"type fixedValue; value uniform {k_in:.6g};")),
        "omega": ("volScalarField", f"dimensions [0 0 -1 0 0 0 0];\ninternalField uniform {om0};\n"
                  + bc(*[f"type omegaWallFunction; value uniform {om0};"] * 3,
                       f"type inletOutlet; inletValue uniform {om0}; value uniform {om0};",
                       f"type fixedValue; value uniform {om_in:.6g};")),
        "nut": ("volScalarField", "dimensions [0 2 -1 0 0 0 0];\ninternalField uniform 0;\n"
                + bc(*["type nutkWallFunction; value uniform 0;"] * 3, *["type calculated; value uniform 0;"] * 2)),
        "alphat": ("volScalarField", "dimensions [1 -1 -1 0 0 0 0];\ninternalField uniform 0;\n"
                   + bc(*["type compressible::alphatJayatillekeWallFunction; Prt 0.85; value uniform 0;"] * 3,
                        *["type calculated; value uniform 0;"] * 2)),
    }
    if multi:  # one scalar per release, s_k = 1/dilution_k during its own pulse
        del out["s"]
        for k, (sk, tr, Tk) in enumerate(multi, 1):
            tab = multi_pulse_table([(tr, Tk, 1.0 / sk["dilution"], False)])
            out[f"s{k}"] = ("volScalarField", "dimensions [0 0 0 0 0 0 0];\ninternalField uniform 0;\n"
                            + bc("type zeroGradient;", "type zeroGradient;", "type zeroGradient;",
                                 "type inletOutlet; inletValue uniform 0; value uniform 0;",
                                 f"type uniformFixedValue; uniformValue {tab}; value uniform 0;"))
    return out


def trousers_dicts(inner, outer, a_fabric):
    """createZonesDict (shell = union of outer offsets minus union of inner offsets) and the porosity fvModel. The
    fabric's EN ISO 9237 air permeability a (m/s at DP_FABRIC) is spread over the modelled thickness FABRIC:
    dp = mu*D*u*FABRIC = DP_FABRIC*u/a  ->  D = DP_FABRIC/(a*mu*FABRIC)."""
    def side(name, files):
        parts = "".join(f'        {name}{k} {{ type insideSurface; zoneType cell; surface closedTriSurface; file "{f}"; }}\n'
                        for k, f in enumerate(files))
        return f"    {name}\n    {{\n        type union;\n        zoneType cell;\n{parts}    }}\n"
    zones = "trousers\n{\n    type difference;\n    zoneType cell;\n" + side("outer", outer) + side("inner", inner) + "}\n"
    D = DP_FABRIC / (a_fabric * 1.81e-5 * FABRIC)
    fvm = f"""trousers
{{
    type porosityForce;
    porosityForceCoeffs
    {{
        cellZone trousers;
        type DarcyForchheimer;
        d ({D:.4e} {D:.4e} {D:.4e});
        f (0 0 0);
        coordinateSystem {{ type cartesian; origin (0 0 0); coordinateRotation {{ type axesRotation; e1 (1 0 0); e2 (0 1 0); }} }}
    }}
}}
"""
    return zones, fvm


def make(case: Path, mode: str, V: float, T: float, d: float, t_rel: float = T_REL, t_end: float = T_END,
         recline: float = 0.0, clothing: str = "bare", a_fabric: float = 0.030, t_pre: float = T_PRE):
    troom = T_ROOM + 273.15
    rho0 = 101325 * 0.02896 / (8.314 * troom)
    multi = None
    if mode == "multi":
        multi = [(equivalent_source(Vk, Tk, dk), t_rel + MULTI_GAP * i, Tk) for i, (_, Vk, Tk, dk) in enumerate(MULTI_RELEASES)]
        t_end = multi[-1][1] + MULTI_WINDOW
    src = equivalent_source(V, T, d) if mode not in ("precursor", "multi") else None
    geo = case / "constant/geometry"
    geo.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ROOT / "cfd/geometry"))
    import manikin
    manikin.write_scene(geo, DY_F, DY_N, recline_farter=recline)
    write_emitter(geo / "emitter.stl", manikin)
    inner, outer = [], []
    if clothing == "trousers":
        for who, dy, rec in (("trF", DY_F, recline), ("trN", DY_N, 0.0)):
            i, o = manikin.write_trousers(geo, who, "seated", GAP, FABRIC, dy=dy, recline_deg=rec)
            inner += i; outer += o
    w(case / "system/blockMeshDict", block_mesh())
    w(case / "system/snappyHexMeshDict", snappy(outer))
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
    for name, (cls, body) in fields(src, t_rel, T, multi).items():
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
    (case / "constant/fvModels").unlink(missing_ok=True)
    (case / "system/createZonesDict").unlink(missing_ok=True)
    if clothing == "trousers":
        zones, fvm = trousers_dicts(inner, outer, a_fabric)
        w(case / "system/createZonesDict", zones)
        w(case / "constant/fvModels", fvm)
    nf = manikin.nose_tip(recline)  # releaser's nose moves back when reclined; probe stays 2.5 cm in front of it
    nose_f = f"({nf[0] + NOSE_X - manikin.NOSE[0]:.4f} {DY_F} {nf[2]:.4f})"
    nose_n = f"({NOSE_X} {DY_N} {NOSE_Z})"
    # branch cases run in two stages (run_sofa.sh): 'release' up to stage1_end with a time step that resolves the
    # inlet pulse and its ramps, then 'drift' to t_end with maxDeltaT 0.1 and writeInterval 5
    scalars = ["s"]
    if multi:
        # schedule for run_multi.sh: (end time, maxDeltaT) segments; each pulse runs with a time step that resolves
        # it and its ramps, the gaps with maxDeltaT 0.1
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
        end, max_dt, write_int = t_pre, 0.1, 5
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
{"".join(f"    #includeFunc scalarTransport({sc}, diffusivity=viscosity, alphal=1.428571, alphat=1.428571)" + chr(10) for sc in scalars)}    #includeFunc probes(funcName=noses, points=({nose_f} {nose_n}), fields=({" ".join(scalars)} T U))
    #includeFunc residuals(p_rgh, U, e, k, omega, {" ".join(scalars)})
    planes
    {{
        type            surfaces;
        libs            ("libsampling.so");
        writeControl    adjustableRunTime;
        writeInterval   0.5;
        surfaceFormat   raw;
        interpolationScheme cell;
        interpolate     false;
        fields          ({" ".join(scalars)} T U);
        surfaces
        {{
            midFarter  {{ type cutPlane; planeType pointAndNormal; point (0 {DY_F} 0); normal (0 1 0); interpolate false; }}
            noseHeight {{ type cutPlane; planeType pointAndNormal; point (0 0 {NOSE_Z}); normal (0 0 1); interpolate false; }}
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
    ap.add_argument("--V", type=float, default=9.2e-5, help="released volume (m^3); median per passage")
    ap.add_argument("--T", type=float, default=None, help="release duration (s)")
    ap.add_argument("--d", type=float, default=None, help="effective orifice diameter (m)")
    ap.add_argument("--t-release", type=float, default=T_REL, help="release start time (s)")
    ap.add_argument("--t-end", type=float, default=T_END, help="end time (s)")
    ap.add_argument("--recline", type=float, default=0.0, help="releaser upper-body recline about the hip (deg)")
    ap.add_argument("--clothing", choices=("bare", "trousers"), default="bare", help="long trousers on both occupants")
    ap.add_argument("--t-pre", type=float, default=T_PRE, help="precursor length (s)")
    ap.add_argument("--fabric-a", type=float, default=0.030, help="fabric air permeability at 100 Pa (m/s); denim")
    a = ap.parse_args()
    # defaults: silent = 92 mL over 2 s through 8 mm (u0 0.9 m/s, below acoustic onset);
    #           audible = 92 mL over 0.5 s through 2.4 mm (u0 41 m/s, above onset ~30 m/s)
    T = a.T if a.T is not None else (2.0 if a.mode != "audible" else 0.5)
    d = a.d if a.d is not None else (0.008 if a.mode != "audible" else 0.0024)
    src = make(Path(a.case), a.mode, a.V, T, d, a.t_release, a.t_end, a.recline, a.clothing, a.fabric_a, a.t_pre)
    if src:
        src["stage1_end"] = min(a.t_end, math.ceil(a.t_release + T + 0.3))
    print("written", a.case, a.mode, {k: round(v, 5) for k, v in (src or {}).items()})
