<#
.SYNOPSIS
    Сборка exe через PyInstaller (окружение uv) и раскладка файлов рядом с exe.

.DESCRIPTION
    1. Собирает exe командой `uv run pyinstaller` (PyInstaller должен быть в зависимостях
       проекта, например `uv add --dev pyinstaller`).
    2. Копирует рядом с exe содержимое папки дополнительных файлов (-AddDir):
       справочники, иконки, пустые папки и т.п.
    3. Кладёт рядом с exe файл настроек .env (по умолчанию из .env.example).

    PyInstaller при пересборке полностью удаляет папку dist/<Name>. Если в ней есть данные
    (архив, логи), скрипт остановится; пересобрать поверх можно с ключом -Force.

.EXAMPLE
    .\build.ps1
    Сборка с параметрами по умолчанию (onedir, без консоли).

.EXAMPLE
    .\build.ps1 -EnvFile .env -Console
    Сборка с локальным .env и окном консоли (удобно для отладки).

.EXAMPLE
    .\build.ps1 -Name MyApp -Entry app.py -Icon res/app.ico -AddDir deploy -DataDirs data
    Для другого проекта.

.NOTES
    Если PowerShell не даёт запускать скрипты:
        powershell -ExecutionPolicy Bypass -File .\build.ps1
#>
param(
    # Имя exe и папки в dist/
    [string]$Name = 'SPG-023MK',
    # Точка входа
    [string]$Entry = 'main.py',
    # Иконка exe (пусто - без иконки)
    [string]$Icon = 'icon/shock-absorber.ico',
    # Папка, содержимое которой копируется рядом с exe (пусто - ничего не копировать)
    [string]$AddDir = 'dist/add',
    # Файл, который кладётся рядом с exe как .env (пусто - не класть)
    [string]$EnvFile = '.env.example',
    # Папки с данными внутри сборки: при наличии в них файлов пересборка без -Force запрещена
    [string[]]$DataDirs = @('archive', 'logs'),
    # Один exe-файл вместо папки
    [switch]$OneFile,
    # Показывать окно консоли
    [switch]$Console,
    # Очистить кэш PyInstaller перед сборкой
    [switch]$Clean,
    # Пересобрать, даже если в сборке есть данные (они будут удалены)
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

function Step($text) { Write-Host "`n==> $text" -ForegroundColor Cyan }
function Fail($text) { Write-Host "ОШИБКА: $text" -ForegroundColor Red; exit 1 }

# --- Проверки -------------------------------------------------------------------------
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { Fail 'не найден uv (https://docs.astral.sh/uv/)' }
if (-not (Test-Path $Entry)) { Fail "не найдена точка входа $Entry" }
if ($Icon -and -not (Test-Path $Icon)) { Fail "не найдена иконка $Icon" }
if ($AddDir -and -not (Test-Path $AddDir)) { Fail "не найдена папка дополнительных файлов $AddDir" }

$target = if ($OneFile) { 'dist' } else { Join-Path 'dist' $Name }

if (-not $OneFile -and (Test-Path $target) -and -not $Force) {
    foreach ($dir in $DataDirs) {
        $path = Join-Path $target $dir
        if ((Test-Path $path) -and (Get-ChildItem $path -Recurse -File | Select-Object -First 1)) {
            Fail ("в $path есть файлы, PyInstaller удалит их при пересборке.`n" +
                  "Сохраните их и запустите с -Force.")
        }
    }
}

# --- Сборка ---------------------------------------------------------------------------
$pyiArgs = @('--noconfirm', '--name', $Name)
$pyiArgs += if ($OneFile) { '--onefile' } else { '--onedir' }
$pyiArgs += if ($Console) { '--console' } else { '--windowed' }
if ($Icon) { $pyiArgs += @('--icon', $Icon) }
if ($Clean) { $pyiArgs += '--clean' }
$pyiArgs += $Entry

Step "uv run pyinstaller $($pyiArgs -join ' ')"
& uv run pyinstaller @pyiArgs
if ($LASTEXITCODE -ne 0) { Fail "PyInstaller завершился с кодом $LASTEXITCODE" }

# --- Файлы рядом с exe ----------------------------------------------------------------
if ($AddDir) {
    Step "Копирование $AddDir -> $target"
    Copy-Item -Path (Join-Path $AddDir '*') -Destination $target -Recurse -Force
}

if ($EnvFile) {
    if (Test-Path $EnvFile) {
        Step "Копирование $EnvFile -> $target\.env"
        Copy-Item -Path $EnvFile -Destination (Join-Path $target '.env') -Force
    } else {
        Write-Host "ВНИМАНИЕ: не найден $EnvFile, .env рядом с exe не положен" -ForegroundColor Yellow
    }
}

# --- Итог -----------------------------------------------------------------------------
$exe = Join-Path $target "$Name.exe"
$sizeMb = [math]::Round(((Get-ChildItem $target -Recurse -File | Measure-Object Length -Sum).Sum) / 1MB)
Step 'Готово'
Write-Host "  exe:    $((Resolve-Path $exe).Path)"
Write-Host "  размер: $sizeMb МБ"
if ($EnvFile) { Write-Host "  .env:   из $EnvFile - проверьте COM-порт и таймауты перед переносом на стенд" }
