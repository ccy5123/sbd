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
- **Preparedness.** The perceived ratio of silent to audible is γ·R^n, and the belief holds when it exceeds 1.
  - Break-even: **γ\* = R^(−n)**.
  - "Plausible expectation effect": ×1.0–1.3. This range is an assumption. The direction is verified (negative names
    raise intensity, Djordjevic 2008; hazard framing causes sensitization instead of adaptation, Dalton 1996–1999),
    but no study measures the intensity of an *unexpected* versus an expected odour.

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

**Fig. 11 — the preparedness break-even** (Stevens n = 0.28):

| scenario | median R | perceived intensity ratio R^n | γ\* | P(belief) at γ = 1 | at γ = 1.15 | at γ = 1.5 |
|---|---|---|---|---|---|---|
| neighbour, as emitted | 0.91 | 0.973 | **1.03** | 0.47 | 0.64 | 0.89 |
| own nose, as emitted | 1.23 | 1.059 | 0.94 | 0.59 | 0.76 | 0.95 |
| neighbour, equal mass | 1.34 | 1.086 | 0.92 | 0.93 | 0.99 | 1.00 |
| neighbour, as emitted, denim | 0.62 | 0.876 | 1.14 | 0.31 | 0.51 | 0.81 |

**Key sentence for the manuscript.** At the neighbour's nose, the median physical difference between a silent and an
audible passage is a 2.7 % difference in perceived intensity. That is **below the olfactory just-noticeable difference
(≈ 7 % in intensity for ΔC/C = 0.28)**. An expectation amplification of only **3 %** for an unwarned exposure (γ\*
= 1.03) is enough for the belief to survive. With a modest 15 % amplification, two thirds of pairs "confirm" it.
*The nose cannot tell the difference; the ears decide.*

**Supplementary — the newcomer effect** (4 m³ lift car, 12 air changes/h, one 100 mL passage, well mixed):

- The initial summed OAV is 3.6, and the odour stays above threshold for 6.4 min.
- By 60 s an occupant who was present at the release perceives only 66 % of what an unadapted nose would.
- A newcomer entering at that moment therefore perceives ≈ 1.5× more than the occupants, which gives the lift
  whodunit (Scenario C) a false-accusation bias towards the last person in.

## Limitations

- γ is not measured. Only its direction and a break-even analysis are offered (plan §16).
- Sniff suppression for malodours (sniff-magnitude ratio 0.64, Frank 2006) is not yet applied. It acts on both
  silent and audible releases after detection, but a warned nose can suppress in anticipation (Frank 2007). This
  would strengthen the warned-avoidance channel.
- The lift-car cabin volume and ventilation rate are assumptions, and the cabin is treated as well mixed.
- The Stevens exponent for H₂S comes from a single study (dog flatus, one judge). n = 0.20–0.45 is carried as the
  sensitivity range (Fig. 11b): γ\* at the neighbour stays between 1.02 and 1.04.
