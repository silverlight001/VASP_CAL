# Article Methods Summary

Source: Nature Communications 16, 2525 (2025), DOI 10.1038/s41467-025-57620-0; PMC full text and Supplementary Information downloaded locally.

## DFT settings reported by the paper

- Code: VASP.
- Method: density functional theory.
- PAW method.
- Exchange-correlation: PBE.
- Plane-wave cutoff: 500 eV.
- Geometry relaxation: full relaxation.
- Energy convergence: `1e-5 eV`.
- Force convergence: `1e-3 eV/Angstrom`.
- SOC: included for electronic structure analysis.
- Postprocessing: VASPKIT.

## DFT observables reported

- Electronic band structure of `(R-3BrMBA)3EuCl6`.
- Projected density of states.

## Reported interpretation

- Nearly dispersionless bands indicate 0D structural features.
- VBM is mainly Eu unpaired 4f electrons and Cl p orbitals.
- CBM is mainly Eu 4f orbitals.
- C p orbitals of the chiral organic cations lie at higher conduction-band energies.
- Near-edge optical behavior is therefore dominated by Eu f-f transitions.

## Non-DFT model quantities in the paper

These are fits or calculations from experimental spectra, not VASP predictions:

- Experimental `g_lum` at 616 nm:
  - R material: `-1.84e-2`.
  - S material: `+1.18e-2`.
- FOM defined as `abs(g_lum) * PLQY`.
- Temperature-dependent DP fit reports CISOC strength around `0.152 eV Angstrom`.
- MPL bright/dark exciton fitting reports `Delta_B-D` around `11.7 meV`.

