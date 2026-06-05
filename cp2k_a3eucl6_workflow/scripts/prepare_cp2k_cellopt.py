from __future__ import annotations

import argparse
from pathlib import Path

from pymatgen.core import Structure


CP2K_WIN_DATA = Path(
    "D:/CPL_CAL/tools/cp2k-windows/cp2k-2025.2.x64/home/user/cp2k-2025.2/data"
)

KIND_DATA = {
    "H": ("DZVP-MOLOPT-SR-GTH", "GTH-PBE-q1"),
    "C": ("DZVP-MOLOPT-SR-GTH", "GTH-PBE-q4"),
    "N": ("DZVP-MOLOPT-SR-GTH", "GTH-PBE-q5"),
    "O": ("DZVP-MOLOPT-SR-GTH", "GTH-PBE-q6"),
    "F": ("DZVP-MOLOPT-SR-GTH", "GTH-PBE-q7"),
    "Cl": ("DZVP-MOLOPT-SR-GTH", "GTH-PBE-q7"),
    "Br": ("DZVP-MOLOPT-SR-GTH", "GTH-PBE-q7"),
    "P": ("DZVP-MOLOPT-SR-GTH", "GTH-PBE-q5"),
    "S": ("DZVP-MOLOPT-SR-GTH", "GTH-PBE-q6"),
    "Eu": ("DZV-MOLOPT-SR-GTH", "GTH-PBE-q17"),
}


def cell_block(structure: Structure) -> str:
    lat = structure.lattice
    a, b, c = lat.abc
    alpha, beta, gamma = lat.angles
    return f"""    &CELL
      ABC {a:.10f} {b:.10f} {c:.10f}
      ALPHA_BETA_GAMMA {alpha:.10f} {beta:.10f} {gamma:.10f}
      PERIODIC XYZ
    &END CELL"""


def coord_block(structure: Structure) -> str:
    lines = ["    &COORD", "      SCALED"]
    for site in structure:
        el = site.specie.symbol
        x, y, z = site.frac_coords
        lines.append(f"      {el:<2s} {x:.12f} {y:.12f} {z:.12f}")
    lines.append("    &END COORD")
    return "\n".join(lines)


def kind_blocks(structure: Structure) -> str:
    elements = sorted({site.specie.symbol for site in structure})
    missing = [el for el in elements if el not in KIND_DATA]
    if missing:
        raise ValueError(f"No default CP2K KIND data for: {', '.join(missing)}")
    blocks = []
    for el in elements:
        basis, potential = KIND_DATA[el]
        blocks.append(
            f"""    &KIND {el}
      BASIS_SET {basis}
      POTENTIAL {potential}
    &END KIND"""
        )
    return "\n".join(blocks)


