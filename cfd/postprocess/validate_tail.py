"""Check of the well-mixed tail of analyze_multi.py against the coupled 10-minute reference runs (sofa upright, 92 mL,
silent and audible; cfd/cases/sofa/run_sofa.sh with T_END=600, release at 0.2 s).

The tail predicts each nose's worst-breath OAV over 300 and 600 s from the first 150 s only. The prediction is compared
with the worst breath the run actually gives over the same window (or over what it has reached so far, marked
'partial'). Acceptance (PLAN v4, as E0-5): within a factor 1.5.
Writes cfd/postprocess/tail_validation.json.
Usage: python3 cfd/postprocess/validate_tail.py [runs_dir]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_multi as am

V_REF, T_REL = 9.2e-5, 0.2
NOSES = ("releaser", "neighbour")
FACTOR = 1.5


def check(case: Path):
    t, s = am.an.read_probe(case)
    v_room, lam = am.room(case)
    early = t <= T_REL + am.LATE[1] + 1e-9
    out = {"reached_s": float(t[-1] - T_REL)}
    if out["reached_s"] < am.LATE[1] - 0.5:
        return out  # the tail needs the first 150 s
    for j, nose in enumerate(NOSES):
        pred = am.release_metrics(t[early], s[early, j], T_REL, V_REF, v_room, lam)
        rows = {}
        for W in am.TAIL_WINDOWS:
            m = t <= T_REL + W + 1e-9
            actual_mean, actual_max = am.worst_breath(t[m], s[m, j])
            p = pred["by_window"][f"{W:g}"]
            ratio = p["worst_breath_OAV_mean"] / actual_mean if actual_mean > 0 else None
            rows[f"{W:g}"] = {"predicted_OAV_mean": p["worst_breath_OAV_mean"], "actual_OAV_mean": actual_mean,
                              "predicted_OAV_max": p["worst_breath_OAV_max"], "actual_OAV_max": actual_max,
                              "ratio_mean": ratio, "partial": bool(t[-1] - T_REL < W - 0.5),
                              "pass": bool(ratio is not None and 1 / FACTOR <= ratio <= FACTOR)}
        out[nose] = {"tail": pred["tail"], "windows": rows}
    return out


def main(runs: Path):
    res = {}
    for mode in ("silent", "audible"):
        case = runs / f"sofa_{mode}"
        if not (case / "postProcessing/noses").exists():
            print("missing", case)
            continue
        res[mode] = check(case)
        if "releaser" not in res[mode]:
            print(f"{mode}: run at {res[mode]['reached_s']:.0f} s, needs {am.LATE[1]:g} s")
            continue
        for nose in NOSES:
            r = res[mode][nose]
            for w, x in r["windows"].items():
                print(f"{mode:7s} {nose:9s} {w:>3s} s{' (partial, run at %.0f s)' % res[mode]['reached_s'] if x['partial'] else ''}: "
                      f"predicted {x['predicted_OAV_mean']:.3g}, actual {x['actual_OAV_mean']:.3g}, "
                      f"ratio {x['ratio_mean'] or float('nan'):.2f}  {'pass' if x['pass'] else 'FAIL'}"
                      f"   f {r['tail']['f_mean']:.2f}, late rising {r['tail']['late_rising']}")
    (Path(__file__).resolve().parent / "tail_validation.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="?", default=str(am.ROOT / "cfd/runs"))
    main(Path(ap.parse_args().runs))
