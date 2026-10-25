"""Routing map (A1 of manuscript/preprint/interface_plan.md section 9): worst-breath OAV at each nose against the
momentum-flux ratio Pi = M0 / m_p of the release and the body's convective boundary layer where it enters.

M0 = Q0 u0 is the release's kinematic momentum flux (cfd/results_v4/<case>.json); m_p is the upward momentum flux of
the boundary layer DZ_REF above the release point (cfd/results_v4/plume_flux.json, plume_flux.py). Doses are at
equal mass (92 mL), over the first 150 s, so the map shows the flow path, not passage size. A Richardson-type number
Ri_p = B_p Q_p / m_p^2 of the boundary layer is listed as a secondary descriptor.
Figure in FIGSTYLE v1.2 (paper, double column): one line per scene through its four releases (S50, S90, A50, A90 in
order of Pi); colour = posture (sofa, standing), marker = scene, solid / filled = bare, dashed / open = trousers.
Writes figures/routing_map_paper.svg/.png and cfd/results_v4/routing_map.json.
Usage (figure venv, see HANDOFF): /root/figenv/bin/python cfd/postprocess/routing_map.py
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from figstyle import *  # noqa: E402,F401,F403  (FIGSTYLE v1.2, verbatim)

RES = ROOT / "cfd/results_v4"
DZ_REF = "0.15"  # m above the release point
COLOR_MAP = {"sofa": PALETTE[0], "standing": PALETTE[1]}
SCENES = {  # name in plume_flux.json -> (result file, label, marker, posture, bare)
    "sofa": ("sofa_v4_multi", "Sofa, upright", MARKERS[0], "sofa", True),
    "sofa_rec4.5": ("sofa_rec4.5_v4_multi", "Sofa, reclined 4.5°", MARKERS[1], "sofa", True),
    "sofa_rec-10": ("sofa_rec-10_v4_multi", "Sofa, leaning forward 10°", MARKERS[3], "sofa", True),
    "sofa_tr": ("sofa_tr_v4_multi", "Sofa, upright, trousers", MARKERS[0], "sofa", False),
    "stand_still": ("stand_still_v4_multi", "Standing, still air", MARKERS[2], "standing", True),
    "stand_vent": ("stand_vent_v4_multi", "Standing, ventilated", MARKERS[4], "standing", True),
    "stand_still_tr": ("stand_still_tr_v4_multi", "Standing, still air, trousers", MARKERS[2], "standing", False),
    "stand_vent_tr": ("stand_vent_tr_v4_multi", "Standing, ventilated, trousers", MARKERS[4], "standing", False),
}
FLOOR = 1e-4  # plotting floor for OAV


def figure(rows):
    apply_style("paper")
    fig, axes = new_figure("double", aspect=0.5, ncols=2, sharex=True)
    pi_label = var(r"\Pi") + " = " + var("M", "0") + "/" + var("m", "p")
    for ax, nose, who in zip(axes, ("neighbour", "releaser"), ("neighbour", "releaser")):
        for name, (_, label, mk, posture, bare) in SCENES.items():
            pts = sorted((r["Pi"], max(r[nose], FLOOR)) for r in rows if r["scene"] == name)
            if not pts:
                continue
            col = COLOR_MAP[posture]
            ax.plot(*zip(*pts), color=col, marker=mk, ls=LINESTYLES[0] if bare else LINESTYLES[1], label=label,
                    markerfacecolor=col if bare else "white", markeredgecolor=col)
        for y in (1, 20):
            ax.axhline(y, color=MUTED, lw=0.6, ls=LINESTYLES[3], zorder=0)
        ax.axvline(1, color=MUTED, lw=0.6, ls=LINESTYLES[3], zorder=0)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_ylim(FLOOR * 0.7, 300)
        ax.set_xlabel(axis_label("Momentum-flux ratio " + pi_label))
        ax.set_ylabel(axis_label(f"Worst-breath OAV at the {who}"))
    for ax in axes:  # reference lines: OAV 1 (trained panel), OAV 20 (attentive observer, 50 %)
        left = ax.get_yaxis_transform()  # x in axes fraction, y in data: labels at the empty left edge
        ax.text(0.02, 1.25, "OAV 1", transform=left, ha="left", va="bottom", color=MUTED)
        ax.text(0.02, 25, "OAV 20", transform=left, ha="left", va="bottom", color=MUTED)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=4)
    panel_labels(axes)
    return save_figure(fig, "routing_map_paper", outdir=ROOT / "figures")


def main():
    flux = json.loads((RES / "plume_flux.json").read_text())["cases"]
    rows = []
    for name, (res, label, mk, posture, bare) in SCENES.items():
        f = RES / f"{res}.json"
        if not f.exists() or name not in flux:
            continue
        p = flux[name]["planes"][DZ_REF]
        ri = p["B_p"] * p["Q_p"] / p["m_p"] ** 2
        for k, r in json.loads(f.read_text())["releases"].items():
            w = {n: r[n]["by_window"]["150"]["worst_breath_OAV_mean_at_V0"] for n in ("releaser", "neighbour")}
            rows.append({"scene": name, "label": label, "release": k, "M0": r["M0"], "m_p": p["m_p"],
                         "Pi": r["M0"] / p["m_p"], "Ri_p": ri, "releaser": w["releaser"], "neighbour": w["neighbour"],
                         "bare": bare})
    out = figure(rows)
    (RES / "routing_map.json").write_text(json.dumps({"DZ_REF": DZ_REF, "rows": rows}, indent=1))
    for r in rows:
        print(f"{r['scene']:15s} {r['release']}  Pi {r['Pi']:9.3g}  nb {r['neighbour']:9.3g}  rel {r['releaser']:9.3g}  Ri_p {r['Ri_p']:.3g}")
    print("wrote", *out)


if __name__ == "__main__":
    main()
