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
- **First CBL "conveyor" result** (23 °C, coarse, iteration 3000; preview figure, since removed and replaced by `figures/fig_conveyor_belt.png`):
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
- **Transient CBL results:**
  - face-front peak at 20 °C: 0.34 ± 0.01 m/s; at 23 °C: 0.28 ± 0.02 m/s;
  - about 40 % above Licina et al., with the right trend (−19 % against −17 % interpolated).
- **26 °C from rest failed** after 1 s (T(h) inversion, max Co 25): the steady 26 °C run never reached iteration 3000.
  - It is re-queued after the sofa pipeline, initialised from the developed 23 °C field without T.
  - `run_transient.sh` now reports FAILED instead of done when the log contains FATAL. The failed run is kept as
    `cbl_t26_tr_fromrest_failed`.

### M4 — Scenario A "sofa duet" (in preparation)
- Case generator `cfd/cases/sofa/make_case.py`; pipeline `cfd/cases/sofa/run_sofa.sh`.
- Set-up:
  - two seated manikins 0.6 m apart on a sofa in a 3.2 × 3.2 × 2.6 m room;
  - 721 k cells (snappyHexMesh, level 4 = 5 mm at the release);
  - precursor of 30 s, then silent and audible branches mapped from it.
- Release: a momentum-equivalent **inlet** at the end face of a 3 cm × 1 cm-radius nozzle stub behind the farter's
  buttocks, pointing down and back into the seat/backrest corner.
  - Audible default (92 mL over 0.5 s through 2.4 mm, u₀ = 41 m/s) → u_eq = 4.9 m/s, pre-diluted 8.3×.
  - Silent default: 92 mL over 2 s through 8 mm (u₀ = 0.9 m/s) → u = 0.15 m/s, no pre-dilution.
  - The pulse has 0.03 s linear ramps (volume preserved). The branch cases run in two stages: the release with
    maxDeltaT ≈ 4 cell-crossing times, then the drift with maxDeltaT 0.1 s.
- **Source-model failures (recorded as null results):**
  - Closed room plus volumetric massSource: the global continuity error grew 1e-7 → 2e-3 within 3 steps and T(h)
    failed. This happened with an equal mass sink, with no temperature excess, and with max Co 0.5. A sealed
    Boussinesq room has no compressibility, so the pressure equation becomes incompatible.
    - Fix: a 0.5 × 0.5 m ceiling vent (p_rgh = 0), cut from the ceiling patch with `createPatch`. The global error
      dropped to ≈ 1e-12.
  - Vent plus massSource: the source still diverged.
    - A 7.5 mm sphere (14 cells, injecting ≈ 2× the cell mass per step) failed at step 5.
    - A 2 cm sphere (328 cells) failed at step 12; the domain-mean Courant number grew ×2.5 per step.
    - The same mesh without the source was stable, so the volumetric source was abandoned for a boundary inlet.
  - **Root cause (found afterwards):** the inlet version also blew up, before the release started, and so did an
    isothermal room at rest. OpenFOAM's Boussinesq equation of state includes h = p/ρ(T) in the enthalpy.
    - With `energy sensibleEnthalpy`, each pressure change shifts T and ρ (≈ 0.025 K per 30 Pa).
    - The expansion leaves through the vent, which changes the pressure again. The first-step outflow volume did not
      depend on Δt, so smaller time steps made it worse.
    - With `sensibleInternalEnergy` (e has no pressure term) the isothermal room stays at rest (mean Co 1e-9).
    - This coupling probably also drove the massSource failures. The inlet is kept because it is the cleaner model.
    - The closed CBL validation rooms pin the pressure with a reference cell. Their p swings of a few Pa give
      < 0.01 K, so they are not affected.
- **Inlet test with internal energy** (audible, from rest, release at 0.02 s, serial):
  - stable through the ramp and the full-flow plateau to t = 0.106 s (stopped there to free the cores);
  - max Co held at 5 by the time-step control (Δt ≈ 0.8 ms); domain-mean Co ≈ 1.6e-5.
- Pipeline `run_sofa.sh` launched detached. It waits for the transient CBL set, then runs the precursor (30 s) and the
  silent and audible branches (release at +0.2 s, 30 s each).
- **Precursor (30 s):** the CBL at both noses (probe 2.5 cm in front) settles to U_z ≈ 0.20–0.21 m/s after 10 s, the
  same at both seats. Nose-height air is +1.3 K.
