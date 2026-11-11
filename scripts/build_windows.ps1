#Requires -Version 5.1
<#
.SYNOPSIS
    Construye el ejecutable de Windows de la Calculadora de Circuitos.

.DESCRIPTION
    Genera una carpeta ``dist\CalcResisAGBL`` con el ejecutable y sus
    dependencias, copia la documentación y crea el ZIP listo para publicar en
    GitHub Releases. Se usa el modo ``--onedir`` porque arranca más rápido y es
    más estable que ``--onefile``.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1
#>

$ErrorActionPreference = "Stop"

$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "No se encontró 'uv'. Instálalo desde https://astral.sh/uv/ antes de continuar."
}

$icono = Join-Path $raiz "src\calc_resis_agbl\assets\icono_app.ico"
if (-not (Test-Path $icono)) {
    throw "No se encontró el icono: $icono"
}

$origen_assets = Join-Path $raiz "src\calc_resis_agbl\assets"
$entrada = Join-Path $raiz "src\calc_resis_agbl\main.py"
$dist = Join-Path $raiz "dist"
$build = Join-Path $raiz "build"
$carpeta = Join-Path $dist "CalcResisAGBL"
$zip = Join-Path $dist "CalcResisAGBL-windows-x64.zip"

if (Test-Path $carpeta) {
    Remove-Item $carpeta -Recurse -Force
}
if (Test-Path $zip) {
    Remove-Item $zip -Force
}

Write-Host "1/4 Sincronizando dependencias..." -ForegroundColor Cyan
uv sync --frozen

Write-Host "2/4 Generando ejecutable con PyInstaller..." -ForegroundColor Cyan
$argumentos = @(
    "--noconfirm",
    "--clean",
    "--windowed",
    "--onedir",
    "--name", "CalcResisAGBL",
    "--icon", $icono,
    "--add-data", "$origen_assets;calc_resis_agbl\assets",
    "--paths", (Join-Path $raiz "src"),
    "--distpath", $dist,
    "--workpath", $build,
    "--specpath", $build,
    $entrada
)
uv run pyinstaller @argumentos
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller falló con el código de salida $LASTEXITCODE."
}

$ejecutable = Join-Path $carpeta "CalcResisAGBL.exe"
if (-not (Test-Path $ejecutable)) {
    throw "PyInstaller no generó el ejecutable esperado: $ejecutable"
}

Write-Host "3/4 Copiando documentación..." -ForegroundColor Cyan
Copy-Item "README.md", "Manual_Usuario.md", "LICENSE" $carpeta -Force

Write-Host "4/4 Comprimiendo el resultado..." -ForegroundColor Cyan
$intentos = 5
for ($intento = 1; $intento -le $intentos; $intento++) {
    try {
        Compress-Archive -Path $carpeta -DestinationPath $zip -CompressionLevel Optimal -Force
        break
    } catch {
        if (Test-Path $zip) {
            Remove-Item $zip -Force -ErrorAction SilentlyContinue
        }
        if ($intento -eq $intentos) {
            throw
        }
        Write-Warning "El ZIP está siendo usado por otro proceso; reintentando ($intento/$intentos)..."
        Start-Sleep -Seconds 2
    }
}

Write-Host ""
Write-Host "Listo:" -ForegroundColor Green
Write-Host "  Ejecutable: $ejecutable"
Write-Host "  ZIP:        $zip"
