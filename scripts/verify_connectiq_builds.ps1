[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$DeveloperKey,

    [string[]]$Targets = @(
        "fr55",
        "vivoactive3",
        "venusq2",
        "fenix7pronowifi",
        "fenix8pro47mm"
    ),

    [switch]$InstalledManifestTargets
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$ProjectDir = Join-Path $RepoRoot "connectiq\GarminSupla"
$JungleFile = Join-Path $ProjectDir "monkey.jungle"
$ManifestFile = Join-Path $ProjectDir "manifest.xml"

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

if (-not (Test-Path $ManifestFile -PathType Leaf)) {
    throw "Connect IQ manifest not found: $ManifestFile"
}

$Sdk = (Get-Content $SdkConfig -Raw).Trim()
$MonkeyC = Join-Path $Sdk "bin\monkeyc.bat"

if (-not (Test-Path $MonkeyC -PathType Leaf)) {
    throw "Monkey C compiler not found: $MonkeyC"
}

if ($InstalledManifestTargets) {
    [xml]$Manifest = Get-Content $ManifestFile -Raw

    $NamespaceManager = New-Object System.Xml.XmlNamespaceManager(
        $Manifest.NameTable
    )
    $NamespaceManager.AddNamespace(
        "iq",
        "http://www.garmin.com/xml/connectiq"
    )

    $ManifestTargets = @(
        $Manifest.SelectNodes(
            "//iq:products/iq:product",
            $NamespaceManager
        ) |
            ForEach-Object {
                $_.GetAttribute("id")
            }
    )

    if ($ManifestTargets.Count -eq 0) {
        throw "No Connect IQ product targets found in manifest."
    }

    $InstalledTargets = @(
        $ManifestTargets |
            Where-Object {
                Test-Path (
                    Join-Path $DevicesRoot $_
                ) -PathType Container
            }
    )

    $NotInstalledTargets = @(
        $ManifestTargets |
            Where-Object {
                -not (
                    Test-Path (
                        Join-Path $DevicesRoot $_
                    ) -PathType Container
                )
            }
    )

    if ($InstalledTargets.Count -eq 0) {
        throw "None of the manifest targets are installed locally."
    }

    $Targets = $InstalledTargets
}
else {
    $NotInstalledTargets = @()
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host ""
Write-Host "GarminSupla Connect IQ build verification"
Write-Host "SDK: $Sdk"
& $MonkeyC --version

if ($InstalledManifestTargets) {
    Write-Host "Mode: installed manifest targets"
    Write-Host "Manifest targets: $($ManifestTargets.Count)"
    Write-Host "Installed manifest targets: $($Targets.Count)"
    Write-Host "Not installed manifest targets: $($NotInstalledTargets.Count)"
}
else {
    Write-Host "Mode: selected targets"
    Write-Host "Selected targets: $($Targets.Count)"
}

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

if (
    $InstalledManifestTargets -and
    $NotInstalledTargets.Count -gt 0
) {
    Write-Host ""
    Write-Host "Manifest targets not installed locally:"
    $NotInstalledTargets | ForEach-Object {
        Write-Host "  $_"
    }
}

$Failures = @(
    $Results | Where-Object {
        $_.Status -ne "Passed"
    }
)

if ($Failures.Count -gt 0) {
    Write-Host ""
    Write-Host "Build verification FAILED."
    exit 1
}

Write-Host ""
Write-Host "All selected builds PASSED."
exit 0
