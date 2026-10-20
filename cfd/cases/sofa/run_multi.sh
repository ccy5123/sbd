#!/bin/bash
# PLAN v4 E2': developed precursor (T_PRE s, default 90) -> one branch with four releases on separate scalars
# (make_case.py --mode multi), run through the segments of its 'schedule' file (each pulse with a time step that
# resolves it, the gaps with maxDeltaT 0.1). Each segment writes exactly at its end (writeInterval = segment length,
# counted from the segment's start time), so the next segment restarts from there.
# Usage: run_multi.sh [runs_dir] [recline_deg] [clothing]    env: NP (4), T_PRE (90), CHECKPOINT, KEEP
source /opt/openfoam13/etc/bashrc >/dev/null 2>&1
HERE=$(cd "$(dirname "$0")" && pwd)
RUN=${1:-$HERE/../../runs}
REC=${2:-0}
CLOTH=${3:-bare}
NP=${NP:-4}
T_PRE=${T_PRE:-90}
TURB=${TURB:-rans}  # les: WALE branch with six releases after 60 s of spin-up (PLAN v4 E4), from the same RANS precursor
if [ "$REC" = "0" ]; then P=sofa; else P=sofa_rec$REC; fi
[ "$CLOTH" = "trousers" ] && P=${P}_tr
P=${P}_v4
mkdir -p "$RUN" && cd "$RUN"
echo "$(date -u +%H:%M) ${P} pipeline start"
if [ ! -f ${P}_pre/constant/polyMesh/owner ]; then
  python3 "$HERE/make_case.py" ${P}_pre --mode precursor --recline $REC --clothing $CLOTH --t-pre $T_PRE > ${P}_pre.make.log
  ( cd ${P}_pre
    blockMesh > log.blockMesh 2>&1
    snappyHexMesh -overwrite > log.snappy 2>&1
    createPatch -overwrite > log.createPatch 2>&1
    [ -f system/createZonesDict ] && createZones > log.createZones 2>&1
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
c=${P}_multi; [ "$TURB" = les ] && c=${P}_multi_les
if [ ! -f "$c/schedule" ]; then
  python3 "$HERE/make_case.py" "$c" --mode multi --turbulence $TURB --t-release $([ "$TURB" = les ] && echo 60.2 || echo 0.2) --recline $REC --clothing $CLOTH > "$c.make.log"
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
echo "$(date -u +%H:%M) ${P} pipeline done"
