[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet("install", "update", "uninstall", "status")]
    [string]$Operation,
    [string]$Destination,
    [switch]$Force,
    [ValidateSet("release", "archive")]
    [string]$SourceMode = "release",
    [string]$ArchiveSha256
)

$ErrorActionPreference = "Stop"
$SourceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ManifestPath = Join-Path $SourceRoot "distribution\managed-files.txt"
$VersionPath = Join-Path $SourceRoot "distribution\version.txt"
$StateName = ".looppilot-installation"
$JournalName = ".looppilot-transaction"
$StateFormat = "2"
$LegacyStateFormats = @("1")
$UnknownHash = "-"
$OriginalSourceRoot = $SourceRoot
$SnapshotRoot = $null
$SnapshotParent = $null
$PinnedCommit = $null
$SnapshotDigest = $null
$ProvenanceMode = $null

function Fail([string]$Message) {
    throw "LoopPilot distribution: $Message"
}

function Trim-PathSeparators([string]$Path) {
    return $Path.TrimEnd([char[]]@(
        [IO.Path]::DirectorySeparatorChar,
        [IO.Path]::AltDirectorySeparatorChar
    ))
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
    if ([string]::IsNullOrWhiteSpace($script:PinnedCommit)) { Fail "source identity has not been prepared" }
    return $script:PinnedCommit
}

function Get-PayloadDigest([string]$Root, [string[]]$Entries) {
    $ordered = [string[]]@($Entries)
    [Array]::Sort($ordered, [StringComparer]::Ordinal)
    $rows = foreach ($entry in $ordered) { "$entry|$(Get-Hash (Join-Path $Root $entry))" }
    $bytes = [Text.Encoding]::UTF8.GetBytes(($rows -join "`n") + "`n")
    $hash = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($hash.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant() }
    finally { $hash.Dispose() }
}

