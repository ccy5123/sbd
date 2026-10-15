"""Fig. 12 — world map of documentary evidence for the Silencer conjecture (Equal Earth projection).

Each country takes the strongest evidence level among its surveyed languages (culture/cross_cultural_table.csv).
Historical languages (Latin, Old Norse, Ancient Greek, Sanskrit, PIE) are not mapped.
Boundaries: Natural Earth 1:110m admin-0 (public domain).
Run from repo root:  python3 culture/make_map.py
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch, Polygon

ROOT = Path(__file__).resolve().parents[1]
SPANISH = "ESP MEX COL ARG PER VEN CHL ECU GTM CUB BOL DOM HND PRY SLV NIC CRI PAN URY".split()
ARABIC = "SAU EGY IRQ SYR JOR LBN YEM OMN ARE QAT KWT LBY TUN DZA MAR SDN MRT PSX".split()

# language: (level, countries). Levels: A = traditional saying, Am = media/fiction only, B, C, D
LANGUAGES = {
    "Mandarin": ("A", ["CHN", "TWN"]), "English": ("A", ["GBR", "USA", "CAN", "AUS", "NZL", "IRL"]),
    "Hindi (film) / Hindi-Urdu": ("Am", ["IND"]), "Urdu": ("C", ["PAK"]),
    "Korean (media)": ("Am", ["KOR"]), "Indonesian (media)": ("Am", ["IDN"]), "Malay (media)": ("Am", ["MYS", "BRN"]),
    "Russian": ("B", ["RUS", "BLR"]), "French": ("B", ["FRA", "BEL", "CHE", "LUX"]),
    "Persian": ("B", ["IRN", "AFG", "TJK"]),
    "Dutch (dialect)": ("C", ["NLD", "BEL"]), "German": ("C", ["DEU", "AUT", "CHE"]), "Spanish": ("C", SPANISH),
    "Portuguese": ("C", ["PRT", "BRA", "AGO", "MOZ"]), "Italian": ("C", ["ITA"]), "Polish": ("C", ["POL"]),
    "Arabic": ("C", ARABIC), "Japanese": ("C", ["JPN"]), "Finnish": ("C", ["FIN"]),
    # Serbo-Croatian is B only etymologically (*pьzděti 'fart' -> 'stink'); no current silent-fart word -> D on the map
    "Serbo-Croatian": ("D", ["HRV", "SRB", "BIH", "MNE"]), "Czech": ("D", ["CZE"]), "Ukrainian": ("D", ["UKR"]),
    "Lithuanian": ("D", ["LTU"]), "Turkish": ("D", ["TUR"]), "Vietnamese": ("D", ["VNM"]), "Thai": ("D", ["THA"]),
    "Hebrew": ("D", ["ISR"]), "Swahili": ("D", ["TZA", "KEN"]), "Korean (DPRK)": ("D", ["PRK"]),
}
RANK = {"A": 5, "Am": 4, "B": 3, "C": 2, "D": 1}
STYLE = {  # ordinal blue ramp (reference palette steps 700/550/400/250) + neutrals
    "A": ("#0d366b", "A · traditional saying: silent ⇒ smellier"),
    "Am": ("#1c5cab", "A · media or film only"),
    "B": ("#3987e5", "B · silent-fart word defined by its smell"),
    "C": ("#86b6ef", "C · silent-fart word, no smell claim"),
    "D": ("#c3c2b7", "D · surveyed, nothing found"),
    None: ("#f0efec", "not surveyed"),
}


def equal_earth(lon, lat):
    A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
    lam, phi = np.radians(lon), np.radians(lat)
    th = np.arcsin(np.sqrt(3) / 2 * np.sin(phi))
    x = 2 * np.sqrt(3) * lam * np.cos(th) / (3 * (9 * A4 * th**8 + 7 * A3 * th**6 + 3 * A2 * th**2 + A1))
    y = A4 * th**9 + A3 * th**7 + A2 * th**3 + A1 * th
    return x, y


def main():
    level = {}
    for lv, isos in LANGUAGES.values():
        for iso in isos:
            if iso not in level or RANK[lv] > RANK[level[iso]]:
                level[iso] = lv
    geo = json.loads((ROOT / "culture/data/ne_110m_admin_0_countries.geojson").read_text())
    fig, ax = plt.subplots(figsize=(11, 5.6))
    fig.patch.set_facecolor("#fcfcfb")
    for f in geo["features"]:
        iso = f["properties"]["ADM0_A3"]
        if iso == "ATA":
            continue
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        color = STYLE[level.get(iso)][0]
        for poly in polys:
            ring = np.asarray(poly[0])
            x, y = equal_earth(ring[:, 0], ring[:, 1])
            ax.add_patch(Polygon(np.c_[x, y], closed=True, fc=color, ec="#fcfcfb", lw=0.4))
    lon = np.r_[np.full(50, -180), np.linspace(-180, 180, 50), np.full(50, 180), np.linspace(180, -180, 50)]
    lat = np.r_[np.linspace(-60, 85, 50), np.full(50, 85), np.linspace(85, -60, 50), np.full(50, -60)]
    bx, by = equal_earth(lon, lat)
    ax.set_xlim(bx.min(), bx.max()); ax.set_ylim(by.min(), by.max())
    ax.set_aspect("equal"); ax.axis("off")
    counts = {k: sum(1 for v in level.values() if v == k) for k in RANK}
    handles = [Patch(fc=STYLE[k][0], ec="none", label=f"{STYLE[k][1]}  ({counts[k]})") for k in ("A", "Am", "B", "C", "D")]
    handles.append(Patch(fc=STYLE[None][0], ec="#c3c2b7", lw=0.5, label=STYLE[None][1]))
    ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=8, title="Strongest evidence (countries)",
              title_fontsize=8.5, bbox_to_anchor=(0.0, 0.0))
    ax.set_title("The Silencer conjecture across the world's lexicons", loc="left", fontsize=11, fontweight="bold",
                 color="#0b0b0b")
    fig.text(0.01, 0.015, "Documentary presence ≠ prevalence. Each country takes the strongest level among its "
             "surveyed languages; historical languages (Latin, Old Norse, Ancient Greek, Sanskrit) not mapped. "
             "Boundaries: Natural Earth 1:110m.", fontsize=7, color="#52514e")
    out = ROOT / "figures" / "fig12_culture_map.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print("wrote", out, counts)


if __name__ == "__main__":
    main()