def input_text(
    structure: Structure,
    project: str,
    cutoff: int,
    rel_cutoff: int,
    run_type: str,
    eps_scf: str,
    max_scf: int,
    fixed_indices: list[int] | None = None,
) -> str:
    constraint = ""
    if fixed_indices:
        fixed_list = " ".join(str(i) for i in fixed_indices)
        constraint = f"""  &CONSTRAINT
    &FIXED_ATOMS
      LIST {fixed_list}
      COMPONENTS_TO_FIX XYZ
    &END FIXED_ATOMS
  &END CONSTRAINT
"""

    geo_opt = """  &GEO_OPT
    OPTIMIZER BFGS
    MAX_ITER 300
    MAX_FORCE 4.5E-4
    RMS_FORCE 3.0E-4
    MAX_DR 1.0E-3
  &END GEO_OPT"""

    cell_opt = """  &CELL_OPT
    OPTIMIZER BFGS
    MAX_ITER 120
    TYPE DIRECT_CELL_OPT
    KEEP_ANGLES .FALSE.
    KEEP_SYMMETRY .FALSE.
    MAX_DR 3.0E-3
  &END CELL_OPT"""

    opt_block = ""
    if run_type == "GEO_OPT":
        opt_block = geo_opt
    elif run_type == "CELL_OPT":
        opt_block = cell_opt

    return f"""&GLOBAL
  PROJECT {project}
  RUN_TYPE {run_type}
  PRINT_LEVEL LOW
&END GLOBAL

&FORCE_EVAL
  METHOD Quickstep
  STRESS_TENSOR ANALYTICAL
  &DFT
    BASIS_SET_FILE_NAME BASIS_A3EUCL6
    POTENTIAL_FILE_NAME POTENTIAL_A3EUCL6
    &MGRID
      CUTOFF {cutoff}
      REL_CUTOFF {rel_cutoff}
    &END MGRID
    &SCF
      EPS_SCF {eps_scf}
      MAX_SCF {max_scf}
      &OT
        PRECONDITIONER FULL_SINGLE_INVERSE
        MINIMIZER DIIS
      &END OT
      &OUTER_SCF
        EPS_SCF {eps_scf}
        MAX_SCF 8
      &END OUTER_SCF
    &END SCF
    &XC
      &XC_FUNCTIONAL PBE
      &END XC_FUNCTIONAL
      &VDW_POTENTIAL
        POTENTIAL_TYPE PAIR_POTENTIAL
        &PAIR_POTENTIAL
          TYPE DFTD3(BJ)
          PARAMETER_FILE_NAME dftd3.dat
          REFERENCE_FUNCTIONAL PBE
        &END PAIR_POTENTIAL
      &END VDW_POTENTIAL
    &END XC
  &END DFT
  &SUBSYS
{cell_block(structure)}
{coord_block(structure)}
{kind_blocks(structure)}
  &END SUBSYS
&END FORCE_EVAL

&MOTION
{constraint}{opt_block}
  &PRINT
    &TRAJECTORY
      FORMAT XYZ
      &EACH
        GEO_OPT 1
        CELL_OPT 1
      &END EACH
    &END TRAJECTORY
    &CELL
      &EACH
        GEO_OPT 1
        CELL_OPT 1
      &END EACH
    &END CELL
  &END PRINT
&END MOTION
"""


def write_combined_cp2k_data(out: Path) -> None:
    basis_files = [CP2K_WIN_DATA / "BASIS_MOLOPT", CP2K_WIN_DATA / "BASIS_MOLOPT_LnPP1"]
    potential_files = [CP2K_WIN_DATA / "GTH_POTENTIALS", CP2K_WIN_DATA / "LnPP1_POTENTIALS"]

    basis_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in basis_files)
    potential_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in potential_files)

    (out / "BASIS_A3EUCL6").write_text(basis_text, encoding="utf-8")
    (out / "POTENTIAL_A3EUCL6").write_text(potential_text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cif", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--project", default="a3eucl6")
    parser.add_argument("--run-type", choices=["CELL_OPT", "GEO_OPT", "ENERGY"], default="CELL_OPT")
    parser.add_argument("--cutoff", type=int, default=300)
    parser.add_argument("--rel-cutoff", type=int, default=40)
    parser.add_argument("--eps-scf", default="1.0E-6")
    parser.add_argument("--max-scf", type=int, default=120)
    parser.add_argument(
        "--fixed-mode",
        choices=["none", "h-only", "h-cl-only"],
        default="none",
        help="h-only fixes all non-H atoms; h-cl-only fixes all atoms except H and Cl.",
    )
    args = parser.parse_args()

    structure = Structure.from_file(args.cif)
    fixed_indices = None
    if args.fixed_mode == "h-only":
        fixed_indices = [
            i + 1 for i, site in enumerate(structure) if site.specie.symbol != "H"
        ]
    elif args.fixed_mode == "h-cl-only":
        fixed_indices = [
            i + 1
            for i, site in enumerate(structure)
            if site.specie.symbol not in {"H", "Cl"}
        ]
    args.out.mkdir(parents=True, exist_ok=True)
    write_combined_cp2k_data(args.out)
    (args.out / "cellopt.inp").write_text(
        input_text(
            structure,
            args.project,
            args.cutoff,
            args.rel_cutoff,
            args.run_type,
            args.eps_scf,
            args.max_scf,
            fixed_indices,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {args.out / 'cellopt.inp'}")


if __name__ == "__main__":
    main()