- **Silent branch (30 s):**
  - Nobody's breathing zone receives odour: the peak OAV in the 5 cm disc in front of either nose is < 1e-10.
  - The release rises through the ~3 cm gap between the releaser's back and the backrest (a "chimney").
  - It passes behind and over the releaser's head at 5 s, with peak OAV ≈ 5 800 within 25 cm of the head axis.
  - It then continues to the ceiling. The neighbour sees nothing within 30 s.
  - **Sensitivity flag:** the gap is a feature of the upright manikin. A reclining posture with the back against the
    cushion would close it. The 30 s window also ends before room-scale mixing brings the ceiling cloud back down.
- **Audible branch (30 s):**
  - The jet escapes the chimney: part reaches the neighbour's head region within 6 s (OAV 369 within 25 cm) and both
    breathing zones at OAV 0.5–0.7 (sub-threshold mean).
  - R = C_silent / C_audible ≈ 1e-10 to 1e-14 in every breathing-zone metric.
  - Report: `cfd/cases/sofa/m4_report.md`; Figs 5 and 6.
  - Open sensitivities: posture (back gap), RANS intermittency, 30 s window.

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

## 2026-10-16 · Paused here (by request)
- **M4 first pass is complete:** `cfd/cases/sofa/m4_report.md`, Figs 5 and 6.
- **Not run yet**, for a later session, in suggested order:
  1. A reclined-posture variant that closes the back/backrest gap.
  2. A longer drift window (120 s) for room-scale mixing.
  3. An intermittency (meandering) correction of the RANS mean.
- **M3b at 26 °C still open.** The re-run (initialised from the 23 °C field) was interrupted by a session restart and is
  partial in `cfd/runs/cbl_t26_tr`, which is gitignored. To finish it: delete that directory, run
  `cfd/validation/cbl/run_transient.sh`, then `cfd/validation/cbl/analyze.py`.
- **Gate 0 update** (own-nose transport time from the CFD trajectories) is still pending.

## 2026-10-16 · Discussion and literature pass 2 (no code changes)
27 papers plus 2 supplements read in full; entries in `refs/references.yaml` under "Literature pass 2". Missing:
Djordjevic 2008 Table S1 (Fig 1B can be digitised instead).

### Definitions settled
- **"Deadliness" of one event** = peak perceived intensity at breath resolution, i.e. the worst single inhalation
  (flow-weighted mean concentration per inhalation), I = k·OAV^n. Cumulative exposure is a secondary metric.
  - Perceived intensity saturates within one sniff: 1 sniff = 7 sniffs (Laing 1983); optimum 0.39–0.64 s, at most
    1.63 s for butanol (Laing 1985).
  - Within that window intensity does integrate: longer 100–300 ms H2S pulses are rated stronger (Frasnelli 2006,
    F = 90.1).
  - The sniff is the unit of processing (Uchida & Mainen 2003; Kepecs 2006). Odour-impact regulation also works per
    breath (Schauberger 2012).
- **Comparison bases**, to be stated in every claim:
  - (A) equal mass and composition (physics);
  - (B) as emitted (population);
  - (C) among *noticed* events (folk experience).

### Physics claims (theory, no new runs)
- **Theorem 1 (linear transport).** For a passive release, C(t) = G * q. The time-integrated dose is invariant to the
  release history, and a slower release (q_silent = q_audible * k, with ||k||₁ = 1) never has a higher peak (Young's
  inequality).
  - Holds for any G: any posture, room or flow.
- **Theorem 2.** Release-mode memory decays with time and distance. In a closed room both modes tend to M / V_room.
- **Exceptions** come only from release momentum and buoyancy (non-linear):
  - near-field jet pre-dilution, which can make R > 1 (bounded by Si);
  - routing changes, either sign (sofa chimney).
  - This is the regime map.

### Composition counter-argument ("loud = swallowed air, odourless"), addressed head-on
- **Suarez 1997, Table 3** (87 passages):
  - r(volume, [H2S]) = +0.195 (ns); MeSH −0.206 (ns); DMS +0.223 (ns);
  - r(volume, [N2]) = −0.503 (P < 0.001); r(volume, [CO2]) = +0.559 (P < 0.001).
  - Concentration criterion: no support. Mass criterion: refuted; sulfur mass rises with volume.
  - Caveat: Suarez 1997 and 1998 are the SAME dataset (16 subjects, 87 passages, beans + lactulose, rectal tube,
    no sound data).
- **N2 is mostly blood-derived**, not swallowed air (Levitt & Bond 1970; Tomlin 1991). High-rate collections are
  fermentation gas (Tomlin: > 80 mL/h ⇒ 98.9 % fermentation gas).
