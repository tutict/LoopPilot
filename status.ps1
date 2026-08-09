[CmdletBinding()]
param(
    [string]$Destination
)

$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "distribution\loop-pilot.ps1") -Operation status -Destination $Destination
