# Silent But Deadly? — Research & Simulation Plan (v3)

> **Working title (preprint):** *The Silencer Conjecture: A Fluid-Dynamical, Perceptual and Cross-Cultural Test of the "Silent But Deadly" Belief*
> **Working title (J. Immat. Sci. version):** *Pursue Excellence, and the Smell Will Follow: Computational Olfactory Ballistics of the Silent Fart*
>
> **Owner:** Chan Young Joe · **Executor:** Claude Code · **Created:** 2026-10-15
> **Status:** Plan approved in chat; v2 draft (Korean, literature-based) exists and is superseded by this plan where they conflict.

---

## 0. How to use this document (instructions for Claude Code)

1. Work **module by module in the order of §15 (Milestones)**. Each module ends with a deliverable and a short `NOTES.md` entry stating assumptions, results and open issues.
2. Anything tagged **[VERIFY]** is a number or claim taken from memory, a non-peer-reviewed source, or a forum. Find a citable source before it enters a figure or the manuscript. If no source is found, keep it as an explicit **[ASSUMPTION]** and include it in the sensitivity analysis.
3. Anything tagged **[ASSUMPTION]** is a deliberate modelling choice. All of them must appear in the parameter table of the manuscript and in the uncertainty analysis (§11).
4. **Copyright rules:** do not reproduce film dialogue, song lyrics, poems or verses (including the *3 Idiots* verse) — paraphrase and cite. Do not render real people or copyrighted characters in figures. Public-domain text (e.g., the 1811 slang dictionary) may be quoted briefly.
5. **Tone rule ("deadpan rigour"):** the physics, units, validation and statistics must be fully serious. The humour lives in the scenarios, titles, figure staging and colour-bar labels — never in fudged numbers.
6. Prefer free/open tools: OpenFOAM, ParaView, Python (NumPy/SciPy/pandas/matplotlib), Blender (optional rendering), MakeHuman or other CC0/open human geometry.

---

## 1. Target venues and decision rule

| Track | Venue | Requirement |
|---|---|---|
| Serious | Preprint (arXiv `physics.flu-dyn` or `physics.pop-ph`; fallback OSF/Zenodo with DOI) | Full methods, validation against canonical jet/plume laws, UQ, open code/data |
| Satirical | *The Journal of Immaterial Science* (open-access, "beer-reviewed", satirical/whimsical papers from all areas of science) | Real results, comedic framing. Check their submissions page manually (it blocks automated access). |

**Dual-track strategy:** post the serious preprint first; the J. Immat. Sci. paper is a separate, shorter, comedic text that **cites** the preprint (avoids duplicate publication). Both may reuse figures with attribution to the preprint.

**Gates now decide the narrative, not whether to publish:**
- Gate 0/1 show a robust concentration penalty for silent releases → narrative = "The Silencer conjecture is physically vindicated (with caveats)".
- No robust penalty → narrative = "Debunked: the nose was fooled by the ears" (psychological explanation becomes the headline).
- Mixed/regime-dependent → narrative = regime map ("it depends on your trousers").

---

## 2. Introduction hook — *3 Idiots* (2009)

Open the paper with the character **Chatur "Silencer" Ramalingam** from Rajkumar Hirani's film *3 Idiots* (2009):

- His nickname comes from his silent but foul flatulence, attributed in the film to the memory-enhancing pills he takes constantly.
- In his (sabotaged) Teachers' Day speech he recites a mock-Sanskrit verse that ranks farts by their sound, descending from a loud, vehicle-like blast down to the silent one, which is declared the deadliest.
- **Do not quote the verse.** Paraphrase it as above and cite the film.

Suggested framing: name the folk belief **"the Silencer conjecture"** (*the less audible the release, the more offensive the odour*), note it is "documented in Sanskrit-styled verse, an 1811 English slang dictionary, a Chinese proverb and the Russian lexicon" (§12), and that it has never been tested with a mechanistic model. Then state the three contributions:

1. A mechanistic chain *sound → release dynamics → dispersion → nose dose → perception* (§5–§9).
2. A psychological "preparedness" layer with a break-even analysis (§9.4).
3. A cross-cultural survey of the belief (§12).

