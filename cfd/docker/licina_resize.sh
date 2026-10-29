#!/bin/bash
# A5: when the x1.5-mesh run (container sbd-a5_mesh15) ends, move the heated Licina chamber onto N cores: wait for its
# next 60-s write, stop the container, re-decompose the latest time into N subdomains and restart it with NP=N (the
# run resumes from the latest time). Same steps as les_resize.sh. N <= 18, the physical cores.
# Runs on the server host from the sbd-main clone: setsid nohup bash scratch/licina_resize.sh 18 &
# (log: cfd/runs/licina_resize.log in sbd-main)
N=${1:?usage: licina_resize.sh <cores>}
[ "$N" -le 18 ] || { echo "N must not exceed the 18 physical cores"; exit 1; }
R=$HOME/cyjoe/research/sbd-main
RUNS=$R/cfd/runs
C=$RUNS/licina2017_heated
LOG=$RUNS/licina_resize.log
say() { echo "$(date '+%F %T') resize: $*" >> $LOG; }
latest() { ls $C/processor0 | grep -v constant | sort -g | tail -1; }
say "waiting for the mesh run to end (last: $(tail -1 $RUNS/pipeline_a5_mesh15.log))"
until grep -qE 'pipeline done|FAILED' $RUNS/pipeline_a5_mesh15.log || ! docker ps --format '{{.Names}}' | grep -q '^sbd-a5_mesh15$'; do
  sleep 60; done
say "mesh run ended: $(tail -1 $RUNS/pipeline_a5_mesh15.log)"
grep -q 'pipeline done' $RUNS/pipeline_a5_licina_heated.log && { say "Licina already done; exit"; exit 0; }
L=$(docker ps --format '{{.Names}}' | grep '^sbd-a5_licina_heated' | head -1)
[ -z "$L" ] && { say "no Licina container running; exit"; exit 1; }
t0=$(latest)
say "waiting for the next write of $L after $t0"
until [ "$(latest)" != "$t0" ] || grep -q 'pipeline done' $RUNS/pipeline_${L#sbd-}.log; do sleep 30; done
grep -q 'pipeline done' $RUNS/pipeline_${L#sbd-}.log && { say "Licina done; exit"; exit 0; }
t1=$(latest); sleep 60  # let every rank finish writing t1
nw=$(ls -d $C/processor*/$t1 | wc -l); np0=$(ls -d $C/processor*/ | wc -l)
say "write $t1 on $nw of $np0 processors; stopping $L"
docker stop -t 20 $L > /dev/null; sleep 5
docker run --rm -u $(id -u):$(id -g) -v $R:/sbd -w /sbd/cfd/runs/licina2017_heated sbd-openfoam13 \
  nice -n 19 bash -c "source /opt/openfoam13/etc/bashrc
    reconstructPar -time $t1 > log.reconstructPar.resize 2>&1 || exit 1
    foamDictionary system/decomposeParDict -entry numberOfSubdomains -set $N > /dev/null
    decomposePar -force -time $t1 > log.decomposePar.resize 2>&1"
rc=$?
np=$(ls -d $C/processor*/ 2>/dev/null | wc -l)
say "re-decompose rc=$rc: $np processors, latest $(latest)"
[ $rc -eq 0 ] && [ $np -eq $N ] || { say "FAILED; Licina left stopped for a manual restart"; exit 1; }
( cd $R && NP=$N cfd/docker/run.sh a5_licina_heated$N $N \
    bash cfd/cases/licina2017/run_licina.sh /sbd/cfd/runs heated > /dev/null )
sleep 120
say "restarted: $(docker ps --format '{{.Names}} {{.Status}}' | grep licina); $(grep '^Time =' $C/log.foamRun | tail -1)"
