# Chemistry layer for the ChemRxiv version (part 1: odorants and buoyancy)

*2026-10-17 · code: `chem/odorants.py`, `chem/buoyancy.py` · numbers: `chem/odorants.json`, `chem/buoyancy.json`.
Updated the same day after a full-text pass of 15 papers (Part 3 below).*

## 1. Which molecule carries the odour

OAV shares for the mean composition of Suarez et al. 1998 (Table 1, umol/L converted to ppbv at 37 °C):

| thresholds | composition | total OAV (undiluted) | H₂S | MeSH | DMS |
|---|---|---|---|---|---|
| trained panel (Nagata 2003) | all | 1.4 × 10⁵ | 46 % | **54 %** | 0.5 % |
| | men | 1.1 × 10⁵ | 34 % | **65 %** | 0.6 % |
| | women | 2.0 × 10⁵ | **56 %** | 44 % | 0.3 % |
| population (Amoore 1983; DMS Wilby 1969) | all | 7.7 × 10³ | 43 % | 43 % | 13 % |
| | men | 5.9 × 10³ | 32 % | **51 %** | 17 % |
| | women | 1.0 × 10⁴ | **54 %** | 37 % | 9 % |
| trained panel (Nagata 2003) | Tangerman 2009 (n = 28) | 8.9 × 10⁴ | 10 % | **88 %** | 1 % |
| population | Tangerman 2009 | 5.7 × 10³ | 8 % | **60 %** | 32 % |
| lowest literature (Tangerman 2009) | Suarez all | 6.8 × 10⁵ | 17 % | **82 %** | 2 % |
| | Tangerman 2009 | 6.1 × 10⁵ | 3 % | **94 %** | 3 % |

Tangerman 2009 (GC, n = 28) measured H₂S 149, MeSH 216 and DMS 144 nM (means), i.e. MeSH ≥ H₂S. Suarez 1998 found
H₂S about five times MeSH. Tangerman suggests the pinto-bean diet of the Suarez study raised H₂S [their
interpretation]. The two datasets therefore disagree on which gas dominates the *concentration*.

**Findings.**
- **Methanethiol carries at least as much of the odour as hydrogen sulfide, and probably most of it.**
  - With the Suarez composition MeSH and H₂S share the OAV about equally: MeSH is one fifth of H₂S in concentration, but
    its threshold is 5–6× lower.
  - With the Tangerman composition, or with the lowest literature thresholds, MeSH carries 60–94 %.
  - Tangerman's own panel came to the same conclusion directly. Gas mixtures with MeSH above its "flatus threshold"
    smelled like most real passages; H₂S and DMS were mostly below theirs.
- **The balance tips with diet and sex.** In men MeSH dominates; in women, whose H₂S is three times higher, H₂S does.
- **DMS** matters only with population thresholds (9–17 %).
- **Tension with the judges.** Suarez et al. found that judged odour correlated best with H₂S (r = 0.64 / 0.44) and
  less with MeSH (r = 0.25 / 0.30; Table 2, n = 54). One reading is that H₂S varies more between passages, so it
  explains more of the *variance*, while MeSH supplies a large, steadier share of the *level*. The per-passage joint
  data needed to test this are not published [open].
- OAV summation assumes additivity; mixture suppression is not modelled.

### Dilution anchor: how much does a passage dilute before the nose?

Tangerman 2009 defines an "experimental flatus perception threshold": the lowest source concentration at which *all*
panel members detected odour when 100 mL was released below the nose (750, 50 and 750 nM for H₂S, MeSH, DMS). Divided
by a perception threshold, this gives the dilution between release and nose in that test.

| quantity | H₂S | MeSH | DMS |
|---|---|---|---|
| implied dilution, Tangerman's lowest literature thresholds | 7.5 × 10⁴ | 1.3 × 10⁵ | 9.4 × 10⁴ |
| implied dilution, Nagata 2003 thresholds | 4.4 × 10⁴ | 1.7 × 10⁴ | 6.0 × 10³ |

The Gate 0 breath-averaged dilution from the Monte Carlo (silent and audible pooled) has a median of 1.8 × 10³ at the
neighbour (10–90 %: 2.5 × 10²–2.9 × 10⁴) and 8.0 × 10² at the releaser's own nose.