- **Odour ratings in Suarez 1998** used fixed 10 mL aliquots, so they rate concentration. The authors argue the nose
  responds to the volume of noxious gas per passage, which supports the mass criterion.
- **Wording fix:** 70–85 % of resting anal pressure is the involuntary internal sphincter (Miller 1988). "The
  sphincter controls sound" must distinguish the external (voluntary) from the internal sphincter.
- No paper on flatus acoustics exists; the reed model is neither supported nor refuted.

### Origin of the belief: restructured
- **Main explanation: selection (Berkson / collider).** Noticed = heard OR smelled, so
  P(smelly | silent, noticed) = 1 while P(smelly | audible, noticed) = p_S, even if sound and smell are independent.
  - Cite this as the deterministic OR-collider case of Berkson's formula, not as his numerical example; the
    direction there depends on the hospitalisation rates (Snoep 2014 appendix, Boyd formulas).
  - Bias = 1 − p_S: stronger when stinky events are rare.
  - Amplifiers: distinctiveness-based illusory correlation (Hamilton & Gifford 1976); availability (Tversky &
    Kahneman 1973); selective-outcome sampling (Fiedler 2000).
  - Competing route: the phrase itself transmits an associative belief (Chapman 1967), which must be separated
    from experience.
- **Expectation factor γ demoted to an auxiliary hypothesis with uncertain sign** (confirmed by the author
  2026-10-16; `perception/m6_report.md` updated, Fig. 11 annotations still to be regenerated).
  - A negative label raises intensity (Djordjevic 2008: partial η² ≈ 0.18; Dalton 1999).
  - No label ≈ positive label (Djordjevic, p = .65). The sound acts as a negative label given in advance, so the
    literature, taken literally, predicts warned ≥ unwarned, which is opposite to γ > 1 for silent releases. No study
    tests warned vs unwarned directly.
  - Magnitude for a brief exposure is 0–3 % (Herz 2001; first ratings in Dalton). The 1.18–1.61 values (Dalton
    1999) are 20-min means.
  - "Sensitisation" was overstated: in Dalton 1999 intensity fell in all groups, and negative framing only slowed
    the fall.
- **Self vs other odour.** Own flatus is rated less unpleasant than a stranger's (Stevenson & Repacholi 2005). This
  is hedonics only: no study measures intensity.
  - Lenk 2019 SI: the only odour item is bad breath. Hygiene disgust: self 2.44 > partner 2.26, stranger 2.89, so
    there is no "self is least disgusting" pattern.
  - Platek 2001: the self advantage needs knowing the source.

### Predictions (theory only; no survey planned)
1. **Emitter vs bystander.** The emitter's noticing does not depend on smell (h₁ = 0 ⇒ OR = 1, Boyd), so the
   emitter should hold the belief less. Supported by Berkson/Boyd, Fiedler 2000 and Denrell 2005 (analogy only).
2. **Noisy environments (masking)** — the original prediction is revised (and see the selection-model result
   below: masking is NOT a clean discriminator, because a physical "loudness selection" also weakens the belief). The accounts disagree, which makes
   masking a discriminating test:
   - pure selection: no change;
   - Hamilton & Gifford: weaker belief;
   - Fiedler sample size: stronger belief.
3. **Anosmic people** never notice silent releases.

### To do (later, with code)
- M6 key sentence rewritten in the report (done 2026-10-16). Still to do: regenerate Fig. 11 without the
  "plausible expectation effect" band, and update the same sentence in `PLAN.md`-derived drafts if any.
- Fix the sphincter wording in the M2 report.
- Behavioural differences (e.g. changing posture to release quietly) are treated in psychological and social terms
  only, with no physics model.
- Selection model implemented 2026-10-16 (see below). Add it to the manuscript outline.

### Selection model implemented (2026-10-16; `perception/selection.py`, `run_selection.py`, Fig. 13)
- Setup: 20 000 single passages from the Gate 0 priors.
  - A log-normal sulfur multiplier: `params.yaml` `sulfur_sigma_ln` = 1.1, from Suarez 1998 SEM over 87 passages
    (per-passage SD 1.87 µmol/L).
  - The `c_H2S` note is corrected: it had treated the SEM as over 16 subjects.
  - M2 audibility at the neighbour's distance for each background.
- Theorem 3 is verified numerically: the memory gap P(S|silent,N) − P(S|audible,N) equals 1 − P(S|H) at every base
  rate.
- Gate 0 nominal (puff centred on the nose): the neighbour smells 93 % of passages.
  - P(belief): truth 0.486, bystander memory 0.525, emitter 0.521 (own-nose physics, no selection; 0.534 before
    the own-nose transport update below).
