#!/bin/bash
# PLAN v4 E0-5: frozen-flow transport from the coupled reference branches (sofa upright, 30 s precursor) to compare
# with the coupled 10-min runs. Usage (repo root, inside the OpenFOAM container): run_e05.sh <mode> <t_src> [t_end]
source /opt/openfoam13/etc/bashrc >/dev/null 2>&1
M=$1; TS=$2; TE=${3:-600}
R=/sbd/cfd/runs
reconstructPar -case $R/sofa_$M -time $TS > $R/sofa_$M/log.reconstructPar.t$TS 2>&1
python3 /sbd/cfd/frozen/make_frozen.py $R/frozen_sofa_$M --bg $R/sofa_pre --t-bg 30 --src $R/sofa_$M --t-src $TS --t-end $TE
cd $R/frozen_sofa_$M
decomposePar -force > log.decomposePar 2>&1
mpirun --allow-run-as-root -np 4 foamRun -parallel > log.foamRun 2>&1
echo "frozen_sofa_$M pipeline done"
