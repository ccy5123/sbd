# M3 report — CFD validation (free round jet, seated-manikin CBL)

*2026-10-15 · OpenFOAM 13 (openfoam.org), RANS · code: `cfd/validation/{jet,cbl}/` · numbers:
`cfd/validation/jet/results.json`, `cfd/validation/cbl/results.json` · figures: `figures/fig4_jet_validation.png`,
`figures/fig4_cbl_validation.png`, `figures/fig_conveyor_belt.png`*

## M3a — free round jet

**Set-up**

- Steady RANS (`incompressibleFluid`) on an axisymmetric 5° wedge. Passive scalar s via `scalarTransport` (Sc_t = 0.7).
- Nozzle d = 10 mm, U₀ = 10 m/s, Re = 6 700. Domain 100 d × 40 d.
- Boundaries:
  - no-slip base wall (jet issuing from a wall);
  - entraining side boundary (total pressure 0);
  - outflow-only outlet.
- Momentum flux is conserved within 3.5 % up to x/d = 95.
- Two earlier set-ups were rejected and are recorded in `NOTES.md`:
  - a 1 % co-flow, whose momentum flux over 40 d rivalled the jet's;
  - an open total-pressure outlet, which let k-ε settle into a spurious reverse-flow state.
- Meshes: coarse / medium / fine = 150 / 300 / 600 axial cells, with radial refinement doubled at each level.
- Fits over x/d = 20–90:
  - centreline velocity decay U₀/U_c = (x − x₀)/(B_u d);
  - scalar decay c₀/c_c = (x − x₀)/(K_c d);
  - spreading rate S = dr½/dx.

**Results** (reference values: B_u = 5.8, Hussein et al. 1994; K_c = 5.11, Dowling & Dimotakis 1990; S = 0.094)

| case | B_u | K_c | S | error B_u / K_c / S |
|---|---|---|---|---|
| SST coarse | 5.03 | 4.57 | 0.117 | −13 % / −11 % / +25 % |
| SST medium | 4.93 | 4.25 | 0.121 | −15 % / −17 % / +28 % |
| SST fine | 5.01 | 4.33 | 0.119 | −14 % / −15 % / +26 % |
| k-ε medium | 4.97 | 4.30 | 0.117 | −14 % / −16 % / +25 % |
| k-ε, C_ε1 = 1.6, medium | 7.54 | 7.85 | 0.083 | +30 % / +54 % / −12 % |

- **Mesh uncertainty.** Convergence is oscillatory for all three quantities. Following Stern et al. 2001, the
  half-range of the three solutions gives U_mesh = 1.0 % (B_u), 3.7 % (K_c) and 1.5 % (S). The model error is an
  order of magnitude larger than the discretisation error.
- **Model error.** Standard RANS shows the known round-jet anomaly. Both SST and k-ε over-spread the jet by about 25 %
  and decay the centreline about 15 % too fast. The classic round-jet correction (C_ε1 = 1.6) over-corrects at this
  Reynolds number (S −12 %, K_c +54 %), so SST is kept.
- **Consequence for the study.** RANS dilutes a free jet about 15 % faster than reality. An audible release is the
  jet-like one, so RANS slightly under-predicts the audible concentration and biases R = C_silent / C_audible upward,
  i.e. *towards* the belief. This bias is stated wherever R comes from CFD.
- **Relevance to Scenario A.** In the sofa scenario the jet impinges on the seat within about 3 cm. Its far-field decay
  constant matters less there than in this free-jet test.

## M3b — human convective boundary layer (CBL)

**Set-up**

- Simplified seated manikin built from primitives (`cfd/geometry/manikin.py`), half model with a symmetry plane, in a
  2.0 × 1.0 × 2.5 m half room.
- Skin 33 °C; walls at room temperature (20 / 23 / 26 °C).
- k-ω SST with wall functions, Boussinesq (`fluid` solver).
- Coarse snappyHexMesh mesh of 340 k cells, with 3 surface layers on the body.
- **Steady runs rejected.** Steady SIMPLE did not converge: the face-front peak velocity swung 0.03 → 1.1 m/s with a
  period of about 2 000 iterations. The closed-room buoyant circulation has no steady state, and averaging pseudo-time
  has no meaning.
- **Transient runs used.** 60 s of physical time, Euler, max Co 5. The 20 and 23 °C runs start from the last steady
  field; the 26 °C run starts from rest. Statistics are taken over 30–60 s (`fieldAverage` UMean/TMean; line samples
  every 0.5 s).

**Results** (pending: 26 °C run)

| room | peak U_z in front of face (mean ± sd) | Licina et al. 2014 |
|---|---|---|
| 20 °C | 0.34 ± 0.01 m/s | 0.24 m/s (clothed), 0.205 m/s (nude) |
| 23 °C | 0.28 ± 0.02 m/s | ≈ 0.20 m/s (linear between 20 and 26 °C) |
| 26 °C | *queued* | 0.16 m/s |

- The CFD conveyor belt is about 40 % faster than the thermal-manikin measurement at both 20 and 23 °C.
- The room-temperature trend has the right sign and size: −19 % from 20 to 23 °C, against −17 % interpolated from
  Licina et al.
- Candidate causes:
  - coarse near-wall resolution with wall functions;
  - a sealed half room whose walls are held at room temperature (no stratification);
  - a geometric manikin with no hair or clothing.
- The full room-temperature trend (Licina: −33 % from 20 to 26 °C) will be checked once the 26 °C run completes.

**Conveyor-belt trajectories** (time-mean field, `cfd/postprocess/conveyor_from_cbl.sh`; the figure shows 23 °C, the
Scenario A room temperature):

- At 20 °C, 5 of 8 massless parcels released at seat level reach nose height, in **4.7–7.4 s**.
- At 23 °C, 6 of 8 reach it: five in **6.8–8.0 s** and one from behind the hips in 18.4 s.
- Gate 0 assumed L/u = 0.74 / 0.17 ≈ 4.4 s for own-nose transport. The CFD time is 1.1–1.8× that at 20 °C and about
  1.6–1.8× at 23 °C (ignoring the slow parcel).
- The earlier 8–18 s from the unconverged steady field is withdrawn.
- Given the 40 % over-prediction of the CBL velocity, the true transport time is probably longer still. Gate 0 will
  carry the CFD range as its own-nose transport-time distribution.

## Limitations

- RANS only (no LES). Coarse CBL mesh; the medium-mesh CBL check is not yet run.
- The CBL validation compares a single scalar (the peak face-front velocity) with one experiment.
- The Licina et al. values are for a thermal manikin in a climate chamber with controlled wall temperatures. The
  half-room domain here is smaller.