- Base-rate sweep, bystander-memory P(belief) by the share of passages the neighbour smells:
  0.91 → 0.54, 0.74 → 0.64, 0.49 → 0.78, 0.34 → 0.86, 0.17 → 0.95. The truth stays at 0.49–0.53.
- Masking: library and living room 0.525, subway 0.495, restaurant 0.43 (only 30 heard).
  - P(S | silent, N) stays 1. The belief weakens because only the largest releases are heard in noise, and they
    carry more sulfur ("loudness selection").
- **The key empirical unknown is the everyday base rate** (how often a neighbour's passage is noticed by smell).
  Gate 0 gives an upper bound (0.93). The sofa CFD suggests it is far lower, because breathing zones were
  sub-threshold for both modes.
- Fig. 11 relabelled: a ±3 % brief-exposure label-effect band with unknown sign replaces the 1.0–1.3 band. M2
  report: the internal and external sphincter roles are added.

### Own-nose transport time from CFD (2026-10-16)
- New parameter `u_own_eff` = 0.07–0.16 m/s (t ≈ 4.7–11 s; CFD 4.7–8.0 s, extended ×1.4 for the 40 % CBL
  over-prediction).
  - It replaces `u_CBL` as Gate 0's own-nose transport speed. `u_CBL` stays the measured CBL velocity.
- Own nose: equal mass 1.93 → **1.73**; as emitted 1.22 → **1.15** (P(R > 1) 0.59 → 0.56).
  - M6 own-nose row: γ\* 0.94 → 0.96; P(belief) at γ = 1: 0.59 → 0.56.
  - Neighbour numbers are unchanged.
  - Updated: `gate0_report.md` §9, M2 table, M6 table, and the selection emitter value (0.521).


### M7 — uncertainty, regime map, headline (2026-10-16; see `uq/m7_report.md`, Fig. 10)
- Deviation: the surrogate is Gate 0, not a CFD Latin hypercube (one sofa branch = 1–2 h). The M4 branches are the
  check (routing, which Gate 0 lacks).
- Regime map (equal mass, room air): acoustic onset Si = 197. JND contour (ratio 1.28) crosses the own-nose time
  (6.7 s) at Si ≈ 110 and the neighbour time (12.5 s) at Si ≈ 200.
- Sobol (given-data, dependent inputs → descriptive):
  - as emitted, the two volumes explain ~0.6 of the variance of log R;
  - at equal mass, K explains 0.35;
  - valve parameters explain < 0.5 % each.
- Headline P(R > 1):
  - neighbour, as emitted: 0.47 (perceptibly worse: silent 0.37 / audible 0.44);
  - equal mass: 0.93;
  - own nose: 0.56 / 0.93;
  - denim: 0.31.
- Base rate p_S: background research found no direct measurement (null result). First bracket 0.1–0.5, central
  0.25 [ASSUMPTION, low]; revised below after the full texts arrived.
  - New refs: ohge2005, amoore1983, rim2009, stevens1988, wilby1969, whisman1978, desiato2021, croy2015,
    olmedo2012, weinberg2005 (abstracts only; PDFs requested). bolin1998 and manichanh2014 were already listed.
  - Most useful if obtained: Bolin 1998 (fraction of odorous passages).
  - Suarez 1998 (full text already in hand), Table 1: odour rated 0 (none) to 8 (very offensive) from 20 mL syringe
    samples, i.e. undiluted. Mean ratings are 3.3 and 5.6 (two judges, n = 87). The table gives means only, with no
    share rated odourless, so it does not constrain p_S.

### p_S revised with observer models (2026-10-16; `uq/observer_ps.py`, M7 report)
- All 11 base-rate papers were supplied by the author and read in full.
- New params (perception):
  - `thr_scale_typ` 0.05 (0.05–0.10): Nagata thresholds are 10–23× below Amoore/Wilby population values;
  - `thr_sd_bs` 2 binary steps (Amoore & Hautala p. 286);
  - `distracted_factor` 26 and `distracted_sd_bs` 3.5 (Amoore & Hautala Fig. 2, from Whisman 1978).
- p_S with the puff still centred on the nose: Gate 0 0.93; attentive 0.59–0.68; distracted 0.21; distracted and
  clothed 0.19. The matching memory beliefs are 0.53, 0.67–0.73, 0.91 and 0.92; the truth stays at 0.49–0.51.
- Bolin & Stanton 1998: odour is reported per day, not per passage. Converting gives ≈ 0.09 per passage (independent
  passages) [INFERRED, low]; bounds 0.05–0.7.
- Revised bracket p_S 0.1–0.6, central 0.2 [ASSUMPTION, low-moderate]. Belief 0.73–0.97, central 0.91.
- Corrections to the first-pass summary:
  - Rim & Novoselac 2009 used off-body sources (a near-floor source behind the occupant gives mouth ≈ 1.2× ambient in
    stratified air, ≈ 1× in mixed air), so it is only weak support for "the plume favours the emitter".
  - Croy 2015 tested no sulfur odorants.

### M3b at 26 °C done (2026-10-16)
- `cbl_t26_tr`: initialised from 23 °C at 60 s without T; interrupted at 35 s by a container restart and resumed from
  30 s with `startFrom latestTime`; no FATAL.
- Face-front peak 0.25 ± 0.04 m/s, against Licina 0.16 (+56 %).
- Bias across temperatures: +42 % (20 °C), ≈ +40 % (23 °C), +56 % (26 °C). Trend 20 → 26 °C: −27 % (Licina −33 %).
- M3 report table filled; Fig. 4 regenerated. `u_own_eff` (×1.4 correction at 23 °C) is unchanged.
- This closes the pause-point item "M3b at 26 °C still open". The Gate 0 own-nose update was already done (see
  above).

### Emitter's own nose: literature pass 3 (2026-10-16; background research, abstracts plus some full texts)
- **Self-source effect.**
  - Own odours are rated less disgusting: BODS questionnaire, N ≈ 6 800 in 9 countries, self 3.39 vs stranger 4.02 on
    a 1–5 scale. The flatus item pair is literally "silent but smells strongly"; item-level means are not yet obtained.
  - Own baby's faeces: d_z ≈ 1.0; blind trials hold, mislabelling abolishes the effect (Case, Repacholi & Stevenson
    2006).
  - Hierl et al. 2021, n = 28: own body odour rated *less intense* (η² = .30), with no pleasantness difference
    (BF₁₀ 0.53).
  - Nulls and sex asymmetries exist (Olsson 2006; Hold & Schleidt 1977).
  - No laboratory study of real flatus, own vs other, and no study of whether emitters detect their own passages
    (null).
