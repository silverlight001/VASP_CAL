# A3EuCl6 CP2K Crystal Optimization Workflow

This workflow is for optimizing `A3EuCl6` hybrid crystals and extracting local `EuCl6` octahedral information.

## What "serial Windows CP2K" means

The installed CP2K is a Windows/Cygwin `ssmp` build. It can run CP2K jobs, but it does not use MPI to split one calculation across many compute nodes or processes. It is fine for:

- learning CP2K input syntax,
- small test calculations,
- preparing and debugging structures,
- short geometry checks.

For large `A3EuCl6` crystal `CELL_OPT` jobs, use this local version for setup, then run the final inputs on WSL/Linux/HPC with an MPI CP2K build.

## Recommended workflow

1. Start from an experimental CIF or a reasonable substituted crystal model.
2. Generate a CP2K `CELL_OPT` input:

```powershell
python D:\CPL_CAL\cp2k_a3eucl6_workflow\scripts\prepare_cp2k_cellopt.py --cif D:\CPL_CAL\your_structure.cif --out D:\CPL_CAL\cp2k_a3eucl6_workflow\runs\A1
```

3. Run CP2K:

```powershell
powershell -ExecutionPolicy Bypass -File D:\CPL_CAL\tools\cp2k-windows\run-cp2k.ps1 -InputFile D:\CPL_CAL\cp2k_a3eucl6_workflow\runs\A1\cellopt.inp -OutputFile D:\CPL_CAL\cp2k_a3eucl6_workflow\runs\A1\cellopt.out
```

4. Convert the last CP2K trajectory frame to CIF:

```powershell
python D:\CPL_CAL\cp2k_a3eucl6_workflow\scripts\cp2k_traj_to_cif.py --xyz D:\CPL_CAL\cp2k_a3eucl6_workflow\runs\A1\a3eucl6-pos-1.xyz --cell D:\CPL_CAL\cp2k_a3eucl6_workflow\runs\A1\a3eucl6-1.cell --out D:\CPL_CAL\cp2k_a3eucl6_workflow\runs\A1\optimized.cif
```

5. Analyze the `EuCl6` octahedron:

```powershell
python D:\CPL_CAL\cp2k_a3eucl6_workflow\scripts\analyze_eucl6_octahedra.py --structure D:\CPL_CAL\cp2k_a3eucl6_workflow\runs\A1\optimized.cif --out D:\CPL_CAL\cp2k_a3eucl6_workflow\runs\A1\eucl6_metrics.csv
```

## Method choice

Default input:

- `CELL_OPT`
- PBE-D3(BJ)
- GPW/Quickstep
- Eu: LnPP2 4f-in-core trivalent lanthanide pseudopotential, `GTH-PBE-q11`
- C/H/N/Cl/Br/O/F/P/S: standard GTH-PBE potentials
- Gamma point by default

This is meant for structural screening. It is not a final electronic-structure model for Eu 4f spectroscopy or CPL.

## Practical advice

- Use `CELL_OPT` when you want the lattice and atoms to relax.
- Use `GEO_OPT` if you want to keep the experimental cell fixed and only relax atoms.
- For a first screen of many organic cations, use `--cutoff 300 --rel-cutoff 40`.
- For refined geometry, rerun promising candidates with `--cutoff 500 --rel-cutoff 60`.
- Compare trends across cations, not absolute energies from loosely converged screening runs.