Optional epigraph (public domain, 1811): Grose's *Dictionary of the Vulgar Tongue* defines *fice* as "a small windy escape backwards, more obvious to the nose than ears".

---

## 3. Corrections carried over from review of v2 (must be applied)

1. **Remove the "heavy H₂S sinks to the floor" argument.** Flatus H₂S is ~1.06 µmol/L (Suarez et al. 1998) ≈ 26 ppm. At that level the mixture density is set by N₂/CO₂/H₂/CH₄, and the gas leaves at ~37 °C, so it is more likely **positively buoyant**. Treat the release as a warm, variable-composition buoyant jet/puff.
2. **Add the human convective boundary layer (CBL).** Seated thermal-manikin measurements give peak CBL velocities of ~0.16–0.24 m/s in front of the body depending on room temperature (Licina et al. 2014, *Build. Environ.* 75:79–91). A low-momentum (silent) puff can be entrained into this rising layer and carried to the breathing zone.
3. **Clothing is a first-order variable.** Model trousers as a porous medium; compare at least none / skirt / leggings / denim.
4. **Normalisation must be explicit.** Run every comparison under two bases: (a) equal total H₂S mass emitted, and (b) equal H₂S concentration in the released gas (loud releases are larger in volume).
5. **The laminar/turbulent dichotomy is borderline.** Example: 100 mL in 1 s through a 5 mm orifice → u ≈ 5 m/s, Re ≈ 1,700 (transitional). Silent releases are likely Re ~ 10²–10³. Orifice diameter and release duration are therefore top-priority sensitivity parameters.
6. **Molecular diffusion alone is negligible on the relevant time scale.** D(H₂S, air) ≈ 1.6×10⁻⁵ m²/s [VERIFY] → diffusion length √(2Dt) ≈ 8 mm in 2 s. The silent puff therefore stays concentrated and is **advected** (by the CBL/room air) rather than diffused — this sharpens H1.
7. The v2 document has a **duplicated survey section**; v2 also relies on popular-media sources for the belief — replace with §12 evidence.

---

## 4. Hypotheses and definitions

### 4.1 Three meanings of "silent"
- **S1 — Sub-oscillation (physical silence):** flow too weak to drive anal-tissue (lip-reed-like) oscillation; no tone is produced.
- **S2 — Inaudible:** oscillation exists but the sound pressure level at the listener is below the hearing threshold at its frequency (low-frequency tones are disadvantaged; ISO 226 equal-loudness contours).
- **S3 — Masked:** audible in quiet, but masked by background noise (e.g., subway, café).

Only S1 changes the release fluid dynamics. S2 and S3 change only the **warning signal** → these isolate the psychological pathway. This separation is a key analytical device of the paper.

### 4.2 Hypotheses
- **H1 (near-field dilution):** For equal emitted H₂S, S1 releases produce higher peak odour activity at a neighbour's nose than audible (high-momentum) releases, because they bypass jet entrainment.
- **H1′ (CBL conveyor):** The silent puff's concentration penalty is amplified by the CBL transporting it to breathing zones (own and neighbour's).
- **H2 (preparedness):** Absence of an auditory warning increases perceived intensity/unpleasantness via prediction error (unwarned exposure).
- **H0:** No robust difference in nose dose; the belief is perceptual/cultural.
- **Competing physiology:** rapidly produced (loud-prone) flatus may be richer in fermentation gases (Tomlin et al. 1991; Suarez et al. 1997) → composition must be an input with a range, not fixed.

---

## 5. Module 0 — Gate 0: analytic order-of-magnitude model (Python, days)

**Goal:** before any CFD, estimate the neighbour-nose concentration ratio C_silent / C_loud.

