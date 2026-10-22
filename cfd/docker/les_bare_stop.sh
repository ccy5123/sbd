#!/bin/bash
# Server side of cfd/local/move_les_bare.sh: wait for the bare sofa LES's next 5-s checkpoint, stop its container and
# leave the marker cfd/runs/.les_bare_stopped (in sbd-v4). Run detached: setsid nohup les_bare_stop.sh &
RUNS=$HOME/cyjoe/research/sbd-v4/cfd/runs
[ -f $RUNS/.les_bare_stopped ] && exit 0
P=$RUNS/pipeline_v4_sofa_les.log
n0=$(grep -c 'segment .* done' $P)
until [ "$(grep -c 'segment .* done' $P)" -gt "$n0" ]; do sleep 30; done
docker stop -t 20 sbd-v4_sofa_les > /dev/null
echo "$(date '+%F %T') stopped after: $(grep 'segment .* done' $P | tail -1)" > $RUNS/.les_bare_stopped
echo "$(date '+%F %T') stopped v4_sofa_les (moved to the local PC)" >> $RUNS/queue_v4.log
