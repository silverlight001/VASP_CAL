from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from pymatgen.electronic_structure.plotter import BSPlotter, DosPlotter
from pymatgen.io.vasp.outputs import BSVasprun, Vasprun


def plot_band(calc: Path, out: Path) -> None:
    vasprun = calc / "03_band_soc" / "vasprun.xml"
    if not vasprun.exists():
        print(f"skip band plot, missing {vasprun}")
        return
    bs = BSVasprun(str(vasprun), parse_projected_eigen=True).get_band_structure(line_mode=True)
    plotter = BSPlotter(bs)
    plotter.get_plot(vbm_cbm_marker=True)
    plt.savefig(out / "band_structure.png", dpi=300, bbox_inches="tight")
    plt.close()


def plot_pdos(calc: Path, out: Path) -> None:
    vasprun = calc / "04_pdos_soc" / "vasprun.xml"
    if not vasprun.exists():
        print(f"skip PDOS plot, missing {vasprun}")
        return
    dosrun = Vasprun(str(vasprun), parse_dos=True, parse_eigen=False)
    complete = dosrun.complete_dos
    plotter = DosPlotter(sigma=0.05)
    for el in ["Eu", "Cl", "C", "N", "Br", "H"]:
        try:
            plotter.add_dos(el, complete.get_element_dos()[el])
        except KeyError:
            pass
    plotter.get_plot(xlim=(-6, 6))
    plt.savefig(out / "element_pdos.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--calc", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    plot_band(args.calc, args.out)
    plot_pdos(args.calc, args.out)


if __name__ == "__main__":
    main()

