#!/usr/bin/env bash
set -euo pipefail

cd /mnt/d/CPL_CAL/cp2k_a3eucl6_workflow/runs/QUVXEO_2401649_R
echo "Started QUVXEO_2401649_R CELL_OPT at $(date)" > run_status.log
echo "Command: mpirun -np 4 cp2k.psmp -i cellopt.inp -o cellopt.out" >> run_status.log
mpirun -np 4 cp2k.psmp -i cellopt.inp -o cellopt.out
echo "Finished QUVXEO_2401649_R CELL_OPT at $(date)" >> run_status.log

