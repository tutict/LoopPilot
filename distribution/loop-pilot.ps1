[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet("install", "update", "uninstall")]
    [string]$Operation,
    [string]$Destination,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$SourceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ManifestPath = Join-Path $SourceRoot "distribution\managed-files.txt"
$VersionPath = Join-Path $SourceRoot "distribution\version.txt"
$StateName = ".looppilot-installation"
$StateFormat = "1"

function Fail([string]$Message) {
    throw "LoopPilot distribution: $Message"
}

function Assert-RelativePath([string]$RelativePath) {
    if ([string]::IsNullOrWhiteSpace($RelativePath) -or
        [IO.Path]::IsPathRooted($RelativePath) -or
        $RelativePath -match '[\\|:\x00-\x1f]' -or
        $RelativePath -match '(^|/)\.\.?(/|$)' -or
        $RelativePath.StartsWith("/") -or
        $RelativePath.EndsWith("/") -or
        $RelativePath.Contains("//")) {
        Fail "unsafe managed path '$RelativePath'"
    }
}

function Resolve-TargetPath([string]$Path) {
    $fullPath = [IO.Path]::GetFullPath($Path)
    $targetItem = Get-Item -LiteralPath $fullPath -Force -ErrorAction SilentlyContinue
    if ($null -ne $targetItem) {
        if (($targetItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            Fail "destination must not be a symbolic link or reparse point: '$fullPath'"
        }
        if (-not (Test-Path -LiteralPath $fullPath -PathType Container)) {
            Fail "destination is not a directory: '$fullPath'"
        }
        return (Resolve-Path -LiteralPath $fullPath).Path
    }

    $missing = New-Object System.Collections.Generic.Stack[string]
    $probe = $fullPath
    while (-not (Test-Path -LiteralPath $probe)) {
        $leaf = Split-Path -Leaf $probe
        $parent = Split-Path -Parent $probe
        if ([string]::IsNullOrWhiteSpace($leaf) -or $parent -eq $probe) {
            Fail "cannot resolve destination '$fullPath'"
        }
        $missing.Push($leaf)
        $probe = $parent
    }
    if (-not (Test-Path -LiteralPath $probe -PathType Container)) {
        Fail "destination parent is not a directory: '$probe'"
    }
    $resolved = (Resolve-Path -LiteralPath $probe).Path
    while ($missing.Count -gt 0) {
        $resolved = Join-Path $resolved $missing.Pop()
    }
    return [IO.Path]::GetFullPath($resolved)
}

function Get-InstallDestination([string]$Requested) {
    if (-not [string]::IsNullOrWhiteSpace($Requested)) {
        return Resolve-TargetPath $Requested
    }
    if (-not [string]::IsNullOrWhiteSpace($env:LOOPPILOT_INSTALL_DIR)) {
        return Resolve-TargetPath $env:LOOPPILOT_INSTALL_DIR
    }

    $home = [Environment]::GetFolderPath("UserProfile")
    $parents = @()
    if (-not [string]::IsNullOrWhiteSpace($env:CLAUDE_CONFIG_DIR)) {
        $parents += Join-Path $env:CLAUDE_CONFIG_DIR "skills"
    } elseif (Test-Path -LiteralPath (Join-Path $home ".claude\skills") -PathType Container) {
        $parents += Join-Path $home ".claude\skills"
    }
    if (Test-Path -LiteralPath (Join-Path $home ".codex\skills") -PathType Container) {
        $parents += Join-Path $home ".codex\skills"
    }

    $parents = @($parents | Sort-Object -Unique)
    if ($parents.Count -eq 1) {
        return Resolve-TargetPath (Join-Path $parents[0] "loop-pilot")
    }
    if ($parents.Count -eq 0) {
        Fail "destination is not detectable; pass -Destination or set LOOPPILOT_INSTALL_DIR"
    }
    Fail "destination is ambiguous; pass -Destination or set LOOPPILOT_INSTALL_DIR"
}

function Get-SourceVersion {
    if (-not (Test-Path -LiteralPath $VersionPath -PathType Leaf)) {
        Fail "missing distribution/version.txt"
    }
    $version = (Get-Content -Raw -LiteralPath $VersionPath).Trim()
    if ($version -notmatch '^[A-Za-z0-9._-]+$') {
        Fail "distribution/version.txt must contain one non-empty version token"
    }
    return $version
}

function Get-SourceCommit {
    $commit = $null
    try {
        $commit = (& git -C $SourceRoot rev-parse --verify HEAD 2>$null)
        if ($LASTEXITCODE -ne 0) { $commit = $null }
    } catch {
        $commit = $null
    }
    if (-not [string]::IsNullOrWhiteSpace($commit)) {
        $commit = $commit.Trim()
    }
    if ([string]::IsNullOrWhiteSpace($commit)) {
        $commitFile = Join-Path $SourceRoot "distribution\commit.txt"
        if (Test-Path -LiteralPath $commitFile -PathType Leaf) {
            $commit = (Get-Content -Raw -LiteralPath $commitFile).Trim()
        }
    }
    if ($commit -notmatch '^[0-9a-f]{40}$') {
        Fail "cannot determine a 40-character source commit; run from Git or provide distribution/commit.txt"
    }
    return $commit
}

function Get-GitRoot {
    try {
        $root = (& git -C $SourceRoot rev-parse --show-toplevel 2>$null)
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($root)) { return $null }
        $resolved = (Resolve-Path -LiteralPath $root.Trim()).Path
        if ($resolved -eq $SourceRoot) { return $resolved }
    } catch {
        return $null
    }
    return $null
}

