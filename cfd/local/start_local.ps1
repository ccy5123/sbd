# Start, or resume, one CFD pipeline on the local PC. It runs in the WSL distro sbd-openfoam13, which is the server
# image sbd-openfoam13 imported with `wsl --import` (Docker Desktop does not start on this PC). The repo copy lives in
# /root/sbd inside the distro. The pipeline skips finished steps and, with CHECKPOINT, resumes long segments from the
# last 5-s piece, so after a reboot or crash run this script again. A lock file stops a second copy from starting.
# Usage: powershell -ExecutionPolicy Bypass -File cfd\local\start_local.ps1 [name] [command] [-NP cores]
# (e.g. -Name elev_FL -NP 3 runs the elevator beside the 4-core bare LES on the 8-core PC, leaving one core free)
param(
  [string]$Name = "stand_still_tr",
  [string]$Cmd = "",
  [int]$NP = 4
)
$known = @{
  stand_still_tr = "bash cfd/cases/standing/run_multi.sh /root/sbd/cfd/runs still trousers"
  # the bare sofa LES moved from the server, then the elevator multi-release run (front-left culprit) on the cores it frees
  sofa_les       = "bash -c 'env TURB=les bash cfd/cases/sofa/run_multi.sh /root/sbd/cfd/runs 0 bare && " +
                   "bash cfd/cases/elevator/run_multi.sh /root/sbd/cfd/runs FL'"
  elev_FL        = "bash cfd/cases/elevator/run_multi.sh /root/sbd/cfd/runs FL"
  # PLAN v4 E0-3 / E0-6 (A5): Licina 2017 chamber with the manikin unheated, then S50 alone on the base sofa mesh
  # (needs the server's sofa_v4_pre copied to /root/sbd/cfd/runs); the server runs the heated chamber and the x1.5 mesh
  a5_local       = "bash -c 'env T_PRE=600 bash cfd/cases/licina2017/run_licina.sh /root/sbd/cfd/runs unheated && " +
                   "env RELEASES=S50 bash cfd/cases/sofa/run_multi.sh /root/sbd/cfd/runs 0 bare'"
}
if (-not $Cmd) { $Cmd = $known[$Name] }
if (-not $Cmd) { Write-Error "unknown run '$Name' and no -Cmd given"; exit 1 }
$sh = "cd /root/sbd && export NP=$NP T_PRE=90 CHECKPOINT=5 KEEP=3 && " +
      "flock -n cfd/runs/.local_$Name.lock nice -n 19 $Cmd >> cfd/runs/pipeline_local_$Name.log 2>&1"
# Created through WMI so the run is not a child of the calling app: a process started from the Claude app dies
# when the app updates or restarts (this killed the run once, 2026-10-22 06:13).
$si = New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{ShowWindow = [uint16]0}
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
  CommandLine = "wsl.exe -d sbd-openfoam13 -- bash -lc `"$sh`""; ProcessStartupInformation = $si }
if ($r.ReturnValue -ne 0) { Write-Error "Win32_Process.Create failed: $($r.ReturnValue)"; exit 1 }
Write-Output "started (or already running): $Name; log /root/sbd/cfd/runs/pipeline_local_$Name.log in sbd-openfoam13"