Components:
1. **Turbulent round jet** centreline decay: C_c/C_0 ≈ K·(d_eff/(x − x₀)), with d_eff = d·(ρ_0/ρ_a)^½ and K ≈ 5 [VERIFY constant; Dowling & Dimotakis 1990].
2. **Low-momentum puff/plume:** treat as a buoyant thermal or a passive puff advected by the CBL (u ≈ 0.2 m/s) with weak mixing; bound with (a) no dilution until the nose and (b) a Gaussian puff with an assumed small turbulent diffusivity [ASSUMPTION].
3. **Jet-to-plume transition length** (momentum length scale L_M = M₀^{3/4}/B₀^{1/2}) to decide where buoyancy/CBL takes over.
4. **Clothing:** crude momentum sink — jet velocity reduced by a factor from fabric permeability [ASSUMPTION; refine in CFD].
5. **Odour threshold scaling:** 26 ppm H₂S vs threshold ~0.45–0.9 ppbv (McGinley & McGinley 2004) → required dilution ~3×10⁴–6×10⁴. Report the "detectability volume" for a typical passage.

**Outputs:** `gate0_ratio_map.png` (ratio vs Re and distance), `gate0_report.md`.
**Decision:** proceed to CFD in all cases (target venues accept either outcome), but use Gate 0 to pick CFD parameter ranges and to choose the narrative branch early.

---

## 6. Module 1 — Source (emission) model

### 6.1 Parameter table (all must be cited or flagged)

| Parameter | Range / value | Source / status |
|---|---|---|
| Volume per passage | ~30–150 mL typical | [VERIFY] Tomlin et al. 1991; Suarez et al. 1997 |
| Daily total | ~200–1500 mL | [VERIFY] primary source needed |
| Passages per day | ~10–20 | [VERIFY] |
| Major gases | N₂, H₂, CO₂, CH₄ (highly variable), O₂ | Suarez et al. 1997 |
| H₂S / CH₃SH / DMS | mean 1.06 / 0.21 / 0.08 µmol/L | Suarez et al. 1998 |
| Gas temperature | 37 °C | physiology |
| Effective orifice diameter | 2–15 mm | [ASSUMPTION] key sensitivity parameter |
| Release duration | 0.3–5 s | [ASSUMPTION] |
| Release waveform | top-hat, half-sine, multi-pulse ("staccato") | [ASSUMPTION] |
| Skin temperature | ~33–34 °C | [VERIFY] |
| Room temperature | 20–26 °C | design range |
| Sphincter tone frequency | ~100–200 Hz | [VERIFY] only non-peer-reviewed source (flatology.com); placeholder |

### 6.2 Postures
- Standing; seated on hard chair; seated on cushioned sofa; **seated with one-cheek lift** (classic manoeuvre: changes orifice geometry and seat sealing simultaneously).

---

## 7. Module 2 — Acoustics

1. **Flow-induced oscillation model:** a one- or two-mass lip-reed (brass-player embouchure) model driven by transmural pressure (Ancalle et al. 2021 describe the anal-tissue vibration mechanism). Output: oscillation onset threshold (defines S1), frequency f, source strength.
2. **Radiation to listener:** monopole-like spherical spreading → SPL at listener distance (0.5–3 m). Include rough seat/clothing attenuation [ASSUMPTION].
3. **Audibility:** compare SPL(f) with ISO 226 threshold of hearing → defines S2.
4. **Masking:** background levels for library, living room, office, café, subway [VERIFY typical dB(A)] → defines S3.
5. **Deliverable:** acoustic regime map over (flow rate, orifice diameter): S1 / S2 / S3 / audible, overlaid on the Re map from Module 0. This is the bridge figure linking "sound" to "flow".

---

## 8. Module 3 — CFD (OpenFOAM)

### 8.1 Solver setup
- Software: OpenFOAM (check fork/version available: openfoam.org vs openfoam.com; solver names differ). Use a buoyant, compressible-low-Mach solver with species transport (multi-component mixture, or simplified: air + "flatus surrogate" + passive odour scalars).
- Turbulence: RANS (k-ω SST) for parameter sweeps; **LES for the "hero" figures** (instantaneous puff structure).
- Heat transfer: heated body surfaces (skin temperature) to generate the CBL; radiation neglected [ASSUMPTION].
- Meshing: `snappyHexMesh`; refinement at the orifice, along the CBL, and at nose positions.

