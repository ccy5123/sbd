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

## 2026-10-15 · Session 1, part 2 (narrative confirmed; M2, M3)

- **Narrative branch confirmed by the owner:** "Debunked (mostly) — the nose was fooled by the ears", with a regime map.

### M2 — acoustics (done, see `acoustics/m2_report.md`)
- Model chain:
  - onset when Δp = ½ρ(u₀/C_d)² > P_th (lip-reed / vocal-fold analogue);
  - harmonic monopole radiation into a half space;
  - ISO 226 audibility;
  - critical-ratio masking.
- Verified anchors:
  - phonation threshold pressure 0.2–0.5 kPa;
  - brass lips p₀ = K·f with K = 4–8 Pa/Hz;
  - glottal C_d 0.85;
  - critical ratio ≈ 17 dB;
  - clothing insertion loss 0–3 dB.
- Still unsourced: anal tissue mechanics and any measured flatus SPL or spectrum. These remain assumptions.
- **S2 is empty:** an oscillating release is audible in any quiet room. Silent means S1 (no oscillation) or S3 (masked).
- Over the release prior, 79 % of releases are S1. The rest are masked in a restaurant (91 % of them) or subway car (76 %).
- Gate 0 now uses u_onset ≈ 30 m/s (14–51) instead of the 1–5 m/s placeholder:
  - neighbour, as emitted: median R = 0.92, P(R > 1) = 0.47, so the narrative holds;
  - own nose, equal mass: median R = 1.93;
  - own nose, as emitted: median R = 1.22. The exception corner is stronger than in the first Gate 0 pass.

### M3 — CFD (in progress)
- OpenFOAM 13 (openfoam.org) installed from apt. Solvers: `foamRun -solver incompressibleFluid` and `fluid`
  (Boussinesq).
- M3a free jet (axisymmetric wedge, Re 6 700):
  - A first attempt with a 1 % co-flow over the 40 d domain was invalid: the co-flow momentum flux rivalled the jet.
    That run was discarded.
  - A second set-up with an open (total-pressure) outlet converged for SST coarse but let k-ε medium settle into a
    spurious solution with reverse flow entering the outlet. It was discarded too.
  - Final set-up: no-slip base wall, entraining side (total pressure 0), outflow-only outlet. Momentum flux is
    conserved to within 3.5 % up to x/d = 95.
  - Coarse results, against Hussein 1994 (B_u), Dowling & Dimotakis 1990 (K_c) and S = 0.094:
    - SST: B_u = 5.03 (−13 %), K_c = 4.57 (−11 %), S = 0.117 (+25 %);
    - k-ε: B_u = 5.07, K_c = 4.31, S = 0.113 (+20 %).
  - This is the known RANS "round-jet anomaly" (over-spreading), so RANS will slightly over-dilute audible jets.
    That bias favours H1 and must be stated. A k-ε case with C_ε1 = 1.6 tests the standard correction.
- M3b CBL:
  - simplified seated manikin from primitives (`cfd/geometry/manikin.py`), half model;
  - skin 33 °C, room 20/23/26 °C;
  - mesh: snappyHexMesh, 340 k cells (coarse).
- Compute budget: 4 cores. Running several cases in parallel on one core each is memory-bound and slow, so the CBL
  cases and the fine jet run one after another on 4 MPI ranks (`cfd/validation/run_pipeline.sh`).
- **First CBL "conveyor" result** (23 °C, coarse, iteration 3000; preview figure `figures/preview_conveyor_belt.png`):
  - 3-D streamlines (OpenFOAM `streamlinesPoints`) from 8 seat-level seeds; 7 of 8 reach nose height in 8–18 s,
    passing 0.09–0.34 m from the nose.
  - Gate 0 assumed own-nose transport of L/u = 0.74/0.17 ≈ 4.4 s. The CFD path is longer and slower, so update Gate 0
    (it lengthens own-nose travel and narrows the own-nose silent penalty) once the CBL validation is final.
- **Steady CBL runs rejected.** Steady SIMPLE did not converge. Sampled every 100 iterations, the face-front peak
  velocity in the 20 °C case swung 0.03 → 1.1 → 0.03 m/s with a period of about 2 000 iterations: the closed-room
  buoyant circulation oscillates in pseudo-time. Averaging over that has no physical meaning. The 23 °C steady values
  (0.27–0.30 m/s) and the trajectory times in the preview figure come from the same unconverged state and are
  **withdrawn** until the transient runs replace them.
- **CBL switched to transient RANS** (`make_case.py --transient 60`, `run_transient.sh`):
  - Euler time stepping; 2 outer correctors; max Co 5;
  - the Co limit binds only in near-wall layer cells (mean Co about 0.02), giving Δt ≈ 0.03 s;
  - 60 s of physical time from the steady state, averaged over 30–60 s;
  - about 1 h per case on 4 cores.

### M6 — perception (done, see `perception/m6_report.md`)
- **Neighbour, as emitted:** the median physical difference is R = 0.91. In perceived intensity that is
  R^0.28 = 0.973, a 2.7 % difference and **below the olfactory JND (≈ 7 %)**. The break-even expectation factor is
  γ\* = 1.03, so a 3 % amplification for unwarned exposures sustains the belief. At γ = 1.15, P(belief) = 0.64; at the
  own nose it is 0.76.
- **Breath-hold:**
  - An audible puff reaches the neighbour after a median of 16 s. Unwarned, the worst breath catches ≈ 93 % of the
    peak.
  - Warned, a 50 % dodge needs a 23 s hold; the typical 33 s maximum gives 68 %.
  - The ear buys a physical escape option only if the warned person holds their breath almost to their limit.
- **Newcomer effect:** in a 4 m³ lift car, an occupant is adapted to 0.66 of a fresh nose at 60 s, so a newcomer
  perceives ≈ 1.5× more. This carries into Scenario C.
- Still assumptions: γ itself (direction verified, size not found), τ_adapt, the post-hold breath, and the lift-car
  ventilation.