- **No "self-blindness".** Own odour is processed equally fast or faster (ERP studies, n ≤ 6), but consciously poorly
  discriminated. Own breath is misjudged (Pham 2012: sensitivity 47 %, specificity 59 %), which looks like chronic
  adaptation.
- **Attention.**
  - Noticing a suprathreshold ambient odour drops from 60 % to 20 % under visual load (Forster & Spence 2018,
    φ = .41).
  - Endogenous attention does not lower the sensory threshold (Ashkenazi & Marks 2004).
  - So Amoore's 26× is mostly awareness and criterion. No study of tactile or proprioceptive cueing of odour detection
    exists (null).
- **Adaptation.** H₂S desensitises fast (Stuck 2014), but its unpleasantness barely adapts over 15 s (Li 2023).
  Distraction speeds desensitisation (Fallon 2018).
- **Prediction for the emitter** [INFERRED, moderate]:
  - The emitter feels every release and is a directed observer for all passages, so the emitter-side factors apply
    equally to silent and audible.
  - The emitter's silent-vs-audible judgement should therefore track physics (≈ coin flip): Theorem 3 with N = 1.
  - The self-source effect lowers absolute unpleasantness (and perhaps intensity), not the silent/audible contrast.
  - The only route to the belief for an emitter is expectation, if they already hold the folk belief (untested).
- **Correction to the agent's synthesis (computed, `uq/observer_ps.py`).** It predicted that sound-cued attention would
  *amplify* the bystander's selection. The opposite holds:
  - cueing raises P(smelled | heard) from 0.21 to 0.60;
  - the gap shrinks from 0.81 to 0.39, and the belief falls from 0.91 to 0.81.
  - Belief across observer models: 0.67–0.92 (truth ≈ 0.5).
- These references are NOT yet added to `refs/references.yaml`; they await the full texts. The DOI list was given to
  the author.

### BODS flatus items, full text (Liuzza et al. 2016 Chem Senses, Table 4; 2026-10-16)
- Scale: 1 (not disgusting at all) to 5 (extremely disgusting); total n = 528 over 3 studies.
- "You are alone at home and pass gas. It is silent but smells strongly": 2.51 (SD 1.15).
- "You are sitting next to a stranger and they pass gas. It is silent but smells strongly": 3.71 (SD 1.05).
- Self–other gap: **1.20**, the largest of the six odour types:
  - sweat 0.69, feet 0.67, breath 0.60, faeces 0.79, urine 0.49;
  - consistent with Stevenson & Repacholi 2005.
