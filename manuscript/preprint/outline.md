# Preprint outline (M9, skeleton)

*2026-10-16 · status: skeleton for review. The manuscript itself is LaTeX with the ACS `achemso` class (author's
choice): `main.tex` + `sections/*.tex`, bibliography generated from `refs/references.yaml` by `make_bib.py`; build with
`latexmk -pdf main.tex` (needs texlive-publishers and texlive-science). Figures carry their own "Fig. N ·" titles from
the analysis scripts; manuscript versions without those titles are a **GAP**, as LaTeX numbers figures itself. Every number below points to the file it comes from; nothing here is new
analysis. Items marked **GAP** are missing before a full draft. Narrative branch (confirmed 2026-10-15): "Debunked
(mostly): the nose was fooled by the ears", plus a regime map.*

**Working title.** *The Silencer Conjecture: a fluid-dynamical, perceptual and selection-bias test of the "silent but
deadly" belief*

**One-sentence result.** As passages are actually emitted, a silent one is stronger at a neighbour's nose in about
half of all pairs (P = 0.47). A bystander nevertheless remembers silent passages as worse in about 90 % of
comparisons, because a silent passage only enters memory if it stank (Berkson selection).

---

## Abstract (~200 words, write last)

- Belief: the less audible the release, the more offensive the odour ("Silencer conjecture"). It is documented across
  languages; never tested mechanistically.
- Chain:
  1. lip-reed acoustics, which sets which releases are heard;
  2. starting-jet/puff dispersion with validated constants and CFD of a seated pair;
  3. breath-resolved perception;
  4. a selection model of memory.
- Results:
  - **Physics, equal mass:** a silent release is more efficient per molecule (median R 1.35 at the neighbour). The
    effect is mostly below the JND.
  - **Physics, as emitted:** coin flip (P = 0.47).
  - **Perception:** the median difference of 2.7 % is below the JND.
  - **Memory:** belief 0.73–0.97 at plausible base rates.
  - **CFD of a sofa:** geometry can reverse everything (the backrest chimney).
- Conclusion: the belief is a memory artefact, not a measurement. An emitter, who notices every release, should not
  share it.

## 1. Introduction

- **Hook** (PLAN §2): Chatur "Silencer" Ramalingam, *3 Idiots* (2009). **Paraphrase only**: no quotation of the
  verse, and no image of the character. Cite the film.
- **Epigraph option:** Grose 1811 (*fice*), public domain.
- **The conjecture**, three meanings of "silent" (PLAN §4.1), and three comparison bases (NOTES 2026-10-16):
  - (A) equal mass and composition (physics);
  - (B) as emitted (population);
  - (C) among *noticed* events (folk experience).
- **Contributions:**
  1. mechanistic chain sound → release → dispersion → nose → brain;
  2. two transport theorems that bound what physics can do;
  3. a selection (memory) model that produces the belief from a coin-flip truth;
  4. a cross-cultural survey.
- **Fig. 1** graphical abstract. **GAP:** not made. Use the sofa CFD scene with OAV iso-surfaces; manikins only.
- **Fig. 2** mechanistic chain diagram. **GAP:** not made.

## 2. Definitions and theory

- **2.1 Deadliness.** The worst single inhalation: flow-weighted mean concentration per breath, I = k·OAV^n.
  - Justification: Laing 1983/1985, Frasnelli 2006, Uchida & Mainen 2003, Kepecs 2006, Schauberger 2012
    (NOTES "Definitions settled").
  - Cumulative exposure is secondary.
