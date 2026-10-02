[CmdletBinding()]
param(
    [string]$Destination,
    [switch]$Force,
    [ValidateSet("release", "archive")]
    [string]$SourceMode = "release",
    [string]$ArchiveSha256
)

$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "distribution\loop-pilot.ps1") -Operation install -Destination $Destination -Force:$Force -SourceMode $SourceMode -ArchiveSha256 $ArchiveSha256
