#!/bin/bash
# Move the sofa trousers LES from 4 to 8 cores without exceeding 20 cores in total: wait until the sofa -10 deg run
# has finished (its 4 cores free), then until the LES completes its next 5-s checkpoint piece, stop it, re-decompose
# the latest time into 8 subdomains and restart it with NP=8 (the pipeline skips finished pieces).
R=$HOME/cyjoe/research/sbd-v4
RUNS=$R/cfd/runs
LOG=$RUNS/les_realloc.log
say() { echo "$(date '+%F %T') $*" >> $LOG; }
say "watcher start"
until tail -1 $RUNS/pipeline_v4_sofa_rec-10.log | grep -q 'pipeline done'; do sleep 120; done
say "sofa_rec-10 done"
n0=$(grep -c 'segment .* done' $RUNS/pipeline_v4_sofa_tr_les.log)
until [ "$(grep -c 'segment .* done' $RUNS/pipeline_v4_sofa_tr_les.log)" -gt "$n0" ]; do sleep 30; done
say "LES piece done: $(grep 'segment .* done' $RUNS/pipeline_v4_sofa_tr_les.log | tail -1)"
docker stop -t 20 sbd-v4_sofa_tr_les > /dev/null; sleep 5
say "LES stopped; containers now $(docker ps --format '{{.Names}}' | grep -c '^sbd-')"
docker run --rm -u $(id -u):$(id -g) -v $R:/sbd -w /sbd/cfd/runs/sofa_tr_v4_multi_les sbd-openfoam13 nice -n 19 bash -c '
  source /opt/openfoam13/etc/bashrc
  reconstructPar -latestTime > log.reconstructPar.realloc 2>&1 || exit 1
  foamDictionary system/decomposeParDict -entry numberOfSubdomains -set 8 > /dev/null
  decomposePar -force -latestTime > log.decomposePar.realloc 2>&1 || exit 1
  ls -d processor*/ | wc -l; ls processor0'
rc=$?
say "re-decompose rc=$rc: $(ls -d $RUNS/sofa_tr_v4_multi_les/processor*/ | wc -l) processors, latest $(ls $RUNS/sofa_tr_v4_multi_les/processor0 | sort -g | tail -1)"
[ $rc -eq 0 ] || { say "re-decompose FAILED; LES left stopped"; exit 1; }
n=$(docker ps --format '{{.Names}}' | grep -c '^sbd-')
[ "$n" -le 3 ] || { say "too many containers ($n); not restarting"; exit 1; }
cd $R && NP=8 T_PRE=90 TURB=les CHECKPOINT=5 KEEP=3 cfd/docker/run.sh v4_sofa_tr_les8 8 bash cfd/cases/sofa/run_multi_v4.sh /sbd/cfd/runs 0 trousers > /dev/null
echo "$(date '+%F %T') started v4_sofa_tr_les8 (LES moved to 8 cores)" >> $RUNS/queue_v4.log
sleep 120
say "restarted on 8 cores: $(docker ps --format '{{.Names}} {{.Status}}' | grep tr_les); $(tail -1 $RUNS/pipeline_v4_sofa_tr_les8.log)"
