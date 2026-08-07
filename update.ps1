[CmdletBinding()]
param(
    [string]$Destination,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "distribution\loop-pilot.ps1") -Operation update -Destination $Destination -Force:$Force
