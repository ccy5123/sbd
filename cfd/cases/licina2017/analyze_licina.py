"""PLAN v4 E0-3: inhalation intake fractions of the Licina 2017 chamber runs against their Table 2.

iF = Qb * int C dt / released mass (their Eq. 1, Qb = 0.5 m^3/h), with C the scalar at a probe (s = 1 in the
release), over three periods from the start of the source: source-active 10 min, unmixed 22 min (their T + 12 min)
and full 100 min. The run ends at 22 min; from there the room is well mixed (their definition of the 22-min mark), so
the full period adds the decay of the room-mean level, C(t) = C_room(22 min) exp(-a (t - 22 min)), a = exhaust flow /
room volume, at every probe [no deposition: gas]. The well-mixed reference (their Table 1, 0.74 / 4.2 per mille) is
recomputed from the same flow, and the room-mean scalar checks the mass balance of the run against it.

Acceptance (PLAN v4 E0-3): heated / unheated and heated / well mixed within a factor 1.5 of the measured ratios.
Usage: python3 analyze_licina.py <runs_dir>   (reads licina2017_heated and, if present, licina2017_unheated)
Writes <runs_dir>/licina2017_result.json.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_case as mc  # noqa: E402

trapz = getattr(np, "trapezoid", None) or np.trapz  # numpy < 2 in the WSL distro

PERIODS = {"source_10min": 600.0, "unmixed_22min": 1320.0, "full_100min": 6000.0}
# their Table 2 (groin, per mille, mean of n = 2) and Table 1 (well mixed, non-depositing)
MEASURED = {"heated": {"source_10min": 5.5, "unmixed_22min": 7.7, "full_100min": 9.8},
            "unheated": {"source_10min": 0.05, "unmixed_22min": 0.1, "full_100min": 1.2},
            "well_mixed": {"source_10min": 0.74, "full_100min": 4.2}}


def read_series(case: Path, func: str, name: str):
    """Concatenate postProcessing/<func>/<start>/<name> over restarts; later files win on overlap."""
    parts = []
    d = case / "postProcessing" / func
    for sub in sorted((p for p in d.iterdir() if re.fullmatch(r"[0-9.eE+-]+", p.name)), key=lambda p: float(p.name)):
        if (sub / name).exists():
            parts.append(np.atleast_2d(np.loadtxt(sub / name, comments="#")))
    a = np.vstack(parts[::-1])
    _, idx = np.unique(a[:, 0], return_index=True)
    return a[idx]


def released(t_rel):
    """Released scalar volume int Q s dt over the pulse tables of make_case (ramps included)."""
    tt = np.linspace(t_rel - 1, t_rel + mc.T_REL + 1, 200001)
    q = mc.Q_SRC * mc.T_REL / (mc.T_REL - mc.sofa.RAMP)
    ramp = np.clip(np.minimum(tt - t_rel, t_rel + mc.T_REL - tt) / mc.sofa.RAMP, 0, 1)
    return float(trapz(q * ramp * ramp, tt))


def well_mixed(a, v_room, mass, t_rel):
    """Their Eqs. 4-5: well-mixed room, constant source over T_REL, exposure from the source start."""
    t = np.linspace(0, PERIODS["full_100min"], 600001)
    e = mass / mc.T_REL
    c = np.where(t <= mc.T_REL, e / (a * v_room) * (1 - np.exp(-a * t)),
                 e / (a * v_room) * (1 - np.exp(-a * mc.T_REL)) * np.exp(-a * (t - mc.T_REL)))
    return {k: 1e3 * mc.QB * float(trapz(c[t <= T], t[t <= T])) / mass for k, T in PERIODS.items()}


def analyze(case: Path):
    info = dict(line.split() for line in (case / "release.txt").read_text().splitlines())
    t_rel = float(info["t_release"])
    names = (case / "probes.txt").read_text().split()
    mon = read_series(case, "monitors", "s")
    room = read_series(case, "roomMean", "volFieldValue.dat")
    exh = read_series(case, "exhaustFlux", "surfaceFieldValue.dat")
    v_room = float(np.prod([b - a for a, b in mc.DOMAIN]))
    rho0 = 101325 * 0.02896 / (8.314 * (mc.T_ROOM + 273.15))  # phi of the 'fluid' solver is a mass flux
    q_exh = float(np.mean(exh[exh[:, 0] >= t_rel, 1])) / rho0
    a = q_exh / v_room
    mass = released(t_rel)
    t = mon[:, 0] - t_rel
    m = t >= 0
    t_end = float(t[-1])
    c_room = np.interp(t_end, room[:, 0] - t_rel, room[:, 1])
    out = {"case": case.name, "t_end_after_release_s": t_end, "exhaust_m3_s": q_exh, "a_per_h": a * 3600,
           "released_m3": mass, "room_mean_s_at_end": float(c_room), "well_mixed": well_mixed(a, v_room, mass, t_rel),
           "iF_per_mille": {}}
    tail = c_room / a * (1 - np.exp(-a * (PERIODS["full_100min"] - t_end)))  # int of the well-mixed decay
    for j, name in enumerate(names + ["room_mean"]):
        c = mon[m, j + 1] if name != "room_mean" else np.interp(t[m], room[:, 0] - t_rel, room[:, 1])
        res = {}
        for k, T in PERIODS.items():
            if T <= t_end + 1.0:
                sel = t[m] <= T
                res[k] = 1e3 * mc.QB * float(trapz(c[sel], t[m][sel])) / mass
            elif k == "full_100min" and PERIODS["unmixed_22min"] <= t_end + 1.0:
                res[k] = 1e3 * mc.QB * (float(trapz(c, t[m])) + tail) / mass
        out["iF_per_mille"][name] = res
    return out


def main(runs: Path):
    res = {}
    for mode in ("heated", "unheated"):
        case = runs / f"licina2017_{mode}"
        if (case / "postProcessing/monitors").exists():
            res[mode] = analyze(case)
    checks = {}
    for k in PERIODS:
        h = res.get("heated", {}).get("iF_per_mille", {}).get("bz", {}).get(k)
        u = res.get("unheated", {}).get("iF_per_mille", {}).get("bz", {}).get(k)
        wm = res.get("heated", {}).get("well_mixed", {}).get(k)
        row = {}
        if h is not None and u:
            row["heated_over_unheated"] = {"cfd": h / u, "measured": MEASURED["heated"][k] / MEASURED["unheated"][k]}
        if h is not None and wm and k in MEASURED["well_mixed"]:
            row["heated_over_well_mixed"] = {"cfd": h / wm, "measured": MEASURED["heated"][k] / MEASURED["well_mixed"][k]}
        for r in row.values():
            r["cfd_over_measured"] = r["cfd"] / r["measured"]
            r["within_1.5"] = bool(1 / 1.5 <= r["cfd_over_measured"] <= 1.5)
        if row:
            checks[k] = row
    out = {"measured": MEASURED, "runs": res, "checks": checks}
    (runs / "licina2017_result.json").write_text(json.dumps(out, indent=1))
    for mode, r in res.items():
        print(mode, "bz", {k: round(v, 2) for k, v in r["iF_per_mille"]["bz"].items()},
              "room", {k: round(v, 2) for k, v in r["iF_per_mille"]["room_mean"].items()},
              "well mixed", {k: round(v, 2) for k, v in r["well_mixed"].items()})
    for k, row in checks.items():
        print(k, {n: (round(r["cfd"], 2), r["measured"], r["within_1.5"]) for n, r in row.items()})


if __name__ == "__main__":
    main(Path(sys.argv[1]))
