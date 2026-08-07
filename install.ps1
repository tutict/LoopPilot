[CmdletBinding()]
param(
    [string]$Destination,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "distribution\loop-pilot.ps1") -Operation install -Destination $Destination -Force:$Force