- The anchor lies 6× to 70× above the Gate 0 median, near Gate 0's 90th percentile.
- The anchor is biased upward. Its criterion is that the *least* sensitive panellist detects, and it is divided by
  thresholds of the *most* sensitive. Both inflate the implied dilution.
- **Reading.** Gate 0, which aims the puff at the nose, is at the concentrated end of what a real nose receives. This
  is consistent with treating it as an upper bound of exposure. It agrees with Tangerman to about one order of
  magnitude, which is all the anchor can support.
- Tangerman's own assumption (100 mL into 4–8 m³, dilution 4–8 × 10⁴) is a stated assumption, not a measurement.

## 2. Removal experiments as a check on OAV summation and the Stevens exponent

Suarez 1998 Table 3 treated flatus with zinc acetate (precipitates H₂S and thiols as ZnS and zinc thiolate) or
activated charcoal (adsorbs all three), and two judges rated the odour (0–8 category scale).

| treatment | total OAV before → after | OAV ratio | predicted intensity ratio, n = 0.20 / 0.28 / 0.45 | judges' rating ratio |
|---|---|---|---|---|
| zinc acetate (n = 16) | 1.0 × 10⁵ → 7.3 × 10³ | 0.072 | 0.59 / 0.48 / 0.31 | 0.28, 0.59 |
| activated charcoal (n = 9) | 2.5 × 10⁵ → 9.4 × 10² | 0.004 | 0.33 / 0.21 / 0.08 | 0.02, 0.06 |

- **Zinc acetate.** The judges' ratios fall inside the band predicted by the Stevens law over its literature range of
  exponents. This is an independent check of the intensity model with real flatus.
- **Activated charcoal.** Near-complete removal is rated far weaker than the power law predicts. This is the known
  failure of a pure power law near threshold, where intensity drops faster (a threshold-corrected or sigmoid law). The
  residual concentrations are also close to the analytical limits. It does not affect the silent/audible comparison,
  which concerns supra-threshold ratios.
- The residual odour after zinc treatment is not from DMS: DMS is only 2 % of the residual OAV, which is still
  dominated by unremoved H₂S and MeSH.

## 3. What makes a passage rise or sink

The reduced gravity g′ is split into a thermal part (37 °C gas in 22 °C air) and a compositional part. Inputs are the
16 dry-basis compositions of Suarez 1997 Table 1 and air at 50 % RH. Water saturation of flatus is not measured, so it
is bracketed.

| water in flatus | g′ median (range), m s⁻² | thermal | compositional median (range) | sinking while hot | heavier than air after cooling |
|---|---|---|---|---|---|
| dry | +1.66 (−0.71 to +4.65) | +0.47 | +1.25 (−1.25 to +4.39) | 12 % | 38 % |
| saturated at 37 °C | +1.81 (−0.42 to +4.61) | +0.47 | +1.40 (−0.94 to +4.34) | 6 % | 25 % |

- **Composition dominates.** For the median passage it contributes three times more than temperature.
  - H₂ (2 g mol⁻¹) and CH₄ (16 g mol⁻¹) make flatus light.
  - CO₂ (44 g mol⁻¹) makes it heavy. The compositional term correlates with %CO₂ at r = −0.80.
- **Water vapour** (18 g mol⁻¹) lightens it slightly.
- **After cooling**, a quarter to a third of passages are denser than air. The odour of a CO₂-rich passage therefore
  sinks once it has mixed to room temperature, which matters for children, pets and anyone lying down
  [interpretation].

# Part 2: reactivity, sorption, biochemistry, receptors (2026-10-17)

*Code: `chem/reactivity.py` → `chem/reactivity.json`. Literature pass by a background agent; DOIs verified on OpenAlex.
Full texts read: Atkinson 2004 and Levitt 1999. Substantially read: Duan 2012 and Haag 2019. The 15 further full
texts supplied by the author were read the same day; the statements below are updated from them.*

## 3. The odorants are conserved tracers over 120 s, against gas-phase chemistry

Rate constants are IUPAC recommended values at 298 K (Atkinson et al. 2004).

