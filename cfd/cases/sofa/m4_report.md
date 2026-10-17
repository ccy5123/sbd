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
   pathway. A reclined occupant whose back touches the cushion would close it. This was the dominant sensitivity; a
   second geometry is now run (see "Posture sensitivity" below): the outcome holds.
2. **RANS mean field.** RANS predicts the ensemble mean. A real puff meanders, and instantaneous peaks at a nose can
   exceed the mean by an order of magnitude (intermittency). Sub-threshold mean OAVs of 0.5–0.7 (audible) are
   therefore consistent with a detectable whiff. Silent values of 10⁻¹¹ are not, because the mean cloud is centimetres
   to decimetres away from the nose and only meandering could bring it there.
3. **Window.** 30 s covers the direct pass, not room-scale mixing. The cloud near the ceiling will mix down over
   minutes, raising room-average OAV towards 92 mL × 1.4 × 10⁵ / 25.6 m³ (fluid volume) ≈ 0.5 for both modes alike.
4. **Validation bias.** The coarse-mesh CBL is about 40 % too fast (M3b), so the chimney may lift the cloud faster than
   reality.
5. **Single realisation.** One release volume, one position and one jet direction.

## Posture sensitivity: releaser reclined 4.5° (2026-10-16)

*Code: `make_case.py --recline 4.5`, `run_sofa.sh <runs> 4.5`, `analyze_sofa.py --recline 4.5`,
`fig_sofa_planes.py --recline 4.5` · numbers: `results_rec4.5.json` · figures: `figures/figS_sofa_rec4.5_noses.png`,
`figures/figS_sofa_rec4.5_planes.png`*

**Set-up.**
- The releaser's upper body (torso, head, arms) is rotated 4.5° backwards about the hip. Pelvis, legs, release point
  and neighbour are unchanged.
- The back now meets the backrest from z ≈ 0.85 m up to its top at 0.95 m (≈ 8 mm overlap). This closes the top of
  the chimney, while the 3 cm gap at seat level stays open.
- The releaser's nose moves back 6 cm and the probes move with it.
- Same mesh recipe (723 k cells). checkMesh flags 4 highly skewed faces (max skewness 5.0, against 2.8 upright),
  presumably at the back–backrest contact. The run was stable: no FATAL, both branches reached 30 s.

**Results** (peak OAV within 30 s; worst breath = max over breathing phase):

| receptor | posture | silent | audible | R (silent / audible) |
|---|---|---|---|---|
| own nose: breathing-zone peak | upright | 5 × 10⁻¹¹ | 0.46 | 1 × 10⁻¹⁰ |
| | reclined | 9 × 10⁻¹¹ | **3.3** | 3 × 10⁻¹¹ |
| own nose: worst breath | upright | 4 × 10⁻¹³ | 0.37 | 1 × 10⁻¹² |
| | reclined | 7 × 10⁻¹² | **2.3** | 3 × 10⁻¹² |
| neighbour: breathing-zone peak | upright | 3 × 10⁻¹⁴ | 0.63 | 5 × 10⁻¹⁴ |
| | reclined | 3 × 10⁻¹⁵ | 0.19 | 2 × 10⁻¹⁴ |
| own head ring (25 cm) | upright | 5 800 (5.3 s) | 200 | 28 |
| | reclined | 3 100 (5.3 s) | 200 | 16 |
| neighbour's head ring | upright | 1 × 10⁻⁶ | 370 | 3 × 10⁻⁹ |
| | reclined | 4 × 10⁻⁵ | 630 | 6 × 10⁻⁸ |

**Pathways.**
- **Silent.** Closing the top of the chimney does not stop it.
  - The release pools in the seat-level wedge for ~3 s.
  - It then leaves the wedge *sideways* at shoulder level. At nose height the cloud first appears behind the head at
    x ≈ −0.19 m, 0.13 m inboard of the releaser's mid-plane, at 4.8 s; it then appears outboard (0.13 m) at 5.3 s.
  - It rises behind and over the head to the ceiling.
  - Neither breathing zone receives a detectable dose; values stay 10⁻¹¹ or below.
- **Audible.** The jet again escapes the wedge. In the reclined posture a filament wraps around the releaser's face
  (Fig. S, 7.8 s and 14.8 s), so the releaser's **own** breathing zone exceeds threshold (OAV 2–4). The neighbour
  stays sub-threshold (0.2).

**Conclusion.** In both postures the silent release is the one that misses every nose, by ten or more orders of
magnitude in the RANS mean. The chimney finding is not an artefact of the 3 cm back gap: the body's convective
boundary layer captures a low-momentum release wherever it leaks out. Reclining makes the audible release *more*
noticeable to the releaser, not less.

**Remaining sensitivities:**
- a 120 s window (room-scale mixing, which equalises both modes towards M/V);
- RANS intermittency;
- a forward-leaning posture (done below);
- a different release direction.

## Posture sensitivity: releaser leaning forward 10° (2026-10-17)

*Code: `make_case.py --recline -10`, `run_sofa.sh <runs> -10`, `analyze_sofa.py --recline -10`,
`fig_sofa_planes.py --recline -10` · numbers: `results_rec-10.json` · figures: `figures/figS_sofa_rec-10_noses.png`,
`figures/figS_sofa_rec-10_planes.png`*

