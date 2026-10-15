#!/bin/bash
# M3b: transient CBL validation runs (coarse mesh), room 20/23/26 C, 60 s of physical time, averaged over 30-60 s.
# Meshes come from the steady cbl_t*_coarse cases (snappyHexMesh). Initial fields: the steady solution at iteration 3000
# where it exists (20, 23 C); otherwise the developed 23 C transient field at 60 s without T, so the new wall
# temperatures apply (a start from rest failed in the first second: T(h) inversion, max Co 25).
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
  elif [ -d cbl_t23_tr/$END ]; then
    for f in U p p_rgh k omega nut alphat; do cp "cbl_t23_tr/$END/$f" "$dst/0/$f"; done
  fi
  ( cd "$dst"
    decomposePar -force > log.decomposePar 2>&1
    mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun 2>&1
    reconstructPar -latestTime > log.reconstructPar 2>&1 )
  if grep -q "FATAL" "$dst/log.foamRun"; then echo "$(date -u +%H:%M) $dst FAILED"; else echo "$(date -u +%H:%M) $dst done"; fi
done
echo "$(date -u +%H:%M) transient CBL set done"
