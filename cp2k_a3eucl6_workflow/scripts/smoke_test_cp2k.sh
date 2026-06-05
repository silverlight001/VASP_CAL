#!/usr/bin/env bash
set -u

run_dir="$1"
np="${2:-4}"
seconds="${3:-180}"
out="${4:-cellopt_smoke.out}"

cd "$run_dir"
rm -f "$out"

timeout "${seconds}s" mpirun -np "$np" cp2k.psmp -i cellopt.inp -o "$out"
code=$?
echo "EXIT_CODE:${code}"

if [ -f "$out" ]; then
  grep -E "PROGRAM STARTED|PROGRAM ENDED|ERROR|ABORT|Unknown|SCF run converged|ENERGY\\|" "$out" | tail -100 || true
fi

