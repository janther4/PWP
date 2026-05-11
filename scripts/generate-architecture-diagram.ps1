param(
    [string]$InputFile = "documents/architecture-production.puml",
    [string]$OutputDir = "documents"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $InputFile)) {
    throw "Input file not found: $InputFile"
}

if (-not (Test-Path -LiteralPath $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

$resolvedInput = (Resolve-Path -LiteralPath $InputFile).Path
$resolvedOutputDir = (Resolve-Path -LiteralPath $OutputDir).Path

Write-Host "Generating architecture diagram from $resolvedInput"

$localPlantUml = Get-Command plantuml -ErrorAction SilentlyContinue
if ($null -ne $localPlantUml) {
    & plantuml "-tpng" "-o$resolvedOutputDir" "$resolvedInput"
    Write-Host "Done with local plantuml binary."
    exit 0
}

$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if ($null -eq $dockerCmd) {
    throw "Neither 'plantuml' nor 'docker' was found in PATH."
}

$mountPath = (Resolve-Path -LiteralPath ".").Path

docker run --rm `
    -v "${mountPath}:/workspace" `
    -w /workspace `
    plantuml/plantuml:latest `
    -tpng `
    -o"/workspace/$OutputDir" `
    "/workspace/$InputFile"

Write-Host "Done with Docker image plantuml/plantuml:latest."