| scenario | H₂S lifetime / lost in 120 s | CH₃SH | DMS |
|---|---|---|---|
| office, measured low (OH 0.6 × 10⁵ cm⁻³, O₃ 0.7 ppb) | 40 d / 0.003 % | 5.7 d / 0.03 % | 28 d / 0.005 % |
| office, measured high (OH 9.8 × 10⁵, O₃ 2.6 ppb) | 2.5 d / 0.06 % | 8.6 h / **0.4 %** | 1.8 d / 0.08 % |
| worst case [ASSUMPTION] (OH 10⁶, O₃ 40 ppb) | 2.5 d / 0.06 % | 8.4 h / 0.4 % | 1.5 d / 0.09 % |
| hypochlorite cleaning (Cl 10⁶ cm⁻³) | 3.5 h / 0.9 % | 1.2 h / 2.8 % | 0.8 h / 4.0 % |

- Gas-phase loss over a passage is below 0.5 % in ordinary rooms. Treating the odorants as non-reacting scalars is
  justified by two to three orders of magnitude.
- **Missing rate constants.** IUPAC gives no rate constant for O₃ + H₂S or O₃ + CH₃SH. O₃ + DMS is an upper limit
  (< 10⁻¹⁸ cm³ s⁻¹).
- **Indoor oxidant levels are now measured values.** Fiorentino et al. 2023 measured OH directly in an office over
  five experiments: weighted means 0.62–9.79 × 10⁵ cm⁻³; daily mean O₃ 0.7–2.6 ppb. (The earlier draft cited this
  work as "2022" and as abstract only.) The worst case is an assumption.
- **No gas-phase O₃ + DMS rate is reported by Barnes et al. 2006 either** (checked in the full text).
  The IUPAC upper limit stands.

**Surface deposition is the unconstrained sink (null result).** No deposition velocity for H₂S, CH₃SH or DMS on indoor
surfaces, textiles or skin could be found. For S/V = 3 m⁻¹, the loss in 120 s is:

| v_d (cm/s) | 0.2 | 0.05 | 0.01 | 0.002 |
|---|---|---|---|---|
| loss in 120 s | 51 % | 16.5 % | 3.5 % | 0.7 % |

- The passive-scalar assumption is therefore safe against chemistry but sensitive to deposition above
  ~0.01 cm/s. This should be stated as an explicit, bounded uncertainty.
- Deposition would act more on the silent release, which lingers in the seat–backrest wedge and along the body. This
  strengthens, not weakens, the sofa result [interpretation].

## 4. Sorption on fabrics (null result)

- No peer-reviewed partition, uptake or breakthrough data exist for H₂S, CH₃SH or DMS on cotton, polyester, wool, PU
  foam or carbon textiles.
- Ohge 2005 (ordinary clothing removes 22 % of sulfide) appears to be the only direct measurement. It cannot be split
  by fibre.
- The method template for a future measurement is the cloth–air partition ratio on cotton measured by Yu, Wania &
  Abbatt 2022. They measured carbonyl, carboxylic-acid and aromatic VOC series; no sulfur gas was included, and their
  correlations must not be extrapolated to H₂S, CH₃SH or DMS.
- Polyester-vs-cotton odour-retention studies concern carboxylic acids, not sulfur gases. They are not transferable.

## 5. Colonic sulfur biochemistry (mechanism box)

**Production.**
- H₂S comes from sulfate-reducing bacteria (Gibson 1993) and, at least as importantly, from cysteine degradation,
  whose genes are widespread in the gut microbiome (Braccia 2021; genomic prediction).
  - SRB outcompete methanogens for H₂ by affinity: K_s ≈ 1 µmol/L for *Desulfovibrio vulgaris* vs ≈ 6 µmol/L for
    methanogens (Gibson 1993). This is why sulfide and methane production tend to exclude each other.
  - Braccia 2021's "1.1 %" for genomes carrying a secondary cysteine-degrading gene is 5/4,644 = **0.11 %**. The
    printed percentage is a typo; cite the count.
- CH₃SH comes mainly from methionine γ-lyase. A primary citation is still needed.
- **The colonic origin of DMS is open.** In rat caecum, CH₃SH is demethylated, not methylated (Levitt 1999).

**Detoxification** (Levitt 1999, read in full).
- Caecal mucosa oxidises H₂S with V_max ≈ 21 nmol min⁻¹ mg⁻¹ and K_m ≈ 25 ppm. 94 % of the label ends as thiosulfate,
  and the rate is about 8× the liver's.
- CH₃SH is demethylated to H₂S; no DMS was detected.
- The paper says oxidation is "10,000×" faster than methylation, but its own rates give ≈ 165×. Quote the rates, not
  the ratio.