- Caveats:
  - context is confounded with source (alone at home vs next to a stranger);
  - both items are silent, so they say nothing about the silent-vs-audible contrast;
  - the items support only a lower absolute unpleasantness for the emitter.
- Remaining 14 full texts (literature pass 3) are being verified; results to follow.

### Literature pass 3 verified in full text (2026-10-16; 14 papers supplied by the author, all in refs)
The abstract-only pass was wrong or overstated in several places:
- **Ashkenazi & Marks 2004.**
  - Measure: 2AFC percent correct (no d′, no thresholds), with retronasal vanillin only.
  - The "control" was divided attention, not distraction; orthonasal smell was not tested.
  - So it does NOT show that attention leaves the olfactory threshold unchanged. The citation was replaced by Fallon
    2018 in `uq/observer_ps.py` and the M7 report.
- **Fallon et al. 2018** (n = 19, pleasant fragrance):
  - peak intensity in the first 10 s was focused 4.85 vs distracted 4.32 (ns);
  - at 15–65 s, 3.12 vs 2.02 (p = .035), i.e. distraction speeds the decay;
  - this supports the peak-breath definition of deadliness being insensitive to attention.
- **Spence et al. 2001 used H₂S** (0.8 vs 3 ppm intensity discrimination). The cue was 67 % valid (not 80 %): RT
  −114 ms, no accuracy gain.
- **Stuck et al. 2014**, H₂S 1–8 ppm:
  - complete desensitization in 40–70 s (n = 10);
  - after 120 s of exposure, intensity is 3.1–4.0/10 at 5 s and still 6.2–7.8/10 at 180 s (n = 20);
  - pleasantness was not measured.
  - [INFERRED] For an emitter whose passages cluster within a few minutes, later passages in a run are perceived
    weaker, whatever their sound; this adds noise, not a silent/audible bias.
- **Li et al. 2023.** 15 s adaptation lowered H₂S intensity by ≈ 25–32 % (figure-read); H₂S unpleasantness was unchanged.
- **Self-source effect**, all on unpleasantness/disgust; none measured intensity:
  - BODS internal–external gap 0.63, 0.5–0.9 by country (Zakrzewska 2023, from Table 2);
  - Stefańczyk 2020: 0.72 EMM, η²p = .10;
  - McBurney 1976: 9/11 donors, and the effect held even when the donor did not recognise his shirt.
  - Intensity evidence for self-odour rests on Hierl 2021 alone.
- **Belief about the source changes hedonics.** In Hold & Schleidt 1977, men rated the shirt they *believed* was theirs
  as pleasant more often than their real shirt (p < .05). This supports expectation as the only route by which an
  emitter could acquire the silent/audible belief.
- **Other corrections:**
  - Hold & Schleidt: men's modal rating of their own odour was "indifferent", not "unpleasant".
  - Wysocki 1997: the butanol threshold difference was ns (not "unchanged"; medians differed 20×).
  - Distel 2001 tested no malodours.
  - Pause 1999 / Krauel 1998: n ≤ 6, with the ignore session always first; directional only.
- The emitter prediction is unchanged: the silent/audible judgement tracks physics (≈ coin flip). The self-effect
  lowers absolute unpleasantness only.

### M9 manuscript skeleton (2026-10-16)
- Format chosen by the author: LaTeX, ACS `achemso` class (`journal=jacsat, manuscript=article`).
- Files:
  - `manuscript/preprint/main.tex` and `sections/*.tex`: claims and sources only, with `\gap{}` markers.
  - `outline.md`: the plan behind them.
  - `refs.bib`: generated by `make_bib.py` from `refs/references.yaml`. Non-ASCII is written as LaTeX accents,
    because classic BibTeX splits UTF-8 when abbreviating names.
- TeX Live installed in the container: texlive-latex-recommended/extra, -publishers (achemso), -science (mhchem,
  siunitx), latexmk. The build is clean (13 pages, 38 references cited).
- New reference: forster2018 (full text read by the literature agent; OpenAlex metadata).

### M4 posture sensitivity: reclined 4.5° (2026-10-16; `cfd/cases/sofa/m4_report.md`)
- The releaser's upper body is reclined about the hip; the back closes onto the backrest above 0.85 m.
- 4 highly skewed faces at the contact; the run is stable.
- The pipeline is detached with setsid (background tool runs are capped at 2 h); the audible branch was re-run once.
- Silent: no breathing-zone dose at either nose (≤ 10⁻¹⁰ OAV). The cloud leaves the seat wedge sideways at shoulder
  level and rises behind the head (head ring 3 100).
