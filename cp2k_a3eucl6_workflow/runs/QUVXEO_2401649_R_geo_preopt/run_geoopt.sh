#!/usr/bin/env bash
set -euo pipefail

cd /mnt/d/CPL_CAL/cp2k_a3eucl6_workflow/runs/QUVXEO_2401649_R_geo_preopt
export OMP_NUM_THREADS=2
echo "Started QUVXEO_2401649_R GEO_OPT preoptimization at $(date)" > run_status.log
echo "Command: OMP_NUM_THREADS=2 mpirun -np 6 cp2k.psmp -i cellopt.inp -o geoopt.out" >> run_status.log
mpirun -np 6 cp2k.psmp -i cellopt.inp -o geoopt.out
echo "Finished QUVXEO_2401649_R GEO_OPT preoptimization at $(date)" >> run_status.log
