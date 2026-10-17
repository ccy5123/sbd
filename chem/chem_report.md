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
