#!/bin/bash
# Scenario A pipeline: precursor (CBL develops, 30 s) -> branch cases silent / audible (mapped from the precursor at
# 30 s, release at +1 s, run to +30 s). Waits for the transient CBL validation and the sofa mesh to finish first.
source /opt/openfoam13/etc/bashrc >/dev/null 2>&1
HERE=$(cd "$(dirname "$0")" && pwd)
RUN=${1:-$HERE/../../runs}
cd "$RUN"
NP=4
while ps -eo args | grep -E "run_transient.sh|sofa_mesh.sh" | grep -vq grep; do sleep 60; done
echo "$(date -u +%H:%M) sofa pipeline start"
if [ ! -d sofa_pre/30 ]; then
  ( cd sofa_pre
    decomposePar -force > log.decomposePar 2>&1
    mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun 2>&1
    reconstructPar -latestTime > log.reconstructPar 2>&1 )
  echo "$(date -u +%H:%M) sofa_pre done"
fi
for mode in silent audible; do
  c=sofa_$mode
  [ -d "$c/31" ] && continue
  rm -rf "$c"
  python3 "$HERE/make_case.py" "$c" --mode $mode --t-release 1 --t-end 31 > /dev/null
  cp -r sofa_pre/constant/polyMesh "$c/constant/"
  ( cd "$c"
    mapFields ../sofa_pre -sourceTime 30 -consistent > log.mapFields 2>&1
    decomposePar -force > log.decomposePar 2>&1
    mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun 2>&1
    reconstructPar > log.reconstructPar 2>&1 )
  echo "$(date -u +%H:%M) $c done"
done
echo "$(date -u +%H:%M) sofa pipeline done"