- Audible: the releaser's own breathing zone is now above threshold (OAV 2–4, a face-wrapping filament); the
  neighbour is at 0.2.
- Breathing-zone R at both noses ≈ 10⁻¹¹–10⁻¹⁴, as upright. **The chimney result is robust to closing the back gap.**
- Scripts take `--recline`. Upright results are reproduced exactly (same triangle set; `results.json` identical
  apart from the new `recline_deg` key).

### M9 first full prose draft (2026-10-16)
- All sections of `manuscript/preprint/sections/*.tex` are written:
  - abstract, introduction, theory (Theorems 1–3 with proofs), methods, results (tables of the ratio, the sofa and the
    observers), discussion, conclusion.
- The parameter table is generated by `make_params_table.py` (77 rows) and placed in an appendix.
- Remaining `\gap{}` markers:
  - TOC graphic, merged validation figure, caption details;
  - 120 s window result (running), survey data citation, Zenodo DOI, acknowledgements, AI disclosure (last).
- 30 pages in the manuscript layout.

### M4 120 s window (2026-10-17; `extend_window.sh`, `m4_report.md`)
- Both upright branches were continued from 30 s to 120 s (detached runs; about 1 s of simulated time per minute).
- **Direct pass (0–45 s):** unchanged; the silent release misses both noses.
- **Return (45–70 s):** both clouds come back from the ceiling.
- **After 70 s:** the neighbour sees identical traces (worst breath 0.39 for both; Theorem 2). The releaser sees silent
  1.5–2× audible, touching OAV ≈ 1 (trained-panel threshold) for ~1 s near 100–110 s.
- 120 s maxima:
  - R_bz is 1.6 at the releaser and 0.67 at the neighbour;
  - R for the worst breath is 1.7 and 1.0;
  - R for exposure is 2.0 and 0.91.
- `analyze_sofa.py --window 30` reproduces the first-pass breathing-zone numbers (`results_W30s.json`).
- Manuscript: results, discussion, abstract and conclusion updated; the gaps closed.

### M9 figures and captions (2026-10-17)
- `manuscript/preprint/make_figures.py` reruns the figure scripts unmodified, with suptitles suppressed and output
  redirected to `manuscript/preprint/figs/`. Result files are reproduced unchanged.
- `fig_chain.py` draws Fig. 2, the mechanism chain.
- The validation figure stacks the jet and CBL panels; the sofa mid-plane snapshots are added.
- All captions are written.
- **Correction:** the M2 report listed 1.7 L/s as the subway minimum audible flow at 0.6 m. That is the 3 m value; at
  0.6 m it is 0.36 L/s (Fig. 3b was right). The report and the manuscript are fixed.
- Remaining gaps:
  - Zenodo DOI, acknowledgements, AI disclosure (author decisions);
  - TOC graphic (ACS journals only).
- Running: forward-lean posture (−10°) sofa CFD, `run_sofa.sh <runs> -10`.

### Chemistry layer for ChemRxiv, part 1 (2026-10-17; `chem/`, `chem/chem_report.md`)
- The author asked for all chemistry items: OAV decomposition, buoyancy, reactivity, sorption, biochemistry and thiol
  receptors. A literature agent is running for items 3–6.
- **OAV shares:** MeSH ≈ H₂S (trained panel: 54 % vs 46 %). Men are MeSH-dominated, women H₂S-dominated. DMS is
  ≤ 1 % (trained) or 9–17 % (population thresholds).
- **Suarez 1998 Table 3 removal check:**
  - zinc acetate: OAV × 0.072. Predicted intensity ratio 0.31–0.59 (n 0.45–0.20); the judges gave 0.28 and 0.59,
    which is consistent.
  - charcoal: rated far weaker than the power law predicts (failure near threshold).
- **Buoyancy:** the compositional part (median +1.25 to +1.4 m/s²) is about 3× the thermal part (+0.47).
  - 6–12 % of passages sink while hot; 25–38 % are heavier than air after cooling.
  - Water saturation is an assumption, bracketed.

### Chemistry layer, part 2 (2026-10-17; `chem/reactivity.py`, `chem/chem_report.md` part 2)
- **Gas-phase loss over 120 s:** < 0.5 % (IUPAC k, indoor OH ≤ 10⁶); ≤ 4 % even during hypochlorite cleaning.
- **Surface deposition:** no data exist (null result); it matters above v_d ≈ 0.01 cm/s.
- **Fabric sorption:** no data beyond Ohge 2005 (null result).
- **Biochemistry:** H₂S from SRB plus cysteine degradation. CH₃SH → H₂S → thiosulfate (Levitt 1999, read in full);
  rhodanese.
