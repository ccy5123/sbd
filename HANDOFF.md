# Status 2026-10-25 (read this first; the sections below are the history behind it)

**Session rules:** CLAUDE.md (say local vs cloud first; Korean; clarify with AskUserQuestion, recommended option
first; no PR watching). Commit on `main` only: `git -c user.name="Chan Young Joe" -c user.email="ccy5123ccy@gmail.com"
commit`, trailer `Co-Authored-By: Claude <noreply@anthropic.com>`, no model identifiers. Server and local-PC work
needs a **local** session (Remote Control cannot start new sessions; the desktop app can).

## Where things stand

- **Venue:** J. R. Soc. Interface (fallback The Science of Nature, EPJ Plus); preprint on engrXiv with full AI
  disclosure. Plan and referee-style work list: `manuscript/preprint/interface_plan.md` §9 (A done, B after the runs).
- **Finished CFD (v4 multi-release RANS, results in `cfd/results_v4/`):** sofa upright / reclined 4.5 / leaning -10,
  standing still / ventilated, all bare; trousers: standing still, sofa upright and standing ventilated (the last
  two done 25 Oct 05:05 / 11:40 KST, analysed the same day). Summary below ("E2' ... done"). Trousers, as emitted,
  150 s worst breath releaser / neighbour: sofa upright A90 115 / 43.1, A50 63.9 / 1.0, S90 1.05 / 0.07, S50 4.97 /
  0.11 (bare 48.9 / 16.9, 6.3 / 0.16, 6.6 / 0.09, 0.33 / 0.07); standing ventilated A90 20.1 / 0.56, A50 38.5 / 0.10,
  S90 21.8 / 0.07, S50 0.16 / 0.15 (bare 6.9 / 0.03, 14.5 / 0.02, 2.8 / 0.05, 0.38 / 0.17). Trousers raise the
  audible releases at both noses; silent ones at the neighbour stay ~0.1. v4 headline, trousers only (three scenes),
  bystanders, frequency-weighted, attentive: physics 0.1 % silent worse vs 11.1 % audible worse, memory 88.0 %.
  Not yet done: the clothed-share mixture (0.7-1.0) in `four_outcomes_v4.py` (decide how passages mix: per passage
  or linear).
- **A1-A4 done (2026-10-24, §9.4-9.7):** routing map (`figures/routing_map_paper.svg/.png`, OAV vs Pi = M0/m_p); v4
  headline `uq/four_outcomes_v4.py` (bare, bystanders, frequency-weighted, attentive: physics 0.4% silent worse vs
  6.8% audible worse, memory 91.5% silent worse); source sensitivity `uq/source_sensitivity.py` (silent share
  76-94%, direction never flips); A3 text plan. A5 (E0-6 mesh x1.5 run, E0-3 Licina 2017 chamber, heated and
  unheated) is approved for after ~29 Oct when cores free up.

## Runs in progress (as of 2026-10-26 09:20 KST)

RANS multi-release runs end at 240.2 s, the LES at 300.2 s. Pipeline log times are UTC (`date -u`): 06:54 = 15:54 KST.
LES releases: S50 60.2, A50 90.2, S90 120.2, A90 150.2, S50b 180.2, A50b 210.2 s. The pulses are slow, A90 most of
all (u0 162 m/s, dt 2.9e-5 s at Co 0.8): bare LES on 4 local cores ~17 h for its 0.69-s pulse piece, S50 (4.8-s jet)
~10 h, A50 ~8 h, S90 ~4 h; gaps ~5 s/h. Trousers LES on 18 server cores: ~4.2 s/h in the gaps.

| run | where | state | expected |
|---|---|---|---|
| LES sofa trousers | server `sbd-v4_sofa_tr_les18`, 18 cores; moves to 12 cores (`sbd-v4_sofa_tr_les12r`) at the 150.84-s checkpoint | in the A90 pulse since 07:22 KST, 150.46 s at 15:34 | ~28 Oct, may slip |

