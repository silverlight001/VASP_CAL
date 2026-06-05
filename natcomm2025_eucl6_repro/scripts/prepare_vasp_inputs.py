from __future__ import annotations

import argparse
from pathlib import Path

from pymatgen.core import Structure
from pymatgen.io.vasp import Kpoints, Poscar


RELAX_INCAR = """SYSTEM = chiral Eu halide relax
PREC = Accurate
ENCUT = 500
EDIFF = 1E-5
EDIFFG = -1E-3
IBRION = 2
ISIF = 3
NSW = 300
ISMEAR = 0
SIGMA = 0.05
LREAL = Auto
LASPH = .TRUE.
LWAVE = .FALSE.
LCHARG = .FALSE.

# The paper reports PBE/PAW/500 eV and full relaxation.
# It does not report D3, U, vdW, k-mesh, or PAW labels.
GGA = PE
"""

STATIC_SOC_INCAR = """SYSTEM = chiral Eu halide static SOC
PREC = Accurate
ENCUT = 500
EDIFF = 1E-6
NSW = 0
IBRION = -1
ISMEAR = 0
SIGMA = 0.05
LREAL = .FALSE.
LASPH = .TRUE.
LORBIT = 11
NEDOS = 3000
LWAVE = .TRUE.
LCHARG = .TRUE.

GGA = PE
LSORBIT = .TRUE.
ISYM = 0
SAXIS = 0 0 1
"""

BAND_SOC_INCAR = """SYSTEM = chiral Eu halide band SOC
PREC = Accurate
ENCUT = 500
EDIFF = 1E-6
NSW = 0
IBRION = -1
ISMEAR = 0
SIGMA = 0.05
LREAL = .FALSE.
LASPH = .TRUE.
LORBIT = 11
LWAVE = .FALSE.
LCHARG = .FALSE.

GGA = PE
LSORBIT = .TRUE.
ISYM = 0
SAXIS = 0 0 1
ICHARG = 11
"""

PDOS_SOC_INCAR = """SYSTEM = chiral Eu halide PDOS SOC
PREC = Accurate
ENCUT = 500
EDIFF = 1E-6
NSW = 0
IBRION = -1
ISMEAR = 0
SIGMA = 0.03
LREAL = .FALSE.
LASPH = .TRUE.
LORBIT = 11
NEDOS = 5000
LWAVE = .FALSE.
LCHARG = .FALSE.

GGA = PE
LSORBIT = .TRUE.
ISYM = 0
SAXIS = 0 0 1
ICHARG = 11
"""


def write_text(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def write_common_files(folder: Path, structure: Structure, incar: str, kpoints: Kpoints) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    Poscar(structure).write_file(folder / "POSCAR")
    write_text(folder / "INCAR", incar)
    kpoints.write_file(folder / "KPOINTS")
    write_text(
        folder / "POTCAR.todo.txt",
        "Create a licensed VASP POTCAR here. Suggested element order follows POSCAR.\n"
        "Use consistent PAW/PBE potentials; Eu valence choice affects 4f bands.\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cif", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--mesh", default="2 2 2", help="Monkhorst-Pack mesh for relax/static/PDOS")
    args = parser.parse_args()

    structure = Structure.from_file(args.cif)
    mesh = tuple(int(x) for x in args.mesh.split())
    mp = Kpoints.monkhorst_automatic(mesh)

    write_common_files(args.out / "01_relax", structure, RELAX_INCAR, mp)
    write_common_files(args.out / "02_static_soc", structure, STATIC_SOC_INCAR, mp)
    write_common_files(args.out / "04_pdos_soc", structure, PDOS_SOC_INCAR, mp)

    band_folder = args.out / "03_band_soc"
    band_folder.mkdir(parents=True, exist_ok=True)
    Poscar(structure).write_file(band_folder / "POSCAR")
    write_text(band_folder / "INCAR", BAND_SOC_INCAR)
    write_text(
        band_folder / "KPOINTS.todo.txt",
        "Use VASPKIT task 303 or pymatgen HighSymmKpath to generate a line-mode KPOINTS file.\n"
        "Because this is a low-symmetry chiral molecular crystal, verify the path manually.\n",
    )
    write_text(
        band_folder / "POTCAR.todo.txt",
        "Copy the same licensed POTCAR used in 02_static_soc.\n",
    )

    write_text(
        args.out / "RUN_ORDER.txt",
        "1. Run 01_relax.\n"
        "2. Copy 01_relax/CONTCAR to 02_static_soc/POSCAR, 03_band_soc/POSCAR, 04_pdos_soc/POSCAR.\n"
        "3. Run 02_static_soc.\n"
        "4. Copy CHGCAR from 02_static_soc to 03_band_soc and 04_pdos_soc.\n"
        "5. Generate 03_band_soc/KPOINTS line path, then run 03_band_soc.\n"
        "6. Run 04_pdos_soc.\n",
    )


if __name__ == "__main__":
    main()