### 8.2 Geometry
- Human bodies: open/CC0 manikin meshes (e.g., MakeHuman export) simplified for meshing; nose sampling probes at anthropometric seated/standing nose height [VERIFY].
- Furniture: sofa (box primitives + porous cushion), chair, elevator cabin, car cabin (simplified), meeting room.
- **Clothing:** Darcy–Forchheimer porous zone wrapping the pelvis; coefficients derived from fabric air permeability for denim vs knit leggings [VERIFY ASTM D737-type data]; skirt = open bottom.
- **Cushion reservoir:** porous zone with storage (slow re-release), modelled as porous medium plus an optional first-order "storage" source/sink term [ASSUMPTION].

### 8.3 Validation (required for the preprint)
1. Free turbulent round jet: centreline velocity and concentration decay vs Dowling & Dimotakis (1990).
2. Plume/buoyant jet entrainment vs List & Imberger (1973) style relations.
3. Human CBL peak velocity vs Licina et al. (2014): 0.16–0.24 m/s range for a seated manikin.
4. Mesh-independence study on one reference case.

### 8.4 Outputs per run
- Time series of H₂S/CH₃SH/DMS at every nose probe; peak and time-integrated dose; arrival time; fields for rendering (OAV iso-surfaces, velocity, temperature).

---

## 9. Module 4 — Perception model

1. **Odour activity value (OAV):** OAV(t) = Σᵢ Cᵢ(t)/thresholdᵢ for H₂S, CH₃SH, DMS. Thresholds: H₂S from McGinley & McGinley (2004); others [VERIFY], e.g., a standard odour-threshold compilation.
2. **Breath sampling:** the nose samples only during inhalation. Tidal volume ~0.5 L, 12–16 breaths/min [VERIFY]. Compute sampled peak OAV as a function of inhalation phase relative to puff arrival → "**breath-hold strategy**" figure (probability of dodging the peak).
3. **Intensity:** log-concentration intensity scale (Greenman et al. 2004 for organoleptic scores) and a Stevens power-law alternative; report both.
4. **Adaptation:** exponential decline of perceived intensity under sustained exposure (Greenberg et al. 2013 review) → the farter (pre-exposed, adapted) vs the newcomer.
5. **Preparedness / prediction-error layer (H2):** perceived intensity I = g · I₀, with g = 1 if warned (audible) and g = γ > 1 if unwarned (S1/S2/S3) [ASSUMPTION]. Grounding literature: expectation and labels modulate odour perception (de Araújo et al. 2005; Djordjevic et al. 2008), auditory–olfactory integration (Seo & Hummel 2011), olfaction's reliance on predictive cues (Pierzchajlo et al. 2024).
   - **Break-even analysis:** compute γ* such that the psychological effect alone equals the physical effect (or overturns it when physics opposes the belief). Report: "If unwarned noses amplify by more than γ*, the belief holds regardless of fluid dynamics."
   - Also note the opposite literature direction (unpleasant sounds/negative labels can *increase* unpleasantness) → treat γ < 1 as a sensitivity case.

---

## 10. Module 5 — Scenarios ("serious & ridiculous" figure set)

Each scenario = one figure panel set. Run under both normalisation bases (§3.4).

| ID | Scenario | Question | Key comparisons |
|---|---|---|---|
| A | **Sofa duet** (two seated people, main scenario) | Who gets the higher dose, the farter or the neighbour? Silent vs loud? | S1 vs audible; clothing types; cushion reservoir on/off |
| B | **"He who smelt it dealt it"** | Does the CBL deliver the farter's own puff to their own nose first? | Arrival time farter vs neighbour; adaptation |
| C | **Elevator whodunit** (N = 4–8 occupants) | Can the culprit be identified from arrival times/order of reactions? | Bayesian source attribution from nose arrival order; silent vs loud |
| D | **Car cabin** | Recirculation vs fresh-air mode; driver vs passenger | Ventilation mode; window cracked |
| E | **Meeting room / airplane row** | Effect of mixing/displacement ventilation | Supply direction and velocity |
| F | **Subway (acoustic masking, S3)** | Physically loud but perceptually silent | Psychological layer only (physics = loud case) |
| G | **Countermeasures** | Fan, open window, hand-waving, fake cough (acoustic disguise) | Dose reduction; fake cough converts S1 → "warned"? |
| H | **One-cheek lift manoeuvre** | Does the lift trade sound for dose? | Seated sealed vs lifted |
| I | **Wardrobe study** | Denim vs leggings vs skirt vs none | Porous momentum sink |

