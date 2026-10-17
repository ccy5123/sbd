# Chemistry layer for the ChemRxiv version (part 1: odorants and buoyancy)

*2026-10-17 · code: `chem/odorants.py`, `chem/buoyancy.py` · numbers: `chem/odorants.json`, `chem/buoyancy.json`.
Parts 3–6 (gas-phase reactivity, sorption, colonic sulfur biochemistry, thiol receptors) await the literature pass.*

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

**Findings.**
- **Methanethiol carries as much of the odour as hydrogen sulfide.** Its concentration is one fifth of H₂S, but its
  threshold is 6–5× lower.
- **The balance tips with diet and sex.** In men MeSH dominates; in women, whose H₂S is three times higher, H₂S does.
- **DMS** matters only with population thresholds (9–17 %).
- **Tension with the judges.** Suarez et al. found that judged odour correlated best with H₂S (r = 0.64 / 0.44) and
  less with MeSH (r = 0.25 / 0.30; Table 2, n = 54). One reading is that H₂S varies more between passages, so it
  explains more of the *variance*, while MeSH supplies a large, steadier share of the *level*. The per-passage joint
  data needed to test this are not published [open].
- OAV summation assumes additivity; mixture suppression is not modelled.

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
Full texts read: Atkinson 2004 and Levitt 1999. Substantially read: Duan 2012 and Haag 2019. Everything else is at
abstract level; the full texts were requested from the author.*

## 3. The odorants are conserved tracers over 120 s, against gas-phase chemistry

Rate constants are IUPAC recommended values at 298 K (Atkinson et al. 2004).

| scenario | H₂S lifetime / lost in 120 s | CH₃SH | DMS |
|---|---|---|---|
| indoor typical (OH 10⁵ cm⁻³, O₃ 10 ppb) | 25 d / 0.006 % | 3.5 d / 0.04 % | 13 d / 0.01 % |
| indoor upper ≈ outdoor day (OH 10⁶) | 2.5 d / 0.06 % | 8.4 h / **0.4 %** | 1.5 d / 0.09 % |
| hypochlorite cleaning (Cl 10⁶ cm⁻³) | 3.5 h / 0.9 % | 1.2 h / 2.8 % | 0.8 h / 4.0 % |

- Gas-phase loss over a passage is below 0.5 % in ordinary rooms. Treating the odorants as non-reacting scalars is
  justified by two to three orders of magnitude.
- **Missing rate constants.** IUPAC gives no rate constant for O₃ + H₂S or O₃ + CH₃SH. O₃ + DMS is an upper limit
  (< 10⁻¹⁸ cm³ s⁻¹).
- **Indoor oxidant levels** are medium confidence: OH from Fiorentino 2022 (abstract only); the indoor O₃ citation is
  not yet pinned down.

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
- The method template for a future measurement is the cloth–air partitioning of VOCs on cotton, log K ≈ 5–8 (Yu,
  Wania & Abbatt 2022, abstract only).
- Polyester-vs-cotton odour-retention studies concern carboxylic acids, not sulfur gases. They are not transferable.

## 5. Colonic sulfur biochemistry (mechanism box)

**Production.**
- H₂S comes from sulfate-reducing bacteria (Gibson 1993) and, at least as importantly, from cysteine degradation,
  whose genes are widespread in the gut microbiome (Braccia 2021; genomic prediction).
- CH₃SH comes mainly from methionine γ-lyase. A primary citation is still needed.
- **The colonic origin of DMS is open.** In rat caecum, CH₃SH is demethylated, not methylated (Levitt 1999).

**Detoxification** (Levitt 1999, read in full).
- Caecal mucosa oxidises H₂S with V_max ≈ 21 nmol min⁻¹ mg⁻¹ and K_m ≈ 25 ppm. 94 % of the label ends as thiosulfate,
  and the rate is about 8× the liver's.
- CH₃SH is demethylated to H₂S; no DMS was detected.
- The paper says oxidation is "10,000×" faster than methylation, but its own rates give ≈ 165×. Quote the rates, not
  the ratio.
- Rhodanese, not thiol S-methyltransferase, is the main H₂S-detoxifying enzyme (Picton 2002, abstract only).
  SELENBP1 is a human methanethiol oxidase (Pol 2017, abstract only).

**Concentration is independent of passage volume.** Suarez 1997 Table 3 (full text checked again 2026-10-17) gives
r(volume, [H₂S]) = 0.195, not significant. Mechanistic inference: sulfur gases are trace products under a fast,
saturable mucosal sink (~95 % of caecal H₂S turns over per minute), whereas bulk volume is set by N₂, CO₂, H₂ and
CH₄. Concentration therefore reflects a local production/consumption balance, not the carrier volume [inference].

**Diet.**
- A protein-rich diet raises colonic sulfide (Magee 2000, abstract only).
- An animal-based diet raised faecal H₂S, but 2 of 11 subjects produced more on a plant diet (Teigen 2022).
- No study links cruciferous vegetables to flatus odour. Do not claim it.

## 6. Why we are so sensitive to thiols (hedged)

- Copper potentiates some thiol receptors:
  - mouse MOR244-3 (Duan 2012): > 20-fold EC₅₀ shift for MTMT with 30 µM Cu²⁺;
  - human OR2T11 (Li 2016, full text needed);
  - human OR2M3 (Haag 2019): ~4-fold, a Hill-coefficient change rather than an EC₅₀ shift.
- **This is not a general mechanism.**
  - For methanethiol, the copper effect appeared only at much higher concentrations (Duan 2012).
  - OR1A1 and OR2W1 respond to their sulfur ligands without copper (Haag 2019).
  - Whether copper dependence generalises is tested by Zhang 2018 (full text needed).
- "Block 2017 PNAS" does not exist as remembered. The relevant papers are Block 2015 PNAS (vibrational theory) and
  Block 2017 Nat. Prod. Rep. (review).
- Ecological explanations (spoilage, predators) are hypotheses, not tested results.

## What this adds to a ChemRxiv paper

1. **Odorant inventory.** MeSH ≈ H₂S, and a removal-experiment check of the intensity model.
2. **Buoyancy from composition.**
3. **"Odorants as conserved tracers."** Quantitative, with deposition as the stated sink.
4. **Sorption.** A short null-result subsection.
5. **Biochemistry box.** Explains why odorant concentration is decoupled from passage volume, which underpins the
   "as emitted" comparison.
6. **Receptor paragraph.** Hedged, pending two full texts.
