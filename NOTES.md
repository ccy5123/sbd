# NOTES — running log (assumptions, results, open issues per module)

## 2026-10-15 · Session 1 (M0, M1, M8)

### M0 — literature / parameter verification (done)
- Bibliography: all 20 seed references exist; 9 corrected. 20 more references were added in the parameter pass
  (`refs/references.yaml`, `refs/bibliography_check.md`). A few new entries still need full titles or author lists.
- Full texts read (user-supplied): Dowling & Dimotakis 1990, Hussein et al. 1994, Sangras et al. 2002 + Diez et al.
  2003 erratum, Cheng et al. 2011, Suarez et al. 1997.
- `params.yaml` is final for Gate 0: every former VERIFY is now VERIFIED, DERIVED, PARTIAL or ASSUMPTION.
- **Erratum matters:** the original Sangras 2002 penetration formulas were wrong. The Gate 0 puff phase originally
  over-stated audible-puff velocity ≈ 2.7×.
- **Plan corrections:**
  - §3.1 buoyancy is signed: CO₂-rich flatus is denser than air.
  - The I:E ratio is 1:1.4 (Wysocki 2006), not 1:2.
  - Individual passages range 17–375 mL (Suarez 1997 text, n = 87).
  - No peer-reviewed flatus sound frequency or SPL exists. f₀ is 100–300 Hz from a non-peer-reviewed source, and
    SPL is a free parameter in M2.
- PARTIAL rows to re-check before figures: ISO 226:2023 low-frequency thresholds, Lebo 1994 restaurant levels, the
  D_H2S estimate, and the ISO 7730 skin-temperature equation.
- Remaining assumptions without any source: orifice diameter, CBL velocity and thickness at pelvis level, skirt
  volume, woven-trouser permeability, flatus SPL.

### M1 — Gate 0 (done, see `gate0/gate0_report.md`)
- Key analytic result: near-field dilution D₁ ≈ β·u₀/u_h (momentum conservation), so the governing parameter is the
  **Silencer number Si = u₀,eff/u_h**, not Re.
- Monte Carlo (n = 20 000, final M0 priors): equal-mass median R = 1.35 at the own nose and 1.12 at the neighbour;
  P(R > 2) = 0.31 / 0.17. As emitted (equal concentration), median R = 0.94 / 0.75, so loud passages deliver more in
  most pairs. Trousers drive the equal-mass R → 1.0.
- **Recommended narrative branch: "Debunked (mostly) — the nose was fooled by the ears" + regime map.** The physical
  exception is own nose, bare, still air (Scenario B).
- Assumptions to carry into UQ: d, T, u_audible (placeholder for M2), u_h, u_room, K lower bound 1e-4, clothing model.
- Open: cushion adsorption (Suarez 1998: charcoal cushion absorbed > 90 % of sulfur gases) is not in Gate 0.

### M8 — cross-cultural survey (first pass done, see `culture/survey_summary.md`)
- 32 languages. A-level traditional sayings: Mandarin, Cantonese, English. B: Russian, French, Persian, historical
  English. Silent-fart lexemes are verified in 5 language families. The PIE *pesd-/*perd- soft/loud split is
  reconstructed in LIV² and Pokorny, so it is supported but needs direct handbook check.
- Fig. 12 world map done (`culture/make_map.py` → `figures/fig12_culture_map.png`; Serbo-Croatian mapped as D since its B is etymological only).
- Open: verify LIV² pp. 473/477 and Mallory & Adams 1997 directly; the Korean native
  saying is still unverified.
