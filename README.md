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
