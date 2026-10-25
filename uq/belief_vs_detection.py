"""Remembered belief against detection rate on the v4 population (robustness analyses, HANDOFF next task 1).

Answers "the 91.5 % is tautological": under the Theorem 3 filter a silent passage is remembered only if smelled, so
one might think the remembered silent-worse share is high by construction. It is not fixed: it is a function of how
often passages are smelled, and it falls to the truth when every passage is smelled. The observer's 50 % detection
point m50 (OAV) is swept over 1e-5-1e4 (far below any real observer at the low end, to reach full detection) at the attentive and distracted spreads (sd 2 and 3.5 binary steps), with the
v4 routes and passages of uq/four_outcomes_v4 (bystanders, bare, 600 s, frequency-weighted central case). For each
point:
  * x: share of passages smelled at a bystander nose, (1 - f_heard) pi_s + f_heard pi_l per nose, scene-weighted;
  * memory: remembered silent-worse share (Theorem 3 filter, uq/four_outcomes.memory_mass);
  * truth: physics silent-worse share among all pairs, and among the pairs where anyone smells anything
    (silent worse / (1 - none));
  * releaser for contrast: the releaser keeps every passage, so memory = truth; shown among smelled pairs.
Baseline observers sit at m50 = 20 (attentive, Amoore) and 520 (distracted). This replaces the basis of the old
Figure 13 (Gate 0 receptor).
Figure in FIGSTYLE v1.2 (paper, double column).
Usage (repo root, figure venv, see HANDOFF): /root/figenv/bin/python uq/belief_vs_detection.py
  -> uq/belief_vs_detection.json, figures/belief_vs_detection_paper.svg/.png
"""
import json
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from figstyle import *  # noqa: E402,F401,F403  (FIGSTYLE v1.2, verbatim)

sys.path.insert(0, str(ROOT / "uq"))
import four_outcomes_v4 as fv  # noqa: E402
from tail_sensitivity import probit  # noqa: E402

ATT, DIS = fv.rh.OBS
SD = {ATT: fv.observers()[ATT][1], DIS: fv.observers()[DIS][1]}
M50_BASE = {ATT: 1.0 / fv.observers()[ATT][0], DIS: 1.0 / fv.observers()[DIS][0]}
M50 = np.logspace(-5, 4, 46)  # down to 1e-5: the bystander OAVs are small, so near-full detection needs m50 << 1
TAG = "frequency, central"


def smelled_share(out, name, cloth="bare", win=600, culprit=False):
    """Share of passages smelled at the group's noses, rows averaged within a scene, scenes frequency-weighted."""
    w = fv.frequency_weights()[TAG]
    rows = [s for s in out["rows"] if s["clothing"] == cloth and s["window_s"] == win
            and (s["nose"] == "culprit") == culprit]
    num = den = 0.0
    for sc, wt in w.items():
        g = [s for s in rows if fv.fo.scene_of(s) == sc]
        if g:
            t = [s["by_observer"][name]["terms"] for s in g]
            num += wt * np.mean([(1 - s["frac_audible"]) * x["pi_s"] + s["frac_audible"] * x["pi_l"] for s, x in zip(g, t)])
            den += wt
    return num / den


def point(out, name):
    by, cu = out["summary_bare_600s_bystanders"][TAG][name], out["summary_bare_600s_culprit"][TAG][name]
    among = lambda ph: ph["silent_worse"] / (1 - ph["none"]) if ph["none"] < 1 - 1e-12 else None
    return {"smelled_bystander": smelled_share(out, name), "smelled_releaser": smelled_share(out, name, culprit=True),
            "memory_silent_worse": by["memory"]["silent_worse"] if by["memory"] else None,
            "truth_silent_worse": by["physics"]["silent_worse"], "truth_among_smelled": among(by["physics"]),
            "releaser_among_smelled": among(cu["physics"]), "releaser_silent_worse": cu["physics"]["silent_worse"]}


SERIES = (  # (key, x key, label); colour, marker and line style follow the index (FIGSTYLE v1.2)
    ("memory_silent_worse", "smelled_bystander", "Bystander, remembered"),
    ("truth_among_smelled", "smelled_bystander", "Bystander, truth (pairs where anything is smelled)"),
    ("truth_silent_worse", "smelled_bystander", "Bystander, truth (all pairs)"),
    ("releaser_among_smelled", "smelled_releaser", "Releaser (remembers all), pairs where anything is smelled"),
)


def figure(res):
    apply_style("paper")
    fig, axes = new_figure("double", aspect=0.42, ncols=2, sharex=True, sharey=True)
    nan = lambda v: np.nan if v is None else v
    for ax, name, who in zip(axes, (ATT, DIS), ("Attentive", "Distracted")):
        pts = res[name]["sweep"]
        for i, (key, xkey, label) in enumerate(SERIES):
            ax.plot([p[xkey] for p in pts], [nan(p[key]) for p in pts], color=PALETTE[i], ls=LINESTYLES[i],
                    marker=MARKERS[i], markevery=(i, 5), label=label)
        xb = res[name]["baseline"]["smelled_bystander"]
        ax.axvline(xb, color=MUTED, lw=0.6, ls=LINESTYLES[3], zorder=0)
        # labels in the empty middle-left band (the remembered curve runs along the top, the truths along the bottom)
        ax.text(xb / 1.25, 0.45, f"Baseline\n(50 % at OAV {M50_BASE[name]:g})", ha="right", va="center", color=MUTED)
        ax.text(0.03, 0.68, f"{who} spread\nsd {SD[name]:g} binary steps", transform=ax.transAxes,
                ha="left", va="center")
        ax.set_xscale("log")
        ax.set_xlim(1e-4, 1.5)
        ax.set_ylim(0, 1.05)
        ax.set_xlabel(axis_label("Share of passages smelled"))
    axes[0].set_ylabel(axis_label('Share judged "silent was worse"'))
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=2)
    panel_labels(axes)
    return save_figure(fig, "belief_vs_detection_paper", outdir=ROOT / "figures")


def main():
    sim = fv.passages()
    res = {"m50_OAV": M50.tolist(), "group": "bare, 600 s, frequency-weighted central", "n_events": int(sim["V"].size)}
    for name in (ATT, DIS):
        sweep = []
        for m in M50:
            out = fv.compute(sim=sim, detectors={ATT: probit(1.0 / m, SD[name]), DIS: probit(1.0 / m, SD[name])})
            sweep.append({"m50": float(m), **point(out, ATT)})
        base = fv.compute(sim=sim)
        res[name] = {"sd": SD[name], "m50_baseline": M50_BASE[name], "sweep": sweep, "baseline": point(base, name)}
        print(name)
        for p in sweep[::3] + [{"m50": M50_BASE[name], **res[name]["baseline"]}]:
            f = lambda v: "  -  " if v is None else f"{100 * v:5.1f}"
            print(f"  m50 {p['m50']:8.1f}  smelled {100 * p['smelled_bystander']:7.3f} %  memory {f(p['memory_silent_worse'])}"
                  f"  truth|smelled {f(p['truth_among_smelled'])}  truth {f(p['truth_silent_worse'])}  "
                  f"releaser|smelled {f(p['releaser_among_smelled'])} (smelled {100 * p['smelled_releaser']:5.1f} %)")
    (ROOT / "uq/belief_vs_detection.json").write_text(json.dumps(res, indent=1))
    figure(res)


if __name__ == "__main__":
    main()
