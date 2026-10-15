#!/bin/bash
# M3b: transient CBL validation runs (coarse mesh), room 20/23/26 C, 60 s of physical time, averaged over 30-60 s.
# Meshes come from the steady cbl_t*_coarse cases (snappyHexMesh); initial fields from the steady solution where the
# room temperature matches (T is not copied otherwise, so the new wall temperatures apply).
# Usage: cfd/validation/cbl/run_transient.sh [runs_dir]
source /opt/openfoam13/etc/bashrc >/dev/null 2>&1
HERE=$(cd "$(dirname "$0")" && pwd)
RUN=${1:-$HERE/../../runs}
cd "$RUN"
NP=4
END=60
for T in 20 23 26; do
  src=cbl_t${T}_coarse
  dst=cbl_t${T}_tr
  [ -d "$dst/$END" ] && { echo "skip $dst"; continue; }
  rm -rf "$dst"
  python3 "$HERE/make_case.py" "$dst" --troom $T --level coarse --transient $END > /dev/null
  cp -r "$src/constant/polyMesh" "$dst/constant/"
  if [ -d "$src/3000" ]; then
    for f in U T p p_rgh k omega nut alphat; do cp "$src/3000/$f" "$dst/0/$f"; done
  fi
  ( cd "$dst"
    decomposePar -force > log.decomposePar 2>&1
    mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun 2>&1
    reconstructPar -latestTime > log.reconstructPar 2>&1 )
  echo "$(date -u +%H:%M) $dst done"
done
echo "$(date -u +%H:%M) transient CBL set done"
