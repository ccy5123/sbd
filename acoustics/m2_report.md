# M2 report — acoustic regime map (Fig. 3)

*2026-10-15 · code: `acoustics/regime.py`, `acoustics/run_m2.py` · tests: `acoustics/test_regime.py` · numbers: `acoustics/results.json` · figure: `figures/fig3_acoustic_regimes.png`*

## Model

The model chains four steps, and each defines one of the plan's §4.1 categories.

1. **Onset (S1).** The anal canal is treated as a soft-tissue self-oscillating flow valve. Ancalle et al. (2021)
   describe it as a lip-reed analogue. The valve oscillates when the driving pressure
   Δp = ½ρ(u₀/C_d)² exceeds a threshold P_th. Equivalently, it oscillates when the exit velocity exceeds
   u_onset = C_d √(2P_th/ρ).
   - P_th = 0.6 kPa (range 0.2–1.3 kPa) is an anchored assumption. Vocal folds give 0.2–0.5 kPa (Titze 2009). Brass
     lips give p₀ = K·f with K = 4–8 Pa/Hz, i.e. 0.64–1.28 kPa at 160 Hz (Fletcher & Tarnopolsky 1999).
   - C_d = 0.85 (0.6–1.0, glottal value).
   - The nominal onset velocity is **u_onset ≈ 30 m/s** (14–51 m/s over the ranges).
   - **Who controls the valve** (added 2026-10-16).
     - Resting closure is mostly involuntary: the internal sphincter supplies about 70–85 % of resting anal pressure,
       and the voluntary external sphincter 15–30 % (literature cited by Miller et al. 1988).
     - A voluntary squeeze adds 10–50 mmHg but can be held for only about a minute (Duthie & Bennett 1963).
     - "Silencing" a passage therefore acts on part of the closing force, plus buttock posture, and works against
       the rectal driving pressure set by the gas volume. This is why the onset criterion is written in terms of the
       exit velocity, which reflects both.
     - P_th is the oscillation threshold of the already-opened valve, not the resting closing pressure (~8.7 kPa).
       No flatus-acoustics study exists, so the reed model is neither supported nor refuted.
2. **Source.** The valve modulates the volume flow. The fundamental has amplitude α·Q with α = 0.7 (0.5–1.0), and the
   harmonics roll off at −12 dB/octave in volume flow, as for a glottal source. Each harmonic radiates as a monopole
   into a half space, p = 2ρωq/(4πr). As a check, Q′ = 10⁻⁴ m³/s at 150 Hz and 1 m gives 56 dB.
3. **Audibility (S2).** All harmonics lie below the ISO 226 threshold of hearing.
4. **Masking (S3).** All harmonics lie below the masked threshold. That threshold is the background spectral density
   plus the critical ratio, ≈ 17 dB below 500 Hz (Hawkins & Stevens 1950). Background spectra are RC-shaped
   (−5 dB/octave), speech-shaped for restaurants and low-frequency-heavy for subway cars. Each is scaled to the room's
   dB(A).

No peer-reviewed measurement of flatus sound level or spectrum exists. The source level is therefore built from the
flow physics and the voice and brass analogues. The fundamental frequency f₀ = 160 Hz (100–300 Hz) is from a
non-peer-reviewed source.

## Results

**S2 is empty.** An oscillating release is always audible in a quiet room. At sofa distance (0.6 m), even 1 mL/s of
oscillating flow gives a fundamental of ≈ 32 dB, against a 160 Hz threshold of 18 dB, and the harmonics are more
audible still. This also holds at 3 m. A "silent" passage is therefore either **physically silent (S1)** or
**masked (S3)**. A release that oscillates but is inaudible does not occur.

**Regime fractions over the release prior** (V 17–375 mL, T 0.3–5 s, d 1–15 mm; n = 200 000; nominal acoustics):

| background | S1 | S2 | S3 (masked) | audible |
|---|---|---|---|---|
| library 40 dB(A) | 0.79 | 0 | 0 | 0.21 |
| living room 35 dB(A) | 0.79 | 0 | 0 | 0.21 |
| open-plan office 45 dB(A) | 0.79 | 0 | 0 | 0.21 |
| restaurant / café 74 dB(A) | 0.79 | 0 | 0.20 | 0.02 |
| subway car 77 dB(A) | 0.79 | 0 | 0.16 | 0.05 |

**Minimum audible flow rate of an oscillating release** at 0.6 m (Fig. 3b):

- quiet rooms: well below the flow rates in the release prior;
- restaurant: ≈ 0.6 L/s;
- subway car: ≈ 1.7 L/s.

In a restaurant or subway car, an "audible" release must therefore be a near-maximal passage. This is Scenario F of the
plan: *physically loud, perceptually silent*.

## Coupling to Gate 0 (replaces the u_audible placeholder)

The Gate 0 Monte Carlo now classifies a release as audible-type iff u₀ > u_onset, with P_th and C_d sampled. Audible
releases are then much faster (median u₀ ≈ 68 m/s through d ≈ 1.6 mm) than the old 1–5 m/s placeholder implied.
Their near-field momentum dilution is correspondingly larger:

| receptor | wardrobe | basis | median R | 5–95 % | P(R > 1) | P(R > 2) |
|---|---|---|---|---|---|---|
| own nose | none | equal mass | 1.93 | 0.92–14.7 | 0.93 | 0.48 |
| own nose | none | as emitted | 1.22 | 0.22–6.1 | 0.59 | 0.31 |
| neighbour | none | equal mass | 1.35 | 0.97–8.7 | 0.93 | 0.30 |
| neighbour | none | as emitted | **0.92** | 0.15–5.0 | **0.47** | 0.23 |
| neighbour | denim | as emitted | 0.63 | 0.11–3.4 | 0.31 | 0.12 |
| neighbour | jet aimed at neighbour | equal mass | 0.73 | 0.06–8.9 | 0.38 | 0.22 |

**Effect on the narrative (confirmed branch: "Debunked (mostly)").** The neighbour receives no systematic penalty from
a silent passage as emitted: the median is 0.92 and the comparison is a coin-flip. Trousers tip it towards the loud
passage. The branch therefore stands.

The physical penalty at the **emitter's own nose** is now clearer: per molecule it is ≈ 2×, and as emitted it is ≈ 1.2×.
This strengthens Scenario B ("he who smelt it dealt it"). The exception corner should be described as *"the dealer
smells it first and worst"*, not as negligible.

## Limitations

- P_th, α and f₀ are anchored assumptions. There is no anal-tissue mechanical data, and anal skin mass, stiffness and
  resonance were all not found.
- The quasi-steady onset criterion ignores hysteresis (offset threshold < onset threshold) and intermittent
  "staccato" opening.
- Harmonic roll-off and directivity (the seat and body as an imperfect baffle) are idealised.
- Masking uses broadband critical-ratio detection. Real babble and subway noise fluctuate, so listening in the dips
  would make releases somewhat more audible.