**Set-up.**
- The releaser's upper body is rotated 10° forward about the hip, the opposite of the reclined case. The gap between
  back and backrest now widens upwards instead of closing.
- The releaser's nose moves 13 cm forward and 4 cm down, to (0.20, 0, 1.18) m; the probes move with it.
- Mesh 713 k cells, checkMesh "Mesh OK" (max skewness 3.3). No FATAL; both branches reached 30 s.

**Results** (peak OAV within 30 s):

| receptor | silent | audible | R (silent / audible) |
|---|---|---|---|
| own nose: breathing-zone peak | 3 × 10⁻⁷ | 1.5 × 10⁻⁵ | 0.02 |
| own nose: worst breath | 4 × 10⁻⁸ | 4 × 10⁻⁷ | 0.08 |
| neighbour: breathing-zone peak | 1.2 × 10⁻⁴ | **2.6** (14 s) | 5 × 10⁻⁵ |
| neighbour: worst breath | 2 × 10⁻⁶ | 0.14 | 2 × 10⁻⁵ |
| own head ring (25 cm) | 1 000 (7.3 s) | 130 (20 s) | 8 |
| neighbour's head ring | **580** (9.8 s) | 450 (6.8 s) | 1.3 |

**Pathways** (Fig. S planes).
- **Both releases** now rise in the open gap behind the back, pass behind the head and go to the ceiling. Leaning
  forward takes the releaser's nose out of that column, so **the releaser smells neither release** in 30 s
  (breathing zone ≤ 3 × 10⁻⁷ silent, 1.5 × 10⁻⁵ audible).
- **Silent.** For the first time the silent cloud reaches the neighbour's head ring (OAV 580 at 9.8 s, comparable to
  the audible 450), but not the neighbour's breathing zone (10⁻⁴). In the RANS mean it passes within 25 cm of the
  neighbour's face without entering the nose. This is where intermittent filaments, which RANS averages away, could
  matter.
- **Audible.** The jet reaches the neighbour's breathing zone above threshold (2.6 at 14 s), though the worst
  breath stays below it (0.14).

**Conclusion.** In three postures the silent release delivers less to both breathing zones than the audible one
during the direct pass. Forward lean weakens the margin at the neighbour's *head* (R ≈ 1 at 25 cm) but not at the
nose. Forward lean also hides the releaser's own nose from both releases.

## Longer window: 120 s (upright, 2026-10-17)

*Code: `extend_window.sh` (continues both branches from 30 s), `analyze_sofa.py` (all data) and
`analyze_sofa.py --window 30` (direct pass) · numbers: `results.json` (120 s), `results_W30s.json` (30 s) · figures:
`figures/fig5_sofa_duet_noses.png` (120 s), `figures/fig5_sofa_duet_noses_W30s.png`*

The 30 s re-analysis reproduces the first-pass breathing-zone numbers exactly. The silent probe values differ at the
10⁻¹³ level, because the window now ends 0.2 s later.

**Results** (peak over 0–120 s; worst breath = max over breathing phase):

| nose | metric | silent | audible | R |
|---|---|---|---|---|
| releaser | breathing-zone peak | 1.0 (108 s) | 0.64 (14 s) | 1.6 |
| releaser | worst breath | 0.99 | 0.59 | 1.7 |
| neighbour | breathing-zone peak | 0.42 (114 s) | 0.63 (6 s) | 0.67 |
| neighbour | worst breath | 0.39 | 0.39 | 1.0 |
| releaser | breathing-zone exposure (s-integral) | 2.0× audible | | 2.0 |
| neighbour | breathing-zone exposure | 0.91× audible | | 0.91 |

**Phases.**
1. **Direct pass (0–45 s).** As before, the silent cloud misses both noses (≤ 10⁻¹⁰), and the audible jet reaches them
   at sub-threshold levels.
2. **Return (45–70 s).** Both clouds have reached the ceiling and come back down through the room. Both modes arrive
   at both noses at OAV 0.01–0.3.
3. **Mixed room (> 70 s).**
   - At the neighbour, silent and audible traces are indistinguishable (OAV 0.1–0.4). This is Theorem 2 in action:
     the release mode is forgotten.
   - At the releaser's own nose the silent cloud runs ~1.5–2× higher. It touches the trained-panel threshold
     (OAV ≈ 1) for about 1 s near 100–110 s. The mechanism of this late own-nose excess was not analysed.

**Interpretation.**
- The 30 s conclusion ("the silent release reaches no nose") is a statement about the **direct pass** only.
- Within about a minute, room recirculation brings both releases back at comparable, near-threshold levels, as the
  well-mixed estimate predicts (92 mL × 1.4 × 10⁵ / 25.6 m³ ≈ 0.5).
- The OAVs here use trained-panel thresholds (Nagata). For a typical untrained observer, thresholds are 10–23×
  higher, so the late-phase values (≤ 1) would mostly go unnoticed; for a distracted one, almost always.
- What a bystander could actually notice is the audible direct pass (OAV up to 0.6 in the breathing zone, with RANS
  intermittency on top). The silent release only becomes faintly detectable once it has been mixed into the room, when
  its origin can no longer be attributed.

**Caveats.**
- The room is sealed except for a pressure-relief vent (no supply air).
- RANS mean field; one realisation.
- The 30 s precursor flow is assumed to stay statistically steady for two minutes.
