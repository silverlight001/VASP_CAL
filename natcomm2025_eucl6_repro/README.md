# Nat. Commun. 2025 EuCl6 CPL DFT Reproduction

This folder reproduces the simulation workflow reported for:

Niu et al., "Chiral europium halides with high-performance magnetic field tunable red circularly polarized luminescence at room temperature", Nature Communications 16, 2525 (2025). DOI: 10.1038/s41467-025-57620-0.

## What the paper computed

The article did not directly compute CPL `g_lum` from first principles. Its simulation work was:

1. Periodic DFT for `(R-3BrMBA)3EuCl6` using VASP.
2. PBE functional, PAW potentials, plane-wave cutoff `500 eV`.
3. Full geometry relaxation to energy `1e-5 eV` and force `1e-3 eV/Angstrom`.
4. Spin-orbit coupling for electronic structure analysis.
5. Band structure and projected density of states, postprocessed with VASPKIT.

Their result: bands are nearly flat, consistent with a 0D crystal. VBM is mainly Eu 4f plus Cl p; CBM is mainly Eu 4f. Carbon p orbitals from the chiral organic cation sit higher in the conduction band, so near-edge optical transitions are dominated by Eu f-f transitions.

## Current local status

This machine currently has Python, but not VASP or VASPKIT. CCDC structures are license-gated from the public web endpoint, so the CIF files must be supplied manually.

Required crystal structures:

- `CCDC 2401649`: `(R-3BrMBA)3EuCl6`
- `CCDC 2401650`: `(S-3BrMBA)3EuCl6`

Put them here:

- `structures/R-3BrMBA3EuCl6.cif`
- `structures/S-3BrMBA3EuCl6.cif`

## Quick start

Install Python helpers:

```powershell
pip install pymatgen matplotlib numpy
```

Generate VASP input folders from a CIF:

```powershell
python scripts/prepare_vasp_inputs.py --cif structures/R-3BrMBA3EuCl6.cif --out vasp_inputs/R
```

Copy or generate `POTCAR` files for every generated calculation folder. The script deliberately does not create `POTCAR` because VASP potentials are licensed.

Run VASP in this order:

1. `vasp_inputs/R/01_relax`
2. `vasp_inputs/R/02_static_soc`
3. `vasp_inputs/R/03_band_soc`
4. `vasp_inputs/R/04_pdos_soc`

Then postprocess:

```powershell
python scripts/plot_vasp_outputs.py --calc vasp_inputs/R --out results/R
```

## Notes on exact reproducibility

The article does not report k-point grids, Eu PAW choice, DFT+U settings, smearing, dispersion correction, or whether H positions were fixed from XRD. The supplied input files therefore follow a conservative molecular-crystal setup and document every assumption in the `INCAR` comments. If you want one-to-one reproduction, use the authors' deposited CIF and ask the corresponding authors for the exact VASP input set.

