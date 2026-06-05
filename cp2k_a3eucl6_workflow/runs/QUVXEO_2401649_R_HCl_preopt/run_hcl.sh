#!/usr/bin/env bash
set -euo pipefail

cd /mnt/d/CPL_CAL/cp2k_a3eucl6_workflow/runs/QUVXEO_2401649_R_HCl_preopt
export OMP_NUM_THREADS=2
export OMP_PROC_BIND=false

mpirun -np 6 cp2k.psmp -i cellopt.inp -o hcl_geoopt.out
