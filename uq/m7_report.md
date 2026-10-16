# M7 report — uncertainty, regime map and the headline P(SBD)

*2026-10-16 · code: `uq/run_m7.py` · numbers: `uq/results.json` · figure: `figures/fig10_regime_uq.png`*

## Deviation from the plan

PLAN.md §11 asked for a CFD Latin-hypercube surrogate (30–60 cases). One sofa branch costs 1–2 h on 4 cores, so that
design is out of reach for now. **The surrogate is the Gate 0 analytic model** (validated against the M3 jet and the
CBL within the stated factors). It uses the same priors (20 000 Monte Carlo pairs, seed 20261016).

The two Scenario A CFD branches (M4) are used as a check. They show what Gate 0 does not model: **routing** by posture
and furniture.

## (a) Regime map

Panel (a) shows log₁₀ R, with R = C_silent / C_audible, inhalation-averaged and at equal emitted mass. It is plotted
against two axes: the Silencer number of the audible comparator, Si = u₀/u_h, and the travel time to the nose. Room air
has K = 10⁻³ m²/s.

- **Acoustic onset.** Si_onset = u_onset/u_h = **197** (vertical line). To the left of it the comparator is not
  audible (regime S1), so only the region to its right is a silent-vs-audible pair. The silent reference release has
  Si = 4.7.
- **Perceptual band.** |log R| < log(1 + Weber C) = log 1.28 is the concentration JND (dashed contour). Below and to
  the right of the contour the silent release is perceptibly stronger.
- **Theorem 2.** R → 1 as travel time grows, at any Si. The colour fades upward.
- **Readings at the nominal travel times (dotted lines).**
  - **Own nose (6.7 s).** The JND contour crosses this line at Si ≈ 110, left of the onset. So *every* audible
    comparator is perceptibly less concentrated than an equal-mass silent release.
  - **Neighbour (12.5 s).** The contour crosses at Si ≈ 200, i.e. at the onset itself. A barely audible comparator is
    indistinguishable; only louder ones (higher Si) fall into the "silent perceptibly worse" zone.

The equal-mass map is the most favourable framing for the belief. It holds volume fixed, which real passages do not
(see (c)).

## (b) What decides the ratio

First-order Sobol indices of log₁₀ R are computed with the given-data (binning) estimator: 20 quantile bins, bias
(B − 1)/N removed, 200 bootstrap resamples.

**Caveat.** Silent/audible pairs come from rejection sampling, so the inputs are not independent and a Saltelli design
is impossible. The indices are therefore "share of variance explained by each input alone", not an exact variance
decomposition. ΣS₁ below 1 signals interactions and dependence.

| rank | neighbour · as emitted (ΣS₁ = 0.96) | neighbour · equal mass (ΣS₁ = 0.64) | own nose · as emitted (ΣS₁ = 0.89) |
|---|---|---|---|
| 1 | silent volume 0.46 | eddy diffusivity K 0.35 | silent volume 0.38 |
| 2 | eddy diffusivity K 0.16 | audible volume 0.20 | eddy diffusivity K 0.23 |
| 3 | audible volume 0.16 | silent volume 0.04 | audible orifice 0.10 |
| 4 | audible orifice 0.08 | room air speed 0.02 | audible volume 0.09 |
| 5 | silent orifice 0.05 | audible orifice 0.01 | silent orifice 0.06 |

The 90 % bootstrap intervals are ±0.01 or narrower and are listed in `uq/results.json`.

- **As emitted, the ratio is decided by how much gas each passage carries** (the two volumes, about 0.6 of the
  variance), not by how it leaves.
- **At equal mass, the near-field mixing (K) matters most.** Volume still matters through the source size and
  release duration.
- **Sphincter onset pressure, C_d, g′ and inhalation time each explain less than 0.5 %.** The valve physics decides
  *whether* a passage is heard, not *how strong* it smells.

## (c) Headline: physics, then the nose

Each row is a share of random silent/audible pairs, with the JND applied as a concentration ratio of 1.28.
P(R > 1) is given with its bootstrap 90 % interval.