function Assert-SourceFile([string]$RelativePath) {
    Assert-RelativePath $RelativePath
    $sourcePath = Join-Path $SourceRoot ($RelativePath.Replace("/", "\"))
    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
        Fail "manifest file is missing: $RelativePath"
    }
    $item = Get-Item -LiteralPath $sourcePath -Force
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        Fail "manifest file must not be a symbolic link or reparse point: $RelativePath"
    }
}

function Get-ManifestEntries {
    if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
        Fail "missing distribution/managed-files.txt"
    }
    $entries = New-Object System.Collections.Generic.List[string]
    $gitRoot = Get-GitRoot
    foreach ($line in Get-Content -LiteralPath $ManifestPath) {
        $entry = $line.Trim()
        if ([string]::IsNullOrWhiteSpace($entry) -or $entry.StartsWith("#")) {
            continue
        }
        $trimmed = $entry.TrimEnd("/")
        Assert-RelativePath $trimmed
        $sourcePath = Join-Path $SourceRoot ($trimmed.Replace("/", "\"))
        if ($entry.EndsWith("/")) {
            if (-not (Test-Path -LiteralPath $sourcePath -PathType Container)) {
                Fail "manifest directory is missing: $entry"
            }
            if ($null -ne $gitRoot) {
                $files = @(& git -C $SourceRoot ls-files -- "$trimmed/")
                if ($LASTEXITCODE -ne 0) { Fail "cannot enumerate tracked files for: $entry" }
                foreach ($file in $files) {
                    if (-not [string]::IsNullOrWhiteSpace($file)) {
                        $entries.Add($file.Replace("\", "/"))
                    }
                }
            } else {
                $prefix = $SourceRoot.TrimEnd("\") + "\"
                foreach ($file in Get-ChildItem -LiteralPath $sourcePath -Recurse -File -Force) {
                    $relative = $file.FullName.Substring($prefix.Length).Replace("\", "/")
                    $entries.Add($relative)
                }
            }
        } else {
            $entries.Add($trimmed.Replace("\", "/"))
        }
    }

    $result = @($entries | Sort-Object -Unique)
    if ($result.Count -eq 0) { Fail "distribution manifest contains no files" }
    foreach ($entry in $result) { Assert-SourceFile $entry }
    return $result
}

function Get-Hash([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-State([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    $state = [ordered]@{
        Format = $null
        Version = $null
        Commit = $null
        Manifest = $null
        Files = [ordered]@{}
        Customized = [ordered]@{}
    }
    $seen = @{}
    foreach ($line in Get-Content -LiteralPath $Path) {
        if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith("#")) { continue }
        $parts = @($line.Split([char]'|'))
        $kind = $parts[0]
        switch ($kind) {
            "FORMAT" {
                if ($parts.Count -ne 2 -or $seen.ContainsKey($kind)) { Fail "invalid installation state FORMAT row" }
                $seen[$kind] = $true
                $state.Format = $parts[1]
            }
            "VERSION" {
                if ($parts.Count -ne 2 -or $seen.ContainsKey($kind)) { Fail "invalid installation state VERSION row" }
                $seen[$kind] = $true
                $state.Version = $parts[1]
            }
            "COMMIT" {
                if ($parts.Count -ne 2 -or $seen.ContainsKey($kind)) { Fail "invalid installation state COMMIT row" }
                $seen[$kind] = $true
                $state.Commit = $parts[1]
            }
            "MANIFEST" {
                if ($parts.Count -ne 2 -or $seen.ContainsKey($kind)) { Fail "invalid installation state MANIFEST row" }
                $seen[$kind] = $true
                $state.Manifest = $parts[1]
            }
            "FILE" {
                if ($parts.Count -ne 4) { Fail "invalid installation state FILE row" }
                Assert-RelativePath $parts[1]
                if ($state.Files.Contains($parts[1])) { Fail "duplicate installation state file '$($parts[1])'" }
                if ($parts[2] -notmatch '^[0-9a-f]{64}$' -or $parts[3] -notmatch '^[01]$') {
                    Fail "invalid installation state metadata for '$($parts[1])'"
                }
                $state.Files[$parts[1]] = $parts[2]
                $state.Customized[$parts[1]] = ($parts[3] -eq "1")
            }
            default { Fail "unknown installation state row '$kind'" }
        }
    }
    if ($state.Format -ne $StateFormat -or
        $state.Version -notmatch '^[A-Za-z0-9._-]+$' -or
        $state.Commit -notmatch '^[0-9a-f]{40}$' -or
        $state.Manifest -notmatch '^[0-9a-f]{64}$' -or
        $state.Files.Count -eq 0) {
        Fail "installation state is incompatible or incomplete"
    }
    return $state
}

function Get-DestinationPath([string]$Root, [string]$RelativePath) {
    Assert-RelativePath $RelativePath
    return Join-Path $Root ($RelativePath.Replace("/", "\"))
}

function Assert-SafeDestinationPath([string]$Root, [string]$RelativePath) {
    Assert-RelativePath $RelativePath
    $current = $Root
    $rootItem = Get-Item -LiteralPath $current -Force -ErrorAction SilentlyContinue
    if ($null -ne $rootItem -and
        ($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        Fail "destination root must not be a symbolic link or reparse point: '$Root'"
    }
    $parts = $RelativePath.Split([char]'/')
    foreach ($part in $parts) {
        $current = Join-Path $current $part
        $item = Get-Item -LiteralPath $current -Force -ErrorAction SilentlyContinue
        if ($null -ne $item) {
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                Fail "destination path contains a symbolic link or reparse point: $RelativePath"
            }
        }
    }
}

function Assert-GeneratedPathSafety([string]$Root) {
    $statePath = Join-Path $Root $StateName
    $stateItem = Get-Item -LiteralPath $statePath -Force -ErrorAction SilentlyContinue
    if ($null -ne $stateItem) {
        if (($stateItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
            -not (Test-Path -LiteralPath $statePath -PathType Leaf)) {
            Fail "generated installation state path must be a regular file: '$statePath'"
        }
    }

    $backupRoot = Join-Path $Root ".looppilot-backups"
    $backupItem = Get-Item -LiteralPath $backupRoot -Force -ErrorAction SilentlyContinue
    if ($null -ne $backupItem) {
        if (($backupItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
            -not (Test-Path -LiteralPath $backupRoot -PathType Container)) {
            Fail "generated backup path must be a regular directory: '$backupRoot'"
        }
    }
}

function New-BackupId {
    return (Get-Date -Format "yyyyMMdd-HHmmssfff") + "-$PID-" + [guid]::NewGuid().ToString("N").Substring(0, 8)
}

function Backup-File([string]$Root, [string]$RelativePath, [string]$BackupId) {
    $source = Get-DestinationPath $Root $RelativePath
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { return }
    $backupRoot = Join-Path $Root (".looppilot-backups\" + $BackupId)
    $backup = Get-DestinationPath $backupRoot $RelativePath
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backup) | Out-Null
    Copy-Item -LiteralPath $source -Destination $backup
}

function Copy-SourceFile([string]$DestinationRoot, [string]$RelativePath) {
    $source = Join-Path $SourceRoot ($RelativePath.Replace("/", "\"))
    $destinationPath = Get-DestinationPath $DestinationRoot $RelativePath
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destinationPath) | Out-Null
    Copy-Item -LiteralPath $source -Destination $destinationPath -Force
}

function Write-State(
    [string]$DestinationRoot,
    [string]$Version,
    [string]$Commit,
    [string]$ManifestHash,
    [string[]]$Entries,
    [System.Collections.IDictionary]$Customized
) {
    $lines = @(
        "FORMAT|$StateFormat",
        "VERSION|$Version",
        "COMMIT|$Commit",
        "MANIFEST|$ManifestHash"
    )
    foreach ($entry in $Entries) {
        $path = Get-DestinationPath $DestinationRoot $entry
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            Fail "managed file is missing while writing state: $entry"
        }
        $flag = if ($Customized.Contains($entry) -and $Customized[$entry]) { "1" } else { "0" }
        $lines += "FILE|$entry|$(Get-Hash $path)|$flag"
    }
    $statePath = Join-Path $DestinationRoot $StateName
    $temporaryPath = "$statePath.tmp.$PID.$([guid]::NewGuid().ToString('N'))"
    try {
        [IO.File]::WriteAllLines($temporaryPath, $lines, [Text.Encoding]::ASCII)
        Move-Item -LiteralPath $temporaryPath -Destination $statePath -Force
    } finally {
        if (Test-Path -LiteralPath $temporaryPath) {
            Remove-Item -LiteralPath $temporaryPath -Force
        }
    }
}

function Get-SourceHashes([string[]]$Entries) {
    $hashes = @{}
    foreach ($entry in $Entries) {
        $hashes[$entry] = Get-Hash (Join-Path $SourceRoot ($entry.Replace("/", "\")))
    }
    return $hashes
}

function Assert-DestinationPreflight([string]$DestinationRoot, [string[]]$Entries) {
    foreach ($entry in $Entries) {
        Assert-SafeDestinationPath $DestinationRoot $entry
        $path = Get-DestinationPath $DestinationRoot $entry
        if ((Test-Path -LiteralPath $path) -and -not (Test-Path -LiteralPath $path -PathType Leaf)) {
            Fail "managed path is not a regular file: $entry"
        }
    }
}

function Show-Installed([string]$DestinationRoot, [string]$Version, [string]$Commit, [string]$Action, [int]$Preserved) {
    Write-Host "LoopPilot $Action complete"
    Write-Host "Destination: $DestinationRoot"
    Write-Host "Installed version: $Version"
    Write-Host "Installed commit: $Commit"
    if ($Preserved -gt 0) {
        Write-Warning "$Preserved local file(s) preserved; review .looppilot-backups before using -Force"
    }
}

function Invoke-Install {
    $destinationRoot = Get-InstallDestination $Destination
    Assert-GeneratedPathSafety $destinationRoot
    $entries = Get-ManifestEntries
    $version = Get-SourceVersion
    $commit = Get-SourceCommit
    $manifestHash = Get-Hash $ManifestPath
    $sourceHashes = Get-SourceHashes $entries
    Assert-DestinationPreflight $destinationRoot $entries

    $statePath = Join-Path $destinationRoot $StateName
    $existingState = Get-State $statePath
    if ($null -ne $existingState) {
        $same = $existingState.Version -eq $version -and
            $existingState.Commit -eq $commit -and
            $existingState.Manifest -eq $manifestHash -and
            $existingState.Files.Count -eq $entries.Count
        foreach ($entry in $entries) {
            $path = Get-DestinationPath $destinationRoot $entry
            if (-not $existingState.Files.Contains($entry) -or
                -not (Test-Path -LiteralPath $path -PathType Leaf) -or
                (Get-Hash $path) -ne $sourceHashes[$entry]) {
                $same = $false
            }
        }
        if ($same) {
            Show-Installed $destinationRoot $version $commit "reinstall (no changes)" 0
            return
        }
        if (-not $Force) {
            Fail "an installation already exists and differs from this source; use update.ps1 or pass -Force"
        }
        Invoke-Update
        return
    }

    $conflicts = New-Object System.Collections.Generic.List[string]
    foreach ($entry in $entries) {
        $path = Get-DestinationPath $destinationRoot $entry
        if ((Test-Path -LiteralPath $path -PathType Leaf) -and (Get-Hash $path) -ne $sourceHashes[$entry]) {
            $conflicts.Add($entry)
        }
    }
    if ($conflicts.Count -gt 0 -and -not $Force) {
        Fail "destination contains $($conflicts.Count) conflicting file(s), including '$($conflicts[0])'; no files were copied or overwritten"
    }

    New-Item -ItemType Directory -Force -Path $destinationRoot | Out-Null
    $backupId = New-BackupId
    foreach ($entry in $entries) {
        $path = Get-DestinationPath $destinationRoot $entry
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            if ((Get-Hash $path) -eq $sourceHashes[$entry]) { continue }
            Backup-File $destinationRoot $entry $backupId
        }
        Copy-SourceFile $destinationRoot $entry
    }
    Write-State $destinationRoot $version $commit $manifestHash $entries ([ordered]@{})
    Show-Installed $destinationRoot $version $commit "install" 0
}

function Invoke-Update {
    $destinationRoot = Get-InstallDestination $Destination
    Assert-GeneratedPathSafety $destinationRoot
    $statePath = Join-Path $destinationRoot $StateName
    $state = Get-State $statePath
    if ($null -eq $state) { Fail "no compatible LoopPilot installation found at '$destinationRoot'" }

    $entries = Get-ManifestEntries
    $version = Get-SourceVersion
    $commit = Get-SourceCommit
    $manifestHash = Get-Hash $ManifestPath
    $sourceHashes = Get-SourceHashes $entries
    $allPaths = @($entries + @($state.Files.Keys) | Sort-Object -Unique)
    Assert-DestinationPreflight $destinationRoot $allPaths

    $newEntrySet = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($entry in $entries) { [void]$newEntrySet.Add($entry) }
    $customized = [ordered]@{}
    $preserved = 0
    $backupId = New-BackupId

    foreach ($entry in @($state.Files.Keys)) {
        if ($newEntrySet.Contains($entry)) { continue }
        $path = Get-DestinationPath $destinationRoot $entry
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { continue }
        Backup-File $destinationRoot $entry $backupId
        if ($state.Customized[$entry] -or (Get-Hash $path) -ne $state.Files[$entry]) {
            $preserved++
            Write-Warning "preserved retired customized file as user-owned content: $entry"
            continue
        }
        Remove-Item -LiteralPath $path -Force
    }

    foreach ($entry in $entries) {
        $destinationPath = Get-DestinationPath $destinationRoot $entry
        if (-not (Test-Path -LiteralPath $destinationPath -PathType Leaf)) {
            Copy-SourceFile $destinationRoot $entry
            continue
        }
        $currentHash = Get-Hash $destinationPath
        if ($currentHash -eq $sourceHashes[$entry]) { continue }

        $wasManaged = $state.Files.Contains($entry)
        $wasCustomized = $wasManaged -and $state.Customized[$entry]
        $matchesBaseline = $wasManaged -and $currentHash -eq $state.Files[$entry]
        if ($Force -or ((-not $wasCustomized) -and $matchesBaseline)) {
            Backup-File $destinationRoot $entry $backupId
            Copy-SourceFile $destinationRoot $entry
            continue
        }

        Backup-File $destinationRoot $entry $backupId
        $customized[$entry] = $true
        $preserved++
        Write-Warning "preserved customized managed file: $entry"
    }

    Write-State $destinationRoot $version $commit $manifestHash $entries $customized
    Show-Installed $destinationRoot $version $commit "update" $preserved
}

function Invoke-Uninstall {
    $destinationRoot = Get-InstallDestination $Destination
    Assert-GeneratedPathSafety $destinationRoot
    $statePath = Join-Path $destinationRoot $StateName
    $state = Get-State $statePath
    if ($null -eq $state) { Fail "no compatible LoopPilot installation found at '$destinationRoot'" }
    Assert-DestinationPreflight $destinationRoot @($state.Files.Keys)

    $preserved = 0
    foreach ($entry in @($state.Files.Keys)) {
        $path = Get-DestinationPath $destinationRoot $entry
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { continue }
        if ($state.Customized[$entry] -or (Get-Hash $path) -ne $state.Files[$entry]) {
            $preserved++
            Write-Warning "preserved modified managed file as user-owned content: $entry"
            continue
        }
        Remove-Item -LiteralPath $path -Force
    }
    Remove-Item -LiteralPath $statePath -Force
    Write-Host "LoopPilot uninstall complete"
    Write-Host "Destination: $destinationRoot"
    Write-Host "Removed files from version: $($state.Version)"
    Write-Host "Installed commit: $($state.Commit)"
    if ($preserved -gt 0) {
        Write-Warning "$preserved modified managed file(s) were preserved as user-owned content"
    }
}

switch ($Operation) {
    "install" { Invoke-Install }
    "update" { Invoke-Update }
    "uninstall" { Invoke-Uninstall }
}
