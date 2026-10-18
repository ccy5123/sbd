"""DRAFT (2026-10-18 headline review), not part of the pipeline. Run from the repo root: python3 uq/drafts/headline_ties.py"""
from pathlib import Path
ROOT = str(Path(__file__).resolve().parents[2])
import sys, numpy as np
sys.path.insert(0,ROOT + "/uq"); sys.path.insert(0,ROOT + "/perception")
import run_selection as rs
from observer_ps import detect, observers
sim = rs.simulate(); heard = sim["heard_living"]; oav = sim["OAV_nb"]
n = rs.g0.P0["n_stevens"]; J = 1.28
for name in ["attentive, Amoore thresholds","distracted (everyday)"]:
    sc, sd, sense, _ = observers()[name]
    p = detect(sc*oav, sd)
    ps, pl = p[~heard], p[heard]; As, Al = oav[~heard], oav[heard]
    # all silent x audible pairs via subsample
    rng = np.random.default_rng(0); i = rng.integers(0, ps.size, 400000); j = rng.integers(0, pl.size, 400000)
    a, b = ps[i], pl[j]; r = As[i]/Al[j]
    none = ((1-a)*(1-b)).mean(); s_w = (a*(1-b) + a*b*(r>J)).mean(); l_w = ((1-a)*b + a*b*(r<1/J)).mean(); tie = (a*b*((r<=J)&(r>=1/J))).mean()
    print(f"{name[:10]}: none {none:.3f} silent> {s_w:.3f} audible> {l_w:.3f} JND-tie {tie:.3f} | half-tie PoS {s_w+0.5*(none+tie):.3f} | given any smelled {s_w/(s_w+l_w):.3f}")