---

## 11. Module 6 — Uncertainty quantification and a dimensionless regime map

1. **Surrogate:** run ~30–60 CFD cases (Latin hypercube over orifice diameter, duration, volume, composition, clothing, room temperature), fit a Gaussian-process (or polynomial chaos) surrogate of neighbour peak OAV.
2. **Monte Carlo:** 10⁴–10⁵ samples on the surrogate → headline number **P(SBD)** = probability that a silent (S1) release yields a higher neighbour peak OAV than an audible release, under each normalisation basis. Report with credible interval.
3. **Global sensitivity:** Sobol indices → which variable matters most (prediction: trousers and orifice diameter).
4. **Dimensionless "Silencer number":** e.g., Si = (jet momentum flux at the nose distance) / (CBL momentum flux), or a release Froude/Richardson number combining momentum, buoyancy and CBL velocity. Show a regime map: dilution-dominated (high Si) vs conveyor-dominated (low Si), with S1/S2/S3 acoustic boundaries overlaid.

---

## 12. Module 7 — Cross-cultural survey of the belief (psychology/background section)

**Purpose:** establish how widespread the Silencer conjecture is, using documentary/lexical evidence (no human-subject survey needed at this stage).

### 12.1 Evidence levels
- **A — Explicit proposition:** a proverb/saying/verse asserting silent ⇒ smellier (or loud ⇒ not smelly).
- **B — Dedicated lexeme with smell connotation:** a distinct word for a silent fart, defined by smell.
- **C — Dedicated lexeme only:** distinct word for a silent fart, no smell claim.
- **D — No evidence found** (absence ≠ absence of belief).

### 12.2 Seed table (to be verified and expanded)

