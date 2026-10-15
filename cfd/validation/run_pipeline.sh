#!/bin/bash
# M3 pipeline after the medium jet runs: fine jet (mapped from medium, 4 cores), then CBL cases (4 cores each).
# Usage: cfd/validation/run_pipeline.sh [runs_dir]
source /opt/openfoam13/etc/bashrc >/dev/null 2>&1
HERE=$(cd "$(dirname "$0")" && pwd)
RUN=${1:-$HERE/../runs}
cd "$RUN"
NP=4

# wait for the medium jet runs to finish
while pgrep -x foamRun > /dev/null; do sleep 60; done
echo "$(date -u +%H:%M) jets medium done"

# 1. fine jet, initialised from the medium SST solution
if [ ! -d jet_sst_fine/3000 ]; then
  rm -rf jet_sst_fine
  python3 "$HERE/jet/make_case.py" jet_sst_fine --level fine --model kOmegaSST > /dev/null
  ( cd jet_sst_fine
    foamDictionary system/controlDict -entry endTime -set 3000 > /dev/null
    foamDictionary system/controlDict -entry writeInterval -set 3000 > /dev/null
    printf 'FoamFile { format ascii; class dictionary; object decomposeParDict; }\nnumberOfSubdomains %d;\nmethod scotch;\n' $NP > system/decomposeParDict
    blockMesh > log.blockMesh 2>&1
    mapFields ../jet_sst_medium -sourceTime latestTime -consistent > log.mapFields 2>&1
    decomposePar > log.decomposePar 2>&1
    mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun 2>&1
    reconstructPar -latestTime > log.reconstructPar 2>&1
    foamPostProcess -func writeCellCentres -latestTime > log.C 2>&1 )
  echo "$(date -u +%H:%M) jet fine done"
fi

# 2. CBL cases
run_cbl () {
  local name=$1 troom=$2 level=$3
  [ -d "$name/3000" ] && return
  python3 "$HERE/cbl/make_case.py" "$name" --troom "$troom" --level "$level" > /dev/null
  ( cd "$name"
    [ -f constant/polyMesh/boundary ] && grep -q body constant/polyMesh/boundary || {
      blockMesh > log.blockMesh 2>&1
      snappyHexMesh -overwrite > log.snappy 2>&1; }
    rm -rf processor*
    decomposePar -force > log.decomposePar 2>&1
    mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun 2>&1
    reconstructPar -latestTime > log.reconstructPar 2>&1 )
  echo "$(date -u +%H:%M) $name done"
}
run_cbl cbl_t23_coarse 23 coarse
run_cbl cbl_t20_coarse 20 coarse
run_cbl cbl_t26_coarse 26 coarse
run_cbl cbl_t23_medium 23 medium
echo "$(date -u +%H:%M) pipeline done"
