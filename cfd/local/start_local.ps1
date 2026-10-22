# Start, or resume, one CFD pipeline on the local PC. It runs in the WSL distro sbd-openfoam13, which is the server
# image sbd-openfoam13 imported with `wsl --import` (Docker Desktop does not start on this PC). The repo copy lives in
# /root/sbd inside the distro. The pipeline skips finished steps and, with CHECKPOINT, resumes long segments from the
# last 5-s piece, so after a reboot or crash run this script again. A lock file stops a second copy from starting.
# Usage: powershell -ExecutionPolicy Bypass -File cfd\local\start_local.ps1 [name] [command]
param(
  [string]$Name = "stand_still_tr",
  [string]$Cmd = ""
)
$known = @{
  stand_still_tr = "bash cfd/cases/standing/run_multi.sh /root/sbd/cfd/runs still trousers"
  sofa_les       = "env TURB=les bash cfd/cases/sofa/run_multi.sh /root/sbd/cfd/runs 0 bare"  # moved from the server
}
if (-not $Cmd) { $Cmd = $known[$Name] }
if (-not $Cmd) { Write-Error "unknown run '$Name' and no -Cmd given"; exit 1 }
$sh = "cd /root/sbd && export NP=4 T_PRE=90 CHECKPOINT=5 KEEP=3 && " +
      "flock -n cfd/runs/.local_$Name.lock nice -n 19 $Cmd >> cfd/runs/pipeline_local_$Name.log 2>&1"
# Created through WMI so the run is not a child of the calling app: a process started from the Claude app dies
# when the app updates or restarts (this killed the run once, 2026-10-22 06:13).
$si = New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{ShowWindow = [uint16]0}
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
  CommandLine = "wsl.exe -d sbd-openfoam13 -- bash -lc `"$sh`""; ProcessStartupInformation = $si }
if ($r.ReturnValue -ne 0) { Write-Error "Win32_Process.Create failed: $($r.ReturnValue)"; exit 1 }
Write-Output "started (or already running): $Name; log /root/sbd/cfd/runs/pipeline_local_$Name.log in sbd-openfoam13"
