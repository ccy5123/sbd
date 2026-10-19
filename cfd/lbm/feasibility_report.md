# FluidX3D feasibility test (2026-10-19)

Question: can a GPU lattice-Boltzmann LES (FluidX3D, RTX 3090) replace or cross-check the OpenFOAM RANS for the
headline runs? Code: FluidX3D fork, branch `sbd` (local `research/FluidX3D-sbd`, server `~/cyjoe/research/FluidX3D`);
setups in `src/setup_sbd.cpp`; analysis in `cfd/lbm/`. Runs on the company server, GPUs 1-3 (GPU 0 is reserved for
the CMAQ service). Uniform 5 mm grid, dt 1.25 ms (u_lb 0.1 at 0.4 m/s), D3Q19 TRT + Smagorinsky, D3Q7 thermal.

## Changes to FluidX3D

- Passive scalar on a second D3Q7 lattice, FP32 without DDF shifting (FP16 storage loses concentrations below ~1e-3),
  fixed-concentration cells, Smagorinsky eddy diffusivity nu_t/Sc_t (Sc_t 0.7).
- Boussinesq-only buoyancy (the full gravity force gives a hydrostatic density change of several hundred percent on
  this lattice).
- Thermal eddy diffusivity nu_t/Pr_t (Pr_t 0.85); bounds on T and C (cells outside the boundary range are reset to
  equilibrium at the bound); optional floor on the thermal and scalar diffusivities.
- Time-step switch for the jet phase of an audible release (fields carried across, velocity scaled).
- Geometry as the union of separately voxelized closed parts (`cfd/lbm/stl_parts.py`): ray-parity voxelization of
  one mesh of overlapping primitives turned the seat/backrest overlap into a sealed fluid pocket that blew up.

## Results

1. **Unit tests.** Scalar diffusivity within 0.4-0.8 %, advection speed within 0.6 %, mass to 1e-7 (periodic).
   FluidX3D's own thermal diffusivity is half the value passed in (`def_w_T = 1/(2 alpha + 1/2)` on a D3Q7 lattice
   with c_s^2 = 1/4); the runs pass 2 alpha.
2. **Seated CBL vs Licina et al. 2014** (M3b room, 81 M cells, 120 s, 60-120 s averages; `cbl_t*/cbl_result.json`):

   | room | FluidX3D | OpenFOAM RANS | Licina | FluidX3D bias |
   |---|---|---|---|---|
   | 20 C | 0.339 m/s | 0.342 | 0.24 | +41 % |
   | 23 C | 0.297 | 0.277 | 0.20 | +48 % |
   | 26 C | 0.259 | 0.249 | 0.16 | +62 % |

   LES and RANS agree within 0-7 %, so the 40-60 % over-prediction comes from the set-up, not from the turbulence
   model or the mesh. Skin 31.5 C: +42 %; 30 C (closer to a clothed surface): +27 %. Clothing explains about half.
3. **Sofa release** (215 M cells, 21.5 GB, ~46 ms/step; 150 s in ~1.5 h per GPU). Without a diffusivity floor the
   scalar is not conserved: the clamping of negative concentrations from D3Q7 oscillations at tau ~0.503 adds mass
   (x18 over 120 s, silent), and the nose signals are at the noise level. With a floor (silent, 20 s after release):

   | floor (m^2/s) | scalar mass drift | releaser nose peak s | neighbour nose |
   |---|---|---|---|
   | 0 | x3.6 | 6.7e-4 | 8e-5 (spurious) |
   | 1.5e-4 | +7 % | 4.0e-4 at 11 s | 4e-12 |
   | 5e-4 | +5 % | 4.8e-5 at 13 s | 1.5e-10 |

   RANS (archive): releaser 6e-18, neighbour 4e-21 within 30 s. With a floor the LES agrees that the neighbour gets
   nothing within 20 s, but it puts a filament on the releaser's own nose ~11-13 s after a silent release, with a
   magnitude set by the floor (x8 between 1.5e-4 and 5e-4).

## Verdict

- Speed and the body plume: go (same plume as RANS at a fraction of the cost).
- Low-concentration scalar transport, which the headline needs: not reliable on a uniform 5 mm D3Q7 SRT lattice. A
  conservative result needs a diffusivity floor ~10x molecular, and the near-threshold nose doses then depend on it;
  a finer grid is out of memory reach for the room (2.5 mm = 1.7e9 cells). Making it reliable needs a better
  advection-diffusion scheme (e.g. regularised or central-moment D3Q7/D3Q19 for the scalar), i.e. further
  development and its own validation.
- Kept as a cross-check: the CBL agreement, and the own-nose filament after a silent release as a hypothesis for an
  OpenFOAM LES check.

## E0-1 follow-up: Licina's measuring point (PLAN v4)

Licina's peak is at mouth height 14 mm from the face (Indoor Air 2014 HP0127; 0.185 m/s clothed, 0.205 m/s nude at
23 C). Time-mean Uz 14 mm in front of the nose tip (faceLine, 60-120 s): 0.314 / 0.278 / 0.242 m/s at 20 / 23 / 26 C
(skin 33 C), 0.266 (skin 31.5 C) and 0.237 (skin 30 C) at 23 C, i.e. about 6 % below the line maximum. Against the
nude reference the 33 C skin is +36 %; the 30 C (clothed) surface against the clothed reference +28 %. The remaining
~30 % (likely the chamber's displacement-ventilation stratification and the manikin shape, neither reproduced here)
is stated as a limitation and carried as a transport-time factor, as `u_own_eff` does now.
