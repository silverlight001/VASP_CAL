# AI-Assisted Computational Chemistry Workflows for Chiral Eu(III) Halides

[中文](#中文简介) · [English](#english-overview)

This repository collects an AI-assisted computational chemistry project focused on chiral europium halide molecular crystals, especially `(R/S-3BrMBA)3EuCl6`. It combines reproducible CP2K and VASP-oriented workflows for structure preparation, geometry optimization, local `EuCl6` octahedron analysis, electronic-structure post-processing, and literature-guided method reconstruction.

> **Research status:** This is an exploratory research repository, not a validated production package. AI was used to assist literature review, workflow design, scripting, debugging, and result organization. Every generated input and scientific conclusion should be checked by a domain expert before publication or reuse.

## 中文简介

本项目探索如何使用 AI 辅助计算化学研究，以手性铕卤化物分子晶体为主要对象，围绕 `(R/S-3BrMBA)3EuCl6` 构建了 CP2K 与 VASP 计算流程。仓库包含晶体结构预处理、几何优化输入生成、并行性能测试、计算过程监控、轨迹格式转换、`EuCl6` 八面体结构分析，以及论文计算方法复现工具。

AI 在本项目中主要用于：

- 从论文及补充材料中提取和整理计算方法；
- 生成、检查和迭代 CP2K/VASP 输入文件；
- 编写数据处理、结构分析和绘图脚本；
- 诊断计算收敛问题并记录可复现的处理流程；
- 整理计算结果、假设和复现限制。

AI 不替代量化计算验证。赝势、基组、截断能、k 点、色散修正、自旋轨道耦合和收敛阈值等设置应根据具体科研问题重新评估。

## English overview

The repository currently covers two connected tracks:

1. **CP2K structural workflow** — prepares and runs `CELL_OPT`, `GEO_OPT`, or single-point calculations for `A3EuCl6`-type crystals, then converts trajectories and measures local `EuCl6` geometry.
2. **VASP reproduction workflow** — reconstructs the periodic DFT workflow reported by Niu *et al.* for chiral europium halides and provides scripts for input preparation, model fitting, and electronic-structure plotting.

The goal is transparent workflow development and method exploration. It is not intended to produce final Eu 4f spectroscopy or CPL observables without further methodological validation.

## Repository layout

```text
.
├── cp2k_a3eucl6_workflow/       # CP2K preparation, runs, benchmarks, and analysis
│   ├── scripts/                  # Reusable Python and shell utilities
│   ├── runs/                     # Example inputs and selected calculation outputs
│   └── benchmarks/               # Parallel benchmark inputs and summaries
├── natcomm2025_eucl6_repro/      # VASP-oriented literature reproduction workflow
│   ├── scripts/                  # Input generation, fitting, and plotting tools
│   ├── results/                  # Demonstration figures
│   └── structures/               # Structure-related notes
├── cp2k_tests/                   # Small CP2K smoke tests
├── tools/cp2k-windows/           # Windows launcher documentation and wrapper
├── paper_docs_text/              # Locally collected supporting text
├── 2401650_S.cif                 # S-enantiomer crystal structure
└── QUVXEO_2401649_R.cif          # R-enantiomer crystal structure
```

For detailed instructions, see:

- [`cp2k_a3eucl6_workflow/README.md`](cp2k_a3eucl6_workflow/README.md)
- [`natcomm2025_eucl6_repro/README.md`](natcomm2025_eucl6_repro/README.md)
- [`natcomm2025_eucl6_repro/ARTICLE_METHODS_SUMMARY.md`](natcomm2025_eucl6_repro/ARTICLE_METHODS_SUMMARY.md)
- [`tools/cp2k-windows/README.md`](tools/cp2k-windows/README.md)

## Requirements

- Python 3.10 or newer is recommended.
- Python packages: `pymatgen`, `numpy`, and `matplotlib`.
- CP2K is required for the CP2K calculations.
- VASP and licensed PAW datasets are required for the VASP workflow.
- VASPKIT is optional for workflows that reproduce the paper's post-processing route.

Install the Python dependencies used by the reproduction scripts:

```bash
python -m pip install -r natcomm2025_eucl6_repro/requirements.txt
```

CP2K/VASP executables and licensed potential files are not distributed in this repository.

## Quick start: CP2K structure workflow

Generate a CP2K input from a CIF file:

```bash
python cp2k_a3eucl6_workflow/scripts/prepare_cp2k_cellopt.py \
  --cif QUVXEO_2401649_R.cif \
  --out cp2k_a3eucl6_workflow/runs/example_R \
  --run-type CELL_OPT
```

After the calculation, convert the last trajectory frame to CIF:

```bash
python cp2k_a3eucl6_workflow/scripts/cp2k_traj_to_cif.py \
  --xyz cp2k_a3eucl6_workflow/runs/example_R/a3eucl6-pos-1.xyz \
  --cell cp2k_a3eucl6_workflow/runs/example_R/a3eucl6-1.cell \
  --out cp2k_a3eucl6_workflow/runs/example_R/optimized.cif
```

Analyze the local `EuCl6` coordination geometry:

```bash
python cp2k_a3eucl6_workflow/scripts/analyze_eucl6_octahedra.py \
  --structure cp2k_a3eucl6_workflow/runs/example_R/optimized.cif \
  --out cp2k_a3eucl6_workflow/runs/example_R/eucl6_metrics.csv
```

The default structural-screening setup uses PBE-D3(BJ), Quickstep/GPW, gamma-point sampling, and an LnPP2 trivalent Eu pseudopotential with 4f electrons in the core. Review the generated input before running production calculations.

## Quick start: VASP reproduction workflow

Prepare the staged VASP folders:

```bash
python natcomm2025_eucl6_repro/scripts/prepare_vasp_inputs.py \
  --cif QUVXEO_2401649_R.cif \
  --out natcomm2025_eucl6_repro/vasp_inputs/R
```

The generated workflow is organized as:

1. geometry relaxation;
2. static calculation with spin-orbit coupling;
3. SOC band-structure calculation;
4. SOC projected-density-of-states calculation.

`POTCAR` is intentionally not generated or included because VASP potential files are licensed. Review all generated `INCAR`, `KPOINTS`, and structure files before submitting calculations.

## Scientific scope and limitations

- The CP2K workflow is primarily designed for structural screening and workflow development.
- The local Windows serial CP2K build is suitable for tests and short calculations; large crystal optimizations should use an MPI build on Linux, WSL, or HPC.
- The referenced paper does not report every setting needed for exact VASP reproduction, including the full k-point choices, Eu PAW dataset, possible DFT+U settings, and some convergence details.
- CPL dissymmetry factors are not directly predicted by the current scripts.
- Included numerical outputs may reflect interrupted, exploratory, or partially converged calculations; inspect each output before using it quantitatively.

## Reference

The VASP reproduction track is based on:

> Niu *et al.*, “Chiral europium halides with high-performance magnetic field tunable red circularly polarized luminescence at room temperature,” *Nature Communications* **16**, 2525 (2025). https://doi.org/10.1038/s41467-025-57620-0

Please cite the original article when using the literature-derived workflow.

## Data and licensing notice

- Crystal structures associated with CCDC deposition numbers `2401649` and `2401650` are subject to the applicable CCDC access and redistribution terms. Users are responsible for confirming that their use and redistribution are permitted.
- VASP, VASPKIT, PAW datasets, and other third-party software or data remain subject to their respective licenses.
- No open-source license has yet been assigned to the original code in this repository. Public visibility alone does not grant reuse rights beyond applicable law and GitHub's terms.
- Large restart, wavefunction, scratch, and licensed executable files are excluded through `.gitignore`.

## Contributing

Issues and reproducibility notes are welcome. When reporting a calculation, include the software version, platform, input files, convergence status, and enough log context to reproduce the behavior without exposing licensed data.

