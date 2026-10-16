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
2. **Noisy environments (masking)** — the original prediction is revised. The accounts disagree, which makes
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
- Add the selection model (Theorem 3, Berkson form) to the manuscript outline. Optionally, simulate apparent R
  under (C) using Gate 0 samples.

