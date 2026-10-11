<#
.SYNOPSIS
    Сборка отдельного exe просмотра архива (точка входа archive_view.py).

.DESCRIPTION
    Обёртка над build.ps1. Просмотрщику рядом с exe нужны только:
      icon/     - иконки окна;
      archive/  - папка архива (пустая; сюда кладутся/копируются файлы архива).
    Справочники (amorts.ini, operators.ini, cascade.ini) и .env ему не нужны.
    Результат: dist/SPG-023MK Archive view/

    Защита данных та же, что в build.ps1: если в archive/ или logs/ готовой сборки есть
    файлы, сборка остановится; пересобрать поверх - с ключом -Force.

.EXAMPLE
    .\build_archive_view.ps1
.EXAMPLE
    .\build_archive_view.ps1 -Console -Force
#>
param(
    [switch]$Console,
    [switch]$Clean,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

# Набор файлов рядом с exe собирается заново при каждой сборке из исходников проекта
$stage = 'dist/add_archive_view'
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Path "$stage/icon", "$stage/archive" -Force | Out-Null
Copy-Item -Path 'icon/*' -Destination "$stage/icon" -Recurse -Force

$params = @{
    Name     = 'SPG-023MK Archive view'
    Entry    = 'archive_view.py'
    Icon     = 'icon/shock-absorber.ico'
    AddDir   = $stage
    EnvFile  = ''
    Console  = $Console
    Clean    = $Clean
    Force    = $Force
}
& (Join-Path $PSScriptRoot 'build.ps1') @params
exit $LASTEXITCODE
