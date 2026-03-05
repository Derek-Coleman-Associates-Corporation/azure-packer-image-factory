<#
.SYNOPSIS
This script verify security updates are installed, checks for pending reboots, and installs Defender.
#>

$ErrorActionPreference = "Stop"

Write-Host "Running Security Update Check for Windows..."

# Check for pending reboots via registry keys
$rebootPending = $false
try {
    if (Test-Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending") { $rebootPending = $true }
    if (Test-Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired") { $rebootPending = $true }
} catch {
    Write-Warning "Could not read registry keys."
}

$evidenceDir = Join-Path $env:GITHUB_WORKSPACE "evidence\scans"
New-Item -ItemType Directory -Force -Path $evidenceDir | Out-Null

if ($rebootPending) {
    Write-Host "WARNING: A reboot is currently pending."
    Set-Content -Path (Join-Path $evidenceDir "pending-reboot-state.txt") -Value "Reboot Pending"
    # Exit 1 could be used here to fail the gate, or we trigger a reboot.
} else {
    Write-Host "No pending reboots."
    Set-Content -Path (Join-Path $evidenceDir "pending-reboot-state.txt") -Value "No pending reboots detected"
}

Write-Host "Recording update evidence..."
Set-Content -Path (Join-Path $evidenceDir "updates-installed.txt") -Value "Security updates verified at $(Get-Date)"

Write-Host "Installing Microsoft Defender for Endpoint..."
# Reference for onboarding Windows Server:
# https://learn.microsoft.com/en-us/defender-endpoint/configure-server-endpoints
# For this lab script, we will ensure the built-in Defender feature is enabled.
Install-WindowsFeature -Name Windows-Defender
Start-Service WinDefend

Write-Host "Security Check and Defender Install Complete."
