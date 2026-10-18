"""DRAFT (2026-10-18 headline review), not part of the pipeline. Run from the repo root: python3 uq/drafts/headline_defs.py"""
from pathlib import Path
ROOT = str(Path(__file__).resolve().parents[2])
import sys, numpy as np
sys.path.insert(0, ROOT + "/uq"); sys.path.insert(0, ROOT + "/gate0")
import routing_headline as rh
from observer_ps import detect, observers
mc = rh.g0.monte_carlo(); vs, vl = mc["V_s"], mc["V_l"]; obs = observers()
J = np.log10(rh.JND)
rows = {}
for scene, role, win, o_s, o_l in rh.scenes():
    if "120 s" in scene: continue
    a_s, a_l = o_s*vs/rh.V0, o_l*vl/rh.V0
    for name in rh.OBS:
        sc, sd = obs[name][0], obs[name][1]
        ps, pl = detect(sc*a_s, sd), detect(sc*a_l, sd)
        with np.errstate(divide="ignore", invalid="ignore"):
            lr = np.log10(np.maximum(a_s,1e-300)) - np.log10(np.maximum(a_l,1e-300))
        both = ps*pl
        r = dict(ps=ps.mean(), pl=pl.mean(),
                 none=((1-ps)*(1-pl)).mean(),
                 only_s=(ps*(1-pl)).mean(), only_l=((1-ps)*pl).mean(),
                 both_s=(both*(lr>J)).mean(), both_eq=(both*(abs(lr)<=J)).mean(), both_l=(both*(lr<-J)).mean())
        rows.setdefault(name, {}).setdefault("culprit" if role=="culprit" else "bystander", []).append((scene, role, r))
for name, g in rows.items():
    for grp, L in g.items():
        m = {k: np.mean([r[k] for _,_,r in L]) for k in L[0][2]}
        print(f"{name[:10]} {grp:9s} n={len(L)}  pi_s {m['ps']:.3f} pi_l {m['pl']:.3f} ratio {m['ps']/m['pl']:.2f} | "
              f"none {m['none']:.3f} only_s {m['only_s']:.3f} only_l {m['only_l']:.3f} both:s>{m['both_s']:.3f} ~{m['both_eq']:.3f} l>{m['both_l']:.3f}"
              f" | silent-deadlier {m['only_s']+m['both_s']:.3f} audible-deadlier {m['only_l']+m['both_l']:.3f}")
        print("   per-scene pi_s/pi_l:", ", ".join(f"{s.split(',')[0][:8]}{s.split(',')[1][:8] if ',' in s else ''}/{ro[:6]} {r['ps']:.3f}/{r['pl']:.3f}" for s,ro,r in L))
