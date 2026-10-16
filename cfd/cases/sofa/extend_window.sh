#!/bin/bash
# M4 sensitivity: extend finished sofa branches from 30 s to a longer drift window (room-scale mixing).
# Continues from the decomposed 30 s fields (startFrom latestTime); probes and planes append under a new start time.
# Usage: extend_window.sh [runs_dir] [end_time] [case ...]   (defaults: cfd/runs, 120, sofa_silent sofa_audible)
source /opt/openfoam13/etc/bashrc >/dev/null 2>&1
HERE=$(cd "$(dirname "$0")" && pwd)
RUN=${1:-$HERE/../../runs}
END=${2:-120}
shift 2 2>/dev/null
CASES=${*:-sofa_silent sofa_audible}
cd "$RUN"
for c in $CASES; do
  [ -d "$c/processor0/$END" ] && { echo "skip $c"; continue; }
  ( cd "$c"
    foamDictionary system/controlDict -entry endTime -set "$END" > /dev/null
    foamDictionary system/controlDict -entry writeInterval -set 10 > /dev/null
    mpirun --allow-run-as-root -np 4 foamRun -parallel > "log.foamRun.extend$END" 2>&1
    reconstructPar -time "$END" > "log.reconstructPar.extend$END" 2>&1 )
  if grep -q FATAL "$c/log.foamRun.extend$END"; then echo "$(date -u +%H:%M) $c FAILED"; else echo "$(date -u +%H:%M) $c extended to $END s"; fi
done
echo "$(date -u +%H:%M) extend done"