| Language / region | Evidence | Level | Seed source |
|---|---|---|---|
| Mandarin/Taiwanese Chinese | Proverb 响屁不臭，臭屁不响 ("loud farts don't stink; stinky farts aren't loud"), widely cited in health media | A | cn-healthcare.com (2019); TVBS Health; HKUST Science Focus (which disputes it) |
| Hindi/Indian (film) | Mock-Sanskrit verse in *3 Idiots* ranking farts by sound, silent = deadliest | A (fictional/pop-culture) | Hirani (2009); Wikiquote summary |
| English (modern) | "Silent but deadly (SBD)" | A | popular usage [VERIFY dictionary attestation, e.g., OED/Green's Dictionary of Slang] |
| English (historical) | *fist/feist/fice*: Middle English *fisten* "break wind"; 1811 Grose defines *fice* as more obvious to the nose than the ears | B | etymonline "feist/feisty"; Grose 1811 |
| Russian | *бздеть* = to fart silently (vs *пердеть*); children's belief that quiet farts are very stinky; *пустить шептуна* ("let out a whisperer") | B | Berdy, *The Moscow Times* (2013, 2019) |
| French | *vesse/vesser* (silent fart) vs *pet/péter*; *pet honteux* = vesse | B/C | Wiktionary "vesse"; Language Log (2013); lalanguefrancaise.com |
| Dutch | *veest/vijst* cognate of *fist* | C [VERIFY meaning] | etymonline |
| Japanese | すかしっ屁 (sukashippe) = silent fart | C → check for A | jisho.org; search Japanese proverb/folk sources |
| Korean | 도둑방귀 ("thief fart", silent fart) in media; belief stated in Korean media translations | C → check for A | Asia Today (2011); HuffPost Korea [VERIFY a native proverb] |
| Finnish | *tuhnu* (silent) vs *pieru* | C [VERIFY — forum only] | Straight Dope forum |
| Others to search | German, Spanish, Portuguese, Italian (*vescia*), Polish, Czech, Arabic, Persian, Turkish, Hebrew, Swahili, Indonesian, Vietnamese, Thai | — | proverb dictionaries, Wiktionary categories, folklore collections |

### 12.3 Method
- Search per language: proverb dictionaries, Wiktionary (`fart` translations and synonyms), etymological dictionaries, folklore archives, national corpora; record exact citation, literal translation, evidence level.
- Note independent origins vs borrowings (e.g., Germanic *fist* family vs Latin *vissire* family vs Chinese proverb).
- **Outputs:** `cross_cultural_table.csv`, world map figure (choropleth by evidence level), and a short paragraph: "the belief appears independently in at least N language families".
- Caveat in text: documentary presence ≠ prevalence; a human-subject survey is listed as future work (would need IRB).

---

## 13. Figure plan and visual style

**Style guide ("serious & ridiculous"):** photoreal-ish grey manikins on a white/green floor, rigorous colour bars in correct SI or OAV units, velocity arrows and streamlines, scientific captions — staged in absurd everyday scenes (cf. livestock-aerodynamics CFD renders). Humour via titles and colour-bar annotations (e.g., OAV = 1 labelled "detectable", OAV = 10³ labelled "relationship-ending"), never via fake data. No real people, no copyrighted characters.

| Fig. | Content |
|---|---|
| 1 | Graphical abstract: two people on a sofa, silent vs loud release side by side, OAV iso-surfaces |
| 2 | Mechanistic chain diagram: sound ↔ flow ↔ dispersion ↔ nose ↔ brain |
| 3 | Acoustic regime map (S1/S2/S3/audible) over flow rate × orifice diameter, with Re contours |
| 4 | CFD validation panel (jet decay, CBL velocity) |
| 5 | Sofa duet: time series of neighbour vs farter nose OAV; LES snapshot render |
| 6 | Wardrobe study (Scenario I) + cushion reservoir |
| 7 | Breath-hold strategy: sampled peak OAV vs inhalation phase |
| 8 | Elevator whodunit: attribution accuracy vs N occupants, silent vs loud |
| 9 | Countermeasures bar chart (fan, window, waving, fake cough) |
| 10 | UQ: P(SBD) distribution + Sobol indices; Silencer-number regime map |
| 11 | Preparedness break-even γ* plot |
| 12 | Cross-cultural world map by evidence level |

Supplementary: car cabin, meeting room/airplane, cheek-lift, subway masking; animations (GIF/MP4) of LES puffs.

---

## 14. Repository structure

```
sbd/
├── README.md
├── NOTES.md                 # running log of assumptions/results per module
├── params/params.yaml       # single source of truth for all parameters (+ source/flag)
├── gate0/                   # analytic model (Python)
├── acoustics/               # lip-reed model, ISO 226 audibility, masking
├── cfd/
│   ├── geometry/            # manikins, sofa, elevator, car, room
│   ├── cases/               # OpenFOAM case templates + parameter sweep generator
│   └── validation/
├── perception/              # OAV, breath sampling, adaptation, gamma model
├── uq/                      # surrogate, Monte Carlo, Sobol
├── culture/                 # cross_cultural_table.csv, map script
├── figures/
└── manuscript/
    ├── preprint/            # LaTeX
    └── jis/                 # satirical version
```

---

## 15. Milestones

| # | Milestone | Deliverable |
|---|---|---|
| M0 | Literature/parameter verification pass | `params.yaml` with every [VERIFY] resolved or downgraded to [ASSUMPTION] |
| M1 | Gate 0 analytic model | ratio map + narrative branch decision |
| M2 | Acoustic regime map | Fig. 3 |
| M3 | CFD validation | Fig. 4, mesh study |
| M4 | Scenario A (sofa) + I (wardrobe) | Figs 1, 5, 6 |
| M5 | Remaining scenarios B–H | Figs 8, 9 + supplementary |
| M6 | Perception layer | Figs 7, 11 |
| M7 | UQ + regime map | Fig. 10, headline P(SBD) |
| M8 | Cross-cultural survey (can run in parallel from M0) | Fig. 12, table |
| M9 | Preprint manuscript | LaTeX, open code/data (Zenodo DOI) |
| M10 | J. Immat. Sci. version | Short comedic paper citing the preprint |

---

## 16. Limitations to state up front

- No human physiological measurements; source parameters (orifice diameter, waveform) are poorly constrained → handled by UQ, not hidden.
- The γ preparedness factor is not measured; only a break-even analysis is offered.
- Cross-cultural evidence is documentary, not prevalence data.
- Room-scale mixing, body motion and real clothing fit are simplified.
- Composition–flow coupling (fast fermentation → loud and rich) is treated as an input range, not modelled mechanistically.

---

## 17. Seed references

*(Carry over v2 references; add the ones below. Verify all bibliographic details.)*

**Flatus chemistry & physiology**
- Suarez FL, Springfield JR, Levitt MD (1998) Identification of gases responsible for the odour of human flatus… *Gut* 43:100–104.
- Suarez FL, Furne JK, Springfield J, Levitt MD (1997) Insights into human colonic physiology obtained from the study of flatus composition. *Am J Physiol* 272:G1028–G1033.
- Tomlin J, Lowis C, Read NW (1991) Investigation of normal flatus production in healthy volunteers. *Gut*.
- Collins SB et al. (2001) In vivo assessment of flatulence in dogs. *Am J Vet Res* 62:1014–1019.
- Ancalle DS, Finn CL, Jiang N, Stewart SA, Hu DL (2021) Physics of flatulence. *J Acoust Soc Am* 150(4 Suppl):A164.
- Danzl DF (1992) Flatology. *J Emerg Med*.

**Jets, plumes, CFD, indoor air**
- Dowling DR, Dimotakis PE (1990) Similarity of the concentration field of gas-phase turbulent jets. *J Fluid Mech* 218:109–141.
- List EJ, Imberger J (1973) Turbulent entrainment in buoyant jets and plumes. *J Hydraul Div* 99:1461–1474.
- Licina D, Melikov A, Sekhar C, Tham KW (2014) Experimental investigation of the human convective boundary layer in a quiescent indoor environment. *Build Environ* 75:79–91.
- Licina D, Melikov A, et al. (2014) Human convective boundary layer and its interaction with room ventilation flow. *Indoor Air*.
- Al Assaad D, Yang S, Licina D (2021) Particle release and transport from human skin and clothing: a CFD modeling methodology. *Indoor Air*.
- Mäck A, Spruijt MPN (2013) Validation of OpenFOAM for heavy gas dispersion applications. *J Hazard Mater* 262:504–516. *(retain only for CFD-validation methodology, not the heavy-gas argument)*

**Odour perception & psychology**
- McGinley MA, McGinley CM (2004) Comparison of field olfactometers… H₂S. *Water Sci Technol*.
- Greenman J et al. (2004) Organoleptic intensity scale for oral malodor. *J Dent Res*.
- Greenberg MI, Curtis JA, Vearrier D (2013) The perception of odor is not a surrogate marker for chemical exposure. *Clin Toxicol*.
- de Araújo IE et al. (2005) Cognitive modulation of olfactory processing. *Neuron* 46:671–679.
- Djordjevic J et al. (2008) A rose by any other name: would it smell as sweet? *J Neurophysiol* 99:386–393.
- Dalton P (1996) Odor perception and beliefs about risk. *Chem Senses* 21:447–458.
- Seo H-S, Hummel T (2011) Auditory–olfactory integration. *Chem Senses* 36:301–309.
- Pierzchajlo S et al. (2024) Olfactory categorization is shaped by a transmodal cortical network for evaluating perceptual predictions. *J Neurosci* 44:e1232232024.
- ISO 226 (latest edition) Acoustics — Normal equal-loudness-level contours. [VERIFY edition]

**Cultural / linguistic**
- Hirani R (dir.) (2009) *3 Idiots* [film]. Vinod Chopra Films.
- Grose F (1811) *Dictionary of the Vulgar Tongue* (entry "fice").
- Online Etymology Dictionary: "feist", "feisty", "fart".
- Berdy MA (2013) Stinking to high heaven; (2019) Breaking wind the Russian way. *The Moscow Times*.
- Language Log (2013) "Ornery fystes".
- Wiktionary: "vesse".

**Non-peer-reviewed prior "data" (cite as such)**
- Invisible College of Experimental Flatology, flatology.com (2020–2022): claims ~1,600 recorded passages with sound and VOC measured at ~2 inches; reports no evidence that quieter is smellier (weak positive loudness–odour correlation) and proposes that low-frequency smelly passages may fall below audibility (= our S2). Self-described as tongue-in-cheek; discuss in the Introduction as the only prior attempt.
