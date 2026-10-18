"""Physics and memory on one population: four outcomes per silent-audible pair, scene by scene (HANDOFF item 1).

Before this, the physics headline (uq/routing_headline.py: CFD routes, paired draws, class = sphincter oscillation, no
sulfur spread) and the memory result (uq/observer_ps.py: Gate 0 receptor with the puff centred on the nose, class =
heard, sulfur spread, ties split) came from different passages. Here both use the same passages:
  * passages: the Theorem 3 stream of perception/run_selection.simulate (Gate 0 priors, one passage at a time, natural
    silent/audible mix, log-normal sulfur multiplier m);
  * route: OAV = m x (V / V0) x OAV_CFD(scene, nose, route), route = audible if the sphincter oscillates, else silent
    (the CFD equal-mass result, linear in the released amount; [APPROXIMATION] route independent of V, as in
    routing_headline.py);
  * class as the nose's owner perceives it: a bystander classes a passage audible iff it is heard at that nose's
    distance from the release point (acoustics/regime.classify, living-room background); the releaser feels the
    oscillation, so the culprit's class is the oscillation itself;
  * detection: p = Phi(log2(s x OAV) / sd) per observer (uq/observer_ps.py); smelling events independent.
For a silent passage i and an audible passage j at the same nose, with p_i, p_j and A_i, A_j (OAV), J = 1 + Weber:
    none           (1 - p_i)(1 - p_j)
    silent worse   p_i (1 - p_j) + p_i p_j 1(A_i > J A_j)
    audible worse  (1 - p_i) p_j + p_i p_j 1(A_j > J A_i)
    JND tie        p_i p_j 1(neither)
Physics ('as emitted'): the mean over all pairs. Memory (Theorem 3): a bystander keeps a passage iff heard or smelled,
so a silent passage enters only if smelled and an audible one always; the remembered-pair shares are the terms with
S_i, divided by E[p_i] (none = 0). The releaser keeps every passage, so for the culprit memory = physics. No outcome
is split. The expectations over smelling are exact (no Bernoulli draws); pair sums use sorting, O(N log N).

Aggregates (until item 3 sets the scene weights): equal weight per (scene, nose), sofa 120 s run excluded, as in
routing_headline.py. Physics shares are averaged; memory shares are pooled (sum of remembered-pair mass over noses,
then normalised), since one memory collects passages from every scene.
Usage (repo root): python3 uq/four_outcomes.py -> uq/four_outcomes.json
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "uq"))
sys.path.insert(0, str(ROOT / "perception"))
sys.path.insert(0, str(ROOT / "cfd/geometry"))
import routing_headline as rh
import run_selection as rs
from observer_ps import detect, observers

OUTCOMES = ("none", "silent_worse", "audible_worse", "tie")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def nose_distances():
    """(scene, role) -> straight-line distance (m) from the CFD release point to that nose probe."""
    import manikin
    sofa = _load("sofa_case", "cfd/cases/sofa/make_case.py")
    el = _load("elevator_case", "cfd/cases/elevator/make_case.py")
    st = _load("standing_case", "cfd/cases/standing/make_case.py")
    dist = lambda a, b: round(float(np.linalg.norm(np.asarray(a) - np.asarray(b))), 3)
    out = {}
    rel = sofa.REL
    for scene, rec in (("sofa, upright", 0.0), ("sofa, reclined 4.5 deg", 4.5), ("sofa, leaning forward 10 deg", -10.0),
                       ("sofa, upright (120 s)", 0.0)):
        nf = manikin.nose_tip(rec)
        out[scene, "culprit"] = dist((nf[0] + sofa.NOSE_X - manikin.NOSE[0], sofa.DY_F, nf[2]), rel)
        out[scene, "beside"] = dist((sofa.NOSE_X, sofa.DY_N, sofa.NOSE_Z), rel)
    roles = {"FL": {"FL": "culprit", "FR": "beside", "BL": "behind", "BR": "diagonal behind"},
             "BL": {"BL": "culprit", "BR": "beside", "FL": "in front", "FR": "diagonal in front"}}
    for c, scene in (("FL", "elevator, front row (person behind)"), ("BL", "elevator, back row (wall behind)")):
        for n, role in roles[c].items():
            out[scene, role] = dist(el.nose_probe(n), el.rel_point(c))
    for scene in ("standing pair, still air", "standing pair, office ventilation"):
        for n, role in (("C", "culprit"), ("N", "facing")):
            out[scene, role] = dist(st.nose_probe(n), st.rel_point())
    return out


def _mass_above(a, b, w_b, factor):
    """For each a_i: sum of w_b over b_j with a_i > factor * b_j."""
    order = np.argsort(b)
    bs, cw = b[order] * factor, np.concatenate(([0.0], np.cumsum(w_b[order])))
    return cw[np.searchsorted(bs, a, side="left")]


def pair_terms(a_s, p_s, a_l, p_l, J):
    """Mean over all silent x audible pairs of p_i(1-p_j), (1-p_i)p_j, p_i p_j 1(A_i > J A_j), p_i p_j 1(A_j > J A_i)."""
    ns, nl = a_s.size, a_l.size
    if ns == 0 or nl == 0:
        return None
    Ps, Pl = p_s.mean(), p_l.mean()
    s_gt = float(np.sum(p_s * _mass_above(a_s, a_l, p_l, J))) / (ns * nl)
    l_gt = float(np.sum(p_l * _mass_above(a_l, a_s, p_s, J))) / (ns * nl)
    return {"pi_s": float(Ps), "pi_l": float(Pl), "only_s": float(Ps * (1 - Pl)), "only_l": float((1 - Ps) * Pl),
            "both": float(Ps * Pl), "both_s_gt": s_gt, "both_l_gt": l_gt,
            "both_tie": max(0.0, float(Ps * Pl) - s_gt - l_gt)}  # clip round-off when both are ~0


def physics(t):
    tie = t["both_tie"]
    return {"none": (1 - t["pi_s"]) * (1 - t["pi_l"]), "silent_worse": t["only_s"] + t["both_s_gt"],
            "audible_worse": t["only_l"] + t["both_l_gt"], "tie": tie}


def memory_mass(t, role):
    """Unnormalised remembered-pair mass per outcome and its total (Theorem 3 filter)."""
    if role == "culprit":
        return {**physics(t), "_total": 1.0}
    return {"none": 0.0, "silent_worse": t["only_s"] + t["both_s_gt"], "audible_worse": t["both_l_gt"],
            "tie": t["both_tie"],
            "_total": t["pi_s"]}


def main():
    dists = nose_distances()
    sim = rs.simulate(distances=sorted(set(dists.values())))
    V0, J = rh.V0, rh.JND
    base = sim["sulfur"] * sim["V"] / V0
    osc = sim["osc"].astype(bool)
    obs = observers()
    out = {"n_events": int(base.size), "JND": J, "observers": list(rh.OBS), "rows": []}
    for scene, role, win, o_s, o_l in rh.scenes():
        A = base * np.where(osc, o_l, o_s)
        r = dists[scene, role]
        audible = osc if role == "culprit" else sim[f"heard_living@{r:.3f}"].astype(bool)
        row = {"scene": scene, "nose": role, "window_s": win, "distance_m": r,
               "frac_audible": float(audible.mean()), "frac_osc": float(osc.mean()), "by_observer": {}}
        for name in rh.OBS:
            scale, sd = obs[name][0], obs[name][1]
            p = detect(scale * A, sd)
            t = pair_terms(A[~audible], p[~audible], A[audible], p[audible], J)
            mm = memory_mass(t, role)
            row["by_observer"][name] = {"terms": t, "physics": physics(t),
                                        "memory": {k: mm[k] / mm["_total"] for k in OUTCOMES},
                                        "memory_mass": mm}
        out["rows"].append(row)
    for grp, keep in (("bystanders", lambda s: s["nose"] != "culprit"), ("culprit", lambda s: s["nose"] == "culprit")):
        rows = [s for s in out["rows"] if keep(s) and "120 s" not in s["scene"]]
        summ = {"n": len(rows)}
        for name in rh.OBS:
            g = [s["by_observer"][name] for s in rows]
            ph = {k: float(np.mean([x["physics"][k] for x in g])) for k in OUTCOMES}
            tot = sum(x["memory_mass"]["_total"] for x in g)
            me = {k: sum(x["memory_mass"][k] for x in g) / tot for k in OUTCOMES}
            pis = [float(np.mean([x["terms"][k] for x in g])) for k in ("pi_s", "pi_l")]
            summ[name] = {"physics": ph, "memory": me, "pi_s": pis[0], "pi_l": pis[1]}
        out[f"summary_{grp}"] = summ
    (ROOT / "uq/four_outcomes.json").write_text(json.dumps(out, indent=1))
    pct = lambda d: " / ".join(f"{100 * d[k]:5.1f}" for k in OUTCOMES)
    print("rows: none / silent worse / audible worse / tie (%), physics | memory")
    for s in out["rows"]:
        for name in rh.OBS:
            x = s["by_observer"][name]
            print(f"{s['scene'][:34]:34s} {s['nose'][:16]:16s} {s['distance_m']:.2f} m heard {s['frac_audible']:.2f} "
                  f"{name[:10]:10s} {pct(x['physics'])} | {pct(x['memory'])}")
    for grp in ("bystanders", "culprit"):
        for name in rh.OBS:
            x = out[f"summary_{grp}"][name]
            print(f"{grp:10s} {name[:10]:10s} physics {pct(x['physics'])} | memory {pct(x['memory'])}"
                  f"   pi_s {x['pi_s']:.3f} pi_l {x['pi_l']:.3f}")


if __name__ == "__main__":
    main()
