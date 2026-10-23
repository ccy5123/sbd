"""Routing map (A1 of manuscript/preprint/interface_plan.md section 9): worst-breath OAV at each nose against the
momentum-flux ratio Pi = M0 / m_p of the release and the body's convective boundary layer where it enters.

M0 = Q0 u0 is the release's kinematic momentum flux (cfd/results_v4/<case>.json); m_p is the upward momentum flux of
the boundary layer DZ_REF above the release point (cfd/results_v4/plume_flux.json, plume_flux.py). Doses are at
equal mass (92 mL), over the first 150 s, so the map shows the flow path, not passage size. A Richardson-type number
Ri_p = B_p Q_p / m_p^2 of the boundary layer is listed as a secondary descriptor.
Writes figures/fig_routing_map.png and cfd/results_v4/routing_map.json.
Usage: python3 cfd/postprocess/routing_map.py
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "cfd/results_v4"
DZ_REF = "0.15"  # m above the release point
SCENES = {  # name in plume_flux.json -> (result file, label, marker, colour, filled = bare)
    "sofa": ("sofa_v4_multi", "sofa, upright", "o", "#1f6fb2", True),
    "sofa_rec4.5": ("sofa_rec4.5_v4_multi", "sofa, reclined 4.5°", "s", "#1f6fb2", True),
    "sofa_rec-10": ("sofa_rec-10_v4_multi", "sofa, leaning forward 10°", "D", "#1f6fb2", True),
    "sofa_tr": ("sofa_tr_v4_multi", "sofa, upright, trousers", "o", "#1f6fb2", False),
    "stand_still": ("stand_still_v4_multi", "standing, still air", "^", "#c2571a", True),
    "stand_vent": ("stand_vent_v4_multi", "standing, ventilated", "v", "#c2571a", True),
    "stand_still_tr": ("stand_still_tr_v4_multi", "standing, still air, trousers", "^", "#c2571a", False),
    "stand_vent_tr": ("stand_vent_tr_v4_multi", "standing, ventilated, trousers", "v", "#c2571a", False),
}
FLOOR = 1e-4  # plotting floor for OAV


def main():
    flux = json.loads((RES / "plume_flux.json").read_text())["cases"]
    rows = []
    for name, (res, label, mk, col, filled) in SCENES.items():
        f = RES / f"{res}.json"
        if not f.exists() or name not in flux:
            continue
        p = flux[name]["planes"][DZ_REF]
        ri = p["B_p"] * p["Q_p"] / p["m_p"] ** 2
        for k, r in json.loads(f.read_text())["releases"].items():
            w = {n: r[n]["by_window"]["150"]["worst_breath_OAV_mean_at_V0"] for n in ("releaser", "neighbour")}
            rows.append({"scene": name, "label": label, "release": k, "M0": r["M0"], "m_p": p["m_p"],
                         "Pi": r["M0"] / p["m_p"], "Ri_p": ri, "releaser": w["releaser"], "neighbour": w["neighbour"],
                         "marker": mk, "colour": col, "filled": filled})
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharex=True, sharey=True)
    for ax, nose, title in zip(axes, ("neighbour", "releaser"), ("(a) neighbour's nose", "(b) releaser's own nose")):
        seen = set()
        for r in rows:
            lab = r["label"] if r["label"] not in seen else None
            seen.add(r["label"])
            ax.scatter(r["Pi"], max(r[nose], FLOOR), marker=r["marker"], s=46, label=lab,
                       facecolors=r["colour"] if r["filled"] else "none", edgecolors=r["colour"], linewidths=1.3)
            ax.annotate(r["release"], (r["Pi"], max(r[nose], FLOOR)), textcoords="offset points", xytext=(4, 3),
                        fontsize=7, color="#555555")
        for y, txt in ((1, "OAV 1 (trained panel)"), (20, "OAV 20 (attentive, 50 %)")):
            ax.axhline(y, color="#999999", lw=0.8, ls="--")
            ax.text(1.2e-2, y * 1.15, txt, fontsize=7, color="#666666")
        ax.axvline(1, color="#bbbbbb", lw=0.8, ls=":")
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlabel(r"momentum-flux ratio $\Pi = M_0 / m_p$")
        ax.set_title(title, fontsize=10, loc="left")
    axes[0].set_ylabel("worst-breath OAV in 150 s, 92 mL released")
    axes[0].set_ylim(FLOOR * 0.7, 300)
    axes[1].legend(fontsize=7, loc="lower right", frameon=False)
    fig.tight_layout()
    out = ROOT / "figures/fig_routing_map.png"
    fig.savefig(out, dpi=200)
    (RES / "routing_map.json").write_text(json.dumps({"DZ_REF": DZ_REF, "rows": [
        {k: v for k, v in r.items() if k not in ("marker", "colour", "filled")} for r in rows]}, indent=1))
    for r in rows:
        print(f"{r['scene']:15s} {r['release']}  Pi {r['Pi']:9.3g}  nb {r['neighbour']:9.3g}  rel {r['releaser']:9.3g}  Ri_p {r['Ri_p']:.3g}")
    print("wrote", out)


if __name__ == "__main__":
    main()