- **Correction:** the agent doubted that Suarez 1997 contains r(volume, [H₂S]). The full text, Table 3, shows 0.195;
  our citation stands.
- **Receptors:** copper is not a general thiol mechanism (Duan 2012, Haag 2019); "Block 2017 PNAS" does not exist as
  remembered.
- New refs: atkinson2004, levitt1999, duan2012, haag2019. 15 DOIs requested from the author.

### Chemistry layer, part 3: full-text verification of 15 papers (2026-10-17; `chem/`, `chem/chem_report.md`)
- **Tangerman 2009** (GC, n = 28): H₂S 149, MeSH 216, DMS 144 nM, so MeSH ≥ H₂S, against Suarez's H₂S ≈ 5× MeSH.
  - With this composition or with the lowest literature thresholds, MeSH carries 60–94 % of the OAV.
  - Tangerman's panel independently names MeSH as the main odorant.
- **Dilution anchor.** Tangerman's experimental flatus threshold implies a dilution of 7.5 × 10⁴–1.3 × 10⁵
  (6 × 10³–4.4 × 10⁴ with the Nagata thresholds). The Gate 0 breath-averaged median is 1.8 × 10³ at the neighbour
  (10–90 %: 2.5 × 10²–2.9 × 10⁴). Gate 0 is at the concentrated end, consistent with an upper bound; the agreement is
  only to an order of magnitude.
- **Reactivity** now uses measured office OH 0.62–9.79 × 10⁵ cm⁻³ and O₃ 0.7–2.6 ppb (Fiorentino 2023); loss stays
  < 0.4 % in 120 s.
- **Corrections:**
  - Braccia's "1.1 %" is 5/4,644 = 0.11 %.
  - Yu 2022 measured carbonyl, acid and aromatic VOCs, no sulfur gases.
  - Free H₂S is < 5 % of faecal total sulfide.
  - The DMS threshold in Block 2017 is for seabirds.
  - The "40 ppb" in Fiorentino is a formaldehyde guide value, not O₃.
- **Receptors:** OR2T11 responds to MeSH, not H₂S (Li 2016). Nasal Cu is ≈ 2.5 µM (Block 2017). Zhang 2018 tested only
  MTMT.
- 15 refs added (152 total).

### M4: forward-leaning posture, −10° (2026-10-17; `cfd/cases/sofa/m4_report.md`)
- Mesh OK (713 k cells, max skewness 3.3); both branches reached 30 s.
- **Releaser's nose:** 13 cm further forward, out of the back column; it receives neither release (≤ 1.5 × 10⁻⁵).
- **Neighbour:** the silent cloud reaches the head ring (OAV 580, vs 450 audible) but not the breathing zone (10⁻⁴).
  The audible jet reaches it at 2.6.
- In all three postures, silent < audible in both breathing zones during the direct pass.
- Forward lean is the one case where RANS intermittency could matter for the silent release.
- Plot titles now say "leaning forward" for negative angles.
- Manuscript: results paragraph, Table 2 rows, methods, discussion and abstract updated ("three postures").

### Chemistry in the single preprint (2026-10-17; `manuscript/preprint/`, `chem/fig_chem.py`)
- **Decision (author):** one preprint that includes the chemistry. It is spread over the existing structure, not set
  apart as its own section; a two-panel figure was added.
- **New figure, Fig. 14** (`chem/fig_chem.py`; palette validated):
  - (a) OAV shares for 2 compositions × 3 threshold sets;
  - (b) g′ at 37 °C and after cooling against %CO₂.
- **Methods:** new subsection "Odorant chemistry" (OAV, removal check, buoyancy split, conserved tracers, dilution
  anchor).
- **Results:** "The chemistry of the odour" replaces "The composition counter-argument" and absorbs it. Adds the
  reactivity table (Table 3) and Fig. 14.
  - Stated explicitly: composition does not change any silent/audible ratio (linear transport); absolute OAVs drop
    11–38 % with the Tangerman composition.
- **Discussion:**
  - new subsection "Where the odour comes from" (production, mucosal clearance, free vs total sulfide, diet, OR2T11
    and copper; inferences marked);
  - limitations now include OAV additivity and deposition.
- **Introduction and abstract:** fifth contribution and one chemistry sentence.
- `chem/buoyancy.py` refactored to expose `per_passage()`; its JSON output is unchanged (diffed).
- Build: 41 pages, clean apart from the pre-existing overfull parameter longtable.
