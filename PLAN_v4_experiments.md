# Experiment redesign for the headline (PLAN v4, reinforced lite; approved 2026-10-19)

Scope chosen by the user: headline-centred (sofa / standing; elevator only as a supplement from the existing 60 s
runs), LES for the key scenes to get instantaneous peaks, clothing at two levels (bare vs trousers). A lighter version
was trimmed to the essentials and then reinforced where the trimming would weaken the headline (marked +).

## 1. The question and what answering it requires

Headline (HANDOFF "goal"): *in passages as they actually happen, how often is a silent one more foul for the people
nearby, and how does that compare with what memory says?* Requirements R1-R5 of HANDOFF.md hold. Answering it needs,
for every scene (weighted by real frequency: sofa 0.73, standing 0.26, elevator 0.005), bystander nose, clothing and
passage (V, T, d):

1. the breath-sampled worst-breath OAV distribution at the nose, not only its mean, because detection happens near
   threshold, where a meandering cloud's peaks decide whether anybody smells it (R2, R4);
2. over the residence time of the passage (10 min; R1);
3. for real passages: volume and exit momentum vary within each class (silent u0 < ~30 m/s onset, audible above),
   and most passages are clothed (R1);
4. through a body plume whose error is known.

## 2. Gaps in the current CFD

| # | gap | fixed by |
|---|---|---|
| G1 | RANS mean only (peaks can exceed the mean ~10x) | E4 |
| G2 | no clothing: trousers may remove most of the momentum difference that drives routing | E1-E4 |
| G3 | body plume 40-56 % above Licina 2014. FluidX3D LES gives the same plume as the RANS (0-7 %), so the bias is in the set-up (bare 33 C skin, small sealed room), not the turbulence model; skin 30 C halves it | E0-1 |
| G4 | one source per class (92 mL) with linear volume scaling; the silent class spans u0 ~0.5-30 m/s | E2 momentum levels |
| G5 | window 30-60 s; release into a 30 s precursor whose room flow is still developing | E1 + E3 |
| G6 | the FluidX3D test put a filament on the releaser's own nose ~11-13 s after a bare silent release (RANS: none); magnitude not reliable there (`cfd/lbm/feasibility_report.md`) | E4 bare sofa |

## 3. Strategy

- Validation (E0) first, including a check of the frozen-flow shortcut against coupled 10-min reference runs.
- RANS response map (E1-E3), split in time: developed background flow (E1); fully coupled release phase, release +
  ~3 s (E2); frozen-flow passive-scalar transport from there to 600 s on the E1 field (E3). Transport is linear, so
  one run per (geometry, clothing, momentum level) serves every volume at that momentum.
- LES (E4) in the scenes that carry ~99 % of the weight, with staggered releases on separate scalars (many
  realisations per run). Output: the peak factor (breath-sampled peak / ensemble mean) applied to the RANS map.

## 4. Experiments

### E0 Validation

