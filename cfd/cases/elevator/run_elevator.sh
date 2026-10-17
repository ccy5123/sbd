#!/bin/bash
# Scenario C pipeline: precursor (four body plumes develop in the closed car, 30 s) -> four branch cases
# elev_{FL,BL}_{silent,audible} (mapped from the precursor at 30 s, release at +0.2 s, run to +60 s in two stages:
# release with a small maxDeltaT, then drift with maxDeltaT 0.1 and writeInterval 5).
# Usage: run_elevator.sh [runs_dir]
source /opt/openfoam13/etc/bashrc >/dev/null 2>&1
HERE=$(cd "$(dirname "$0")" && pwd)
RUN=${1:-$HERE/../../runs}
cd "$RUN"
NP=4
P=elev
echo "$(date -u +%H:%M) ${P} pipeline start"
if [ ! -f ${P}_pre/constant/polyMesh/owner ]; then
  python3 "$HERE/make_case.py" ${P}_pre --mode precursor > /dev/null
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
for culprit in FL BL; do
  for mode in silent audible; do
    c=${P}_${culprit}_$mode
    [ -d "$c/60" ] && continue
    # resume an interrupted drift stage (e.g. after a container restart) from its latest write
    if [ -f "$c/log.foamRun.drift" ] && [ -d "$c/processor0" ]; then
      ( cd "$c"
        n=$(ls log.foamRun.drift* | wc -l)
        mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun.drift.$n 2>&1
        reconstructPar > log.reconstructPar 2>&1 )
      echo "$(date -u +%H:%M) $c resumed and done"
      continue
    fi
    rm -rf "$c"
    python3 "$HERE/make_case.py" "$c" --mode $mode --culprit $culprit --t-release 0.2 --t-end 60 > "$c.make.log"
    cp -r ${P}_pre/constant/polyMesh "$c/constant/"
    ( cd "$c"
      mapFields ../${P}_pre -sourceTime 30 -consistent > log.mapFields 2>&1
      decomposePar -force > log.decomposePar 2>&1
      mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun.release 2>&1
      foamDictionary system/controlDict -entry maxDeltaT -set 0.1 > /dev/null
      foamDictionary system/controlDict -entry writeInterval -set 5 > /dev/null
      foamDictionary system/controlDict -entry endTime -set 60 > /dev/null
      mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun.drift 2>&1
      reconstructPar > log.reconstructPar 2>&1 )
    echo "$(date -u +%H:%M) $c done"
  done
done
echo "$(date -u +%H:%M) ${P} pipeline done"