function Prepare-Source {
    if ($SourceMode -eq "release") {
        if ($ArchiveSha256) { Fail "archive digest is not valid in release mode" }
        if ($null -eq (Get-GitRoot)) { Fail "Git source identity unavailable; release install refused" }
        # Refuse existing refs; every Git read also ignores replacements added later.
        $replacementBases = @("refs/replace/")
        if ($env:GIT_REPLACE_REF_BASE) { $replacementBases += $env:GIT_REPLACE_REF_BASE }
        $replacements = @(& git --no-replace-objects -C $OriginalSourceRoot for-each-ref '--format=%(refname)' -- @replacementBases)
        if ($LASTEXITCODE -ne 0) { Fail "cannot inspect Git replacement refs" }
        if ($replacements.Count -gt 0) { Fail "Git replacement refs present; release install refused" }
        $script:PinnedCommit = (& git --no-replace-objects -C $OriginalSourceRoot rev-parse --verify 'HEAD^{commit}')
        if ($LASTEXITCODE -ne 0 -or $script:PinnedCommit -notmatch '^[0-9a-f]{40}$') { Fail "Git commit identity cannot be resolved; release install refused" }
        & git --no-replace-objects -C $OriginalSourceRoot cat-file -e "$($script:PinnedCommit)^{commit}"
        if ($LASTEXITCODE -ne 0) { Fail "Git commit object unavailable; release install refused" }
        $dirty = @(& git --no-replace-objects -C $OriginalSourceRoot status --porcelain=v1 --untracked-files=all)
        if ($LASTEXITCODE -ne 0) { Fail "cannot inspect Git source status" }
        if ($dirty.Count -gt 0) { Fail "dirty Git source refused; install requires a clean source checkout" }
        $script:ProvenanceMode = "git-release"
    } else {
        if ((Test-Path -LiteralPath (Join-Path $OriginalSourceRoot ".git")) -or $null -ne (Get-GitRoot)) {
            Fail "archive mode cannot replace Git source identity"
        }
        if ($ArchiveSha256 -cnotmatch '^[0-9a-f]{64}$') { Fail "explicit archive mode requires -ArchiveSha256" }
        $script:ProvenanceMode = "archive"
    }
    $script:SnapshotParent = Trim-PathSeparators ([IO.Path]::GetFullPath([IO.Path]::GetTempPath()))
    $script:SnapshotRoot = Join-Path $SnapshotParent ("looppilot-source-" + [guid]::NewGuid().ToString("N"))
    $sourcePrefix = (Trim-PathSeparators ([IO.Path]::GetFullPath($OriginalSourceRoot))) + [IO.Path]::DirectorySeparatorChar
    if ($SnapshotRoot.StartsWith($sourcePrefix, [StringComparison]::OrdinalIgnoreCase)) { Fail "snapshot must be outside source root" }
    $payload = Join-Path $SnapshotRoot "payload"
    New-Item -ItemType Directory -Path $payload -Force | Out-Null
    if ($SourceMode -eq "release") {
        $tree = @(& git --no-replace-objects -C $OriginalSourceRoot -c core.quotepath=false ls-tree -r $PinnedCommit)
        if ($LASTEXITCODE -ne 0) { Fail "cannot read pinned tree" }
        $expected = [System.Collections.Generic.Dictionary[string,string]]::new([StringComparer]::Ordinal)
        foreach ($row in $tree) {
            $fields = $row -split "`t", 2
            if ($fields.Count -ne 2 -or $fields[0] -notmatch '^(100644|100755) blob ([0-9a-f]{40})$') { Fail "unsupported snapshot entry" }
            $blob = $Matches[2]
            Assert-RelativePath $fields[1]
            $expected[$fields[1]] = $blob
            $workingPath = Join-Path $OriginalSourceRoot $fields[1]
            if (-not (Test-Path -LiteralPath $workingPath -PathType Leaf) -or
                ((Get-Item -LiteralPath $workingPath -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                Fail "dirty Git source: missing or indirect tracked file $($fields[1])"
            }
            $workingHash = (& git --no-replace-objects -C $OriginalSourceRoot hash-object "--path=$($fields[1])" $workingPath)
            if ($LASTEXITCODE -ne 0 -or $workingHash -ne $blob) { Fail "dirty Git source content differs from pinned commit: $($fields[1])" }
        }
        $archive = Join-Path $SnapshotRoot "source.zip"
        & git --no-replace-objects -C $OriginalSourceRoot archive --format=zip "--output=$archive" $PinnedCommit
        if ($LASTEXITCODE -ne 0) { Fail "cannot export pinned commit" }
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [IO.Compression.ZipFile]::ExtractToDirectory($archive, $payload)
        foreach ($item in Get-ChildItem -LiteralPath $payload -Recurse -Force -ErrorAction Stop) {
            $relative = $item.FullName.Substring($payload.Length + 1).Replace('\', '/')
            Assert-RelativePath $relative
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
                (-not $item.PSIsContainer -and -not $expected.ContainsKey($relative))) {
                Fail "unexpected snapshot file: $relative"
            }
        }
        foreach ($entry in $expected.Keys) {
            $path = Join-Path $payload $entry
            if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { Fail "snapshot is missing a regular committed file: $entry" }
            if (((Get-Item -LiteralPath $path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { Fail "indirect snapshot path" }
            $actual = (& git --no-replace-objects -C $OriginalSourceRoot hash-object --no-filters $path)
            if ($LASTEXITCODE -ne 0 -or $actual -ne $expected[$entry]) { Fail "snapshot content does not match pinned commit: $entry" }
        }
    } else {
        $inputs = @(@(Get-ManifestEntries) + @("distribution/managed-files.txt", "distribution/version.txt", "distribution/commit.txt") | Sort-Object -Unique)
        foreach ($entry in $inputs) {
            Assert-SourceFile $entry
            $target = Join-Path $payload $entry
            New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
            Copy-Item -LiteralPath (Join-Path $OriginalSourceRoot $entry) -Destination $target
        }
    }
    $script:SourceRoot = $payload
    $script:ManifestPath = Join-Path $payload "distribution/managed-files.txt"
    $script:VersionPath = Join-Path $payload "distribution/version.txt"
    $marker = Join-Path $payload "distribution/commit.txt"
    if ($SourceMode -eq "archive") {
        $script:PinnedCommit = (Get-Content -Raw -LiteralPath $marker).Trim()
        if ($PinnedCommit -cnotmatch '^[0-9a-f]{40}$') { Fail "invalid publisher archive commit" }
    } elseif ((Test-Path -LiteralPath $marker) -and (Get-Content -Raw -LiteralPath $marker).Trim() -ne $PinnedCommit) {
        Fail "source identity conflicts with snapshot commit.txt"
    }
    $null = Get-SourceVersion
    $entries = Get-ManifestEntries
    $script:SnapshotDigest = Get-PayloadDigest $payload $entries
    if ($SourceMode -eq "archive" -and $SnapshotDigest -cne $ArchiveSha256) { Fail "archive snapshot digest mismatch" }
    Get-ChildItem -LiteralPath $payload -Recurse -File -Force | ForEach-Object { $_.IsReadOnly = $true }
    Write-Output "Install mode: $ProvenanceMode"
    Write-Output "Source snapshot SHA-256: $SnapshotDigest"
    Write-Output "Source validation: passed"
    if ($SourceMode -eq "release") { Write-Output "Source clean determination: preflight passed (not a live worktree claim)" }
    if ($SourceMode -eq "archive") { Write-Output "Archive commit is publisher-declared, not verified Git provenance" }
}

function Remove-SourceSnapshot {
    if ($null -eq $SnapshotRoot -or -not (Test-Path -LiteralPath $SnapshotRoot)) { return }
    $resolved = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $SnapshotRoot).Path)
    $parent = (Trim-PathSeparators ([IO.Path]::GetFullPath($SnapshotParent))) + [IO.Path]::DirectorySeparatorChar
    if (-not $resolved.StartsWith($parent, [StringComparison]::OrdinalIgnoreCase) -or
        (Split-Path -Leaf $resolved) -notmatch '^looppilot-source-[0-9a-f]{32}$' -or
        ((Get-Item -LiteralPath $resolved -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        Fail "refused unsafe snapshot cleanup path"
    }
    Remove-Item -LiteralPath $resolved -Recurse -Force
}

function Get-GitRoot {
    try {
        $root = (& git --no-replace-objects -C $SourceRoot rev-parse --show-toplevel 2>$null)
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
                $files = @(& git --no-replace-objects -C $SourceRoot ls-files -- "$trimmed/")
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
        ProvenanceMode = "legacy-unverified"
        SnapshotDigest = $null
        InstalledDigest = $null
        Files = [ordered]@{}
        Customized = [ordered]@{}
        Base = [ordered]@{}
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
            "PROVENANCE" {
                if ($parts.Count -ne 4 -or $seen.ContainsKey($kind) -or $parts[1] -notin @("git-release", "archive") -or
                    $parts[2] -cnotmatch '^[0-9a-f]{64}$' -or $parts[3] -cnotmatch '^[0-9a-f]{64}$') { Fail "invalid installation state PROVENANCE row" }
                $seen[$kind] = $true
                $state.ProvenanceMode = $parts[1]
                $state.SnapshotDigest = $parts[2]
                $state.InstalledDigest = $parts[3]
            }
            "FILE" {
                # Format 1 rows carry four fields; format 2 adds the baseline hash.
                if ($parts.Count -ne 4 -and $parts.Count -ne 5) { Fail "invalid installation state FILE row" }
                Assert-RelativePath $parts[1]
                if ($state.Files.Contains($parts[1])) { Fail "duplicate installation state file '$($parts[1])'" }
                if ($parts[2] -notmatch '^[0-9a-f]{64}$' -or $parts[3] -notmatch '^[01]$') {
                    Fail "invalid installation state metadata for '$($parts[1])'"
                }
                $customized = ($parts[3] -eq "1")
                if ($parts.Count -eq 5) {
                    if ($parts[4] -ne $UnknownHash -and $parts[4] -notmatch '^[0-9a-f]{64}$') {
                        Fail "invalid installation state baseline for '$($parts[1])'"
                    }
                    $baseline = $parts[4]
                } elseif ($customized) {
                    # A format 1 customized row recorded the local hash and lost its
                    # baseline, so the upstream content it came from is unknown.
                    $baseline = $UnknownHash
                } else {
                    $baseline = $parts[2]
                }
                $state.Files[$parts[1]] = $parts[2]
                $state.Customized[$parts[1]] = $customized
                $state.Base[$parts[1]] = $baseline
            }
            default { Fail "unknown installation state row '$kind'" }
        }
    }
    $known = @($StateFormat) + $LegacyStateFormats
    if ($known -notcontains $state.Format -or
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

    $journalPath = Join-Path $Root $JournalName
    $journalItem = Get-Item -LiteralPath $journalPath -Force -ErrorAction SilentlyContinue
    if ($null -ne $journalItem) {
        if (($journalItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
            -not (Test-Path -LiteralPath $journalPath -PathType Leaf)) {
            Fail "generated transaction path must be a regular file: '$journalPath'"
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

function Copy-SourceFile([string]$DestinationRoot, [string]$RelativePath, [string]$ExpectedHash) {
    $source = Join-Path $SourceRoot ($RelativePath.Replace("/", "\"))
    $destinationPath = Get-DestinationPath $DestinationRoot $RelativePath
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destinationPath) | Out-Null
    Copy-Item -LiteralPath $source -Destination $destinationPath -Force
    (Get-Item -LiteralPath $destinationPath -Force).IsReadOnly = $false
    if ((Get-Hash $destinationPath) -ne $ExpectedHash) { Fail "source changed during copy: $RelativePath" }
}

function Write-State(
    [string]$DestinationRoot,
    [string]$Version,
    [string]$Commit,
    [string]$ManifestHash,
    [string[]]$Entries,
    [System.Collections.IDictionary]$Customized,
    [System.Collections.IDictionary]$Baseline
) {
    $lines = @(
        "FORMAT|$StateFormat",
        "VERSION|$Version",
        "COMMIT|$Commit",
        "MANIFEST|$ManifestHash"
        "PROVENANCE|$ProvenanceMode|$SnapshotDigest|$(Get-PayloadDigest $DestinationRoot $Entries)"
    )
    foreach ($entry in $Entries) {
        $path = Get-DestinationPath $DestinationRoot $entry
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            Fail "managed file is missing while writing state: $entry"
        }
        $flag = if ($Customized.Contains($entry) -and $Customized[$entry]) { "1" } else { "0" }
        $base = if ($null -ne $Baseline -and $Baseline.Contains($entry)) { $Baseline[$entry] } else { $UnknownHash }
        $lines += "FILE|$entry|$(Get-Hash $path)|$flag|$base"
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

function Get-JournalPath([string]$Root) {
    return Join-Path $Root $JournalName
}

function Start-Journal([string]$Root, [string]$BackupId, [string]$Version, [string]$Commit, [string]$ManifestHash) {
    $path = Get-JournalPath $Root
    [IO.File]::WriteAllLines($path, @("BEGIN|$BackupId|$Version|$Commit|$ManifestHash"), [Text.Encoding]::ASCII)
}

function Add-JournalEntry([string]$Root, [string]$Action, [string]$RelativePath) {
    # Recorded before the action so an interruption always leaves a recoverable trace.
    $path = Get-JournalPath $Root
    [IO.File]::AppendAllText($path, "$Action|$RelativePath`n", [Text.Encoding]::ASCII)
}

function Complete-Journal([string]$Root) {
    $path = Get-JournalPath $Root
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        Remove-Item -LiteralPath $path -Force
    }
}

function Read-Journal([string]$Root) {
    $path = Get-JournalPath $Root
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return $null }
    $records = New-Object System.Collections.Generic.List[object]
    $backupId = $null
    foreach ($line in Get-Content -LiteralPath $path) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $parts = @($line.Split([char]'|'))
        if ($parts[0] -eq "BEGIN") {
            if ($parts.Count -ne 5) { Fail "invalid interrupted-update journal BEGIN row" }
            $backupId = $parts[1]
            continue
        }
        if ($parts.Count -ne 2 -or @("REPLACE", "CREATE", "DELETE") -notcontains $parts[0]) {
            Fail "invalid interrupted-update journal row"
        }
        Assert-RelativePath $parts[1]
        $records.Add([pscustomobject]@{ Action = $parts[0]; Path = $parts[1] })
    }
    if ([string]::IsNullOrWhiteSpace($backupId)) { Fail "interrupted-update journal has no BEGIN row" }
    return [pscustomobject]@{ BackupId = $backupId; Records = $records }
}

function Restore-Journal([string]$Root) {
    # Roll the destination back to the pre-update content, newest action first.
    $journal = Read-Journal $Root
    if ($null -eq $journal) { return 0 }
    $backupRoot = Join-Path $Root (".looppilot-backups\" + $journal.BackupId)
    $restored = 0
    for ($index = $journal.Records.Count - 1; $index -ge 0; $index--) {
        $record = $journal.Records[$index]
        $target = Get-DestinationPath $Root $record.Path
        if ($record.Action -eq "CREATE") {
            if (Test-Path -LiteralPath $target -PathType Leaf) {
                Remove-Item -LiteralPath $target -Force
                $restored++
            }
            continue
        }
        $backup = Get-DestinationPath $backupRoot $record.Path
        if (Test-Path -LiteralPath $backup -PathType Leaf) {
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
            Copy-Item -LiteralPath $backup -Destination $target -Force
            $restored++
        }
    }
    Complete-Journal $Root
    return $restored
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

function Compare-Installation(
    [string]$DestinationRoot,
    [string[]]$Entries,
    [System.Collections.IDictionary]$SourceHashes,
    $State
) {
    <#
        Three-way comparison for every managed path.

            BASE   = content recorded at the previous successful installation
            LOCAL  = content currently on disk
            REMOTE = content in the source repository

        Classification is deliberately conservative: whenever BASE is unknown and
        LOCAL differs from REMOTE, the file is a conflict rather than an
        overwrite candidate.
    #>
    $plan = [ordered]@{
        Current = New-Object System.Collections.Generic.List[string]
        Update = New-Object System.Collections.Generic.List[string]
        Local = New-Object System.Collections.Generic.List[string]
        Conflict = New-Object System.Collections.Generic.List[string]
        Add = New-Object System.Collections.Generic.List[string]
        Remove = New-Object System.Collections.Generic.List[string]
        RemovePreserve = New-Object System.Collections.Generic.List[string]
    }

    $remoteSet = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($entry in $Entries) { [void]$remoteSet.Add($entry) }
    $baseKeys = if ($null -ne $State) { @($State.Files.Keys) } else { @() }
    $all = @(@($Entries) + @($baseKeys) | Sort-Object -Unique)

    foreach ($entry in $all) {
        $path = Get-DestinationPath $DestinationRoot $entry
        $localExists = Test-Path -LiteralPath $path -PathType Leaf
        $local = if ($localExists) { Get-Hash $path } else { $null }
        $baseKnown = $null -ne $State -and $State.Files.Contains($entry)
        $base = if ($baseKnown) { $State.Base[$entry] } else { $null }
        if ($base -eq $UnknownHash) { $base = $null }
        $remote = if ($remoteSet.Contains($entry)) { $SourceHashes[$entry] } else { $null }

        if ($null -eq $remote) {
            # Retired from the manifest.
            if (-not $localExists) { continue }
            if ($null -ne $base -and $local -eq $base) {
                $plan.Remove.Add($entry)
            } else {
                $plan.RemovePreserve.Add($entry)
            }
            continue
        }

        if (-not $localExists) {
            if ($baseKnown) { $plan.Update.Add($entry) } else { $plan.Add.Add($entry) }
            continue
        }

        if ($local -eq $remote) {
            # Already converged, whatever the baseline says.
            $plan.Current.Add($entry)
            continue
        }

        if (-not $baseKnown) {
            # A newly managed path colliding with pre-existing user content.
            $plan.Conflict.Add($entry)
            continue
        }

        if ($null -eq $base) {
            # Baseline lost by a legacy format 1 state; cannot prove safety.
            $plan.Conflict.Add($entry)
            continue
        }

        $localChanged = $local -ne $base
        $remoteChanged = $remote -ne $base
        if (-not $localChanged -and $remoteChanged) {
            $plan.Update.Add($entry)
        } elseif ($localChanged -and -not $remoteChanged) {
            $plan.Local.Add($entry)
        } elseif ($localChanged -and $remoteChanged) {
            $plan.Conflict.Add($entry)
        } else {
            $plan.Current.Add($entry)
        }
    }
    return $plan
}

function Get-SynchronizationState($Plan, [bool]$MetadataChanged, [bool]$RecoveryRequired) {
    if ($RecoveryRequired) { return "RECOVERY_REQUIRED" }
    if ($Plan.Conflict.Count -gt 0) { return "CONFLICT" }
    if ($Plan.Update.Count -gt 0 -or $Plan.Add.Count -gt 0 -or $Plan.Remove.Count -gt 0 -or $MetadataChanged) {
        return "UPDATE_AVAILABLE"
    }
    if ($Plan.Local.Count -gt 0 -or $Plan.RemovePreserve.Count -gt 0) { return "LOCAL_MODIFICATIONS" }
    return "CURRENT"
}

function Show-Installed([string]$DestinationRoot, [string]$Version, [string]$Commit, [string]$Action, [int]$Preserved) {
    Write-Host "LoopPilot $Action complete"
    Write-Host "Destination: $DestinationRoot"
    Write-Host "Installed version: $Version"
    Write-Host "Installed commit: $Commit"
    $receipt = Get-State (Join-Path $DestinationRoot $StateName)
    Write-Host "Installed source mode: $($receipt.ProvenanceMode)"
    Write-Host "Installed SHA-256: $($receipt.InstalledDigest)"
    if ($Preserved -gt 0) {
        Write-Warning "$Preserved local file(s) preserved; review .looppilot-backups before using -Force"
    }
}

function Invoke-Install {
    $destinationRoot = Get-InstallDestination $Destination
    Assert-GeneratedPathSafety $destinationRoot
    $commit = Get-SourceCommit
    $entries = Get-ManifestEntries
    $version = Get-SourceVersion
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
    $baseline = [ordered]@{}
    foreach ($entry in $entries) {
        $path = Get-DestinationPath $destinationRoot $entry
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            if ((Get-Hash $path) -eq $sourceHashes[$entry]) {
                $baseline[$entry] = $sourceHashes[$entry]
                continue
            }
            Backup-File $destinationRoot $entry $backupId
        }
        Copy-SourceFile $destinationRoot $entry $sourceHashes[$entry]
        $baseline[$entry] = $sourceHashes[$entry]
    }
    Write-State $destinationRoot $version $commit $manifestHash $entries ([ordered]@{}) $baseline
    Show-Installed $destinationRoot $version $commit "install" 0
}

function Invoke-Update {
    $destinationRoot = Get-InstallDestination $Destination
    Assert-GeneratedPathSafety $destinationRoot

    # Reject a dirty source before even recovering an interrupted destination.
    $commit = Get-SourceCommit
    # An interrupted update is rolled back first so every update starts from a
    # known-good baseline and retrying is deterministic.
    $recovered = Restore-Journal $destinationRoot
    if ($recovered -gt 0) {
        Write-Warning "recovered $recovered file(s) from an interrupted update before continuing"
    }

    $statePath = Join-Path $destinationRoot $StateName
    $state = Get-State $statePath
    if ($null -eq $state) { Fail "no compatible LoopPilot installation found at '$destinationRoot'" }

    $entries = Get-ManifestEntries
    $version = Get-SourceVersion
    $commit = Get-SourceCommit
    $manifestHash = Get-Hash $ManifestPath
    $sourceHashes = Get-SourceHashes $entries
    $allPaths = @(@($entries) + @($state.Files.Keys) | Sort-Object -Unique)
    Assert-DestinationPreflight $destinationRoot $allPaths

    $plan = Compare-Installation $destinationRoot $entries $sourceHashes $state
    if ($plan.Conflict.Count -gt 0 -and -not $Force) {
        $names = @($plan.Conflict) -join ", "
        Fail "update stopped: $($plan.Conflict.Count) conflicting file(s) changed both locally and upstream ($names); resolve them or pass -Force. No managed file was changed."
    }

    $customized = [ordered]@{}
    $baseline = [ordered]@{}
    $preserved = 0
    $backupId = New-BackupId
    Start-Journal $destinationRoot $backupId $version $commit $manifestHash

    try {
        foreach ($entry in $plan.Remove) {
            Add-JournalEntry $destinationRoot "DELETE" $entry
            Backup-File $destinationRoot $entry $backupId
            Remove-Item -LiteralPath (Get-DestinationPath $destinationRoot $entry) -Force
        }
        foreach ($entry in $plan.RemovePreserve) {
            Backup-File $destinationRoot $entry $backupId
            $preserved++
            Write-Warning "preserved retired customized file as user-owned content: $entry"
        }
        foreach ($entry in $plan.Add) {
            Add-JournalEntry $destinationRoot "CREATE" $entry
            Copy-SourceFile $destinationRoot $entry $sourceHashes[$entry]
            $baseline[$entry] = $sourceHashes[$entry]
        }
        foreach ($entry in $plan.Update) {
            $path = Get-DestinationPath $destinationRoot $entry
            if (Test-Path -LiteralPath $path -PathType Leaf) {
                Add-JournalEntry $destinationRoot "REPLACE" $entry
                Backup-File $destinationRoot $entry $backupId
            } else {
                Add-JournalEntry $destinationRoot "CREATE" $entry
            }
            Copy-SourceFile $destinationRoot $entry $sourceHashes[$entry]
            $baseline[$entry] = $sourceHashes[$entry]
        }
        foreach ($entry in $plan.Current) {
            $baseline[$entry] = $sourceHashes[$entry]
        }
        foreach ($entry in $plan.Local) {
            Backup-File $destinationRoot $entry $backupId
            $customized[$entry] = $true
            # REMOTE still equals BASE here, so the baseline is retained exactly.
            $baseline[$entry] = $sourceHashes[$entry]
            $preserved++
            Write-Warning "preserved customized managed file: $entry"
        }
        foreach ($entry in $plan.Conflict) {
            if ($Force) {
                $path = Get-DestinationPath $destinationRoot $entry
                if (Test-Path -LiteralPath $path -PathType Leaf) {
                    Add-JournalEntry $destinationRoot "REPLACE" $entry
                    Backup-File $destinationRoot $entry $backupId
                } else {
                    Add-JournalEntry $destinationRoot "CREATE" $entry
                }
                Copy-SourceFile $destinationRoot $entry $sourceHashes[$entry]
                $baseline[$entry] = $sourceHashes[$entry]
                continue
            }
            Backup-File $destinationRoot $entry $backupId
            $customized[$entry] = $true
            $baseline[$entry] = $sourceHashes[$entry]
            $preserved++
            Write-Warning "preserved conflicting managed file: $entry"
        }

        # Verify before the transaction is marked complete.
        foreach ($entry in $entries) {
            $path = Get-DestinationPath $destinationRoot $entry
            if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
                Fail "managed file is missing after update: $entry"
            }
            $expectCustomized = $customized.Contains($entry) -and $customized[$entry]
            if (-not $expectCustomized -and (Get-Hash $path) -ne $sourceHashes[$entry]) {
                Fail "managed file does not match the source after update: $entry"
            }
        }

        Write-State $destinationRoot $version $commit $manifestHash $entries $customized $baseline
    } catch {
        Write-Warning "update failed; the previous installation is recoverable from .looppilot-backups\$backupId"
        throw
    }

    Complete-Journal $destinationRoot
    Show-Installed $destinationRoot $version $commit "update" $preserved
}

function Invoke-Status {
    $destinationRoot = Get-InstallDestination $Destination
    Assert-GeneratedPathSafety $destinationRoot
    $journalPath = Get-JournalPath $destinationRoot
    $interrupted = Test-Path -LiteralPath $journalPath -PathType Leaf

    $entries = Get-ManifestEntries
    $version = Get-SourceVersion
    $commit = Get-SourceCommit
    $manifestHash = Get-Hash $ManifestPath
    $sourceHashes = Get-SourceHashes $entries
    $statePath = Join-Path $destinationRoot $StateName

    $state = $null
    $stateBroken = $false
    if (Test-Path -LiteralPath $statePath -PathType Leaf) {
        try {
            $state = Get-State $statePath
        } catch {
            $stateBroken = $true
        }
    } else {
        $present = 0
        foreach ($entry in $entries) {
            if (Test-Path -LiteralPath (Get-DestinationPath $destinationRoot $entry) -PathType Leaf) { $present++ }
        }
        if ($present -eq 0) {
            Fail "no compatible LoopPilot installation found at '$destinationRoot'"
        }
        $stateBroken = $true
    }

    $plan = Compare-Installation $destinationRoot $entries $sourceHashes $state
    $metadataChanged = $null -eq $state -or
        $state.Version -ne $version -or
        $state.Commit -ne $commit -or
        $state.Manifest -ne $manifestHash
    $synchronization = Get-SynchronizationState $plan $metadataChanged ($interrupted -or $stateBroken)

    Write-Output "LoopPilot installation status"
    Write-Output "Destination: $destinationRoot"
    Write-Output "State: $synchronization"
    Write-Output "State format: $(if ($null -ne $state) { $state.Format } else { 'unreadable' })"
    Write-Output "Installed version: $(if ($null -ne $state) { $state.Version } else { 'unknown' })"
    Write-Output "Installed commit: $(if ($null -ne $state) { $state.Commit } else { 'unknown' })"
    Write-Output "Source version: $version"
    Write-Output "Source commit: $commit"
    if ($null -ne $state) { Write-Output "Installed source mode: $($state.ProvenanceMode)" }
    Write-Output "Revision: $(if ($null -ne $state -and $state.Commit -eq $commit) { 'unchanged' } else { 'changed' })"
    Write-Output "Manifest: $(if ($null -ne $state -and $state.Manifest -eq $manifestHash) { 'unchanged' } else { 'changed' })"
    Write-Output "Interrupted update: $(if ($interrupted) { 'yes' } else { 'no' })"
    Write-Output "Files current: $($plan.Current.Count)"
    Write-Output "Files updatable: $($plan.Update.Count)"
    Write-Output "Files locally modified: $($plan.Local.Count)"
    Write-Output "Files conflicted: $($plan.Conflict.Count)"
    Write-Output "Files to add: $($plan.Add.Count)"
    Write-Output "Files to remove: $($plan.Remove.Count)"
    Write-Output "Files preserved on remove: $($plan.RemovePreserve.Count)"
    foreach ($entry in $plan.Update) { Write-Output "UPDATE|$entry" }
    foreach ($entry in $plan.Local) { Write-Output "LOCAL|$entry" }
    foreach ($entry in $plan.Conflict) { Write-Output "CONFLICT|$entry" }
    foreach ($entry in $plan.Add) { Write-Output "ADD|$entry" }
    foreach ($entry in $plan.Remove) { Write-Output "REMOVE|$entry" }
    foreach ($entry in $plan.RemovePreserve) { Write-Output "REMOVE-PRESERVE|$entry" }
}

function Invoke-Uninstall {
    $destinationRoot = Get-InstallDestination $Destination
    Assert-GeneratedPathSafety $destinationRoot
    # Roll back an interrupted update first, so removal works from recorded state.
    $recovered = Restore-Journal $destinationRoot
    if ($recovered -gt 0) {
        Write-Warning "recovered $recovered file(s) from an interrupted update before uninstalling"
    }
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
    Write-Output "LoopPilot uninstall complete"
    Write-Output "Destination: $destinationRoot"
    Write-Output "Removed files from version: $($state.Version)"
    Write-Output "Installed commit: $($state.Commit)"
    if ($preserved -gt 0) {
        Write-Warning "$preserved modified managed file(s) were preserved as user-owned content"
    }
}

try {
    if ($Operation -ne "uninstall") { Prepare-Source }
    switch ($Operation) {
        "install" { Invoke-Install }
        "update" { Invoke-Update }
        "uninstall" { Invoke-Uninstall }
        "status" { Invoke-Status }
    }
} finally { Remove-SourceSnapshot }
