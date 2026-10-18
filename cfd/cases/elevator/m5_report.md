# M5 scenario C: elevator whodunit (2026-10-18)

*Code: `cfd/cases/elevator/{make_case.py, run_elevator.sh, analyze_elevator.py, fig_elevator.py}`,
`cfd/geometry/manikin.py` (`standing`, `write_elevator`) · numbers: `results.json` · figure:
`figures/fig15_elevator.png`*

## Set-up

- **Car:** 630 kg / 8-person elevator, inside 1.10 m wide × 1.40 m deep × 2.10 m high.
  - Width and depth are the KONE MonoSpace planning-guide car for 8/630.
  - 1.54 m² is within the EN 81-20 Table 6 maximum of 1.66 m² for 630 kg (as reproduced by Barney, 13th Symposium on
    Lift & Escalator Technologies).
  - The height is the lower of the two offered (2.10 / 2.20 m).
- **Occupants:** four standing manikins in a 2 × 2 grid, all facing the door.
  - Front row FL, FR at x = 0.95 m; back row BL, BR at x = 0.45 m; lateral ±0.27 m.
  - Built from the seated manikin's primitives; nose at 1.59 m (stature ≈ 1.69 m).
- **Physics:** same as the sofa duet. Transient RANS k–ω SST with Boussinesq buoyancy; skin 33 °C, walls 23 °C.
- **Ventilation:** fan off; a 0.2 × 0.2 m pressure-relief opening at the ceiling centre [ASSUMPTION].
- **Release:** the same 92 mL behind the culprit's buttocks, as a momentum-equivalent inlet.
  - silent: 2 s through 8 mm;
  - audible: 0.5 s through 2.4 mm.
- **Runs:** precursor 30 s, then four 60 s branches: culprit FL or BL × silent or audible. FR and BR follow by mirror
  symmetry.
- **Mesh:** 909 k cells, checkMesh OK (max skewness 2.9).
- **Run history:** the first branch was interrupted by a container reclaim at 20 s and resumed from its 20 s write.
  The second branch's final reconstruction hit the disk allowance and was redone. No solver errors.

## Doses (expected worst-breath OAV within 60 s, trained-panel thresholds)

| culprit | nose | silent | audible | R = silent / audible | first OAV ≥ 1, silent / audible (s) |
|---|---|---|---|---|---|
| front (FL) | culprit | 6.7 | 1.9 | 3.4 | 17.6 / 13.3 |
| | beside | 3.6 | 0.82 | 4.3 | 35.7 / – |
| | behind | **27** | 20 | 1.4 | **8.8** / 8.6 |
| | diagonal behind | 7.6 | 2.7 | 2.9 | 17.3 / 28.3 |
| back (BL) | culprit | 4.5 | **23** | 0.20 | 28.2 / 23.1 |
| | beside | 2.3 | 5.9 | 0.39 | 38.5 / 45.2 |
| | in front | 0.57 | 2.8 | 0.20 | – / 37.3 |
| | diagonal in front | 0.41 | 0.74 | 0.55 | – / – |

**Pathways** (cloud centroid in the culprit's mid-plane, `midLeft`):
- **Silent:** it follows the culprit's own back plume.
  - Front culprit: it rises in the 0.2 m gap between the culprit's back and the face of the person behind, reaching
    1.5 m by 10 s, i.e. straight into that person's breathing zone.
  - Back culprit: it rises in the gap between back and car wall, the same chimney as the sofa backrest, and reaches
    the front row only below threshold.
- **Audible:** the jet, aimed down and back, hits the floor (and, from the back row, the wall corner). It spreads
  along the floor and is lifted by all four body plumes, so it reaches more noses, more evenly.

**What decides silent vs audible is what stands behind the culprit.**
- A person behind: silent is stronger at every nose (R 1.4–4.3).
- A wall behind: audible is stronger at every nose (R 0.2–0.55).

Over the four equally likely culprit positions, silent is stronger in half of the culprit–nose pairs (8 of 16 by
symmetry). Equal mass, so this is routing, not momentum pre-dilution: the effect Theorem 1 allows to take either sign.

## Whodunit (odour only)

Detection per occupant: Φ(log₂(scale·OAV)/σ) (`uq/observer_ps.py`). Observers see only who reacted.

| mode | observer | culprit | no one reacts | P(culprit identified) |
|---|---|---|---|---|
| silent | attentive (population thresholds) | stays still | 61 % | 0.52 |
| | | acts along | 51 % | 0.49 |
| | distracted (everyday) | stays still | 91 % | 0.31 |
| | | acts along | 88 % | 0.31 |
| audible | attentive | stays still | 60 % | 0.46 |
| | | acts along | 39 % | 0.39 |
| | distracted | stays still | 92 % | 0.29 |
| | | acts along | 87 % | 0.28 |

Chance is 0.25.
- **An everyday (distracted) car:** about nine passages in ten go unnoticed by everyone. When someone does react,
  identification barely beats chance.
- **Attentive occupants** do better, but only about one time in two.
- **Silent vs audible:** odour-based identification is similar for both. The audible release is of course identified
  by ear, which is not modelled here.

**"He who smelt it dealt it"** (first nose to reach threshold, culprit acting along):
- Front culprit: the person **behind** is first (8.8 s, against the culprit's own 17.6 s), so the rule accuses an
  innocent.
- Back culprit: the culprit is first (28 s), so the rule is right.
- Overall the rule is right in half of the positions, for both modes.
- With attentive population thresholds:
  - silent: only the person behind a front-row culprit ever reaches threshold (16.5 s), so the rule picks that
    innocent or no one;
  - audible: the outcome is as with the trained panel (front culprit: the person behind at 16.4 s; back culprit: the
    culprit at 30.3 s).

## Caveats

- **Standing posture not validated.** The convective boundary layer was validated for the seated manikin only
  (M3b, 40–56 % too fast); standing plumes are stronger and taller.
- **RANS mean field:** instantaneous filaments are not resolved.
- **Assumed parameters:** the relief opening and the closed-door, fan-off car are assumptions. A running car fan would
  mix the car within seconds and erase the routing.
- **Fixed scene:** one volume and one release direction (down and back, as on the sofa); occupants all face the door.
- **Attribution model:** independent reactions, no sound cue, and a uniform prior.
