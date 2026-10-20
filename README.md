# Silent But Deadly? — The Silencer Conjecture

A fluid-dynamical, perceptual and cross-cultural test of the folk belief that *the less audible a fart, the
worse it smells* ("silent but deadly", the "Silencer conjecture").

Deadpan rigour: the physics, units, validation and statistics are serious; the humour lives in the scenarios.

- `PLAN.md` — research & simulation plan (v3), the governing document
- `NOTES.md` — running log of assumptions, results and open issues per module
- `params/params.yaml` — single source of truth for every parameter, with source and status flag
- `refs/` — verified bibliography (`references.yaml`) and the M0 verification log
- `gate0/` — Module 0: analytic order-of-magnitude model (`model.py`, `run_gate0.py`, tests, report)
- `culture/` — Module 7: cross-cultural documentary survey of the belief
- `figures/` — generated figures

## Reproduce

```bash
pip install numpy scipy pandas matplotlib pyyaml pytest
python3 -m pytest gate0 -q          # model limit/consistency tests
python3 gate0/run_gate0.py          # ratio maps, Monte Carlo P(SBD), sensitivity -> figures/, gate0/results.json
```

## Source files of each result in the manuscript

The manuscript (`manuscript/preprint/`) points here from its Data accessibility statement; the electronic
supplementary material does not repeat this list.

| result | files |
|---|---|
| parameters (ESM parameter table) | `params/params.yaml` |
| odorant shares, buoyancy, losses | `chem/odorants.py`, `chem/buoyancy.py`, `chem/reactivity.py`, `chem/chem_report.md` |
| acoustics | `acoustics/regime.py`, `acoustics/run_m2.py`, `acoustics/m2_report.md` |
| analytic dispersion model | `gate0/model.py`, `gate0/run_gate0.py`, `gate0/gate0_report.md` |
| uncertainty, regime map | `uq/run_m7.py`, `uq/m7_report.md` |
| passages as emitted in the scenes | `uq/routing_headline.py`, `uq/routing_headline.json`, `uq/fig_routing.py` |
| CFD validation | `cfd/validation/jet`, `cfd/validation/cbl`, `cfd/validation/m3_report.md` |
| sofa | `cfd/cases/sofa`, `cfd/cases/sofa/m4_report.md` |
| elevator | `cfd/cases/elevator`, `cfd/cases/elevator/m5_report.md` |
| standing pair | `cfd/cases/standing` |
| geometry | `cfd/geometry/manikin.py` |
| nose-probe series of the CFD runs | `cfd/probe_archive/nose_probes.tar.xz` |
| breath sampling, perception | `perception/model.py`, `perception/run_m6.py`, `perception/m6_report.md` |
| observer models, memory | `uq/observer_ps.py`, `perception/selection.py`, `perception/run_selection.py` |
| cross-cultural survey | `culture/cross_cultural_table.csv`, `culture/survey_summary.md` |
| manuscript figures | `manuscript/preprint/make_figures.py` |
