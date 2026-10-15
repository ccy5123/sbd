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

All parameters are in `params/params.yaml`, with source and status. Verified in this pass:

- Suarez 1998 sulfur gases.
- Nagata 2003 thresholds.
- Dowling & Dimotakis K_c.
- Hussein et al. B_u.
- Sangras/Diez C_x and C_p.
- Licina 2014 CBL velocity.
- Cheng 2011 indoor K = 0.0019–0.013 m²/s.
- Per-passage volume, 32–207 mL (median 92), derived from Suarez 1997 Table 1.
- Flatus buoyancy, derived from the Suarez 1997 Table 1 compositions.

The derived values are computed in `params/derive_from_suarez1997.py`.

**Correction to plan §3.1.** Median flatus is positively buoyant (g′ = +1.7 m/s² at 37 °C). However, CO₂-rich flatus is
denser than air: 1/16 subjects at 37 °C, and 4/16 after cooling to room temperature. Buoyancy is therefore treated as
signed, and the Monte Carlo resamples the 16 empirical values.

Still **assumptions**:

- orifice diameter (2–15 mm) and release duration (0.3–5 s);
- the audibility threshold u_audible (1–5 m/s), a placeholder until M2;
- the hand-off velocity u_h (0.05–0.25 m/s);
- the room transport speed (0.03–0.15 m/s);
- the lower bound K = 10⁻⁴ m²/s for puff relative dispersion near the body.

## 4. Results

**Source strength.** The flatus mean contains 26 977 ppb H₂S, 5 345 ppb CH₃SH and 2 036 ppb DMS. The summed odour
activity value is 1.4 × 10⁵: methanethiol (OAV 7.6 × 10⁴) slightly out-ranks H₂S (6.6 × 10⁴). **One 100 mL passage
therefore needs ≈ 14 m³ of air to fall to the detection threshold** — about the volume of a lift car. At both noses and
for both release types, the median inhalation-averaged OAV is 10¹–10² (Monte Carlo medians: own nose ≈ 380, neighbour
≈ 80–100). Every release is clearly detectable, so the question is purely relative.

**Reference pair** (silent: 40 mL, 2 s, d = 6 mm, Re ≈ 250; audible: 100 mL, 0.5 s, Re ≈ 2 500):

| | Si | near-field D₁ | regime | total dilution, own nose | total dilution, neighbour |
|---|---|---|---|---|---|
| silent | 4.7 | 5.7 (buoyancy-dominated) | thermal | 690 | 4 500 |
| audible | 47 | 14 | puff | 320 | 1 900 |

Near-field mixing differs by only a factor of ≈ 2.4, far less than the factor of 10 in u₀. A short audible release
becomes a puff, and puffs decelerate fast (u ∝ x⁻³). Meanwhile, the buoyancy of the silent release mixes it by itself.

**Monte Carlo** (random S1 vs audible pairs; R = C_silent/C_audible, inhalation-averaged; Fig. `figures/gate0_psbd.png`):

| receptor | wardrobe | basis | median R | 5–95 % | P(R > 1) | P(R > 2) "noticeably deadlier" | P(R < ½) |
|---|---|---|---|---|---|---|---|
| own nose | none | equal mass | 1.18 | 0.81–3.4 | 0.84 | 0.16 | 0.01 |
| own nose | none | equal conc. | 1.00 | 0.36–2.9 | 0.50 | 0.14 | 0.13 |
| neighbour | none | equal mass | 1.05 | 0.91–2.2 | 0.84 | 0.06 | 0.01 |
| neighbour | none | equal conc. | 0.89 | 0.30–2.7 | 0.42 | 0.11 | 0.21 |
| neighbour | denim | equal mass | 1.00 | 0.87–1.5 | 0.65 | 0.02 | 0.01 |
| neighbour | none, jet aimed at neighbour | equal mass | 0.75 | 0.28–1.7 | 0.20 | 0.03 | 0.17 |

**Ratio maps** (`figures/gate0_ratio_map.png`). In quiescent air near the body (K = 10⁻⁴ m²/s), the equal-mass silent
penalty reaches a factor of 3–30 for travel times of 1–5 s against highly turbulent audible comparators. At room-scale
turbulence (K = 10⁻³ m²/s) it collapses to ≲ 1.5 beyond ~3 s. On the equal-concentration basis, the larger audible
release is the worse one everywhere except in the near-field corner.

**Rank sensitivity** (`figures/gate0_sensitivity.png`; Spearman ρ with log R, neighbour, equal mass):

| input | ρ |
|---|---|
| V_audible / V_silent | +0.58 |
| eddy diffusivity K | −0.51 |
| u₀ of the audible release | +0.37 |
| orifice diameter of the audible release | −0.15 |
| room transport speed | +0.14 |
| buoyancy g′ | −0.11 |

The jet constants (K_c, Γ) do not matter (|ρ| ≤ 0.01). This is good: the verified constants are not the bottleneck.

## 5. Gate decision (narrative branch, plan §1)

The physical silent-release penalty is **real but small and regime-dependent**:

- It is a factor of ≈ 1.2 at the emitter's own nose with no clothing. It is ≲ 1.05 at the neighbour and vanishes
  under trousers ("trousers are the great equaliser": fabric removes the jet momentum from both releases).
- It reverses when releases are compared at equal source concentration, or when the audible jet is aimed at the
  neighbour.
- A "noticeably deadlier" silent release (R > 2) occurs in only 2–16 % of pairs.

→ **Recommended branch: "Debunked (mostly) — the nose was fooled by the ears", with a regime map.** The physics cannot
carry the belief on its own. The psychological "preparedness" layer (H2, M6) becomes the headline: the break-even
γ* needed to sustain the belief is small (≈ 1.05–1.2 in the typical regime). The physical exception is a
well-defined corner — **own nose, bare, still air, short delay** — which "He who smelt it dealt it" (Scenario B) can
exploit for comedy.

This is a Gate 0 result. CFD (M3–M5) is still required, mainly to replace the two weakest links:

1. the hand-off and Gaussian-puff idealisation inside the CBL, where K for a seconds-old puff is unknown — the single
   largest physical uncertainty;
2. the jet direction and its interaction with seat and clothing.

## 6. Recommended CFD ranges (from Gate 0 sensitivity)

- **Releases:** V 30–210 mL; d 2–15 mm (log-spaced, 5 levels); T 0.3–5 s; signed g′ ∈ {−0.7, +1.7, +4.7} m/s².
- **Most valuable CFD outputs:** puff relative dispersion within the CBL (an effective K for 1–15 s), and the
  momentum-sink efficiency of each fabric.
- **Mesh:** resolve the orifice to ≥ 10 cells per d for the audible releases (d ≥ 2 mm → cell ≤ 0.2 mm locally). An
  LES of the starting jet is only needed for hero figures. RANS + scalar transport is adequate for sweeps, since the
  jet constants are insensitive.

## 7. Limitations

- Single receptor on the centreline (an upper bound for both releases).
- No room walls or ventilation.
- Clothing is a crude Darcy momentum sink.
- The audibility threshold is a placeholder.
- The Gaussian puff ignores CBL shear stretching.
- Odorant adsorption on fabric and cushions is ignored. Suarez 1998 reports that a charcoal cushion "absorbed more than
  90% of the sulphur gases" — a first-order effect for the sofa scenario with cushion reservoir, still to be modelled.