| case | P(R > 1) [90 % CI] | median R | silent perceptibly worse | indistinguishable | audible perceptibly worse |
|---|---|---|---|---|---|
| neighbour · as emitted | **0.47** [0.46, 0.47] | 0.92 | 0.37 | 0.19 | 0.44 |
| neighbour · equal mass | 0.93 [0.92, 0.93] | 1.35 | 0.54 | 0.44 | 0.02 |
| own nose · as emitted | 0.56 [0.56, 0.57] | 1.15 | 0.46 | 0.19 | 0.35 |
| own nose · equal mass | 0.93 [0.92, 0.93] | 1.73 | 0.68 | 0.29 | 0.03 |
| neighbour · as emitted · denim | 0.31 [0.31, 0.32] | 0.63 | 0.22 | 0.20 | 0.58 |

Wardrobe effect at the neighbour, as emitted (P(R > 1)): none 0.47, skirt 0.38, leggings 0.39, chino 0.31,
denim 0.31. Fabric strips the jet momentum from both releases, which removes the silent release's mixing advantage.
What remains is the larger volume of loud passages, so R falls further below 1 (Gate 0 report §5).

**Reading.**
- As passages are actually emitted, a silent one is stronger at the neighbour's nose in **47 %** of pairs. That is a
  coin flip, and only 37 % are *perceptibly* stronger.
- The equal-mass framing (0.93) answers a different question: "the same gas, released quietly". Nobody gets to
  compare that in daily life.

### The memory layer (from M6, Fig. 13)

The belief is formed from *remembered* passages. The selection model (Theorem 3, `perception/selection.py`) maps the
base rate p_S (the fraction of a neighbour's passages that the bystander smells) to the probability that a
remembered silent passage seems stronger than a remembered audible one.

| p_S | 0.93 (Gate 0 upper bound) | 0.75 | 0.50 | 0.25 | 0.10 |
|---|---|---|---|---|---|
| P(belief) | 0.53 | 0.63 | 0.78 | **0.91** | 0.97 |

Truth over all passages: 0.49.

**Base rate p_S.** A literature search (2026-10-16) found **no published measurement** of how often bystanders smell
a neighbour's flatus (null result). All 11 component papers were then read in full; the numbers come from
`uq/observer_ps.py` → `uq/observer_ps.json`.

The method applies observer models from the literature to the same 20 000 Gate 0 passages, in the living room. The
puff centre is still placed on the neighbour's nose, so each p_S is an **upper bound for that observer**.

| observer | OAV scale | spread (binary steps) | p_S | memory belief | truth |
|---|---|---|---|---|---|
| Gate 0 (Nagata 2003 trained-panel thresholds, deterministic) | 1 | — | 0.93 | 0.53 | 0.49 |
| attentive, Wilby 1969 recognition medians | 1/10 | 2.0 | 0.68 | 0.67 | 0.50 |
| attentive, Amoore & Hautala 1983 population thresholds | 1/20 | 2.0 | 0.59 | 0.73 | 0.50 |
| **distracted (everyday)**: 50 % response at 26× threshold | 1/520 | 3.5 | **0.21** | **0.91** | 0.50 |
| distracted, clothed emitter (−22 % sulfide, Ohge 2005) | 1/667 | 3.5 | 0.19 | 0.92 | 0.51 |
| distracted, but sound cues attention for audible passages | 1/520 (audible 1/20) | 3.5 (2.0) | 0.31 | 0.81 | 0.32 |

- **Thresholds.** Nagata's triangle-bag thresholds (H₂S 0.41 ppb, CH₃SH 0.07 ppb) are 10–23× lower than population
  values:
  - Amoore & Hautala 1983 Table 2: H₂S 8.1 ppb, CH₃SH 1.6 ppb;
  - Wilby 1969 Table V, recognition medians from 35 untrained people: H₂S 4.1 ppb, CH₃SH 0.80 ppb.
- **Spread.** Population thresholds have SD 1.97 ≈ 2 binary steps (Amoore & Hautala 1983, p. 286). One person's
  thresholds vary about as much over time (Stevens et al. 1988: typically a ~2000-fold within-person range, near-equal
  subject means). So detection is treated as a per-passage probability, Φ(log₂ OAV / SD).
- **Distraction.** A bystander is not expecting an odour. Amoore & Hautala's warning line (from Whisman et al. 1978,
  more than 1 600 undirected/misdirected people): 50 % of distracted people respond at 26× threshold, SD 3.5 binary
  steps. They note the data do not support extrapolation below the 50 % level, so the distracted row carries that
  extra uncertainty.
