param(
  [Parameter(Mandatory=$true)]
  [string]$InputFile,
  [string]$OutputFile = ""
)

$Root = Join-Path $PSScriptRoot "cp2k-2025.2.x64"
$Bat = Join-Path $Root "startcp2k.bat"

if ($OutputFile -eq "") {
  & $Bat -i $InputFile
} else {
  & $Bat -i $InputFile -o $OutputFile
}

