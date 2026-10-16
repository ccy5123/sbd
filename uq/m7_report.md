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
a neighbour's flatus (null result). The bracket below is constrained from its components [ASSUMPTION, low
confidence]:

- **Thin dilution margin.** A 100 mL passage with ~26 ppm H₂S (Suarez 1998) mixed into a 1 m-radius sphere gives
  ~0.6 ppb. That is below the median H₂S detection threshold (~8 ppb, Amoore & Hautala 1983).
- **The plume favours the emitter.** The thermal plume carries lower-body releases to the emitter's own breathing
  zone (Rim & Novoselac 2009), as the M4 chimney also shows.
- **Clothing** removes ~22 % of sulfide gas (Ohge 2005).
- **Observer-side losses.** About 7.5 % of adults aged 55 or under have olfactory dysfunction (Desiato 2021).
  Threshold sensitivity spans ~250-fold across people (Amoore 1985, grey literature), and a single person's threshold
  fluctuates over time (Stevens 1988).

Bracket: **p_S ≈ 0.1–0.5, central ≈ 0.25**. This gives a memory-layer belief of **0.78–0.97, central 0.91**: a strong
belief built on a coin-flip truth.

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
- p_S is unmeasured. The memory-layer numbers are conditional on the bracket.