| id | test | acceptance / use |
|---|---|---|
| E0-1 | seated CBL vs Licina 2014 (B&E 75:79; Indoor Air 2014 HP0127 set-up: NUS chamber 11.1 x 8 x 2.6 m, displacement ventilation at minimum flow, female manikin in summer clothing, total heat output 65 W/m^2; peak 0.185 m/s at mouth height 14 mm from the face, 23 C; nude 0.205 m/s, clothing -17 to -40 %). Set-up variants instead of mesh refinement (FluidX3D showed the bias is not a mesh/model effect): compare at the measured point (mouth height, 14 mm), heat-flux skin instead of a fixed 33 C, larger room. Done in FluidX3D (same plume as the RANS, 30 min per run) and confirmed with one RANS run | within 20 %; otherwise the remaining bias is stated and carried as a transport-time factor (as `u_own_eff` does now) |
| E0-2 + | standing plume vs Craven & Settles 2006 (J Fluids Eng 128:1251, doi 10.1115/1.2353274; real person, clothed, 0.24 m/s at 0.43 m above the head; clothing surface 26.6 C at 21.3 C room) | within 20 % |
| E0-3 + | near-body source to breathing zone vs Licina, Tian & Nazaroff 2017 (B&E 123:14, doi 10.1016/j.buildenv.2017.06.037, Table 2: seated heated manikin, groin source at 0.5 m: intake fraction 9.8 per mille vs 1.2 unheated; well mixed 4.2); Rim & Novoselac 2010 Table IV (source accessibility of 12 body positions) as a second check | intake-fraction ratio heated/unheated and groin/well-mixed within a factor 1.5 |
| E0-4 | free jet (existing `cfd/validation/jet`) | passed |
| E0-5 | frozen-flow shortcut (E2+E3 on the 30 s precursors) vs coupled 10-min reruns: sofa upright and standing still, silent and audible (4 branches, running) | worst-breath OAV within a factor 1.5 and the same four-outcome class at >= 90 % of noses; else coupled E3 for that scene |
| E0-6 + | mesh convergence: one E2+E3 case (sofa upright, bare, silent median) on a mesh refined once more | change in nose dose stated as numerical uncertainty |
| E0-7 | reproduction of the archived runs in the OpenFOAM 13 container (elev_BL_silent to 60 s) | bitwise identical so far (1.2 s) |

### E1 Developed background flow

5 geometries (sofa upright, reclined +4.5 and -10 deg (+), standing still, standing ventilated) x 2 clothing (bare,
trousers as a porous layer over pelvis and thighs with woven-trouser permeability, open at waist and hems) = 10
fields. Transient RANS to statistical stationarity (room-mean T and |U| change < 1 % over 60 s); steady SIMPLE did
not converge in M3b.

### E2 Coupled release phase

10 fields x 4 momentum levels (silent median and 90th percentile, audible median and 90th percentile (+) of M0 from
the Gate 0 Monte Carlo) = 40 runs, each release + 3 s; unit source strength; median composition buoyancy
(g' = 1.70 m/s^2). Plus 1 mesh-convergence run (E0-6).

### E3 Frozen-flow transport to 600 s

41 runs, scalar only on the frozen E1 field (U, turbulent diffusivity) from the end of E2 to 600 s. Nose probes
every step; windows 30, 60, 120, 300, 600 s.

### E4 LES

Sofa upright (bare (+) and trousers) and standing still (trousers): 3 runs. Each: LES precursor to stationarity,
then ~360 s with 6 releases 45 s apart, alternating class and momentum level, each on its own scalar. Per nose:
breath-sampled worst-breath OAV per release vs the ensemble mean -> peak-factor distribution (by mean level and time
since release). The bare sofa run also tests the own-nose filament (G6).

## 5. How the results feed the headline

Monte Carlo over passages (V, T, d -> class, M0), scenes (real-frequency weights, central + two bounding cases),
sofa posture (equal weights over the three, as a stated assumption), clothing (clothed share: assumption with a range,
e.g. 0.7-1.0), noses and breath phase: nose OAV = E3 response at the nearest momentum levels (log-interpolated)
x V-scaling x LES peak-factor draw -> observer detection (attentive / distracted / sound-cued) -> four outcomes,
physics and memory on the same population (HANDOFF items 1, 4, 5, 6, 7).

## 6. Budget (20 cores, nice 19) and schedule

| block | runs | core-h |
|---|---|---|
| reference coupled runs (running) | 4 | ~300 |
| E0 (CBL variants, frozen check, mesh run, optional E0-2/3) | ~10 | ~350 |
| E1 developed flow | 10 | ~120 |
| E2 + E3 | 41 + 41 | ~350 |
| E4 LES | 3 | ~900 |
| total | | ~2,000 (~1,600 new) |

About 3.5 days of computing at 20 cores, 5-6 days in all with set-up and analysis (E4 overlaps E1-E3 after E0).
Extra time if E0-5 fails (coupled 600 s runs instead of the shortcut: +1-2 days) or the porous trousers misbehave
(+0.5-1 day). GPUs are not used (FluidX3D stays a cross-check).

## 7. Decisions still open

- Clothed share of passages per scene (assumption or a source).
- Sofa posture weights (equal by default).
