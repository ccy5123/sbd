# NOTES — running log (assumptions, results, open issues per module)

## 2026-10-15 · Session 1 (M0, M1, M8)

### M0 — literature / parameter verification (in progress)
- Bibliography: all 20 seed references exist; 9 corrected (`refs/bibliography_check.md`, `refs/references.yaml`).
- Full texts read (user-supplied): Dowling & Dimotakis 1990, Hussein et al. 1994, Sangras et al. 2002 + Diez et al.
  2003 erratum, Cheng et al. 2011, Suarez et al. 1997.
- Now VERIFIED in `params.yaml`: sulfur gases, odour thresholds, K_c = 5.11, B_u = 5.8, starting-jet C_x = 2.8,
  puff C_p = 2.6, CBL peak 0.16–0.24 m/s, indoor K 0.0019–0.013 m²/s, per-passage volume 32–207 mL,
  daily volume, passages/day, flatus buoyancy g′.
- **Erratum matters:** the original Sangras 2002 penetration formulas were wrong. Before the fix, the Gate 0 puff
  phase over-stated audible-puff velocity ≈ 2.7×, which biased the analysis towards H1.
- **Plan §3.1 refined:** flatus is positively buoyant at the median (g′ = +1.7 m/s²), but CO₂-rich flatus is denser
  than air (1/16 subjects at 37 °C, 4/16 after cooling). The heavy-gas argument stays dropped, and buoyancy is now
  treated as signed.
- Open: parameter-verification agent still running (nose heights, breathing, fabric permeability, ISO 226 thresholds,
  background noise, flatus sound frequency). Leggings/knit air permeability still has no numeric source. Denim
  (hemp/stretch, ASTM D737) is 97–253 mm/s, higher than the Gate 0 prior — **update pending**.

### M1 — Gate 0 (done, see `gate0/gate0_report.md`)
- Key analytic result: near-field dilution D₁ ≈ β·u₀/u_h (momentum conservation), so the governing parameter is the
  **Silencer number Si = u₀,eff/u_h**, not Re.
- Monte Carlo (n = 20 000): equal-mass median R = 1.18 at the own nose and 1.05 at the neighbour; P(R > 2) = 0.16 /
  0.06. Under equal concentration, R ≈ 0.9–1.0. Trousers drive R → 1.
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
