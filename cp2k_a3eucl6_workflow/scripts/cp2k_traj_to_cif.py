from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from pymatgen.core import Lattice, Structure
from pymatgen.io.cif import CifWriter


def read_last_xyz_frame(path: Path) -> tuple[list[str], np.ndarray]:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    i = 0
    last = None
    while i < len(lines):
        try:
            n = int(lines[i].strip())
        except ValueError:
            i += 1
            continue
        frame = lines[i + 2 : i + 2 + n]
        elems = []
        coords = []
        for line in frame:
            parts = line.split()
            if len(parts) >= 4:
                elems.append(parts[0])
                coords.append([float(parts[1]), float(parts[2]), float(parts[3])])
        last = (elems, np.array(coords))
        i += n + 2
    if last is None:
        raise ValueError(f"No XYZ frames found in {path}")
    return last


def read_last_cell(path: Path) -> Lattice:
    vals = None
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) >= 12:
            vals = [float(x) for x in parts[2:11]]
    if vals is None:
        raise ValueError(f"No cell vectors found in {path}")
    matrix = np.array(vals, dtype=float).reshape(3, 3)
    return Lattice(matrix)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xyz", required=True, type=Path)
    parser.add_argument("--cell", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    elems, coords = read_last_xyz_frame(args.xyz)
    lattice = read_last_cell(args.cell)
    structure = Structure(lattice, elems, coords, coords_are_cartesian=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    CifWriter(structure).write_file(args.out)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
