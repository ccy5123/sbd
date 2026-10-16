# Gate 0 report — analytic order-of-magnitude model (Milestone M1)

*2026-10-15 · code: `gate0/model.py`, `gate0/run_gate0.py` · tests: `gate0/test_model.py` (11 pass) · numbers: `gate0/results.json` (seed 20261015, n = 20 000)*

## 1. Question

Before any CFD: for the same flatus, does a **silent (S1, sub-oscillation)** release deliver a higher odorant
concentration to a nose than an **audible** release? We report R = C_silent / C_audible at (i) the emitter's own nose and
(ii) a seated neighbour's nose, under the two normalisation bases required by the plan (§3.4):
**equal emitted mass** and **equal source concentration** (audible releases are larger in volume).

## 2. Model and a result that simplifies everything

The release (volume V, duration T, effective orifice diameter d, exit velocity u₀ = 4V/(πd²T)) goes through
two stages:

1. **Near field (phase 1).** The release mixes under its own momentum until its self-induced velocity decays to the
   ambient velocity u_h (CBL / room air), and is then handed over to the ambient flow. The starting-jet tip follows
   x = C_x (Q̇₀u₀)^{1/4} t^{1/2} (C_x = 2.8). After the source cuts off it becomes a puff,
   x⁴ = C_p⁴ (Q₀u₀) t (C_p = 2.6), as measured by Sangras et al. (2002) with the Diez et al. (2003) erratum. The
   jet-phase concentration follows Dowling & Dimotakis (1990): C_c/C₀ = K_c d*/x with K_c = 5.11 and
   d* = d(ρ₀/ρ_a)^{1/2}. The puff's volume grows as x³. A buoyant-thermal branch (r = αz, α = 0.25) is computed in
   parallel, and the larger of the two dilutions wins.
2. **Transport (phase 2).** The handed-over cloud is advected to the nose for t = L/u. It grows as a Gaussian
   puff, σ² = σ₀² + 2Kt, with an eddy diffusivity K. We report the instantaneous peak and the average over one
   inspiration (T_insp ≈ 1.5 s).

**Momentum-dilution law.** For any momentum-conserving release — steady jet, starting jet or puff, laminar or
turbulent — the near-field dilution at hand-off is

  D₁ ≈ β · u₀ / u_h,  β = O(1)

For a starting jet, β = C_x²√π/(4K_c)·(ρ_a/ρ₀)^{1/2} ≈ 0.68. For a laminar jet, β = 1 for the centreline
(Schlichting similarity). For a release that turns into a puff, β ≈ 0.25–0.5, depending on how far the jet travelled
before the source cut off. The tests check the jet and puff limits. Both concentration and
velocity decay as 1/x in a jet, and both as 1/x³ in a puff. This is momentum conservation: the entrained mass is
inversely proportional to the remaining velocity.

**Consequence.** The governing near-field parameter is the velocity ratio, which we name the **Silencer number**,

  **Si ≡ u₀,eff / u_h**,

and not the Reynolds number. Re matters only through whether the release is audible at all, which is the acoustic
module's job (M2). In the Monte Carlo, Si is ≈ 5 for a median silent release and ≈ 58 for a median audible one.

**Bias.** Every simplification is biased **against** H1 (that silent releases are worse), so that any surviving
silent penalty is robust:

- turbulent-jet constants are used even for laminar silent releases, which over-mixes them;
- the receptor sits on the cloud centreline;
- the jet concentration is the centreline value.

## 3. Parameters

All parameters are in `params/params.yaml`, with source and status. The M0 pass is complete: every former [VERIFY]
entry is now VERIFIED, DERIVED, PARTIAL or an explicit ASSUMPTION. Gate 0 uses:

- sulfur gases (Suarez 1998) and odour thresholds (Nagata 2003);
- K_c (Dowling & Dimotakis), and the starting-jet and puff coefficients (Sangras 2002 / Diez 2003 erratum);
- the thermal entrainment coefficient α = 0.25 ± 0.1 (Landeau et al. 2014);
- CBL velocity 0.11–0.24 m/s (Licina 2014);
- indoor K 0.0019–0.013 m²/s (Cheng 2011);
- individual passage volume **17–375 mL**, quoted from the Suarez 1997 text (n = 87);
- seat-to-nose height from ANSUR II;
- inspiratory time 1.6–2.7 s (Wysocki 2006: Ti/Ttot = 0.42, so the plan's I:E = 1:2 is not supported);
- fabric air permeability at 100 Pa — denim 17–46 mm/s, stretch denim up to 253 mm/s, stretched jersey leggings
  0.16–1.9 m/s;
- flatus buoyancy, derived from the Suarez 1997 Table 1 compositions.

**Correction to plan §3.1.** Median flatus is positively buoyant (g′ = +1.7 m/s² at 37 °C; independently +1.2 m/s² from
the Modesto 2022 meta-analysis mean composition). However, CO₂-rich flatus is denser than air: 1/16 subjects at 37 °C,
4/16 after cooling to room temperature. Buoyancy is therefore treated as signed, and the Monte Carlo resamples the
16 empirical values.

Still **assumptions**:

- orifice diameter (1–15 mm; a Bernoulli check gives 1.7–3 mm for a 0.1 L/s release at 0.1–1 kPa) and release
  duration (0.3–5 s);
- the audibility threshold u_audible (1–5 m/s), a placeholder until M2;
- the hand-off velocity u_h (0.05–0.25 m/s);
- the room transport speed (0.03–0.15 m/s);
- the lower bound K = 10⁻⁴ m²/s for puff relative dispersion near the body;
- the skirt volume and the woven-trouser permeability.

## 4. Results

**Source strength.** The flatus mean contains 26 977 ppb H₂S, 5 345 ppb CH₃SH and 2 036 ppb DMS. The summed odour
activity value is 1.4 × 10⁵: methanethiol (OAV 7.6 × 10⁴) slightly out-ranks H₂S (6.6 × 10⁴). **One 100 mL passage
therefore needs ≈ 14 m³ of air to fall to the detection threshold** — about the volume of a lift car. The median
inhalation-averaged OAV is ≈ 220 at the emitter's nose and ≈ 60–90 at the neighbour's. Every release is clearly
detectable, so the question is purely relative.

**Reference pair** (silent: 40 mL, 2 s, d = 6 mm, Re ≈ 250; audible: 100 mL, 0.5 s, Re ≈ 2 500):

| | Si | near-field D₁ | dominant mixer | total dilution, own nose | total dilution, neighbour |
|---|---|---|---|---|---|
| silent | 4.7 | 5.7 | buoyancy (thermal) | 950 | 4 500 |
| audible | 47 | 14 | momentum (puff) | 430 | 1 900 |

Near-field mixing differs by only a factor of ≈ 2.4, far less than the factor of 10 in u₀. A short audible release
becomes a puff, and puffs decelerate fast (u ∝ x⁻³). Meanwhile, the buoyancy of the silent release mixes it by itself.

**Monte Carlo** (random S1 vs audible pairs; R = C_silent/C_audible, inhalation-averaged; Fig. `figures/gate0_psbd.png`):

| receptor | wardrobe | basis | median R | 5–95 % | P(R > 1) | P(R > 2) "noticeably deadlier" | P(R < ½) |
|---|---|---|---|---|---|---|---|
| own nose | none | equal mass | 1.35 | 0.83–9.1 | 0.88 | 0.31 | 0.02 |
| own nose | none | as emitted (equal conc.) | 0.94 | 0.18–4.9 | 0.47 | 0.21 | 0.27 |
| neighbour | none | equal mass | 1.12 | 0.92–5.2 | 0.88 | 0.17 | 0.01 |
| neighbour | none | as emitted (equal conc.) | 0.75 | 0.13–4.4 | 0.39 | 0.17 | 0.36 |
| neighbour | denim | equal mass | 1.02 | 0.85–2.3 | 0.73 | 0.07 | 0.01 |
| neighbour | denim | as emitted (equal conc.) | 0.59 | 0.11–3.6 | 0.31 | 0.12 | 0.44 |
| neighbour | none, jet aimed at neighbour | equal mass | 0.74 | 0.11–4.1 | 0.27 | 0.11 | 0.26 |

**Interpreting the two bases.**

- **Equal emitted mass** isolates the fluid mechanics: per odorant molecule, a silent release *is* delivered more
  efficiently. The near-field penalty is real: median 1.35 at the emitter's own nose, and 1.12 at the neighbour's.
- **Equal source concentration** compares passages *as they actually come out of one gut*. Here the larger volume of
  audible releases wins: the median R is 0.75 at the neighbour, and **loud passages deliver more odorant in the
  majority of pairs** (P(R > 1) = 0.39). This basis is the closest Gate 0 analogue of the folk belief.
- This basis still assumes the same composition. Faster fermentation (loud-prone releases) would, if anything, make
  audible gas richer (plan §4.2), which would strengthen the reversal.

**Ratio maps** (`figures/gate0_ratio_map.png`). In quiescent air near the body (K = 10⁻⁴ m²/s), the equal-mass silent
penalty reaches a factor of 3–30 for travel times of 1–5 s against highly turbulent audible comparators. At room-scale
turbulence (K = 10⁻³ m²/s) it collapses to ≲ 1.5 beyond ~3 s. On the equal-concentration basis, the larger audible
release is the worse one everywhere except in the near-field corner.

**Rank sensitivity** (`figures/gate0_sensitivity.png`; Spearman ρ with log R, neighbour, equal mass):

| input | ρ |
|---|---|
| V_audible / V_silent | +0.58 |
| eddy diffusivity K | −0.51 |
| u₀ of the audible release | +0.50 |
| orifice diameter of the audible release | −0.17 |
| room transport speed | +0.15 |

Buoyancy, breathing and the jet constants are all |ρ| ≤ 0.06. This is good: the verified constants are not the
bottleneck. The bottleneck is K near the body and the release geometry.

## 5. Gate decision (narrative branch, plan §1)

The physical silent-release penalty is **real per molecule, but modest, regime-dependent, and reversed for real
passages**:

- Per molecule (equal mass), a silent release is delivered ≈ 1.1–1.35× more efficiently. Fewer than one pair in five
  reaches the neighbour noticeably (×2) deadlier.
- Trousers drive the penalty to ≈ 1.0 ("trousers are the great equaliser": fabric strips the jet momentum from both
  releases).
- For passages as emitted (equal source concentration), the larger volume of loud releases outweighs the mixing
  advantage. The neighbour receives *more* odour from the audible release in the majority of pairs.
- The penalty is large only in one corner: **emitter's own nose, bare, still air, within ~5 s**.

→ **Recommended branch: "Debunked (mostly) — the nose was fooled by the ears", with a regime map.** The physics cannot
carry the belief on its own. The psychological "preparedness" layer (H2, M6) becomes the headline: the break-even
γ* needed to sustain the belief for real passages is ≈ 1.3–1.7 at the neighbour (1/median R on the as-emitted
basis). The physical exception corner is a natural home for "He who smelt it dealt it" (Scenario B).

This is a Gate 0 result. CFD (M3–M5) is still required, mainly to replace the two weakest links:

1. the hand-off and Gaussian-puff idealisation inside the CBL, where K for a seconds-old puff is unknown — the single
   largest physical uncertainty;
2. the jet direction and its interaction with seat and clothing.

## 6. Recommended CFD ranges (from Gate 0 sensitivity)

- **Releases:** V 17–375 mL; d 1–15 mm (log-spaced, 5 levels); T 0.3–5 s; signed g′ ∈ {−0.7, +1.7, +4.7} m/s².
- **Most valuable CFD outputs:** puff relative dispersion within the CBL (an effective K for 1–15 s), and the
  momentum-sink efficiency of each fabric.
- **Mesh:** resolve the orifice to ≥ 10 cells per d for the audible releases (d ≥ 2 mm → cell ≤ 0.2 mm locally). An
  LES of the starting jet is only needed for hero figures. RANS + scalar transport is adequate for sweeps, since the
  jet constants are insensitive.

## 7. Limitations

- Single receptor on the centreline (an upper bound for both releases).
- No room walls or ventilation.
- Clothing is a crude Darcy momentum sink. Open knits have Re_k up to ≈ 1.8, so CFD needs a Forchheimer term.
- The audibility threshold is a placeholder.
- The Gaussian puff ignores CBL shear stretching.
- Odorant adsorption on fabric and cushions is ignored. Suarez 1998 reports that a charcoal cushion "absorbed more than
  90% of the sulphur gases" — a first-order effect for the sofa scenario with cushion reservoir, still to be modelled.

## 8. Update after M2 (2026-10-15)

The placeholder audibility threshold (u_audible 1–5 m/s) has been replaced by the acoustic onset criterion from M2:
u_onset = C_d √(2P_th/ρ) ≈ 14–51 m/s. Audible releases are therefore faster and dilute more in the near field.

Updated headline numbers:

- **Equal emitted mass:** median R is 1.93 at the emitter's own nose and 1.35 at the neighbour's.
- **As emitted:** median R is 1.22 at the own nose and **0.92 at the neighbour's**, with P(R > 1) = 0.47.

The confirmed narrative branch stands for the neighbour (own-nose numbers superseded by §9). The own-nose exception is stronger than in §5. See
`acoustics/m2_report.md`. The figures and `results.json` in this directory reflect the M2-coupled run.

## 9. Update after M3b: own-nose transport from CFD (2026-10-16)

The releaser's own cloud used to reach the nose in L_own/u_CBL ≈ 0.75/0.175 ≈ 4.4 s, i.e. at the measured
breathing-zone CBL speed. The transient CBL CFD (M3b, time-mean field) gives longer paths:

- seat-level parcels reach nose height in 4.7–7.4 s (20 °C) and 6.8–8.0 s (23 °C);
- the coarse-mesh CBL is about 40 % faster than Licina et al. 2014, so the upper time is extended ×1.4;
- Gate 0 now samples an effective transport speed `u_own_eff` = 0.07–0.16 m/s (t ≈ 4.7–11 s). `u_CBL` keeps its
  measured meaning.

Headline own-nose numbers (neighbour numbers are unchanged):

| basis | median R before | median R now | P(R > 1) now |
|---|---|---|---|
| equal emitted mass | 1.93 | **1.73** | 0.93 |
| as emitted | 1.22 | **1.15** | 0.56 |

The own-nose exception survives but is weaker: the longer trip lets the cloud spread, which erodes the near-field
jet pre-dilution difference (Theorem 2 in `NOTES.md`). The figures and `results.json` reflect this run.