**26 Oct, server shared:** from 09:20 KST another session on the `user` account (from 192.168.50.213) runs a `python3`
job on ~5 cores; load 26 on 18 physical cores slowed the 18-rank LES ~2.4x (A90 pulse 0.07 -> 0.03 s/h). User's choice:
re-decompose to 12 cores at the next checkpoint. Watcher `cfd/docker/les_resize.sh 12` (running from
`sbd-main/scratch/`, started 15:40, log `les_grow.log`). When that job ends, grow back with `les_resize.sh 18`. (A
`python3` job in the local `Ubuntu` distro, user cyjoe, also competed with the local LES for a while on 26 Oct.)
| LES sofa bare | local PC (WSL `sbd-openfoam13`, `/root/sbd/cfd/runs/sofa_v4_multi_les`), 4 cores | restarted 26 Oct 09:09 KST from 175.84 s (see below) | ~28 Oct 03:00 |
| elevator multi-release, FL culprit | stopped (plan C) | precursor written to 45 s of 90 (`elev_v4_pre`, 3 subdomains) | ~28 Oct night |

**Elevator, plan C (user's choice 26 Oct):** run beside the bare LES on 3 local cores (25 Oct 21:50), it doubled the
LES's time per step (5.7 -> 11.8 s, same dt and steps: memory-bandwidth contention on the 8-core PC), so running both
gained nothing. Stopped 26 Oct ~09:05 at the 45-s write. When the trousers LES ends (~28 Oct morning) move the elevator
to the server (copy `elev_v4_pre` + elevator scripts; the server clone may lack `make_case.py --mode multi`) and run it
on several cores there, next to the A5 runs. The local chain `sofa_les` still calls the elevator after the bare LES
(~28 Oct 03:00, alone, 3 subdomains kept), so by then it may have advanced locally: move it from wherever it is, or
keep it local if that is faster. `elevator/run_multi.sh` holds a lock (`cfd/runs/.elev_FL.lock`) against a second copy.

**26 Oct incident (local):** stopping the elevator with `pgrep -f 'elevator/run_multi.sh'` also matched the bare-LES
chain (its command line names the elevator script) and killed its parent shells; WSL then ended the whole session,
LES included. Lost the 175.84-177.37 s piece (~30 min); restarted with `start_local.ps1 -Name sofa_les`. Stop runs by
exact PID (or by the case name in the mpirun working directory), never by a pattern that the chain's command matches.

**25 Oct incident:** at 13:32 KST `les_grow.sh` moved the trousers LES from 16 to 20 cores; mpirun refused 20 ranks
(the server has 18 physical cores: "not enough slots"), `run_multi.sh` only checked "FOAM FATAL", so it marked
segments 20-64 done in seconds and exited; no data lost (90.92 s intact). ~2.3 h idle. Restarted by hand on 18 cores
(user's choice). Fixed: `run_multi.sh` now also fails on a nonzero mpirun exit (copied to the server's
`run_multi_v4.sh`; the local WSL copy is unchanged while it runs), `les_grow.sh` caps one run at MAXNP=18.

Automation (all committed):
- server `cfd/docker/les_grow.sh`: done (exited 25 Oct; the LES now has all 18 physical cores). It moved every 4 freed
  cores to the trousers LES at its next 5-s checkpoint.
- local `cfd/local/start_local.ps1 -Name sofa_les` chains the bare LES and then the elevator; the Startup shortcut
  `sbd local CFD resume.lnk` reruns it at login (lock prevents duplicates; launched through WMI so app updates
  cannot kill it). `move_les_bare.sh` and its shortcut are done/retired. **Delete the Startup shortcut when the
  local runs finish**, and later `wsl --unregister sbd-openfoam13` (~10 GB) only after copying results out and with
  the user's OK.
- all v4 run scripts resume from their latest write; CHECKPOINT=5 / KEEP=3 everywhere now.

Watch-outs:
- **Server access needs the office Wi-Fi "EH R&C"** (192.168.50.x). On the wired 192.168.0.x network SSH times out.
  If the server stops answering ARP on Wi-Fi, ask the user to check it.
- **After a server reboot** (happened 23 Oct 09:35): `docker ps` shows no sbd containers. Restart each run with
  `cfd/docker/run.sh` and the same env (they resume), re-decompose the LES if its core count changes, restart
  `les_grow.sh`. Ask the user to warn before rebooting so runs can stop at a checkpoint.
- Git Bash rewrites `/root/...` arguments to WSL: prefix `MSYS_NO_PATHCONV=1` or feed scripts on stdin.
- Python for analysis runs in the `sbd-openfoam13` distro (numpy 1.26, scipy, matplotlib):
  `MSYS_NO_PATHCONV=1 wsl.exe -d sbd-openfoam13 -- bash -c 'cd "/mnt/c/Users/EH R&C CY/research/sbd" && python3 ...'`.
  **Figures (FIGSTYLE v1.2, `~/.claude/FIGSTYLE.md`):** run figure scripts with `/root/figenv/bin/python` (venv with
  system site packages + matplotlib 3.11.2; Arial installed in the distro). The system matplotlib 3.6.3 sets
  superscripts too high with Arial (kg⁻¹, m²), so do not draw figures with plain `python3`.

## Side task: 1st Liner Scholar research contest (user registered; submission 26 Oct - 8 Nov 23:59 KST)

Literature comparison of a common belief; written and exported as PDF in Liner Scholar (~10,000 characters with
spaces, references excluded); file name `제1회 라이너 스콜라 연구공모전_논문 제목_이름`; finalists 13 Nov 18:00, on-site
finals 19 Nov 10:00 (absence = elimination); eligibility: Korean nationality, 14+. Guideline docx: Batang body text.
- Draft: `manuscript/liner_contest/draft_ko.md` (user's choices: the silent-but-deadly belief; literature in three
  topics, composition / dispersion / perception and memory, with the v4 CFD and Monte Carlo folded into each as
  "unpublished simulation"; conclusion "wrong for bystanders' real exposure, the memory filter makes the belief").
  Length: `python manuscript/liner_contest/count_chars.py` (9,251 with spaces on 26 Oct). Placeholders `[ ]`: name,
  date, the user's actual Liner Scholar steps (the methods section also discloses Claude use; keep it truthful).
- Figure 1 (comic, from the 3D viewer): the user picks scenes and puts screenshots in `manuscript/liner_contest/raw/`;
  annotate with speech bubbles and labels, FIGSTYLE v1.2 paper `onehalf`, except the font: Batang (user's choice
  "the docs' font", from the guideline docx; one-line override note in the script). Batang is installed in the
  sbd-openfoam13 distro (`/usr/local/share/fonts/korean/batang.ttc`). No images of the film's characters.

## Next tasks

1. **[DONE 2026-10-24, `interface_plan.md` §9.8]** `uq/tail_sensitivity.py` (audible:silent 4-111, memory 62-100 %,
   never flips), `uq/belief_vs_detection.py` + `figures/belief_vs_detection_paper.svg/.png` (memory falls to the truth, 29 %,
   at full detection), `uq/peak_breakeven.py` (a silent-only factor ~14 flips the headline, a uniform one never;
   compare with the LES in task 3). Rerun all three when the remaining runs land. Original brief:
   - psychometric-tail sensitivity: the bystander OAVs sit far below the 50% point, so vary the slope sd (attentive
     1-4, distracted 2-5 binary steps), the tail shape (probit, logistic, hard floor) and the deterministic Nagata
     case; report whether audible-worse : silent-worse (~17:1) and the memory share keep their direction;
   - belief vs detection rate on the v4 population (bystanders, bare, frequency-weighted): sweep the observer scale,
     plot the remembered "silent seems worse" share and the truth against the share of passages smelled, with the
     releaser for contrast (answers "91.5% is tautological"; replaces the old Figure 13 basis);
   - peak-factor break-even: the uniform multiplier, and a silent-only one, that would lift the silent release over
     OAV 1 and OAV 20 at a bystander in each scene, and that would make silent-worse >= audible-worse in the headline
     (to compare with the LES peak factors when they land).
2. **Figures: follow FIGSTYLE v1.2 (user's rules, 25 Oct; see memory and `figstyle.py` once the full code block is
   in).** As runs finish: `analyze_multi.py` on each (fetch `postProcessing/noses` from the server as a tar.xz,
   extract into `cfd/runs/`, run in the WSL distro) (`--noses FL,FR,BL,BR` for the elevator), copy JSON and nose probes to
   `cfd/results_v4/`, rerun `uq/four_outcomes_v4.py` (clothed share 0.7-1.0 once both trousers runs are in) and
   `cfd/postprocess/routing_map.py`; refresh the 3D viewer (`export_viewer.py`, `export_iso.py`; artifact
   https://claude.ai/artifact/5sLUdRH1bG9nksx2vJFcvL, data files under the scratchpad viewer folder).
3. LES peak factors from the two sofa LES runs, then the headline with peak factors.
4. A5 validation runs after ~29 Oct; then the B stage (rewrite Methods/Results/figures on v4, fill gaps, title check,
   Zenodo with the user's OK, AI statement by the author).

# Status 2026-10-19 to 2026-10-23 (history)

- **Plan:** `PLAN_v4_experiments.md` (approved): validation, RANS response map, LES for the peak factor. Target: one
  complete preprint after these runs (user chose option A: no partial preprint). Preprint server: engrXiv (user's choice
  2026-10-20), although its AI policy bans verbatim LLM-generated text; the author submits without rewriting,
  accepting a possible hold or rejection, with full AI disclosure (`interface_plan.md` §8). The J. Immat. Sci. bans all AI-generated
  content, so a JIS version would have to be written by the author without AI.
- **E2' bare runs done (2026-10-21):** sofa upright, sofa reclined +4.5, standing still air; `analyze_multi.py`
  results in `cfd/results_v4/<case>.json`, nose probes in `cfd/results_v4/nose_probes_bare.tar.xz`. Worst breath
  over 150 s, as emitted (RANS mean), releaser / neighbour: sofa upright A90 48.9 / 16.9, A50 6.3 / 0.16,
  S90 6.6 / 0.09, S50 0.33 / 0.07; reclined A90 25.2 / 19.4, A50 2.1 / 0.95, S90 19.8 / 0.95, S50 0.26 / 0.12;
  standing A90 1.9 / 0.002, A50 0.26 / <0.001, S90 0.85 / 0.002, S50 0.13 / 0.006. No silent release reaches a
  neighbour above OAV 1. Standing ventilated (done 2026-10-22): A90 6.9 / 0.03, A50 14.5 / 0.02, S90 2.8 / 0.05,
  S50 0.38 / 0.17 (`stand_vent_v4_multi.json`, `nose_probes_stand_vent.tar.xz`). Sofa leaning forward -10 (done
  2026-10-22 15:17): A90 22.3 / 35.8 (neighbour reached in 2.3 s), A50 0.51 / 0.29, S90 1.2 / 0.26, S50 0.49 / 0.30
  (`sofa_rec-10_v4_multi.json`, `nose_probes_sofa_rec-10.tar.xz`). Standing still air, **trousers** (local PC, done
  2026-10-23 03:43): A90 40.2 / 0.02, A50 12.9 / 0.003, S90 0.07 / 0.01, S50 0.04 / 0.01 - against bare 1.9 / 0.26 /
  0.85 / 0.13 at the releaser: trousers raise the audible releases at the releaser's own nose and lower the silent ones
  (`stand_still_tr_v4_multi.json`, `nose_probes_stand_still_tr.tar.xz`). Many noses are still rising at 150 s (`late_rising`), mostly at low levels; the 600 s tail
  check on the reference runs passed. Viewer updated with all four clouds per case.
- **E4 LES started (2026-10-21 09:44, user's go):** sofa upright bare, `sofa_v4_multi_les` in sbd-v4 from the
  RANS precursor `sofa_v4_pre` (WALE, maxCo 0.8, dt ~0.0075 s; 60 s spin-up, six releases from 60.2 s, to 300.2 s).
  Started by hand (queue.sh exits once every job has started): container `sbd-v4_sofa_les`, script
  `run_multi_v4.sh` (= main's run_multi.sh) with `TURB=les CHECKPOINT=5 KEEP=3`. Roughly 3-4 days (later ~5-6
  with other server load). **Sofa trousers LES started 2026-10-22 04:37 (user's go):** `sofa_tr_v4_multi_les`, container
  `sbd-v4_sofa_tr_les`, same settings, porous trousers zone present; dt ~0.005 s, first-minutes speed suggests
  ~2 weeks; reassess after a day. **Speed-up (user's choice: move cores, nothing else changed):** a watcher
  (`sbd-main/scratch/les_realloc.sh`, log `cfd/runs/les_realloc.log`, started 2026-10-22 09:16) waits for the
  sofa -10 run to finish, then for the LES's next 5-s checkpoint, stops it, re-decomposes the latest time into 8
  subdomains (scotch) and restarts it as container `sbd-v4_sofa_tr_les8` with NP=8 (total stays 20 cores).
  **Replaced the same day by the full core plan (user approved; target: all runs done ~28-29 Oct instead of ~8 Nov):**
  - server: `cfd/docker/les_grow.sh` (running from `sbd-main/scratch/`, log `cfd/runs/les_grow.log`) grows the
    trousers LES onto every 4 cores the other sbd runs free (cap 20), at its next checkpoint each time
    (expected 4 -> 8 -> 12 -> 16 -> 20 as sofa -10, the bare LES, sofa_tr and stand_vent_tr leave);
  - local: `cfd/local/move_les_bare.sh` (running in WSL Ubuntu; Startup shortcut "sbd move LES"; log
    `C:\Users\EH R&C CY\wsl\move_les_bare.log`) waits for the local stand_still_tr run to finish, has
    `cfd/docker/les_bare_stop.sh` stop the bare LES on the server after its next checkpoint, copies the case to the
    PC and resumes it there (`start_local.ps1 -Name sofa_les`), then switches the login shortcut to it. Needs the
    EH R&C Wi-Fi for the server steps (they retry). Afterwards the server's `sofa_v4_multi_les` is stale: the
    results live on the PC (`/root/sbd/cfd/runs/sofa_v4_multi_les` in sbd-openfoam13).
  - **Server reboot 2026-10-23 09:35** (while the user checked the server's power and cable; it had been unreachable
    from the PC that morning): all sbd containers and both watchers stopped (`--rm` containers do not come back).
    Restarted 23:48 the same day from the latest writes: `sbd-v4_sofa_tr3` (from 95.26 s), `sbd-v4_stand_vent_tr2`
    (from 61.15 s, new `standing/run_multi_v4.sh` = main's script), both with CHECKPOINT=5 now; the trousers LES
    re-decomposed onto 12 cores (`sbd-v4_sofa_tr_les12`, from 30 s); `les_grow.sh` restarted. The bare LES (stopped
    at 90.15 s) was handed to the local mover, which copied it and started it on the PC at 23:52. About 14 h of
    server time lost; new estimate: everything done ~29 Oct. After any server reboot: check `docker ps`, restart the
    sbd runs from their scripts (they resume) and restart `les_grow.sh`.
  - **Elevator supplement (user's request 2026-10-22, on spare local cores):** `elevator/make_case.py --mode multi`
    and `elevator/run_multi.sh [runs] FL|BL` (four releases as the sofa case, 90 s precursor, iso-surfaces).
    Tested on the PC: mesh 908,842 cells (Mesh OK, kept in `/root/sbd/cfd/runs/elev_v4_pre`), precursor and multi
    steps across the first pulse run clean. `start_local.ps1 -Name sofa_les` now chains the bare LES and then
    `elev_v4_FL_multi` (front-left culprit, person behind), so it starts on its own when the LES ends (~Mon) and
    should finish ~Tue evening, before the trousers LES. Analyse with `analyze_multi.py <case> --noses FL,FR,BL,BR`. The standing LES
  branch is not set up yet (`standing/make_case.py` accepts only `--turbulence rans`).
- **Local PC run (2026-10-20, user's offer):** `stand_still_tr` (standing pair, still air, trousers) moved off the
  server queue (`v4_stand_still_tr2` commented out in the server's jobs_v4.txt) and runs on the user's PC (i7-10700F,
  4 cores, nice 19) in the WSL distro `sbd-openfoam13`, an import of the server image (`wsl --import`; Docker Desktop
  crashes on this PC). Repo copy and run in `/root/sbd` inside that distro, started from the server's precursor case
  (mesh). Resume after a reboot: `powershell -ExecutionPolicy Bypass -File cfd\local\start_local.ps1`
  (`CHECKPOINT=5` splits long segments into 5-s pieces, `KEEP=3` prunes old time directories; a lock prevents a
  second copy). A shortcut in the Windows Startup folder (`sbd local CFD resume.lnk`, user's request) runs it at
  every login; delete it when the run is done. **Paused 2026-10-21 15:50 at the user's request (C: had 8 GB free,
  filled by other files):** stopped after the 30.15 s piece (seg9, the A50 pulse, restarts from 30.15 s); the
  shortcut was moved to `C:\Users\EH R&C CY\wsl\` so it does not restart at login. To resume: run
  start_local.ps1 and move the shortcut back into the Startup folder. Resumed 2026-10-21 16:50 from 30.15 s
  (shortcut back in Startup; C: 101 GB free). **Paused again 2026-10-21 17:00 (user):** stopped at once during
  seg9 (30.20 s, not saved); restarts from 30.15 s. Resumed 17:25 the same day (shortcut back in Startup).
  Killed 2026-10-22 06:13 when the Claude desktop app updated (the run was a child of the app); restarted 08:57
  from 90.15 s, and start_local.ps1 now creates the process through WMI so it no longer depends on the app.
  **Server access:** the PC reaches 192.168.50.192 only on the office Wi-Fi "EH R&C" (192.168.50.x); on the wired
  network (192.168.0.x) the route goes to the internet and SSH times out. Per job about twice as fast as the (oversubscribed) server: ~3 days;
  ~8-10 GB on C:. Bring the results back to the server or the repo for analysis.
- **Venue decided 2026-10-20:** J. R. Soc. Interface (fallback The Science of Nature, EPJ Plus); plan in
  `manuscript/preprint/interface_plan.md`. Approved the same day; its "now" tasks 1-9 are done (see its §8):
  article class, appendix A/B, chemistry, acoustics and odour origin moved to the ESM, 47 main-text references,
  ~7,370 words. Remaining: the "after v4" list (numbers marked `\gap{v4; preprint: ...}`), and the AI statement,
  which the author writes last (ORCID, CRediT, funding and no suggested reviewers are settled). `cover_letter.md` is a draft.
- **Server** (company machine, `ssh user@192.168.50.192` from WSL Ubuntu; all work inside `~/cyjoe/`, see memory):
  OpenFOAM 13 in the Docker image `sbd-openfoam13` (`cfd/docker/`), runs via `cfd/docker/run.sh` (nice 19, 4 cores
  each) and `cfd/docker/queue.sh` (at most 5 containers = 20 cores, the user's cap). Two clones:
  `~/cyjoe/research/sbd` runs the coupled 10-min reference branches `sofa_silent`, `sofa_audible` (old scripts; do
  not `git pull` there while they run, bash reads the running scripts incrementally); `~/cyjoe/research/sbd-v4`
  runs the v4 jobs (`cfd/docker/jobs_v4.txt`, queue log `cfd/runs/queue_v4.log`); do not pull there either while its
  run_multi.sh jobs run. The LES runs (E4, `TURB=les`) go in a third clone when slots free up. GPUs 1-3 may be used when idle
  (GPU 0 belongs to the CMAQ service; Ollama/vLLM services may load models on any GPU).
- **Reproduction:** the container reproduces the archived elevator run bitwise (checked to 1.2 s).
- **FluidX3D test** (`cfd/lbm/feasibility_report.md`, fork in `research/FluidX3D-sbd`, branch `sbd`): same body plume
  as the RANS (0-7 %), so the 40-60 % plume over-prediction is a set-up effect (at Licina's point, 14 mm from the
  face: +36 % bare, +28 % with a 30 C clothed surface; carried as a transport-time factor). Low-concentration scalar
  transport is not reliable there (needs a diffusivity floor). Kept as a cross-check only.
- **E0-5 failed:** frozen-flow transport is 1e3-1e4 too low at the noses because the URANS room flow keeps
  meandering (0.13-0.33 m/s at the noses). Replaced by the hybrid scheme the user chose: one coupled run per
  configuration with four releases on scalars s1..s4 (A90, A50, S90, S50: 50th/90th percentile of M0 per class from
  the Gate 0 priors; `MULTI_RELEASES` in `cfd/cases/sofa/make_case.py`), 30 s apart, to 150 s after the last; the
  150-600 s tail from a well-mixed model validated on the two sofa reference runs.
- **Running / queued (v4):** sofa upright bare, sofa upright trousers, sofa reclined +4.5 (running); standing still
  bare/trousers, standing ventilated bare/trousers, sofa reclined -10 (queued). Precursors 90 s. Trousers = porous
  shell (`createZones` union-minus-union of offset surfaces, Darcy from denim permeability), 123 k cells for the
  sofa pair; write_trousers orients each part by its signed volume (inverted normals gave an empty zone).
- **Next:** tail model + validation when the reference runs pass ~300-600 s; analysis script for the multi-release
  probes (s1..s4 per nose, worst-breath OAV, scaling by V/V_rep within a momentum level); E4 LES set-up (sofa bare and
  trousers, standing trousers); headline Monte Carlo; manuscript.
- **Decided 2026-10-19 (after an independent from-scratch design review):** no new CFD beyond PLAN v4; extra runs only
  if their error could change the conclusion, not to meet formal standards (no 3-level GCI, no active-breathing
  manikin, no separate V check run: predict the 92 mL reference runs from the v4 levels instead). "Seldom" is judged on
  two bases, both reported: the four-outcome shares (headline, C) and, among pairs where both are smelled, the share
  where silent wins (earlier numbers: 5.5 / (5.5 + 8.5) ~ 39 %, attentive); the title keeps "seldom" only if both
  support it. The headline Monte Carlo adds a boundary for the sulfur-content correlation with sound and its spread
  sigma (where the conclusion flips); behavioural response (breath-holding on hearing) and a scaling section were
  not adopted. `analyze_multi.py` now gives nested windows, 92 mL equal-mass OAV and `nose_oav` (V/V_rep scaling,
  log-log in M0 between the class's levels, clamped).
- **Tail model (2026-10-19):** 92 mL well mixed in the 26.6 m^3 room is OAV ~0.49, far below detection (attentive 50 %
  at OAV 20); the reference runs' noses sit at 0.2-2x that level already at 80-150 s, so the headline is decided in
  the first ~150 s. `analyze_multi.py` adds 300/600 s windows from a well-mixed plateau (late level f relative to
  V/V_room, decay only with ventilation), which by construction equals the 150 s value ("nothing worse arrives after
  150 s"); `cfd/postprocess/validate_tail.py` checks this on the 10-min reference runs (factor 1.5).
  **300 s check passed (2026-10-20 00:10, runs at 334 / 302 s):** predicted / actual worst breath 1.00 (silent
  releaser), 0.88 (silent neighbour), 0.84 (audible releaser), 0.81 (audible neighbour); after 150 s the noses stay at
  0.4-1.8x the well-mixed level, with slight growth (up to 1.24x) for the audible branch, so the tail runs at most ~20 %
  low; all OAV < 1 (92 mL). **600 s check passed (2026-10-20 19:45, both runs complete):** ratios 1.00 (silent
  releaser), 0.67 (silent neighbour), 0.84 (audible releaser), 0.71 (audible neighbour). The neighbours' level
  keeps creeping up after 300 s (no late peak), so the tail runs up to ~1/3 low at 600 s for a bystander, still
  within the factor 1.5; state this in the manuscript. `tail_validation.json` holds the 600 s check.
- **Server (2026-10-19 12:30 KST):** reference runs at 149 / 118 s of 600 (~220 wall-s per sim-s, done Tue 20
  afternoon/evening); v4 sofa bare and rec4.5 precursors done ~17:00 today, multi phase ~20-24 h more; sofa trousers
  ~6x slower (1.32 M cells, Darcy d = 1.8e10 m^-2 makes p_rgh stiff), ~6 days in all; the user chose to let it run.
  Both server clones are still on the deleted branch `claude/handoff-review-fixes-qkpzin`: switch them to `main` when
  their runs finish. Old branches deleted on GitHub; work only on `main`.

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

## Item 2 plan: 10-minute runs on the user's server (decided 2026-10-18)

The user chose new CFD runs (not a well-mixed tail), every scene 10 min after release, residence times as stated
assumptions plus a headline-vs-window curve. The runs go on the user's own server (36 threads, 251 GB; OpenFOAM is
CPU-only, the GPUs do not help). The cloud session was moved to the user's local machine (`claude --teleport`),
which reaches the server over SSH; drive the runs from there (repo clone + OpenFOAM 13 on the server).
- Branch `claude/handoff-review-fixes-qkpzin`. OpenFOAM 13 (openfoam.org), as before; the run scripts source
  `/opt/openfoam13/etc/bashrc`. Raise `NP=4` in `cfd/cases/*/run_*.sh` to suit the cores (several cases at once).
- Rerun all 14 release branches from scratch (precursors too; the old run directories are gone): sofa x3 postures,
  elevator x2 layouts, standing x2 ventilations, each silent and audible. Release end time = release start + 600 s
  (sofa: `make_case.py --t-end`, and the `endTime -set 30/60` lines in the run scripts).
- Before the full set, check that the rerun of one branch reproduces the archived probe series
  (`cfd/probe_archive/nose_probes.tar.xz`) over the old window.
- Bring back: nose-probe series (archive as before) and the `results*.json` from the analyze scripts with windows
  30, 60, 120, 300, 600 s. Run directories stay on the server.
- Item 3 status: `uq/four_outcomes.py` aggregates per scene (variants and noses averaged inside a scene). The user
  chose real-frequency scene weights: weight ∝ time per day spent near another person in that setting (passages
  uniform over waking hours). A literature search for these weights (ATUS / NHAPS time use, elevator trips and ride
  time, face-to-face standing conversation time; DOIs verified via OpenAlex) finished: `refs/scene_weights_sources.md`
  (central 0.73 / 0.005 / 0.26 for sofa / elevator / standing, with two bounding cases). Approved (central +
  both bounding cases as a sensitivity range); in params.yaml `scene_weights`, used by `uq/four_outcomes.py`.
  With the current windows the frequency-weighted bystander result is ~100 % "none" (only the elevator, weight
  <= 4 %, smells anything); the numbers mean something only after the item 2 runs.
- Not yet: add `scene_weights` to SECTIONS in `manuscript/preprint/make_params_table.py` (manuscript stage).
- Meanwhile: item 3 onwards. With the current windows only the elevator bystanders smell
  anything (sofa and standing bystanders: pi_s = pi_l = 0), so items 3 and 7 numbers wait for these runs.

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
  Co-Authored-By and Claude-Session lines; commit and push on `main` only (no new branches, PRs or forks). No model
  identifiers in commits or PR text.
- Publisher PDFs stay out of the repo (`refs/pdfs_incoming/` is gitignored). Literature searches return DOIs only.
