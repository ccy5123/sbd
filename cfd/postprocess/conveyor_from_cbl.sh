#!/bin/bash
# 'Conveyor Belt' figure from a transient CBL case: mid-plane cut and seat-level 3-D streamlines of the time-mean
# velocity (fieldAverage UMean, TMean over the second half of the run).
# Usage: cfd/postprocess/conveyor_from_cbl.sh <case_dir> <time> <out.png> <room_C>
source /opt/openfoam13/etc/bashrc >/dev/null 2>&1
HERE=$(cd "$(dirname "$0")" && pwd)
CASE=$(cd "$1" && pwd); TIME=$2; OUT=$(realpath "$3"); ROOM=${4:-23}
cd "$CASE"
foamPostProcess -time "$TIME" -func "cutPlaneSurface(funcName=midPlane, point=(0 0.003 0), normal=(0 1 0), \
fields=(UMean TMean), interpolate=false, surfaceFormat=raw)" > log.midPlane 2>&1
foamPostProcess -time "$TIME" -func "streamlinesPoints(funcName=seatParcels, \
points=((0.06 0.02 0.47) (0.10 0.02 0.47) (0.14 0.03 0.48) (0.10 0.05 0.50) (-0.05 0.20 0.48) (0.02 0.19 0.48) \
(-0.205 0.03 0.50) (-0.205 0.12 0.50) (-0.12 0.17 0.47)), U=UMean, fields=(UMean), direction=forward, \
setFormat=raw, lifeTime=100000, nSubCycle=5)" > log.seatParcels 2>&1
python3 "$HERE/fig_conveyor.py" "$CASE" "$TIME" "$OUT" "$ROOM"
