#!/bin/bash
# Scenario A pipeline: precursor (CBL develops, 30 s) -> branch cases silent / audible (mapped from the precursor at
# 30 s, release at +0.2 s, run to +30 s). Meshes the precursor if needed (blockMesh, snappyHexMesh, createPatch for the
# ceiling vent). Waits for the transient CBL validation to finish first.
# Usage: run_sofa.sh [runs_dir] [recline_deg]; a non-zero recline (releaser's upper body, M4 posture sensitivity)
# writes cases sofa_rec<deg>_{pre,silent,audible} instead of sofa_{pre,silent,audible}.
source /opt/openfoam13/etc/bashrc >/dev/null 2>&1
HERE=$(cd "$(dirname "$0")" && pwd)
RUN=${1:-$HERE/../../runs}
REC=${2:-0}
if [ "$REC" = "0" ]; then P=sofa; else P=sofa_rec$REC; fi
cd "$RUN"
NP=4
while ps -eo args | grep -E "run_transient.sh" | grep -vq grep; do sleep 60; done
echo "$(date -u +%H:%M) ${P} pipeline start"
while ps -eo args | grep -E "sofa_mesh.sh" | grep -vq grep; do sleep 60; done
if [ ! -f ${P}_pre/constant/polyMesh/owner ]; then
  python3 "$HERE/make_case.py" ${P}_pre --mode precursor --recline $REC > /dev/null
  ( cd ${P}_pre
    blockMesh > log.blockMesh 2>&1
    snappyHexMesh -overwrite > log.snappy 2>&1
    createPatch -overwrite > log.createPatch 2>&1
    checkMesh > log.checkMesh 2>&1 )
  echo "$(date -u +%H:%M) ${P} mesh done"
fi
if [ ! -d ${P}_pre/30 ]; then
  ( cd ${P}_pre
    decomposePar -force > log.decomposePar 2>&1
    mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun 2>&1
    reconstructPar -latestTime > log.reconstructPar 2>&1 )
  echo "$(date -u +%H:%M) ${P}_pre done"
fi
# branch cases: release at +0.2 s, run to +30 s in two stages (release: small maxDeltaT; drift: maxDeltaT 0.1)
for mode in silent audible; do
  c=${P}_$mode
  [ -d "$c/30" ] && continue
  rm -rf "$c"
  python3 "$HERE/make_case.py" "$c" --mode $mode --t-release 0.2 --t-end 30 --recline $REC > "$c.make.log"
  cp -r ${P}_pre/constant/polyMesh "$c/constant/"
  ( cd "$c"
    mapFields ../${P}_pre -sourceTime 30 -consistent > log.mapFields 2>&1
    decomposePar -force > log.decomposePar 2>&1
    mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun.release 2>&1
    foamDictionary system/controlDict -entry maxDeltaT -set 0.1 > /dev/null
    foamDictionary system/controlDict -entry writeInterval -set 5 > /dev/null
    foamDictionary system/controlDict -entry endTime -set 30 > /dev/null
    mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun.drift 2>&1
    reconstructPar > log.reconstructPar 2>&1 )
  echo "$(date -u +%H:%M) $c done"
done
echo "$(date -u +%H:%M) ${P} pipeline done"
