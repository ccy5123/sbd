#!/bin/bash
# PLAN v4 supplement for the elevator: developed precursor (T_PRE s, default 90, shared by both culprit positions) ->
# one branch with the four releases on separate scalars (make_case.py --mode multi), run through the segments of its
# 'schedule' file as in cfd/cases/sofa/run_multi.sh. Each segment writes exactly at its end (writeInterval = segment
# end, counted from t = 0), so the next segment restarts from there.
# Usage: run_multi.sh [runs_dir] [FL|BL]    env: NP (4), T_PRE (90), CHECKPOINT, KEEP
source /opt/openfoam13/etc/bashrc >/dev/null 2>&1
HERE=$(cd "$(dirname "$0")" && pwd)
RUN=${1:-$HERE/../../runs}
CULPRIT=${2:-FL}
NP=${NP:-4}
T_PRE=${T_PRE:-90}
P=elev_v4
mkdir -p "$RUN" && cd "$RUN"
echo "$(date -u +%H:%M) ${P}_${CULPRIT} pipeline start"
if [ ! -f ${P}_pre/constant/polyMesh/owner ]; then
  python3 "$HERE/make_case.py" ${P}_pre --mode precursor --t-pre $T_PRE > ${P}_pre.make.log
  ( cd ${P}_pre
    blockMesh > log.blockMesh 2>&1
    snappyHexMesh -overwrite > log.snappy 2>&1
    createPatch -overwrite > log.createPatch 2>&1
    checkMesh > log.checkMesh 2>&1 )
  echo "$(date -u +%H:%M) ${P} mesh done"
fi
if [ ! -f ${P}_pre/$T_PRE/U ]; then
  ( cd ${P}_pre
    [ -d processor0 ] || decomposePar -force > log.decomposePar 2>&1  # resume an interrupted precursor
    mpirun --allow-run-as-root -np $NP foamRun -parallel >> log.foamRun 2>&1 < /dev/null
    reconstructPar -latestTime > log.reconstructPar 2>&1
    [ -f $T_PRE/U ] && rm -rf processor[0-9]* )
  echo "$(date -u +%H:%M) ${P}_pre done"
fi
c=${P}_${CULPRIT}_multi
if [ ! -f "$c/schedule" ]; then
  python3 "$HERE/make_case.py" "$c" --mode multi --culprit $CULPRIT --t-release 0.2 > "$c.make.log"
  cp -r ${P}_pre/constant/polyMesh "$c/constant/"
  ( cd "$c"
    mapFields ../${P}_pre -sourceTime $T_PRE -consistent > log.mapFields 2>&1
    decomposePar -force > log.decomposePar 2>&1 )
fi
( cd "$c"
  # CHECKPOINT (s, default off): split long segments into pieces of about this length, so an interrupted run
  # restarts from the last piece; KEEP: keep only the newest KEEP time directories per processor
  awk -v c=${CHECKPOINT:-0} '{ if (c > 0) while ($1 - p > 1.5 * c) { p += c; printf "%.10g %s\n", p, $2 }
                              print $1, $2; p = $1 }' schedule > schedule.run
  n=0
  while read te dt; do
    n=$((n+1))
    ts=$(ls -d processor0/[0-9]* | sed 's|processor0/||' | sort -g | tail -1)
    awk -v a=$ts -v b=$te 'BEGIN{exit !(a >= b-1e-6)}' && continue  # segment already done (restart)
    foamDictionary system/controlDict -entry endTime -set $te > /dev/null
    foamDictionary system/controlDict -entry maxDeltaT -set $dt > /dev/null
    # write exactly at the segment end: OpenFOAM writes at multiples of writeInterval counted from t = 0
    foamDictionary system/controlDict -entry writeInterval -set $te > /dev/null
    mpirun --allow-run-as-root -np $NP foamRun -parallel > log.foamRun.seg$n 2>&1 < /dev/null  # mpirun would otherwise eat the schedule on stdin
    grep -q "FOAM FATAL" log.foamRun.seg$n && { echo "$(date -u +%H:%M) $c segment $n FAILED"; exit 1; }
    echo "$(date -u +%H:%M) $c segment $n to $te s done"
    [ -n "$KEEP" ] && for d in processor[0-9]*; do
      ls -d $d/[0-9]* | grep -v '/0$' | sort -t/ -k2 -g | head -n -$KEEP | xargs -r rm -rf; done
  done < schedule.run
  reconstructPar -latestTime > log.reconstructPar 2>&1 )
echo "$(date -u +%H:%M) ${P}_${CULPRIT} pipeline done"
