# M6 report — perception layer (Figs 7, 11, S-adaptation)

*2026-10-15 · code: `perception/model.py`, `perception/run_m6.py` · tests: `perception/test_perception.py` (6) · numbers: `perception/results.json` · Monte Carlo pairs from Gate 0 with M2 acoustic onset (n = 6 000)*

## Model

- **Breath sampling.** The nose samples only while inhaling. Inspiratory flow is sinusoidal, with f = 12 /min,
  Ti/Ttot = 0.42 (Wysocki 2006) and V_T = 0.63 L. Each inhalation delivers its flow-weighted mean concentration;
  the perceived peak is the **worst breath**.
- **Warned breath-hold.** A listener who hears the release holds their breath after a reaction latency of 0.5 s,
  for H seconds. The first breath after the hold is 1.5× deeper (assumption).
- **Intensity.** Perceived intensity follows a Stevens law, I ∝ OAV^n with n = 0.28 (Collins et al. 2001; flatus H₂S;
  sensitivity range 0.20–0.45). The log scale (k_w ≈ 0.95 per decade, Japan MoE) is retained for reporting.
- **Adaptation.** A(t) = a∞ + (1 − a∞)e^(−t/τ), with a∞ = 0.35 (25–40 % for H₂S; Berglund 1978, Ekman 1967) and
  τ = 80 s (assumption: asymptote reached by ~4 min).
- **Expectation (auxiliary hypothesis, demoted 2026-10-16).** The perceived ratio of silent to audible is γ·R^n,
  and the belief holds when it exceeds 1.
  - Break-even: **γ\* = R^(−n)**. It is kept only as a sensitivity bound, not as the explanation of the belief.
  - **The sign of γ is not established.** A negative label raises rated intensity (Djordjevic 2008; Dalton 1999), but
    no label rates the same as a positive label (Djordjevic 2008, p = .65).
    - An audible release acts as a negative label given *in advance*, so taken literally the literature predicts
      warned ≥ unwarned, i.e. γ ≤ 1 for silent releases.
    - No study compares warned and unwarned exposure directly.
  - **Size:** 0–3 % for brief exposures (Herz 2001; first ratings in Dalton 1996/1999). The 1.18–1.61 ratios of Dalton
    1999 are 20-min means and do not apply to a single release.
  - The main account of the belief is selection: only noticed events are remembered (see `NOTES.md`, 2026-10-16).

## Results

**Fig. 7 — the breath-hold strategy** (neighbour, audible releases):

- An audible puff reaches the neighbour after a median of **16 s** and passes in σ_t ≈ 3.8 s, with a 10–90 % range of
  1.4–12 s.
- **Unwarned:** the breathing phase barely helps. For a median passage the worst breath still captures 81–99 % of the
  peak (mean 93 %). Only very short passages (σ_t ≈ 1.4 s) are sometimes dodged by luck: in a third of phases the worst
  breath is below half the peak.
- **Warned:**
  - A 50 % chance of dodging the puff entirely (worst breath < 10 % of peak) needs **H ≈ 23 s** of breath-hold.
  - Holding for 33 s, the typical maximum at end-expiration (Marks 1997; Roujol 2014), gives 68 %.
  - Holding for 45 s, which needs a deep breath first, gives 79 %.
- The ear therefore buys a real, physical escape option. It works only if the warned person holds their breath almost
  to their limit, because the puff takes about 16 s to arrive.

**Fig. 11 — the expectation break-even** (Stevens n = 0.28; γ is an auxiliary hypothesis, see Model):

| scenario | median R | perceived intensity ratio R^n | γ\* | P(belief) at γ = 1 | at γ = 1.15 | at γ = 1.5 |
|---|---|---|---|---|---|---|
| neighbour, as emitted | 0.91 | 0.973 | **1.03** | 0.47 | 0.64 | 0.89 |
| own nose, as emitted | 1.23 | 1.059 | 0.94 | 0.59 | 0.76 | 0.95 |
| neighbour, equal mass | 1.34 | 1.086 | 0.92 | 0.93 | 0.99 | 1.00 |
| neighbour, as emitted, denim | 0.62 | 0.876 | 1.14 | 0.31 | 0.51 | 0.81 |

**Key sentence for the manuscript.** At the neighbour's nose, the median physical difference between a silent and an
audible passage is a 2.7 % difference in perceived intensity. That is **below the olfactory just-noticeable difference
(≈ 7 % in intensity for ΔC/C = 0.28)**.

- With no expectation effect (γ = 1), a silent release seems stronger in **47 %** of pairs, a coin flip. Physics and
  perception alone do not produce the belief.
- The belief is explained by selection: a silent release is noticed only when it smells, so every remembered silent
  release was smelly.
- An expectation effect could add to this, but its sign is not established. γ\* = 1.03 is reported only as a
  sensitivity bound.

*Superseded (2026-10-15 wording): "an expectation amplification of only 3 % (γ\* = 1.03) is enough for the belief to
survive". The figure annotations in Fig. 11 (literature band 1.0–1.3, labelled a plausible expectation effect) still
use the old framing and will be regenerated.*

