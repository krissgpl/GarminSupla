[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$DeveloperKey,

    [string[]]$Targets = @(
        "fenix5s",
        "fr55",
        "vivoactive3",
        "venusq2",
        "fenix7pronowifi",
        "fenix8pro47mm"
    )
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$ProjectDir = Join-Path $RepoRoot "connectiq\GarminSupla"
$JungleFile = Join-Path $ProjectDir "monkey.jungle"

$SdkConfig = Join-Path $env:APPDATA "Garmin\ConnectIQ\current-sdk.cfg"
$DevicesRoot = Join-Path $env:APPDATA "Garmin\ConnectIQ\Devices"
$OutputDir = Join-Path $env:TEMP "GarminSupla-connectiq-builds"

if (-not (Test-Path $DeveloperKey -PathType Leaf)) {
    throw "Developer key not found: $DeveloperKey"
}

if (-not (Test-Path $SdkConfig -PathType Leaf)) {
    throw "Connect IQ SDK configuration not found: $SdkConfig"
}

if (-not (Test-Path $JungleFile -PathType Leaf)) {
    throw "Monkey C project not found: $JungleFile"
}

$Sdk = (Get-Content $SdkConfig -Raw).Trim()
$MonkeyC = Join-Path $Sdk "bin\monkeyc.bat"

if (-not (Test-Path $MonkeyC -PathType Leaf)) {
    throw "Monkey C compiler not found: $MonkeyC"
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host ""
Write-Host "GarminSupla Connect IQ build verification"
Write-Host "SDK: $Sdk"
& $MonkeyC --version
Write-Host ""

$Results = @()

Push-Location $ProjectDir

try {
    foreach ($Target in $Targets) {
        Write-Host "=== $Target ==="

        $DeviceDir = Join-Path $DevicesRoot $Target

        if (-not (Test-Path $DeviceDir -PathType Container)) {
            Write-Host "Device package is not installed."
            Write-Host ""

            $Results += [PSCustomObject]@{
                Target   = $Target
                Status   = "Not installed"
                ExitCode = $null
            }

            continue
        }

        $OutputFile = Join-Path $OutputDir "GarminSupla-$Target.prg"

        if (Test-Path $OutputFile) {
            Remove-Item $OutputFile -Force
        }

        & $MonkeyC `
            -f "monkey.jungle" `
            -d $Target `
            -o $OutputFile `
            -y $DeveloperKey

        $ExitCode = $LASTEXITCODE

        if ($ExitCode -eq 0) {
            $Status = "Passed"
        }
        else {
            $Status = "Failed"
        }

        $Results += [PSCustomObject]@{
            Target   = $Target
            Status   = $Status
            ExitCode = $ExitCode
        }

        Write-Host ""
    }
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "Build verification summary:"
$Results | Format-Table -AutoSize

$Failures = @(
    $Results | Where-Object {
        $_.Status -ne "Passed"
    }
)

if ($Failures.Count -gt 0) {
    Write-Host "Build verification FAILED."
    exit 1
}

Write-Host "All representative builds PASSED."
exit 0
