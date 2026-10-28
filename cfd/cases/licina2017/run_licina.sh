#!/bin/bash
# PLAN v4 E0-3: Licina, Tian & Nazaroff 2017 chamber (make_case.py), heated or unheated manikin, one case each: mesh,
# then the flow develops for T_PRE s and the groin source runs 600 s from T_PRE + 0.2; the run ends 22 min after the
# source starts. Restarts from the latest write (every 60 s, the last three kept).
# Usage: run_licina.sh [runs_dir] [heated|unheated]    env: NP (4), T_PRE (600)
source /opt/openfoam13/etc/bashrc >/dev/null 2>&1
HERE=$(cd "$(dirname "$0")" && pwd)
RUN=${1:-$HERE/../../runs}
MODE=${2:-heated}
NP=${NP:-4}
T_PRE=${T_PRE:-600}
c=licina2017_$MODE
mkdir -p "$RUN" && cd "$RUN"
echo "$(date -u +%H:%M) $c pipeline start"
if [ ! -f $c/constant/polyMesh/owner ]; then
  python3 "$HERE/make_case.py" $c --t-pre $T_PRE $([ "$MODE" = unheated ] && echo --unheated) > $c.make.log
  ( cd $c
    blockMesh > log.blockMesh 2>&1
    snappyHexMesh -overwrite > log.snappy 2>&1
    createPatch -overwrite > log.createPatch 2>&1
    checkMesh > log.checkMesh 2>&1 )
  echo "$(date -u +%H:%M) $c mesh done"
fi
( cd $c
  if [ ! -d processor0 ]; then
    foamDictionary system/decomposeParDict -entry numberOfSubdomains -set $NP > /dev/null
    decomposePar -force > log.decomposePar 2>&1
  fi
  [ -f log.foamRun ] && mv log.foamRun log.foamRun.prev  # a restart: keep the old log out of the FATAL check
  mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun 2>&1 < /dev/null
  rc=$?
  { [ $rc -ne 0 ] || grep -q "FOAM FATAL" log.foamRun; } && { echo "$(date -u +%H:%M) $c FAILED (rc $rc)"; exit 1; }
  reconstructPar -latestTime > log.reconstructPar 2>&1 )
echo "$(date -u +%H:%M) $c pipeline done"
