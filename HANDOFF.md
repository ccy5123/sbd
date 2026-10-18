# HANDOFF — headline redesign (written 2026-10-18, end of session)

Branch `m0-m1-m8-gate0`. Last pipeline commit `0ab410e` (literature findings applied, PDFs built clean). This file
and `uq/drafts/` and `cfd/probe_archive/` were added in the handoff commit that follows it.

The user (Korean; reply in Korean; clarify each question before answering; ask via AskUserQuestion with the
recommended option first) decided: **fix the headline-definition problems below in order (1 → 7), starting next
session.** Nothing below has been implemented yet. Explain the approach for each item and get approval before
changing code or manuscript.

## The goal the headline must answer

Chosen by the user earlier ("현실 빈도"): *in passages as they actually happen, how often is a silent one more
foul for the people nearby?* Requirements derived from it:

| | requirement |
|---|---|
| R1 | real passages: volumes as emitted (done) and scenes mixed by how often they occur (not done) |
| R2 | "foul" = perceived; a passage nobody smells has foulness 0 |
| R3 | comparative ("more foul"), not absolute |
| R4 | bystanders; a bystander who hears a passage becomes attentive |
| R5 | a frequency, and the memory side ("memory says mostly") must use the same population so the title's contrast is like for like |

## Rigorous definitions (current state)

Setup: CFD gives equal-mass (92 mL) worst-breath OAV per scene k and nose j, O_s and O_l. Gate 0 Monte Carlo gives
20 000 draws, one silent volume V_s,i and one audible V_l,i, each from its own distribution (class from the acoustic
onset). Linear scaling A = O·V/92 mL (route assumed independent of volume). Observer o detects with
p_o(A) = Φ(log2(s_o·A)/σ_o); smell events S_s, S_l are independent Bernoulli. JND = 1.28 (Weber 0.28). Groups are
averaged with equal weight per (scene, nose): 11 bystander noses, 7 culprit noses (the sofa 120 s run is excluded,
`uq/routing_headline.py:108`).

| | definition | bystanders, attentive | bystanders, distracted |
|---|---|---|---|
| A | P(A_s > A_l) | 0.30 | 0.30 |
| B | E[w·1(A_s > A_l)]/E[w], w = 1−(1−p_s)(1−p_l) (`uq/routing_headline.py:82`) | 0.35 | 0.37 |
| C | four outcomes: none / silent worse = S_s ∧ (¬S_l ∨ A_s > 1.28·A_l) / audible worse (symmetric) / JND tie | 82.5 / 6.3 / 10.6 / 0.7 % | 96.0 / 1.6 / 2.4 / 0.0 % |
| D | π_s = E[p_o(A_s)] vs π_l = E[p_o(A_l)] | 8.6 vs 12.5 % (ratio 0.69) | 1.7 vs 2.5 % (ratio 0.70) |

C and D come from `uq/drafts/headline_defs.py` (draft, not in the pipeline). The older "83 / 6 / 11" for C came from
the R > 1 weighted approximation in the code and is superseded.

Observers (`uq/observer_ps.py:37`, params `params/params.yaml:126-129`): all OAV use Nagata 2003 trained-panel
thresholds; observers differ only in the scale s and the spread σ (binary steps).

| observer | s | σ | 50 % detection at OAV | source |
|---|---|---|---|---|
| Nagata deterministic (Gate 0) | 1 | step | 1 | trained panel, upper bound |
| attentive, Wilby | 1/10 | 2 | 10 | Wilby 1969 |
| attentive, Amoore | 1/20 | 2 | 20 | Amoore & Hautala 1983 |
| distracted (everyday) | 1/520 | 3.5 | 520 | 26× threshold, Whisman 1978 via Amoore & Hautala |
| distracted, clothed emitter | 1/667 | 3.5 | 667 | Ohge 2005, clothing removes 22 % |
| distracted, sound cues attention | distracted if silent, attentive if heard | | | memory analysis only |

The headline uses only attentive-Amoore and distracted (`uq/routing_headline.py:36`). Intensity always uses the
attentive OAV (Fallon 2018); attention changes detection only.

## Problems to fix, in order

1. **[DONE 2026-10-18, code only: `uq/four_outcomes.py`, NOTES]** **Physics and memory numbers come from different populations** (confidence high). The headline uses CFD-routed
   scenes. The memory result "truth 0.32–0.51 → remembered 0.68–0.93" (`sections/discussion.tex:13`, Table
   `tab:observers`) uses the Gate 0 receptor, which puts the puff centre on the nose with no routing
   (`uq/observer_ps.py:3`). Its "truth" also counts both-unsmelled pairs as half ties (`perception/selection.py:35`).
   Gate 0, distracted: none 64 %, silent worse 19 %, audible worse 17 %, so "0.51" = 0.19 + 0.64/2
   (`uq/drafts/headline_ties.py`). Attentive: none 16 % in Gate 0 vs 83 % in the CFD scenes. Fix: run the memory
   filter (Theorem 3, `perception/selection.py` `noticed`/`compare`) on the routed population, and report it with the
   same four outcomes, without splitting ties.
