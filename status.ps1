[CmdletBinding()]
param(
    [string]$Destination,
    [ValidateSet("release", "archive")]
    [string]$SourceMode = "release",
    [string]$ArchiveSha256
)

$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "distribution\loop-pilot.ps1") -Operation status -Destination $Destination -SourceMode $SourceMode -ArchiveSha256 $ArchiveSha256
