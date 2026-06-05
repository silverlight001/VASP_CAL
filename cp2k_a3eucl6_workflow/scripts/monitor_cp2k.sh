#!/usr/bin/env bash
set -u

run_dir="$1"
out="${2:-cellopt.out}"

python3 /mnt/d/CPL_CAL/cp2k_a3eucl6_workflow/scripts/monitor_cp2k.py "$run_dir" --out "$out"

