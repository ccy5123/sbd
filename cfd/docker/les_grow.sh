#!/bin/bash
# Grow the sofa trousers LES onto the server cores the other sbd runs free, within the user's cap (CAP, 20 cores
# over all sbd-* containers). Whenever at least 4 more cores are free than the LES has, wait for its next 5-s
# checkpoint piece, stop it, re-decompose the latest time into that many subdomains (scotch) and restart it as
# container sbd-v4_sofa_tr_les<N> with NP=N; the pipeline skips finished pieces. Exits when the LES is done.
# Runs on the server host: setsid nohup cfd/docker/les_grow.sh &   (log: cfd/runs/les_grow.log in sbd-v4)
CAP=20
MAXNP=18  # physical cores (i9-10980XE): mpirun refuses more slots ("not enough slots"), 25 Oct
R=$HOME/cyjoe/research/sbd-v4
RUNS=$R/cfd/runs
LOG=$RUNS/les_grow.log
say() { echo "$(date '+%F %T') $*" >> $LOG; }
les() { docker ps --format '{{.Names}}' | grep '^sbd-v4_sofa_tr_les' | head -1; }
cores() { docker inspect --format '{{.HostConfig.NanoCpus}}' "$1" | awk '{print int($1 / 1e9 + 0.5)}'; }
others() {
  local s=0 n
  for n in $(docker ps --format '{{.Names}}' | grep '^sbd-' | grep -v '^sbd-v4_sofa_tr_les'); do s=$((s + $(cores $n))); done
  echo $s
}
pieces() { grep -c 'segment .* done' "$1"; }

say "grow watcher start (cap $CAP)"
while true; do
  L=$(les)
  [ -z "$L" ] && { say "no LES container running; exit"; exit 0; }
  P=$RUNS/pipeline_${L#sbd-}.log
  grep -q 'pipeline done' $P && { say "LES done; exit"; exit 0; }
  cur=$(cores $L)
  free=$((CAP - $(others))); [ $free -gt $MAXNP ] && free=$MAXNP
  if [ $free -ge $((cur + 4)) ]; then
    n0=$(pieces $P)
    say "$free cores free, LES has $cur: waiting for its next checkpoint"
    until [ "$(pieces $P)" -gt "$n0" ] || grep -q 'pipeline done' $P; do sleep 30; done
    grep -q 'pipeline done' $P && { say "LES done; exit"; exit 0; }
    free=$((CAP - $(others))); [ $free -gt $MAXNP ] && free=$MAXNP
    [ $free -ge $((cur + 4)) ] || { say "cores taken meanwhile; LES stays on $cur"; continue; }
    say "checkpoint: $(grep 'segment .* done' $P | tail -1); stopping $L"
    docker stop -t 20 $L > /dev/null; sleep 5
    docker run --rm -u $(id -u):$(id -g) -v $R:/sbd -w /sbd/cfd/runs/sofa_tr_v4_multi_les sbd-openfoam13 \
      nice -n 19 bash -c "source /opt/openfoam13/etc/bashrc
        reconstructPar -latestTime > log.reconstructPar.grow 2>&1 || exit 1
        foamDictionary system/decomposeParDict -entry numberOfSubdomains -set $free > /dev/null
        decomposePar -force -latestTime > log.decomposePar.grow 2>&1"
    rc=$?
    np=$(ls -d $RUNS/sofa_tr_v4_multi_les/processor*/ 2>/dev/null | wc -l)
    say "re-decompose rc=$rc: $np processors, latest $(ls $RUNS/sofa_tr_v4_multi_les/processor0 | sort -g | tail -1)"
    [ $rc -eq 0 ] && [ $np -eq $free ] || { say "re-decompose FAILED; LES left stopped"; exit 1; }
    free2=$((CAP - $(others)))
    [ $free2 -ge $free ] || { say "only $free2 cores free now; LES left stopped for a manual restart"; exit 1; }
    ( cd $R && NP=$free T_PRE=90 TURB=les CHECKPOINT=5 KEEP=3 \
        cfd/docker/run.sh v4_sofa_tr_les$free $free bash cfd/cases/sofa/run_multi_v4.sh /sbd/cfd/runs 0 trousers > /dev/null )
    echo "$(date '+%F %T') started v4_sofa_tr_les$free (LES grown to $free cores)" >> $RUNS/queue_v4.log
    sleep 120
    say "restarted: $(docker ps --format '{{.Names}} {{.Status}}' | grep tr_les); $(tail -1 $RUNS/pipeline_v4_sofa_tr_les$free.log)"
  fi
  sleep 300
done