- **Sound-cued attention (last row).**
  - Distraction changes *noticing*, not sensory magnitude (Forster & Spence 2018; Ashkenazi & Marks 2004). So
    perceived intensity always uses the attentive OAV; only the detection probability depends on the observer state.
  - If a sound makes the bystander attentive for that passage, P(smelled | heard) rises from 0.21 to 0.60. That
    shrinks the Berkson gap from 0.81 to 0.39, and the belief falls from 0.91 to 0.81. It stays far above the truth.
  - The "truth" column here is over all passages through this observer's nose: the observer genuinely smells audible
    passages more often (0.32).
  - So cueing *weakens* the selection effect but does not remove it. Across all observer models the belief stays at
    0.67–0.92.
- **Routing (not in the table).** Rim & Novoselac 2009 tested a near-floor source behind one occupant: about 1.2×
  ambient at the mouth in stratified air, about 1× in mixed air. Olmedo et al. 2012 found a neighbour at 0.35–1.1 m
  inhales about the fully mixed room level under mixing ventilation. Neither tested a seat-level puff; both only
  suggest that a puff centred on the neighbour's nose is optimistic. The M4 chimney is the strongest evidence that it
  is.
- **Emitter-side anchor (indirect).** Bolin & Stanton 1998 (n = 120, 3-day diaries) report flatus rated odorous on
  69 % of days for men (12.7 passages/day) and 47 % of days for women (7.1/day). They report per day, not per
  passage. If passages are independent, about 0.09 of passages were odorous to the emitter [INFERRED, low]. Bounds:
  0.05 if one odorous passage per flagged day; 0.5–0.7 if every passage on a flagged day was odorous. The authors
  also suggest men "may be more willing to admit to aroma".
- **Anosmia.** Olfactory dysfunction affects 7.5 % of identification-test samples with mean age ≤ 55, and 34.5 % above
  55 (Desiato et al. 2021). Total anosmia is about 1 in 500 (Amoore & Hautala). Specific anosmia to sulfur compounds
  was not tested by Croy et al. 2015.

**Bracket (revised): p_S ≈ 0.1–0.6, central ≈ 0.2** [ASSUMPTION, low-moderate confidence; up from low].
- Upper end: attentive observer with the puff on the nose.
- Central: distracted observer, which is the everyday case; routing would lower it.
- Lower end: the Bolin emitter-side estimate.

This gives a memory-layer belief of **0.73–0.97, central ≈ 0.91**, against a truth of 0.49–0.51: a strong belief built
on a coin-flip truth.

## CFD check: routing that Gate 0 does not model

In the M4 sofa duet (one realisation, RANS, 30 s window) the silent release was carried up the backrest chimney and
never reached a breathing zone. The jet escaped the chimney and reached the neighbour's head region.

Breathing-zone R ≈ 10⁻¹⁰–10⁻¹⁴. This is far outside the Gate 0 distribution and in the *opposite* direction from the
belief.

So geometry can dominate every factor in panel (b). The Gate 0 headline is a statement about well-mixed transport, not
about any particular sofa. Posture variants (M4 sensitivities) are deferred.

## Summary

- **Physics.** As emitted, P(silent stronger at the neighbour) = 0.47. Equal-mass releases favour silent at the
  neighbour in 0.93 of pairs, but over half of those differences are below the JND. Real seating geometry can
  overturn either result.
- **Perception.** At the JND, 37 % of as-emitted pairs are perceptibly worse for silent and 44 % for audible.
- **Memory.** Selection alone turns 0.49 into ~0.9 at plausible base rates.

  > The belief is a memory artefact, not a measurement.

## Caveats

- The surrogate is analytic: there is no CFD-based UQ, and routing is absent.
- The Sobol inputs are dependent, so the indices are descriptive (see (b)).
- The JND applies only to concentration ratios. Intensity curvature (Stevens n) is not used here; it is in M6.
- p_S is unmeasured. The memory-layer numbers are conditional on the bracket. The distracted-observer row
  extrapolates Amoore & Hautala's warning line below 50 % response, which they flag as unsupported by data.
