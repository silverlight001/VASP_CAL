from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def first(pattern: str, text: str, default: str = "-") -> str:
    match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else default


def all_matches(pattern: str, text: str) -> list[str]:
    return [m.strip() for m in re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)]


def tail_lines(path: Path, n: int) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return lines[-n:]


def running_processes(run_dir: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["wsl", "-d", "Ubuntu-22.04", "-u", "cpl", "--", "bash", "-lc", "ps -eo pid,etime,cmd | grep -E 'cp2k.psmp|mpirun' | grep -v grep"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=10,
        )
    except Exception:
        return []
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    needle = str(run_dir).replace("\\", "/")
    if needle.startswith("D:/"):
        needle = "/mnt/d/" + needle[3:]
    related = [line for line in lines if needle in line]
    return related or lines


def parse_input(inp: Path) -> dict[str, str | list[str]]:
    text = read_text(inp)
    kinds = all_matches(r"^\s*&KIND\s+([A-Za-z][A-Za-z]?)\b", text)
    basis_files = all_matches(r"^\s*BASIS_SET_FILE_NAME\s+(.+)$", text)
    potential_files = all_matches(r"^\s*POTENTIAL_FILE_NAME\s+(.+)$", text)
    return {
        "project": first(r"^\s*PROJECT\s+(.+)$", text),
        "run_type": first(r"^\s*RUN_TYPE\s+(.+)$", text),
        "method": first(r"^\s*METHOD\s+(.+)$", text),
        "cutoff": first(r"^\s*CUTOFF\s+(.+)$", text),
        "rel_cutoff": first(r"^\s*REL_CUTOFF\s+(.+)$", text),
        "xc": first(r"^\s*&XC_FUNCTIONAL\s+(.+)$", text),
        "vdw_type": first(r"^\s*TYPE\s+(.+)$", text),
        "vdw_ref": first(r"^\s*REFERENCE_FUNCTIONAL\s+(.+)$", text),
        "basis_files": basis_files,
        "potential_files": potential_files,
        "kinds": kinds,
        "abc": first(r"^\s*ABC\s+(.+)$", text),
        "angles": first(r"^\s*ALPHA_BETA_GAMMA\s+(.+)$", text),
        "geo_optimizer": first(r"^\s*OPTIMIZER\s+(.+)$", text),
        "max_iter": first(r"^\s*MAX_ITER\s+(.+)$", text),
    }


def parse_output(out: Path) -> dict[str, str | list[str]]:
    text = read_text(out)
    energies = all_matches(r"ENERGY\|\s+Total FORCE_EVAL.*?(-?\d+\.\d+)", text)
    total_energies = all_matches(r"^\s*Total energy:\s+(-?\d+\.\d+)", text)
    if not energies and total_energies:
        energies = total_energies
    scf_count = len(re.findall(r"SCF run converged", text, re.IGNORECASE))
    return {
        "started": "yes" if "PROGRAM STARTED" in text else "no",
        "ended": "yes" if "PROGRAM ENDED" in text else "no",
        "aborts": all_matches(r"(\[ABORT\].*|ABORT.*|ERROR.*|Error.*|failed.*)", text)[-10:],
        "last_energy": energies[-1] if energies else "-",
        "energy_count": str(len(energies)),
        "scf_converged_count": str(scf_count),
        "tail": tail_lines(out, 25),
    }


def file_size(path: Path) -> str:
    if not path.exists():
        return "missing"
    size = path.stat().st_size
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--out", default="cellopt.out")
    parser.add_argument("--inp", default="cellopt.inp")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    inp = run_dir / args.inp
    out = run_dir / args.out
    info = parse_input(inp)
    status = parse_output(out)
    procs = running_processes(run_dir)

    print("=== CP2K Run Monitor ===")
    print(f"Run directory: {run_dir}")
    print(f"Input: {inp.name} ({file_size(inp)})")
    print(f"Output: {out.name} ({file_size(out)})")
    print()

    print("=== Calculation ===")
    print(f"Project: {info['project']}")
    print(f"Run type: {info['run_type']}")
    print(f"Method: {info['method']}")
    print(f"XC functional: {info['xc']}")
    print(f"Dispersion: {info['vdw_type']} / reference {info['vdw_ref']}")
    print(f"MGRID cutoff / rel_cutoff: {info['cutoff']} / {info['rel_cutoff']}")
    print(f"Basis files: {', '.join(info['basis_files']) if info['basis_files'] else '-'}")
    print(f"Potential files: {', '.join(info['potential_files']) if info['potential_files'] else '-'}")
    print(f"KIND elements: {', '.join(info['kinds']) if info['kinds'] else '-'}")
    print(f"Initial cell ABC: {info['abc']}")
    print(f"Initial angles: {info['angles']}")
    print(f"Optimizer: {info['geo_optimizer']}; MAX_ITER: {info['max_iter']}")
    print()

    print("=== Status ===")
    print(f"Running processes: {'yes' if procs else 'no'}")
    for line in procs[:8]:
        print(f"  {line}")
    print(f"Program started: {status['started']}")
    print(f"Program ended: {status['ended']}")
    print(f"SCF converged count: {status['scf_converged_count']}")
    print(f"Energy records: {status['energy_count']}")
    print(f"Last total energy: {status['last_energy']}")
    if status["aborts"]:
        print("Recent errors/aborts:")
        for line in status["aborts"]:
            print(f"  {line}")
    print()

    print("=== Output Tail ===")
    for line in status["tail"]:
        print(line)


if __name__ == "__main__":
    main()
