#!/bin/bash
# Move the sofa trousers LES onto N cores at its next checkpoint: wait for the next 'segment ... done' line of the
# running LES pipeline, stop the container, re-decompose the latest time into N subdomains (scotch) and restart it as
# container sbd-v4_sofa_tr_les<N>r with NP=N; the pipeline skips finished pieces. Use it when other jobs share the
# server (MPI ranks that share a physical core make every rank wait) or when cores free up again (N <= 18, the
# physical cores). Same steps as les_grow.sh, once.
# Runs on the server host: setsid nohup bash cfd/docker/les_resize.sh 12 &   (log: cfd/runs/les_grow.log in sbd-v4)
N=${1:?usage: les_resize.sh <cores>}
[ "$N" -le 18 ] || { echo "N must not exceed the 18 physical cores"; exit 1; }
R=$HOME/cyjoe/research/sbd-v4
RUNS=$R/cfd/runs
C=$RUNS/sofa_tr_v4_multi_les
LOG=$RUNS/les_grow.log
say() { echo "$(date '+%F %T') resize: $*" >> $LOG; }
L=$(docker ps --format '{{.Names}}' | grep '^sbd-v4_sofa_tr_les' | head -1)
[ -z "$L" ] && { say "no LES container running; exit"; exit 1; }
P=$RUNS/pipeline_${L#sbd-}.log
pieces() { grep -c 'segment .* done' "$P"; }
n0=$(pieces)
say "to $N cores: waiting for the next checkpoint of $L (last: $(grep 'segment .* done' $P | tail -1))"
until [ "$(pieces)" -gt "$n0" ] || grep -q 'pipeline done' $P; do sleep 30; done
grep -q 'pipeline done' $P && { say "LES done; exit"; exit 0; }
say "checkpoint: $(grep 'segment .* done' $P | tail -1); stopping $L"
docker stop -t 20 $L > /dev/null; sleep 5
docker run --rm -u $(id -u):$(id -g) -v $R:/sbd -w /sbd/cfd/runs/sofa_tr_v4_multi_les sbd-openfoam13 \
  nice -n 19 bash -c "source /opt/openfoam13/etc/bashrc
    reconstructPar -latestTime > log.reconstructPar.resize 2>&1 || exit 1
    foamDictionary system/decomposeParDict -entry numberOfSubdomains -set $N > /dev/null
    decomposePar -force -latestTime > log.decomposePar.resize 2>&1"
rc=$?
np=$(ls -d $C/processor*/ 2>/dev/null | wc -l)
say "re-decompose rc=$rc: $np processors, latest $(ls $C/processor0 | grep -v constant | sort -g | tail -1)"
[ $rc -eq 0 ] && [ $np -eq $N ] || { say "FAILED; LES left stopped for a manual restart"; exit 1; }
( cd $R && NP=$N T_PRE=90 TURB=les CHECKPOINT=5 KEEP=3 \
    cfd/docker/run.sh v4_sofa_tr_les${N}r $N bash cfd/cases/sofa/run_multi_v4.sh /sbd/cfd/runs 0 trousers > /dev/null )
echo "$(date '+%F %T') started v4_sofa_tr_les${N}r (LES resized to $N cores)" >> $RUNS/queue_v4.log
sleep 120
say "restarted: $(docker ps --format '{{.Names}} {{.Status}}' | grep tr_les); $(tail -1 $RUNS/pipeline_v4_sofa_tr_les${N}r.log)"
