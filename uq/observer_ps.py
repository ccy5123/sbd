"""Base rate p_S for realistic observers: the M7 memory layer with literature odour thresholds and observer spread.

The Gate 0 neighbour receptor puts the puff centre on the nose, and the OAV uses Nagata 2003 thresholds (a trained
triangle-bag panel), so its p_S = 0.93 is an upper bound. Here the same 20 000 passages (perception/run_selection.py)
are seen by an untrained observer:
  * thresholds scaled to population values (params thr_scale_typ: Amoore & Hautala 1983, Wilby 1969);
  * per-passage detection probability Phi(log2(OAV) / sd), sd in binary steps (Amoore & Hautala 1983; Stevens et al.
    1988 show the spread applies within a person from moment to moment);
  * a distracted observer needs 26x the threshold for 50 % detection, sd 3.5 binary steps (Amoore & Hautala 1983 from
    Whisman et al. 1978); 'distracted' is the everyday state of a bystander who is not expecting an odour;
  * clothing removes 22 % of sulfide gas (Ohge et al. 2005, ordinary garments, 30 s);
  * sound-cued attention: an audible passage turns the distracted bystander into an attentive one for that passage.
Distraction changes noticing, not sensory magnitude (Forster & Spence 2018; Ashkenazi & Marks 2004), so perceived
intensity always uses the attentive OAV; only the detection probability depends on the observer state.
Routing by posture and furniture (M4 CFD) is still absent, so every p_S here remains an upper bound for its observer.

Usage (repo root): python3 uq/observer_ps.py -> uq/observer_ps.json
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "perception"))
import run_selection as rs
from selection import compare, noticed

P0 = rs.g0.P0
CLOTHING_PASS = 1.0 - 0.22  # Ohge et al. 2005, ordinary garments, H2S at 30 s


def observers():
    """name -> (detection OAV scale, sd in binary steps or None, sensory OAV scale, audible override or None).
    The audible override (scale, sd) applies to heard passages (sound-cued attention)."""
    s, sd = P0["thr_scale_typ"], P0["thr_sd_bs"]
    s_hi = rs.g0.P_RAW["perception"]["thr_scale_typ"]["high"]
    dist, dsd = s / P0["distracted_factor"], P0["distracted_sd_bs"]
    return {
        "Nagata thresholds, deterministic (Gate 0)": (1.0, None, 1.0, None),
        "attentive, Wilby thresholds": (s_hi, sd, s_hi, None),
        "attentive, Amoore thresholds": (s, sd, s, None),
        "distracted (everyday)": (dist, dsd, s, None),
        "distracted, clothed emitter": (dist * CLOTHING_PASS, dsd, s * CLOTHING_PASS, None),
        "distracted, sound cues attention": (dist, dsd, s, (s, sd)),
    }


def detect(o, sd):
    return (o >= 1.0).astype(float) if sd is None else norm.cdf(np.log2(np.maximum(o, 1e-300)) / sd)


def main(seed=7):
    sim = rs.simulate()
    rng = np.random.default_rng(seed)
    n = P0["n_stevens"]
    heard, oav = sim["heard_living"], sim["OAV_nb"]
    out = {"n_events": rs.N_EVENTS, "background": "living", "observers": {}}
    for name, (scale, sd, sense, aud) in observers().items():
        p = detect(scale * oav, sd)
        if aud is not None:
            p = np.where(heard, detect(aud[0] * oav, aud[1]), p)
        smelled = rng.random(oav.size) < p
        intensity = np.where(smelled, (sense * oav) ** n, 0.0)
        mem = compare(~heard, intensity, smelled, noticed(heard, smelled, "bystander"))
        truth = compare(~heard, intensity, smelled, np.ones_like(smelled))
        out["observers"][name] = {"OAV_scale": scale, "sd_binary_steps": sd, "audible_override": aud,
                                  "p_S": float(p.mean()), "P_smelled_heard": float(smelled[heard].mean()),
                                  "P_smelled_silent": float(smelled[~heard].mean()),
                                  "belief_memory": mem["P_belief"], "truth": truth["P_belief"]}
        print(f"{name:44s} p_S {p.mean():.3f}  P(S|heard) {smelled[heard].mean():.2f}  "
              f"P(S|silent) {smelled[~heard].mean():.2f}  belief {mem['P_belief']:.3f}  truth {truth['P_belief']:.3f}")
    (ROOT / "uq/observer_ps.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
