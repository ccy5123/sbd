#!/bin/bash
# Run CFD jobs from a job file through run.sh, at most SLOTS containers (named sbd-*) at a time, each with CPUS cores.
# Job file lines: name|dependency|env|command   ('#' comments and blank lines skipped). The dependency is a shell
# test evaluated in cfd/runs; empty means none. 'finished <job>' is true once container sbd-<job> has exited and
# cfd/runs/pipeline_<job>.log ends with 'pipeline done'. Jobs start in file order as dependencies allow. Runs until
# every job has started. Usage (repo root): nohup cfd/docker/queue.sh <jobfile> > cfd/runs/queue.log 2>&1 &
SLOTS=${SLOTS:-5}
CPUS=${CPUS:-4}
REPO=$(cd "$(dirname "$0")/../.." && pwd)
JOBS=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
RUNS=$REPO/cfd/runs
mkdir -p "$RUNS"
finished() { ! docker ps -q --filter "name=^sbd-$1\$" | grep -q . && tail -1 "$RUNS/pipeline_$1.log" 2>/dev/null | grep -q "pipeline done"; }
declare -A started
while true; do
  left=0
  while IFS='|' read -r name dep envs cmd; do
    [[ -z "$name" || "$name" == \#* ]] && continue
    [ -n "${started[$name]}" ] && continue
    left=1
    [ "$(docker ps -q --filter name=^sbd- | wc -l)" -ge "$SLOTS" ] && break
    if [ -n "$dep" ] && ! (cd "$RUNS" && eval "$dep"); then continue; fi
    if docker ps -aq --filter "name=^sbd-$name\$" | grep -q .; then echo "$(date +%F\ %T) $name: container exists, skipped"; started[$name]=1; continue; fi
    (cd "$REPO" && env $envs cfd/docker/run.sh "$name" "$CPUS" $cmd > /dev/null) && echo "$(date +%F\ %T) started $name"
    started[$name]=1
  done < "$JOBS"
  [ $left = 0 ] && { echo "$(date +%F\ %T) all jobs started"; exit 0; }
  sleep 60
done
