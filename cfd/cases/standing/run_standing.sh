#!/bin/bash
# Scenario D' pipeline (standing pair, face to face). One mesh (stand_mesh) for both ventilation states.
#   precursors: stand_still_pre (30 s, body plumes) and stand_vent_pre (90 s, body plumes + diffuser circulation)
#   branches:   stand_{still,vent}_{silent,audible}, mapped from the precursor's last time, release at +0.2 s, run to
#               +60 s in two stages (release with a small maxDeltaT, then drift with maxDeltaT 0.1, writeInterval 15).
# Decomposed copies are removed after reconstruction (disk allowance). An interrupted drift stage is resumed.
# Usage: run_standing.sh [runs_dir]
source /opt/openfoam13/etc/bashrc >/dev/null 2>&1
HERE=$(cd "$(dirname "$0")" && pwd)
RUN=${1:-$HERE/../../runs}
cd "$RUN"
# Environment overrides (defaults reproduce the original runs): NP ranks per case; T_END branch end time (s);
# PURGE>0 keeps only the last PURGE field writes in the drift stage (purgeWrite; does not change time steps) and
# removes the decomposed copies afterwards; ONLY a glob on branch names (e.g. "elev_FL_silent").
NP=${NP:-4}
T_END=${T_END:-60}
PURGE=${PURGE:-0}
ONLY=${ONLY:-*}
echo "$(date -u +%H:%M) standing pipeline start"
if [ ! -f stand_mesh/constant/polyMesh/owner ]; then
  python3 "$HERE/make_case.py" stand_mesh --mode precursor --vent on > /dev/null
  ( cd stand_mesh
    blockMesh > log.blockMesh 2>&1
    snappyHexMesh -overwrite > log.snappy 2>&1
    createPatch -overwrite > log.createPatch 2>&1
    checkMesh > log.checkMesh 2>&1 )
  echo "$(date -u +%H:%M) standing mesh done"
fi
for vent in still vent; do
  # with ONLY naming branches, skip the ventilation state (and its precursor) that has none of them
  if [ "$ONLY" != "none" ] && [[ "stand_${vent}_silent" != $ONLY ]] && [[ "stand_${vent}_audible" != $ONLY ]]; then continue; fi
  v=$([ $vent = vent ] && echo on || echo off)
  tp=$([ $vent = vent ] && echo 90 || echo 30)
  pre=stand_${vent}_pre
  if [ ! -f $pre/$tp/U ]; then
    rm -rf $pre
    python3 "$HERE/make_case.py" $pre --mode precursor --vent $v > $pre.make.log
    cp -r stand_mesh/constant/polyMesh $pre/constant/
    ( cd $pre
      decomposePar -force > log.decomposePar 2>&1
      mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun 2>&1
      reconstructPar -latestTime > log.reconstructPar 2>&1
      [ -f $tp/U ] && rm -rf processor[0-9]* )
    echo "$(date -u +%H:%M) $pre done"
  fi
  for mode in silent audible; do
    c=stand_${vent}_$mode
    [[ "$c" == $ONLY ]] || continue
    [ -f "$c/$T_END/s" ] && continue
    if [ -f "$c/log.foamRun.drift" ] && [ -d "$c/processor0" ]; then
      ( cd "$c"
        n=$(ls log.foamRun.drift* | wc -l)
        mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun.drift.$n 2>&1
        reconstructPar > log.reconstructPar 2>&1
        [ -f $T_END/s ] && rm -rf processor[0-9]* )
      echo "$(date -u +%H:%M) $c resumed and done"
      continue
    fi
    rm -rf "$c"
    python3 "$HERE/make_case.py" "$c" --mode $mode --vent $v --t-release 0.2 --t-end $T_END > "$c.make.log"
    cp -r stand_mesh/constant/polyMesh "$c/constant/"
    ( cd "$c"
      mapFields ../$pre -sourceTime $tp -consistent > log.mapFields 2>&1
      decomposePar -force > log.decomposePar 2>&1
      mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun.release 2>&1
      foamDictionary system/controlDict -entry maxDeltaT -set 0.1 > /dev/null
      foamDictionary system/controlDict -entry writeInterval -set 15 > /dev/null
      foamDictionary system/controlDict -entry endTime -set $T_END > /dev/null
      [ "$PURGE" != 0 ] && foamDictionary system/controlDict -entry purgeWrite -set $PURGE > /dev/null
      mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun.drift 2>&1
      reconstructPar > log.reconstructPar 2>&1
      [ -f $T_END/s ] && rm -rf processor[0-9]* )
    echo "$(date -u +%H:%M) $c done"
  done
done
echo "$(date -u +%H:%M) standing pipeline done"