2. **Time window cuts silent releases short** (high). Sofa 30 s (`uq/routing_headline.py:43`, `results_W30s.json`),
   elevator and standing 60 s (lines 56, 63). Silent releases are slow: sofa upright culprit R_eq goes from
   1.5e-12 (30 s) to 2.1 (120 s). Fix: window = residence time per scene. CFD only reaches 120 s (sofa) and 60 s
   (others); beyond that the options are new longer runs or a Theorem 2 well-mixed tail (C → V/V_room). Needs a
   source or an explicit assumption for residence times; discuss with the user.
3. **Scene weights are nose counts** (high). The elevator holds 6 of 11 bystander noses (3 people × 2 layouts). The
   three sofa postures count as separate scenes. Fix: weight per scene (postures/layouts averaged within a scene),
   or report per scene; real-frequency weights would need a source.
4. **B conditions on "at least one smelled"** (medium). Selecting on a union of two causes is the Berkson structure
   of Theorem 3, so B mixes the as-emitted and as-remembered bases. Drop B as a headline; keep at most as a remark.
5. **No sound-cued attention in the headline** (medium). The distracted bystander stays distracted when they hear a
   passage. `observer_ps.py` already has "distracted, sound cues attention"; use it for the bystander headline.
   This moves the result towards "audible worse", opposite to item 2.
6. **Eq. (1) has no detection threshold** (high). `sections/theory.tex:10` defines I = k·OAV^n, positive even
   below threshold; definition A violates R2 because of this. Fix: deadliness X = k·OAV^n if smelled, else 0 (the
   memory code already does this: `perception/run_selection.py`, `observer_ps.py` `intensity = np.where(smelled, …)`).
   Update theory text and the "every comparison states its basis" list.
7. **Headline choice** (my earlier recommendation of D was withdrawn). P(X_s > X_l) for independent draws is the
   standard probability of superiority; it answers R3 directly. Recommendation: C (four outcomes, no tie splitting)
   as the headline for both physics and memory; D as a secondary ("how often is a silent passage smelled at all").

Note on robustness: D's ratio ≈ 0.7 is the same for both observers partly because only the elevator noses are
non-zero and both observers sit in the low tail of Φ; Amoore & Hautala say extrapolation below 50 % response is not
supported (`params/params.yaml:128`). State this when quoting it.

Whether "seldom" survives is open: item 2 favours silent, item 5 favours audible.

## Data needed

CFD run directories (`cfd/runs/`, gitignored, ~16 GB) are lost when the container is reclaimed. The nose-probe time
series of all 14 release branches (sofa ×3 postures incl. the 120 s extension of upright, elevator ×2 layouts,
standing ×2 ventilations; fields s, T, U) are archived in `cfd/probe_archive/nose_probes.tar.xz` (1.7 MB). Extract
with `tar -xJf cfd/probe_archive/nose_probes.tar.xz -C cfd/runs` (creates `<case>/postProcessing/noses/…`), then the
`analyze_*.py` scripts can recompute worst-breath OAVs for other windows. Breathing-zone discs and planes are not
archived; longer windows than simulated need new runs (`cfd/cases/*/run_*.sh`, `sofa/extend_window.sh`).

## After the redesign (already pending)

- Fill the standing-pair GAP (`sections/results.tex:190`, `si.tex:198`) and update Fig. 16
  (`uq/fig_routing.py`), abstract, discussion, conclusion with the new headline.
- Decide whether the title keeps "seldom" (`main.tex:24`).
- AI-use disclosure (write last; do not mention the AI-generated ToC image).
- Zenodo DOI needs a GitHub release; outward-facing, confirm with the user first.

## Working rules carried over

- Rebuild: `python3 manuscript/preprint/make_figures.py <scripts>`, `python3 manuscript/preprint/make_params_table.py`,
  then latexmk `si.tex` before `main.tex` (xr cross-references, SI- prefix); check
  `grep -E "^! |undefined|multiply"` in both logs.
- Commits: `git -c user.name="Chan Young Joe" -c user.email="ccy5123ccy@gmail.com" commit`, message ends with the
  Co-Authored-By and Claude-Session lines; push with `git push -u origin m0-m1-m8-gate0`. No model identifiers in
  commits or PR text.
- Publisher PDFs stay out of the repo (`refs/pdfs_incoming/` is gitignored). Literature searches return DOIs only.