- **2.2 Theorem 1 (linear transport).** C = G * q.
  - The time-integrated dose is invariant to release history.
  - A slower release never has a higher peak (Young's inequality), for any Green's function G: any posture, room or
    flow.
- **2.3 Theorem 2.** Release-mode memory decays with time and distance; in a closed room, C → M / V_room.
- **2.4 Where the theorems fail:** only momentum and buoyancy (non-linear).
  - Near-field jet pre-dilution makes R > 1, bounded by the Silencer number Si = u₀/u_h.
  - Routing changes can push either sign.
  - This motivates the regime map.
- **2.5 Theorem 3 (selection).** With N = H ∨ S:
  - P(S | ¬H, N) = 1 and P(S | H, N) = P(S | H), so the gap is 1 − P(S | H);
  - the emitter has N = 1, hence no bias (Berkson 1946; Snoep et al. 2014, Boyd formulas);
  - verified numerically: `perception/test_selection.py`.

## 3. Methods

- **3.1 Source.** `params/params.yaml` is the single source of truth; every value is VERIFIED, DERIVED, PARTIAL or
  ASSUMPTION.
  - Passage volume 17–375 mL (Suarez 1997).
  - Signed buoyancy (CO₂-rich flatus can be denser than air).
  - Sulfur spread σ_ln = 1.1.
  - **Table 1:** parameter table generated from params.yaml. **GAP:** script to render it.
- **3.2 Acoustics** (`acoustics/m2_report.md`):
  - lip-reed onset ½ρ(u₀/C_d)² > P_th, harmonic monopole, ISO 226 audibility, critical-ratio masking;
  - onset u₀ ≈ 30 m/s (14–51); 79 % of releases are S1.
  - Sphincter wording: internal (involuntary) vs external (voluntary) is already in the M2 report ("Who controls
    the valve").
- **3.3 Gate 0 analytic dispersion** (`gate0/gate0_report.md`):
  - starting jet → puff, then Gaussian puff transport, then inhalation averaging;
  - Monte Carlo over 20 000 pairs;
  - own-nose transport from CFD trajectories (`u_own_eff`).
- **3.4 CFD** (`cfd/validation/m3_report.md`, `cfd/cases/sofa/m4_report.md`):
  - OpenFOAM 13, transient RANS k-ω SST, Boussinesq in internal-energy form.
  - **Jet validation:** B_u 5.0, K_c 4.3–4.6, the known +25 % round-jet spreading anomaly, GCI ≤ 3.7 %.
  - **CBL validation:** +42 % / ≈ +40 % / +56 % at 20 / 23 / 26 °C; trend −27 % vs −33 % measured.
  - **Sofa duet:** 722 k cells; momentum-equivalent inlet; 30 s precursor, then 30 s branches.
- **3.5 Perception** (`perception/m6_report.md`): breath sampling, warned breath-hold, Stevens n = 0.28,
  adaptation, Weber C = 0.28.
- **3.6 Observers and selection** (`perception/selection.py`, `uq/observer_ps.py`):
  - population thresholds: Amoore & Hautala 1983, Wilby 1969;
  - per-passage spread of 2 binary steps;
  - distracted factor 26× (from Whisman 1978);
  - sound-cued attention.
- **3.7 UQ** (`uq/run_m7.py`): Gate 0 as surrogate (deviation from the plan); given-data Sobol indices; the JND as a
  concentration ratio of 1.28.

## 4. Results

- **4.1 Who is heard** (Fig. 3). Most releases are silent (S1, 79 %). S2 is empty: an oscillating release is
  audible in any quiet room.
- **4.2 Validation** (Fig. 4, two panels: jet and CBL).
- **4.3 Physics of the ratio** (Fig. 10a regime map; Gate 0 tables):
  - equal mass: R = 1.35 (neighbour), 1.73 (own nose);
  - as emitted: 0.92 (neighbour, P = 0.47), 1.15 (own nose, P = 0.56);
  - denim: 0.31.
- **4.4 What decides it** (Fig. 10b, Sobol):
  - as emitted, volumes explain ~0.6 of the variance;
  - at equal mass, mixing K explains 0.35;
  - valve parameters explain < 0.5 % each.
- **4.5 The sofa** (Figs 5–6; M4 report). The backrest chimney carries the silent release over the head; the jet
  escapes and reaches the neighbour; breathing-zone R ≈ 10⁻¹⁰–10⁻¹⁴.
  - **Posture sensitivity (done):** reclined 4.5°, with the back closed onto the backrest above 0.85 m.
    - Silent still reaches no breathing zone; it leaves the wedge sideways and rises behind the head.
    - Audible now exceeds threshold at the releaser's own nose (OAV 2–4).
    - Breathing-zone R ≈ 10⁻¹¹–10⁻¹⁴ in both postures (`cfd/cases/sofa/m4_report.md`).
- **4.6 Perception** (Figs 7, 11): median difference 2.7 % at the neighbour, below the JND. γ is an auxiliary
  hypothesis (0–3 %, sign unknown).
- **4.7 Composition counter-argument.** Suarez 1997 Table 3: no volume–sulfur-concentration link; sulfur mass rises
  with volume. N₂ is blood-derived, not swallowed air.
- **4.8 Memory** (Fig. 13 + observer table):
  - truth 0.49; bystander belief 0.67–0.92 across observer models; emitter shows no bias.
  - Masking is not a clean discriminator (loudness selection).
  - **GAP:** mark the observer-model points on Fig. 13b.
- **4.9 Headline in layers** (Fig. 10c): physics → nose (JND) → memory.

## 5. Discussion

- **Why the belief exists.** Berkson selection is the main route. Amplifiers: distinctiveness (Hamilton & Gifford
  1976), availability (Tversky & Kahneman 1973), sampling (Fiedler 2000). Cultural transmission of the phrase
  (Chapman 1967) is the competing route (Fig. 12, `culture/`).
- **The emitter.**
  - Notices every release, so there is no selection.
  - Self-source effect: BODS gas items 2.51 vs 3.71 (Liuzza 2016). This lowers absolute unpleasantness only.
  - Belief about the source shifts hedonics (Hold & Schleidt 1977), so expectation is the one route left.
  - No study compares real own vs other flatus (null).
- **Testable predictions** (no survey run):
  1. emitters hold the belief less than bystanders;
  2. anosmic people never notice silent passages;
  3. masking effects are ambiguous.
- **When a silent release really is worse:** bare, still air, own nose, within ~5 s (regime map corner).
- **Limitations** (PLAN §16 plus):
  - RANS, single realisation, 30 s window, CBL bias;
  - no human measurements;
  - p_S unmeasured;
  - Sobol inputs dependent;
  - Suarez 1997 and 1998 are one dataset.

## 6. Conclusion

One paragraph. Deadpan.

## Figures: manuscript numbering → files

| Fig. | Content | File | Status |
|---|---|---|---|
| 1 | Graphical abstract | — | **GAP** |
| 2 | Mechanistic chain diagram | — | **GAP** |
| 3 | Acoustic regimes | `figures/fig3_acoustic_regimes.png` | done |
| 4 | Validation: jet + CBL | `figures/fig4_jet_validation.png`, `figures/fig4_cbl_validation.png` | merge into one figure |
| 5 | Sofa: nose time series | `figures/fig5_sofa_duet_noses.png` | done; add posture variant |
| 6 | Sofa: plane snapshots | `figures/fig6_sofa_duet_planes.png` | done |
| 7 | Breath-hold | `figures/fig7_breath_hold.png` | done |
| 8 | Conveyor belt (CBL streamlines) | `figures/fig_conveyor_belt.png` | renumber (plan's Fig. 8 elevator not done) |
| 9 | — | — | plan's countermeasures figure dropped or **GAP** |
| 10 | Regime map, Sobol, layered headline | `figures/fig10_regime_uq.png` | done |
| 11 | γ (auxiliary) | `figures/fig11_gamma.png` | move to SI? |
| 12 | Culture map | `figures/fig12_culture_map.png` | done |
| 13 | Memory filter | `figures/fig13_memory_filter.png` | add observer points |
| 14 | Chemistry of the passage | `figures/fig14_chemistry.png` (`chem/fig_chem.py`) | done |
| S1 | Adaptation | `figures/figS_adaptation.png` | done |
| S2–S4 | Gate 0 ratio map, sensitivity, P(SBD) | `figures/gate0_*.png` | SI |

## Open decisions for the author

- Figure count: keep 12–13 main figures, or move Figs 7, 11 and 8 to the SI?
- Plan Figs 8 (elevator whodunit) and 9 (countermeasures): drop, or run later as M5 scenarios?
- Venue order (PLAN §1): preprint first, J. Immat. Sci. second.
- Preprint server (open, decide before submission; 2026-10-16 discussion):
  - arXiv `physics.flu-dyn` (best audience fit; needs endorsement for a first submission);
  - otherwise ChemRxiv (no endorsement; basic screening; matches achemso);
  - bioRxiv excluded (requires biological research with new data);
  - post to one server only.
- Chemistry: **one preprint** (author, 2026-10-17). The chemistry is spread over the existing structure: Methods
  "Odorant chemistry", Results "The chemistry of the odour" (absorbs the composition counter-argument; Fig. 14,
  Table 3), Discussion "Where the odour comes from"; the introduction lists it as a fifth contribution. With this
  content ChemRxiv becomes a stronger server candidate; the server choice is still open.
- AI-use disclosure: required (arXiv, ACS); to be written last, gap marker in `main.tex`.
- Affiliation: "Independent Researcher, Incheon, Republic of Korea" (author's choice). The author is to check employer
  rules on outside publication and IP.
