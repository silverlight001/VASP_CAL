from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import time
from pathlib import Path


def win_to_wsl(path: Path) -> str:
    p = path.resolve()
    s = str(p).replace("\\", "/")
    if re.match(r"^[A-Za-z]:/", s):
        return f"/mnt/{s[0].lower()}/{s[3:]}"
    return s


def check_running() -> list[str]:
    result = subprocess.run(
        ["wsl", "-d", "Ubuntu-22.04", "-u", "cpl", "--", "bash", "-lc", "ps -eo pid,etime,cmd | grep -E 'cp2k.psmp|mpirun' | grep -v grep"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        check=False,
        timeout=10,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def parse_step_times(out: Path) -> tuple[list[float], str, str]:
    text = out.read_text(encoding="utf-8", errors="ignore") if out.exists() else ""
    times = []
    conv = "-"
    energy = "-"
    for line in text.splitlines():
        m = re.match(r"\s*\d+\s+OT\s+\S+\s+\S+\s+([0-9.]+)\s+([0-9.Ee+-]+)\s+(-?[0-9.]+)", line)
        if m:
            times.append(float(m.group(1)))
            conv = m.group(2)
            energy = m.group(3)
    return times, conv, energy


def copy_inputs(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for name in ["cellopt.inp", "BASIS_A3EUCL6", "POTENTIAL_A3EUCL6"]:
        shutil.copy2(src / name, dst / name)


def run_combo(work: Path, np: int, omp: int, seconds: int) -> dict[str, str | float | int]:
    out = work / "bench.out"
    out.unlink(missing_ok=True)
    cmd = (
        f"cd {win_to_wsl(work)} && "
        f"export OMP_NUM_THREADS={omp} && "
        f"timeout {seconds}s mpirun -np {np} cp2k.psmp -i cellopt.inp -o bench.out"
    )
    t0 = time.time()
    result = subprocess.run(
        ["wsl", "-d", "Ubuntu-22.04", "-u", "cpl", "--", "bash", "-lc", cmd],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        check=False,
        timeout=seconds + 60,
    )
    wall = time.time() - t0
    times, conv, energy = parse_step_times(out)
    used = times[1:] if len(times) > 2 else times
    avg = sum(used) / len(used) if used else 0.0
    return {
        "np": np,
        "omp": omp,
        "total_threads": np * omp,
        "seconds_limit": seconds,
        "exit_code": result.returncode,
        "wall_s": round(wall, 1),
        "steps": len(times),
        "avg_step_s_excl_first": round(avg, 2) if avg else "-",
        "last_convergence": conv,
        "last_energy": energy,
        "run_dir": str(work),
    }


def print_table(rows: list[dict[str, str | float | int]]) -> None:
    headers = ["np", "omp", "total_threads", "steps", "avg_step_s_excl_first", "last_convergence", "exit_code"]
    widths = {h: max(len(h), *(len(str(r[h])) for r in rows)) for h in headers}
    print(" | ".join(h.ljust(widths[h]) for h in headers))
    print("-+-".join("-" * widths[h] for h in headers))
    for r in rows:
        print(" | ".join(str(r[h]).ljust(widths[h]) for h in headers))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out-root", type=Path, default=Path("D:/CPL_CAL/cp2k_a3eucl6_workflow/benchmarks"))
    parser.add_argument("--seconds", type=int, default=90)
    parser.add_argument("--combos", default="4x1,6x1,8x1,10x1,4x2,6x2")
    parser.add_argument("--force", action="store_true", help="Run even if a CP2K process is already active")
    args = parser.parse_args()

    active = check_running()
    if active and not args.force:
        print("Active CP2K processes detected. Stop them first or rerun with --force.")
        for line in active:
            print(line)
        raise SystemExit(2)

    stamp = time.strftime("%Y%m%d_%H%M%S")
    root = args.out_root / stamp
    rows = []
    for combo in args.combos.split(","):
        np_s, omp_s = combo.lower().split("x")
        np = int(np_s)
        omp = int(omp_s)
        work = root / f"np{np}_omp{omp}"
        copy_inputs(args.source, work)
        print(f"Running benchmark np={np}, OMP_NUM_THREADS={omp} for {args.seconds}s...")
        rows.append(run_combo(work, np, omp, args.seconds))

    root.mkdir(parents=True, exist_ok=True)
    csv_path = root / "benchmark_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print()
    print_table(rows)
    print()
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()

