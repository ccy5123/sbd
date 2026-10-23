#!/bin/bash
# Move the bare sofa LES from the server to this PC once the local stand_still_tr run is done (core plan of
# 2026-10-22: the freed server cores go to the trousers LES through cfd/docker/les_grow.sh).
#  1. wait until the local pipeline is done;
#  2. on the server, start cfd/docker/les_bare_stop.sh detached (it stops sbd-v4_sofa_les right after its next
#     5-s checkpoint and leaves a marker), and wait for the marker;
#  3. copy sofa_v4_multi_les and the precursor pieces the pipeline checks (sofa_v4_pre/90, constant, system) into
#     the WSL distro sbd-openfoam13 (/root/sbd/cfd/runs);
#  4. start it there (start_local.ps1 -Name sofa_les, 4 cores) and point the login shortcut at it.
# Each step leaves a marker in /root/sbd/cfd/runs/.move_les/ and network steps retry, so it can be rerun at any
# time; a lock keeps one copy running. Runs in WSL Ubuntu (it holds the server key). The Startup shortcut
# "sbd move LES" starts it at login until it is done. Log: C:\Users\EH R&C CY\wsl\move_les_bare.log
exec 9> /tmp/move_les_bare.lock
flock -n 9 || exit 0
SSH="ssh -o BatchMode=yes -o ConnectTimeout=20 user@192.168.50.192"
SRV=cyjoe/research/sbd-v4/cfd/runs
PS1='C:\Users\EH R&C CY\research\sbd\cfd\local\start_local.ps1'
LOG="/mnt/c/Users/EH R&C CY/wsl/move_les_bare.log"
M=/root/sbd/cfd/runs/.move_les
say() { echo "$(date '+%F %T') $*" >> "$LOG"; }
in_sbd() { wsl.exe -d sbd-openfoam13 -- bash -c "$1" 2> /dev/null; }
mark() { in_sbd "mkdir -p $M && touch $M/$1"; }
marked() { in_sbd "test -f $M/$1"; }

say "mover start"
until marked local_done || in_sbd "grep -q 'pipeline done' /root/sbd/cfd/runs/pipeline_local_stand_still_tr.log"; do
  sleep 300
done
marked local_done || { mark local_done; say "local stand_still_tr done"; }

if ! marked server_stopped; then
  until $SSH "test -f ~/$SRV/.les_bare_stopped || pgrep -f '[l]es_bare_stop.sh' > /dev/null ||
              { setsid nohup ~/cyjoe/research/sbd-main/scratch/les_bare_stop.sh > /dev/null 2>&1 < /dev/null & }" 2> /dev/null; do
    sleep 120
  done
  say "server: waiting for the bare LES's next checkpoint"
  until $SSH "test -f ~/$SRV/.les_bare_stopped" 2> /dev/null; do sleep 120; done
  mark server_stopped; say "server: $($SSH "cat ~/$SRV/.les_bare_stopped" 2> /dev/null)"
fi

until marked copied; do
  in_sbd "rm -rf /root/sbd/cfd/runs/sofa_v4_multi_les /root/sbd/cfd/runs/sofa_v4_pre"
  $SSH "cd ~/$SRV && tar -cf - sofa_v4_multi_les sofa_v4_pre/90 sofa_v4_pre/constant sofa_v4_pre/system" 2> /dev/null \
    | wsl.exe -d sbd-openfoam13 -- tar -x -C /root/sbd/cfd/runs
  rc="${PIPESTATUS[0]}${PIPESTATUS[1]}"
  if [ "$rc" = "00" ] && in_sbd "test -f /root/sbd/cfd/runs/sofa_v4_pre/90/U && test -d /root/sbd/cfd/runs/sofa_v4_multi_les/processor3"; then
    mark copied; say "copied: $(in_sbd 'du -sh /root/sbd/cfd/runs/sofa_v4_multi_les | cut -f1')"
  else
    say "copy failed (rc $rc), retrying in 10 min"; sleep 600
  fi
done

if ! marked started; then
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$PS1" -Name sofa_les >> "$LOG" 2>&1
  sleep 90
  if in_sbd "pgrep -c foamRun" | grep -q '^4$'; then
    # the login shortcut now resumes the local LES; this mover's own shortcut is retired
    powershell.exe -NoProfile -Command "\$st = [Environment]::GetFolderPath('Startup');
      \$s = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path \$st 'sbd local CFD resume.lnk'));
      \$s.Arguments = \$s.Arguments + ' -Name sofa_les'; \$s.Save();
      Remove-Item -LiteralPath (Join-Path \$st 'sbd move LES.lnk') -ErrorAction SilentlyContinue" >> "$LOG" 2>&1
    mark started; say "local LES running on 4 cores; login shortcut now resumes it"
  else
    say "local LES did not start; see /root/sbd/cfd/runs/pipeline_local_sofa_les.log"; exit 1
  fi
fi
say "mover done"
