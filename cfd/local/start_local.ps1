# Start, or resume, one CFD pipeline on the local PC. It runs in the WSL distro sbd-openfoam13, which is the server
# image sbd-openfoam13 imported with `wsl --import` (Docker Desktop does not start on this PC). The repo copy lives in
# /root/sbd inside the distro. The pipeline skips finished steps and, with CHECKPOINT, resumes long segments from the
# last 5-s piece, so after a reboot or crash run this script again. A lock file stops a second copy from starting.
# Usage: powershell -ExecutionPolicy Bypass -File cfd\local\start_local.ps1 [name] [command]
param(
  [string]$Name = "stand_still_tr",
  [string]$Cmd = "bash cfd/cases/standing/run_multi.sh /root/sbd/cfd/runs still trousers"
)
$sh = "cd /root/sbd && export NP=4 T_PRE=90 CHECKPOINT=5 KEEP=3 && " +
      "flock -n cfd/runs/.local_$Name.lock nice -n 19 $Cmd >> cfd/runs/pipeline_local_$Name.log 2>&1"
Start-Process wsl.exe -ArgumentList "-d sbd-openfoam13 -- bash -lc `"$sh`"" -WindowStyle Hidden
Write-Output "started (or already running): $Name; log /root/sbd/cfd/runs/pipeline_local_$Name.log in sbd-openfoam13"
