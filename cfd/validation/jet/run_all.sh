#!/bin/bash
# M3a jet validation set: SST at three mesh levels, standard k-epsilon, k-epsilon with C1 = 1.6 (round-jet correction).
# One case per core; endTime scales with mesh level.
source /opt/openfoam13/etc/bashrc >/dev/null 2>&1
HERE=$(cd "$(dirname "$0")" && pwd)
RUN=${1:-$HERE/../../runs}
mkdir -p "$RUN"; cd "$RUN"
run_case () {
  local name=$1 level=$2 model=$3 iters=$4 extra=$5
  [ -d "$name/$iters" ] && { echo "skip $name"; return; }
  python3 "$HERE/make_case.py" "$name" --level "$level" --model "$model" $extra >/dev/null
  (cd "$name" && foamDictionary system/controlDict -entry endTime -set $iters >/dev/null \
     && foamDictionary system/controlDict -entry writeInterval -set $iters >/dev/null \
     && blockMesh > log.blockMesh 2>&1 && foamRun > log.foamRun 2>&1 \
     && foamPostProcess -func writeCellCentres -latestTime > log.C 2>&1; echo "done $name $?")
}
run_case jet_sst_coarse coarse kOmegaSST 3000 &
run_case jet_sst_medium medium kOmegaSST 4000 &
run_case jet_sst_fine fine kOmegaSST 6000 &
run_case jet_ke_medium medium kEpsilon 4000 &
wait
run_case jet_ke_pope_medium medium kEpsilon 4000 "--c1 1.6"