- Rhodanese, not thiol S-methyltransferase, is the main H₂S-detoxifying enzyme in human colon: V_max 14.6 nmol
  mg⁻¹ min⁻¹, K_m 8.8 mM (Picton 2002). No product was found with TMT or TPMT.
- SELENBP1 is a human methanethiol oxidase with an apparent K_m of 4.8 nM for MeSH (Pol 2018). Mutations cause
  extraoral halitosis; it is the obvious enzyme for clearing absorbed MeSH.
- **Free vs total sulfide.** Most faecal sulfide is bound (acid-labile, probably as metal sulfides). Free H₂S is
  < 5 % of the total: mean total 0.8 µmol/g wet weight, free < 0.04 µmol/g (Tangerman 2009, citing earlier work).
  Acidic assays (methylene blue) measure total, not free, sulfide. Only the free fraction can enter the gas.

**Concentration is independent of passage volume.** Suarez 1997 Table 3 (full text checked again 2026-10-17) gives
r(volume, [H₂S]) = 0.195, not significant. Mechanistic inference: sulfur gases are trace products under a fast,
saturable mucosal sink (~95 % of caecal H₂S turns over per minute), whereas bulk volume is set by N₂, CO₂, H₂ and
CH₄. Concentration therefore reflects a local production/consumption balance, not the carrier volume [inference].

**Diet.**
- A meat-rich diet raises faecal sulfide from 0.22 to 3.38 mmol/kg (0 vs 600 g meat per day; Magee 2000, n = 5).
  This is total sulfide, and the sample is small.
- An animal-based diet raised faecal H₂S, but 2 of 11 subjects produced more on a plant diet (Teigen 2022).
- No study links cruciferous vegetables to flatus odour. Do not claim it.

## 6. Why we are so sensitive to thiols (hedged)

- Copper potentiates some thiol receptors:
  - mouse MOR244-3 (Duan 2012): > 20-fold EC₅₀ shift for MTMT with 30 µM Cu²⁺;
  - human OR2T11 (Li 2016): copper-dependent responses to straight-chain thiols with one to four carbons, including
    MeSH. **OR2T11 does not respond to H₂S**, which Li et al. attribute to its weaker Lewis basicity toward copper;
  - human OR2M3 (Haag 2019): ~4-fold, a Hill-coefficient change rather than an EC₅₀ shift.
- **Copper is present.** Human nasal mucus contains about 16 µg/dL Cu (≈ 2.5 µM; Block 2017, citing earlier work).
  The receptor assays use 30 µM added Cu²⁺, so the in-vivo relevance is plausible but not shown.
- **Odour-chemistry link [inference].** If a dedicated copper-gated thiol receptor responds to MeSH but not to H₂S,
  this is a receptor-level reason, independent of thresholds, why MeSH is the "foul" note of flatus.
- **This is not a general mechanism.**
  - For methanethiol, the copper effect appeared only at much higher concentrations (Duan 2012).
  - OR1A1 and OR2W1 respond to their sulfur ligands without copper (Haag 2019).
  - Zhang 2018 found a second copper-dependent mouse MTMT receptor (Olfr1019) and a third (Olfr15) without a copper
    effect. It tested only MTMT, so it says nothing about MeSH or H₂S.
- "Block 2017 PNAS" does not exist as remembered. The relevant papers are Block 2015 PNAS (vibrational theory) and
  Block 2017 Nat. Prod. Rep. (review). A DMS threshold quoted in Block 2017 refers to seabirds, not humans; do not use it.
- Ecological explanations (spoilage, predators) are hypotheses, not tested results.

## What this adds to a ChemRxiv paper

1. **Odorant inventory.** MeSH ≈ H₂S, and a removal-experiment check of the intensity model.
2. **Buoyancy from composition.**
3. **"Odorants as conserved tracers."** Quantitative, with deposition as the stated sink.
4. **Sorption.** A short null-result subsection.
5. **Biochemistry box.** Explains why odorant concentration is decoupled from passage volume, which underpins the
   "as emitted" comparison.
6. **Receptor paragraph.** OR2T11 (MeSH yes, H₂S no) and nasal copper; still hedged.
7. **Dilution anchor.** Tangerman's experimental flatus threshold supports Gate 0 as an upper bound, to an order of
   magnitude.
