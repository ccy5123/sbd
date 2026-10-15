# M4 report — Scenario A, the sofa duet (first pass)

*2026-10-15 · code: `cfd/cases/sofa/{make_case,run_sofa.sh,analyze_sofa,fig_sofa_planes}.py` · numbers:
`cfd/cases/sofa/results.json` · figures: `figures/fig5_sofa_duet_noses.png`, `figures/fig6_sofa_duet_planes.png`*

## Set-up

- **Room and occupants.** A 3.2 × 3.2 × 2.6 m living room with walls at 23 °C. Two seated manikins (skin 33 °C) sit
  0.6 m apart on a two-seat sofa.
- **Model.** Transient RANS k-ω SST, Boussinesq (`fluid` solver, internal-energy form).
- **Mesh.** 722 k cells: 5 mm at the release, 2.5 mm on the nozzle face.
- **Ventilation.** A 0.5 × 0.5 m ceiling vent provides pressure relief.
- **Sequence.**
  - A 30 s precursor develops the convective boundary layer (CBL). Both noses then show U_z ≈ 0.20 m/s, 2.5 cm in front
    of the face.
  - Silent and audible branches start from the same precursor field. Release begins at +0.2 s; each branch runs for 30 s.
- **Release.** 92 mL (the median passage), as a momentum-equivalent inlet at the end of a 1 cm-radius nozzle stub
  behind the releaser's buttocks. It points down and back into the seat/backrest corner, 2.8 cm above the seat.

  | | physical release | equivalent inlet |
  |---|---|---|
  | silent | 2 s through 8 mm, u₀ = 0.9 m/s | 0.15 m/s, undiluted |
  | audible | 0.5 s through 2.4 mm, u₀ = 41 m/s | 4.9 m/s, pre-diluted 8.3× |

- **Odour.** Passive scalar s (s = 1 is undiluted flatus), converted to a summed odour activity value (OAV) of H₂S +
  CH₃SH + DMS (`params.yaml`).
- **Receptors.**
  - A point probe 2.5 cm in front of each nose.
  - A 5 cm breathing-zone disc on the nose-height plane (every 0.5 s).
  - The peak value within 25 cm of each head axis.
  - The worst breath (sinusoidal breathing, 24 phases).

## Results (30 s after release onset)

| receptor | silent | audible |
|---|---|---|
| own nose: probe peak OAV | 5 × 10⁻¹³ | 0.72 (at 14 s) |
| own nose: breathing-zone peak OAV | 5 × 10⁻¹¹ | 0.46 |
| own nose: worst breath OAV (mean / max over phase) | ~10⁻¹³ | 0.11 / 0.37 |
| own head, within 25 cm: peak OAV | **5 800 (at 5 s)** | 205 (at 8 s) |
| neighbour: probe peak OAV | 2 × 10⁻¹⁶ | 0.07 (at 6 s) |
| neighbour: breathing-zone peak OAV | 3 × 10⁻¹⁴ | 0.63 (at 6 s) |
| neighbour's head, within 25 cm: peak OAV | 10⁻⁶ | 369 (at 6 s) |

**Pathways**

- **Silent: the backrest chimney.** The low-momentum release is captured by the ~3 cm gap between the releaser's back
  and the backrest. The back's convective boundary layer carries it straight up behind the releaser's head (OAV ≈ 6 000
  within 25 cm at 5 s), over the head and on to the ceiling. Neither breathing zone, the releaser's own included, gets a
  detectable dose within 30 s.
- **Audible: the jet escapes the chimney.** The 4.9 m/s jet hits the seat/backrest corner and spreads sideways and
  forwards before the boundary layer lifts it. Part of it still rises behind the releaser. Another part reaches the
  neighbour's head region within 6 s (OAV 369 within 25 cm) and both breathing zones at sub-threshold levels
  (OAV 0.5–0.7).
- **Ratio.** R = C_silent / C_audible ≈ 10⁻¹⁰–10⁻¹⁴ in every breathing-zone metric. In this configuration the audible
  release is the one that reaches noses. The silent one is "deadly" only to the air above the releaser's head.

**Relation to Gate 0**

- Gate 0 predicted R ≈ 1 at the neighbour (as emitted, median 0.92) for a well-mixed puff transported by advection.
- The CFD shows a more extreme, geometry-driven outcome: the release momentum decides which flow the cloud joins. The
  low-momentum silent release joins the back's convective boundary layer; the jet escapes it.
- This *strengthens* the "nose fooled by the ears" branch for the neighbour: the audible release delivers more odour,
  not less. It also overturns Gate 0's own-nose exception for this posture (Gate 0 gave a median R of 1.2 at the own
  nose).

## Caveats (first pass; not yet publishable numbers)

1. **Posture.** The upright manikin leaves a ~3 cm channel between back and backrest, and that channel *is* the silent
   pathway. A reclined occupant whose back touches the cushion would close it. This is the dominant sensitivity and
   needs a second geometry.
2. **RANS mean field.** RANS predicts the ensemble mean. A real puff meanders, and instantaneous peaks at a nose can
   exceed the mean by an order of magnitude (intermittency). Sub-threshold mean OAVs of 0.5–0.7 (audible) are
   therefore consistent with a detectable whiff. Silent values of 10⁻¹¹ are not, because the mean cloud is centimetres
   to decimetres away from the nose and only meandering could bring it there.
3. **Window.** 30 s covers the direct pass, not room-scale mixing. The cloud near the ceiling will mix down over
   minutes, raising room-average OAV towards 92 mL × 1.4 × 10⁵ / 25.6 m³ (fluid volume) ≈ 0.5 for both modes alike.
4. **Validation bias.** The coarse-mesh CBL is about 40 % too fast (M3b), so the chimney may lift the cloud faster than
   reality.
5. **Single realisation.** One release volume, one position and one jet direction.
