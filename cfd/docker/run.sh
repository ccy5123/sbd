#!/bin/bash
# Start one CFD pipeline in a detached, CPU-capped, low-priority container (image sbd-openfoam13, see Dockerfile).
# The repo is mounted at /sbd and files are written as the calling user. NP, T_END, PURGE, ONLY and T_PRE are passed through.
# The container is named sbd-<name>; its output goes to cfd/runs/pipeline_<name>.log.
# Usage: cfd/docker/run.sh <name> <cpus> <command ...>
#   e.g. NP=4 T_END=600 PURGE=3 cfd/docker/run.sh elev 4 bash cfd/cases/elevator/run_elevator.sh /sbd/cfd/runs
NAME=$1; CPUS=$2; shift 2
REPO=$(cd "$(dirname "$0")/../.." && pwd)
mkdir -p "$REPO/cfd/runs"
docker run -d --rm --name "sbd-$NAME" --cpus "$CPUS" --memory 32g --shm-size 2g \
  -u "$(id -u):$(id -g)" -e HOME=/tmp -e NP -e T_END -e PURGE -e ONLY -e T_PRE \
  -v "$REPO:/sbd" -w /sbd sbd-openfoam13 \
  nice -n 19 bash -c "$* > cfd/runs/pipeline_$NAME.log 2>&1"
