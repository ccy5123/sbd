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

## Limitations

- γ is not measured, and neither its size nor its sign is established for a single brief release. It is an
  auxiliary hypothesis; only a break-even analysis is offered (plan §16).
- Sniff suppression for malodours (sniff-magnitude ratio 0.64, Frank 2006) is not yet applied. It acts on both
  silent and audible releases after detection, but a warned nose can suppress in anticipation (Frank 2007). This
  would strengthen the warned-avoidance channel.
- The lift-car cabin volume and ventilation rate are assumptions, and the cabin is treated as well mixed.
- The Stevens exponent for H₂S comes from a single study (dog flatus, one judge). n = 0.20–0.45 is carried as the
  sensitivity range (Fig. 11b): γ\* at the neighbour stays between 1.02 and 1.04.