**Supplementary — the newcomer effect** (4 m³ lift car, 12 air changes/h, one 100 mL passage, well mixed):

- The initial summed OAV is 3.6, and the odour stays above threshold for 6.4 min.
- By 60 s an occupant who was present at the release perceives only 66 % of what an unadapted nose would.
- A newcomer entering at that moment therefore perceives ≈ 1.5× more than the occupants, which gives the lift
  whodunit (Scenario C) a false-accusation bias towards the last person in.

## Selection model — the memory filter (Fig. 13; added 2026-10-16)

*Code: `perception/selection.py`, `perception/run_selection.py` · tests: `perception/test_selection.py` (4) · numbers:
`perception/selection.json` · 20 000 single passages from the Gate 0 priors, a log-normal sulfur multiplier
(σ_ln = 1.1, independent of volume), M2 audibility at the neighbour's distance per background.*

**Theorem 3 (Berkson / collider form).** Let H = heard and S = smelled (OAV ≥ 1). An observer remembers a passage
iff N = H ∨ S. Then, whatever the joint law of H and S:

- P(S | ¬H, N) = 1 and P(S | H, N) = P(S | H);
- so the memory gap is 1 − P(S | H), even if sound and smell are independent;
- an observer whose noticing does not depend on S (the emitter, who feels every release) has no bias (Boyd's
  h₁ = 0 case; Snoep et al. 2014, appendix).

**Results**

1. **Gate 0 nominal case** (living room; the puff passes centred on the nose, so this is an upper bound on how often
   a passage is smelled):

   | | P(smelled \| silent) | P(smelled \| audible) | P(belief) |
   |---|---|---|---|
   | neighbour's nose, all passages | 0.92 | 0.96 | 0.486 |
   | bystander's memory | **1.00** | 0.96 | 0.525 |
   | emitter (own nose, all passages) | 0.99 | 1.00 | 0.534 |

   - The neighbour smells 93 % of passages, so the filter has little to remove and the belief barely moves.
   - The emitter's 0.534 is physics, not selection: it is the own-nose near-field exception of Gate 0.

2. **The base rate controls the belief** (Fig. 13b; all OAVs scaled together).
   - The memory gap equals 1 − P(S | H) at every scale, a numerical check of Theorem 3.

   | fraction of passages smelled by the neighbour | 0.91 | 0.84 | 0.74 | 0.62 | 0.49 | 0.34 | 0.17 | 0.06 |
   |---|---|---|---|---|---|---|---|---|
   | P(belief), bystander's memory | 0.54 | 0.58 | 0.64 | 0.71 | 0.78 | 0.86 | 0.95 | 0.99 |

   - Over the same range the truth at the neighbour's nose stays at 0.49–0.53, and the emitter at 0.50–0.56.
   - **The belief is produced by memory, not by noses**, and it grows as stinky passages become rarer.

3. **Masking noise** (Fig. 13c).
   - Library and living room: 0.525.
   - Subway: 0.495, with 7 % of oscillating releases still heard.
   - Restaurant: 0.43, with 1 % still heard (only 30 heard passages; noisy).
   - P(S | silent, N) stays exactly 1. The belief still weakens, because in noise only the loudest, i.e. largest,
     releases are heard, and by the mass criterion those carry the most sulfur. This "loudness selection" is a
     physical effect that predicts a weaker belief even without the Hamilton & Gifford mechanism. **Masking is
     therefore not a clean test between the psychological accounts**; this revises the prediction in `NOTES.md`.

**What sets the real base rate.** Gate 0 assumes the puff is centred on the receptor's nose, which gives the
neighbour a smelling rate of 0.93. The Scenario A CFD shows that in a real seated geometry the cloud usually
misses the breathing zone: the sub-threshold mean OAV was 10⁻¹¹ for the silent release and 0.5–0.7 for the
audible one. So the everyday base rate is probably far lower, which is where the filter turns a coin flip into a
near-certain belief. The fraction of a neighbour's passages that one actually notices by smell is the single
empirical number this account needs.

## Limitations

- γ is not measured, and neither its size nor its sign is established for a single brief release. It is an
  auxiliary hypothesis; only a break-even analysis is offered (plan §16).
- The selection model treats noticing as deterministic (OAV ≥ 1, or heard). A graded detection probability would
  soften P(S | silent, N) = 1 to a value just below 1. Its base rate is not measured (see above).
- Sniff suppression for malodours (sniff-magnitude ratio 0.64, Frank 2006) is not yet applied. It acts on both
  silent and audible releases after detection, but a warned nose can suppress in anticipation (Frank 2007). This
  would strengthen the warned-avoidance channel.
- The lift-car cabin volume and ventilation rate are assumptions, and the cabin is treated as well mixed.
- The Stevens exponent for H₂S comes from a single study (dog flatus, one judge). n = 0.20–0.45 is carried as the
  sensitivity range (Fig. 11b): γ\* at the neighbour stays between 1.02 and 1.04.
