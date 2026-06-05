# CP2K for Windows

Installed package:

- CP2K 2025.2 x64 Windows serial binary
- Location: `D:\CPL_CAL\tools\cp2k-windows\cp2k-2025.2.x64`
- Launcher: `D:\CPL_CAL\tools\cp2k-windows\cp2k-2025.2.x64\startcp2k.bat`

Version check:

```powershell
& "D:\CPL_CAL\tools\cp2k-windows\cp2k-2025.2.x64\startcp2k.bat" --version
```

Run an input file:

```powershell
powershell -File "D:\CPL_CAL\tools\cp2k-windows\run-cp2k.ps1" -InputFile "D:\CPL_CAL\cp2k_tests\h2o.inp" -OutputFile "D:\CPL_CAL\cp2k_tests\h2o.out"
```

Notes:

- This is a Windows/Cygwin serial build, so it is suitable for learning, small test calculations, and preparing workflows.
- For large A3EuCl6 crystal optimizations, a Linux/WSL/HPC CP2K build with MPI is much better.
- WSL Ubuntu was installed via winget, but WSL registration failed because the Windows Subsystem for Linux feature is not enabled. Enabling that requires administrator privileges.

