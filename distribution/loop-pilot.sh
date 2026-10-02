#!/usr/bin/env bash
set -euo pipefail

SOURCE_ROOT=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
MANIFEST_PATH="$SOURCE_ROOT/distribution/managed-files.txt"
VERSION_PATH="$SOURCE_ROOT/distribution/version.txt"
STATE_NAME=".looppilot-installation"
JOURNAL_NAME=".looppilot-transaction"
STATE_FORMAT="2"
LEGACY_STATE_FORMATS="1"
UNKNOWN_HASH="-"
TEMP_PATHS=()
ORIGINAL_SOURCE_ROOT=$SOURCE_ROOT
SNAPSHOT_ROOT=''
SNAPSHOT_PARENT=''
PINNED_COMMIT=''
SOURCE_MODE=release
ARCHIVE_SHA256=''
SNAPSHOT_DIGEST=''
PROVENANCE_MODE=''

cleanup() {
  local path
  for path in "${TEMP_PATHS[@]}"; do
    rm -f -- "$path"
  done
  if [ -n "$SNAPSHOT_ROOT" ] && [ -d "$SNAPSHOT_ROOT" ] && [ ! -L "$SNAPSHOT_ROOT" ]; then
    case "$SNAPSHOT_ROOT" in
      "$SNAPSHOT_PARENT"/looppilot-source.*)
        chmod -R u+w -- "$SNAPSHOT_ROOT"
        rm -rf -- "$SNAPSHOT_ROOT"
        ;;
      *) printf 'Refused unsafe snapshot cleanup path\n' >&2 ;;
    esac
  fi
}
trap cleanup EXIT

fail() {
  printf 'LoopPilot distribution: %s\n' "$1" >&2
  exit 1
}

usage() {
  printf 'Usage: %s {install|update|uninstall|status} [--destination DIR] [--force] [--source-mode release|archive] [--archive-sha256 SHA256]\n' "$0" >&2
  exit 2
}

resolve_target_path() {
  local target=$1 probe leaf suffix base
  case "$target" in
    /*) ;;
    *) target="$PWD/$target" ;;
  esac
  while [ "$target" != "/" ] && [ "${target%/}" != "$target" ]; do
    target=${target%/}
  done
  case "/$target/" in
    */../*) fail "destination must not contain '..': '$target'" ;;
  esac
  if [ -L "$target" ]; then
    fail "destination must not be a symbolic link: '$target'"
  fi
  if [ -e "$target" ]; then
    [ -d "$target" ] || fail "destination is not a directory: '$target'"
    (CDPATH= cd -P -- "$target" && pwd)
    return
  fi

  probe=$target
  suffix=''
  while [ ! -e "$probe" ]; do
    [ ! -L "$probe" ] || fail "destination path contains a symbolic link: '$target'"
    leaf=${probe##*/}
    [ -n "$leaf" ] || fail "cannot resolve destination '$target'"
    suffix="/$leaf$suffix"
    probe=${probe%/*}
    [ -n "$probe" ] || probe=/
  done
  [ -d "$probe" ] || fail "destination parent is not a directory: '$probe'"
  base=$(CDPATH= cd -P -- "$probe" && pwd)
  printf '%s%s\n' "${base%/}" "$suffix"
}

resolve_destination() {
  local home_dir
  local -a candidates=()
  if [ -n "${DESTINATION:-}" ]; then
    resolve_target_path "$DESTINATION"
    return
  fi
  if [ -n "${LOOPPILOT_INSTALL_DIR:-}" ]; then
    resolve_target_path "$LOOPPILOT_INSTALL_DIR"
    return
  fi

  home_dir=${HOME:?HOME is required when destination is not explicit}
  if [ -n "${CLAUDE_CONFIG_DIR:-}" ]; then
    candidates+=("$CLAUDE_CONFIG_DIR/skills")
  elif [ -d "$home_dir/.claude/skills" ]; then
    candidates+=("$home_dir/.claude/skills")
  fi
  if [ -d "$home_dir/.codex/skills" ]; then
    candidates+=("$home_dir/.codex/skills")
  fi
  if [ "${#candidates[@]}" -eq 2 ] && [ "${candidates[0]}" = "${candidates[1]}" ]; then
    candidates=("${candidates[0]}")
  fi
  if [ "${#candidates[@]}" -eq 1 ]; then
    resolve_target_path "${candidates[0]}/loop-pilot"
    return
  fi
  if [ "${#candidates[@]}" -eq 0 ]; then
    fail 'destination is not detectable; pass --destination or set LOOPPILOT_INSTALL_DIR'
  fi
  fail 'destination is ambiguous; pass --destination or set LOOPPILOT_INSTALL_DIR'
}

source_version() {
  local version
  [ -f "$VERSION_PATH" ] || fail 'missing distribution/version.txt'
  version=$(tr -d '\r\n' < "$VERSION_PATH")
  case "$version" in
    ''|*[!A-Za-z0-9._-]*) fail 'distribution/version.txt must contain one non-empty version token' ;;
  esac
  printf '%s\n' "$version"
}

source_commit() {
  [ -n "$PINNED_COMMIT" ] || fail 'source identity has not been prepared'
  printf '%s\n' "$PINNED_COMMIT"
}

stream_hash() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum | awk '{print $1}'
  else shasum -a 256 | awk '{print $1}'; fi
}

payload_digest() {
  local root=$1 entries=$2 path
  while IFS= read -r path; do
    printf '%s|%s\n' "$path" "$(file_hash "$root/$path")"
  done < <(LC_ALL=C sort -u "$entries") | stream_hash
}

prepare_source() {
  local dirty replacements tree_record metadata path mode expected actual entries input
  case "$SOURCE_MODE" in release|archive) ;; *) fail 'invalid source mode' ;; esac
  if [ "$SOURCE_MODE" = release ]; then
    [ -z "$ARCHIVE_SHA256" ] || fail 'archive digest is not valid in release mode'
    git_source_root || fail 'Git source identity unavailable; release install refused'
    # Refuse existing refs; every Git read also ignores replacements added later.
    replacements=$(git --no-replace-objects -C "$SOURCE_ROOT" for-each-ref --format='%(refname)' -- refs/replace/ "${GIT_REPLACE_REF_BASE:-refs/replace/}") ||
      fail 'cannot inspect Git replacement refs'
    [ -z "$replacements" ] || fail 'Git replacement refs present; release install refused'
    PINNED_COMMIT=$(git --no-replace-objects -C "$SOURCE_ROOT" rev-parse --verify 'HEAD^{commit}') ||
      fail 'Git commit identity cannot be resolved; release install refused'
    [ "${#PINNED_COMMIT}" -eq 40 ] && ! printf '%s' "$PINNED_COMMIT" | grep -Eq '[^0-9a-f]' ||
      fail 'unsupported source commit identity; installation state requires a 40-character Git commit'
    git --no-replace-objects -C "$SOURCE_ROOT" cat-file -e "$PINNED_COMMIT^{commit}" ||
      fail 'Git commit object unavailable; release install refused'
    dirty=$(git --no-replace-objects -C "$SOURCE_ROOT" status --porcelain=v1 --untracked-files=all) ||
      fail 'cannot inspect Git source status'
    [ -z "$dirty" ] || fail 'dirty Git source refused; install requires a clean source checkout'
    PROVENANCE_MODE=git-release
  else
    [ ! -e "$SOURCE_ROOT/.git" ] && [ ! -L "$SOURCE_ROOT/.git" ] ||
      fail 'archive mode cannot replace Git source identity'
    if git_source_root; then fail 'archive mode cannot replace Git source identity'; fi
    [ "${#ARCHIVE_SHA256}" -eq 64 ] && ! printf '%s' "$ARCHIVE_SHA256" | grep -Eq '[^0-9a-f]' ||
      fail 'explicit archive mode requires --archive-sha256'
    PROVENANCE_MODE=archive
  fi
  SNAPSHOT_PARENT=$(CDPATH= cd -P -- "${TMPDIR:-/tmp}" && pwd)
  SNAPSHOT_ROOT=$(mktemp -d "$SNAPSHOT_PARENT/looppilot-source.XXXXXXXX")
  case "$SNAPSHOT_ROOT/" in "$ORIGINAL_SOURCE_ROOT/"*) fail 'snapshot must be outside source root' ;; esac
  mkdir "$SNAPSHOT_ROOT/payload"
  if [ "$SOURCE_MODE" = release ]; then
    git --no-replace-objects -C "$ORIGINAL_SOURCE_ROOT" ls-tree -rz "$PINNED_COMMIT" > "$SNAPSHOT_ROOT/tree" || fail 'cannot read pinned tree'
    : > "$SNAPSHOT_ROOT/expected-files"
    while IFS= read -r -d '' tree_record; do
      metadata=${tree_record%%$'\t'*}; path=${tree_record#*$'\t'}
      assert_relative "$path"
      printf '%s\n' "$path" >> "$SNAPSHOT_ROOT/expected-files"
      mode=${metadata%% *}
      case "$mode" in 100644|100755) ;; *) fail "unsupported snapshot entry: $path" ;; esac
      expected=${metadata##* }
      [ -f "$ORIGINAL_SOURCE_ROOT/$path" ] && [ ! -L "$ORIGINAL_SOURCE_ROOT/$path" ] || fail "dirty Git source: missing or indirect tracked file $path"
      actual=$(git --no-replace-objects -C "$ORIGINAL_SOURCE_ROOT" hash-object --path="$path" "$ORIGINAL_SOURCE_ROOT/$path") || fail 'cannot verify tracked worktree content'
      [ "$actual" = "$expected" ] || fail "dirty Git source content differs from pinned commit: $path"
    done < "$SNAPSHOT_ROOT/tree"
    command -v tar >/dev/null 2>&1 || fail 'tar is required for release snapshots'
    git --no-replace-objects -C "$ORIGINAL_SOURCE_ROOT" archive --format=tar --output="$SNAPSHOT_ROOT/source.tar" "$PINNED_COMMIT" ||
      fail 'cannot export pinned commit'
    tar -xf "$SNAPSHOT_ROOT/source.tar" -C "$SNAPSHOT_ROOT/payload" || fail 'cannot extract pinned snapshot'
    find "$SNAPSHOT_ROOT/payload" -mindepth 1 -print0 > "$SNAPSHOT_ROOT/actual-nodes" || fail 'cannot enumerate snapshot'
    while IFS= read -r -d '' actual; do
      path=${actual#"$SNAPSHOT_ROOT/payload/"}
      assert_relative "$path"
      [ ! -L "$actual" ] || fail "unexpected snapshot file: $path"
      if [ -f "$actual" ]; then
        grep -F -x -q -- "$path" "$SNAPSHOT_ROOT/expected-files" || fail "unexpected snapshot file: $path"
      elif [ ! -d "$actual" ]; then
        fail "unexpected snapshot file: $path"
      fi
    done < "$SNAPSHOT_ROOT/actual-nodes"
    while IFS= read -r -d '' tree_record; do
      metadata=${tree_record%%$'\t'*}; path=${tree_record#*$'\t'}; expected=${metadata##* }
      [ -f "$SNAPSHOT_ROOT/payload/$path" ] && [ ! -L "$SNAPSHOT_ROOT/payload/$path" ] ||
        fail "snapshot is missing a regular committed file: $path"
      actual=$(git --no-replace-objects -C "$ORIGINAL_SOURCE_ROOT" hash-object --no-filters "$SNAPSHOT_ROOT/payload/$path") || fail 'snapshot validation failed'
      [ "$actual" = "$expected" ] || fail "snapshot content does not match pinned commit: $path"
    done < "$SNAPSHOT_ROOT/tree"
  else
    entries="$SNAPSHOT_ROOT/archive-inputs"
    manifest_entries > "$entries"
    printf '%s\n' distribution/managed-files.txt distribution/version.txt distribution/commit.txt >> "$entries"
    while IFS= read -r input; do
      assert_source_file "$input"
      mkdir -p -- "$(dirname -- "$SNAPSHOT_ROOT/payload/$input")"
      cp -p -- "$ORIGINAL_SOURCE_ROOT/$input" "$SNAPSHOT_ROOT/payload/$input"
    done < <(LC_ALL=C sort -u "$entries")
  fi
  SOURCE_ROOT="$SNAPSHOT_ROOT/payload"
  MANIFEST_PATH="$SOURCE_ROOT/distribution/managed-files.txt"
  VERSION_PATH="$SOURCE_ROOT/distribution/version.txt"
  if [ "$SOURCE_MODE" = archive ]; then
    PINNED_COMMIT=$(tr -d '\r\n' < "$SOURCE_ROOT/distribution/commit.txt")
    [ "${#PINNED_COMMIT}" -eq 40 ] && ! printf '%s' "$PINNED_COMMIT" | grep -Eq '[^0-9a-f]' || fail 'invalid publisher archive commit'
  elif [ -f "$SOURCE_ROOT/distribution/commit.txt" ]; then
    [ "$(tr -d '\r\n' < "$SOURCE_ROOT/distribution/commit.txt")" = "$PINNED_COMMIT" ] || fail 'source identity conflicts with snapshot commit.txt'
  fi
  source_version >/dev/null
  entries="$SNAPSHOT_ROOT/payload-entries"
  manifest_entries > "$entries"
  SNAPSHOT_DIGEST=$(payload_digest "$SOURCE_ROOT" "$entries")
  if [ "$SOURCE_MODE" = archive ]; then
    [ "$SNAPSHOT_DIGEST" = "$ARCHIVE_SHA256" ] || fail 'archive snapshot digest mismatch'
  fi
  chmod -R a-w -- "$SOURCE_ROOT"
  printf 'Install mode: %s\nSource snapshot SHA-256: %s\nSource validation: passed\n' "$PROVENANCE_MODE" "$SNAPSHOT_DIGEST"
  if [ "$SOURCE_MODE" = release ]; then printf 'Source clean determination: preflight passed (not a live worktree claim)\n'; fi
  if [ "$SOURCE_MODE" = archive ]; then printf 'Archive commit is publisher-declared, not verified Git provenance\n'; fi
}

assert_relative() {
  case "$1" in
    ''|/*|*\\*|*'|'*|*:*|*//*|*/|.|./*|*/./*|*/.|..|../*|*/../*|*/..)
      fail "unsafe managed path '$1'"
      ;;
  esac
  case "$1" in
    *$'\r'*|*$'\n'*) fail "unsafe managed path '$1'" ;;
  esac
}

git_source_root() {
  local root=''
  command -v git >/dev/null 2>&1 || return 1
  root=$(git --no-replace-objects -C "$SOURCE_ROOT" rev-parse --show-toplevel 2>/dev/null || true)
  [ -n "$root" ] || return 1
  root=$(CDPATH= cd -P -- "$root" && pwd)
  [ "$root" = "$SOURCE_ROOT" ]
}

assert_source_file() {
  assert_relative "$1"
  [ -f "$SOURCE_ROOT/$1" ] || fail "manifest file is missing: $1"
  [ ! -L "$SOURCE_ROOT/$1" ] || fail "manifest file must not be a symbolic link: $1"

}

manifest_entries() {
  local entry trimmed absolute relative raw git_root
  [ -f "$MANIFEST_PATH" ] || fail 'missing distribution/managed-files.txt'
  raw=$(mktemp)
  TEMP_PATHS+=("$raw")
  git_root=0
  git_source_root && git_root=1

  while IFS= read -r entry || [ -n "$entry" ]; do
    entry=${entry%$'\r'}
    case "$entry" in ''|'#'*) continue ;; esac
    trimmed=${entry%/}
    assert_relative "$trimmed"
    if [ "$trimmed" != "$entry" ]; then
      [ -d "$SOURCE_ROOT/$trimmed" ] || fail "manifest directory is missing: $entry"
      if [ "$git_root" -eq 1 ]; then
        git --no-replace-objects -C "$SOURCE_ROOT" ls-files -- "$trimmed/" >> "$raw" ||
          fail "cannot enumerate tracked files for: $entry"
      else
        while IFS= read -r absolute; do
          relative=${absolute#"$SOURCE_ROOT/"}
          printf '%s\n' "$relative" >> "$raw"
        done < <(find "$SOURCE_ROOT/$trimmed" -type f -print)
      fi
    else
      printf '%s\n' "$trimmed" >> "$raw"
    fi
  done < "$MANIFEST_PATH"

  [ -s "$raw" ] || fail 'distribution manifest contains no files'
  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    assert_source_file "$entry"
    printf '%s\n' "$entry"
  done < <(sort -u "$raw")
}

file_hash() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    fail 'sha256sum or shasum is required'
  fi
}

state_value() {
  awk -F'|' -v key="$1" '{sub(/\r$/, "")} $1 == key {print $2; exit}' "$2"
}

state_file_row() {
  awk -F'|' -v path="$1" '{sub(/\r$/, "")} $1 == "FILE" && $2 == path {print; exit}' "$2"
}

state_file_hash() {
  state_file_row "$1" "$2" | awk -F'|' '{print $3}'
}

state_customized() {
  state_file_row "$1" "$2" | awk -F'|' '{print $4}'
}

state_base() {
  # Format 2 records the baseline in field 5. A format 1 row keeps its baseline
  # only when the file was never customized, because a customized format 1 row
  # overwrote the baseline with the local hash.
  state_file_row "$1" "$2" | awk -F'|' -v unknown="$UNKNOWN_HASH" '
    {
      if (NF >= 5) { print $5 }
      else if ($4 == "1") { print unknown }
      else { print $3 }
    }'
}

validate_state() {
  local state=$1 destination_root=$2
  [ -f "$state" ] || fail "no compatible LoopPilot installation found at '$destination_root'"
  awk -F'|' -v expected_format="$STATE_FORMAT" -v legacy_formats="$LEGACY_STATE_FORMATS" -v unknown="$UNKNOWN_HASH" '
    BEGIN {
      ok=1; files=0
      known[expected_format]=1
      split(legacy_formats, legacy, " ")
      for (i in legacy) known[legacy[i]]=1
    }
    { sub(/\r$/, "") }
    /^[[:space:]]*$/ || /^#/ { next }
    $1 == "FORMAT" {
      if (NF != 2 || format_seen++) ok=0
      format=$2
      next
    }
    $1 == "VERSION" {
      if (NF != 2 || version_seen++ || $2 == "" || $2 ~ /[^A-Za-z0-9._-]/) ok=0
      next
    }
    $1 == "COMMIT" {
      if (NF != 2 || commit_seen++ || length($2) != 40 || $2 ~ /[^0-9a-f]/) ok=0
      next
    }
    $1 == "MANIFEST" {
      if (NF != 2 || manifest_seen++ || length($2) != 64 || $2 ~ /[^0-9a-f]/) ok=0
      next
    }
    $1 == "PROVENANCE" {
      if (NF != 4 || provenance_seen++ || ($2 != "git-release" && $2 != "archive") ||
          length($3) != 64 || $3 ~ /[^0-9a-f]/ || length($4) != 64 || $4 ~ /[^0-9a-f]/) ok=0
      next
    }
    $1 == "FILE" {
      if ((NF != 4 && NF != 5) || $2 == "" || $2 ~ /^\// || $2 ~ /\\/ || $2 ~ /:/ || $2 ~ /\/\// || $2 ~ /\/$/ ||
          length($3) != 64 || $3 ~ /[^0-9a-f]/ || $4 !~ /^[01]$/ || seen_file[$2]++) ok=0
      if (NF == 5 && $5 != unknown && (length($5) != 64 || $5 ~ /[^0-9a-f]/)) ok=0
      count=split($2, parts, "/")
      for (i=1; i<=count; i++) if (parts[i] == "" || parts[i] == "." || parts[i] == "..") ok=0
      files++
      next
    }
    { ok=0 }
    END {
      if (format_seen != 1 || !(format in known) || version_seen != 1 || commit_seen != 1 ||
          manifest_seen != 1 || files == 0) ok=0
      exit(ok ? 0 : 1)
    }
  ' "$state" || fail 'installation state is incompatible or incomplete'
}

assert_safe_destination_path() {
  local root=$1 relative=$2 current part
  assert_relative "$relative"
  current=$root
  [ ! -L "$current" ] || fail "destination path contains a symbolic link: $relative"
  IFS='/' read -r -a parts <<< "$relative"
  for part in "${parts[@]}"; do
    current="$current/$part"
    [ ! -L "$current" ] || fail "destination path contains a symbolic link: $relative"
  done
}

preflight_generated_paths() {
  local root=$1 state_path backup_root journal_path
  state_path="$root/$STATE_NAME"
  backup_root="$root/.looppilot-backups"
  journal_path="$root/$JOURNAL_NAME"
  if [ -L "$state_path" ] || { [ -e "$state_path" ] && [ ! -f "$state_path" ]; }; then
    fail "generated installation state path must be a regular file: '$state_path'"
  fi
  if [ -L "$backup_root" ] || { [ -e "$backup_root" ] && [ ! -d "$backup_root" ]; }; then
    fail "generated backup path must be a regular directory: '$backup_root'"
  fi
  if [ -L "$journal_path" ] || { [ -e "$journal_path" ] && [ ! -f "$journal_path" ]; }; then
    fail "generated transaction path must be a regular file: '$journal_path'"
  fi
}

start_journal() {
  local root=$1 backup_id=$2 version=$3 commit=$4 manifest_hash=$5
  printf 'BEGIN|%s|%s|%s|%s\n' "$backup_id" "$version" "$commit" "$manifest_hash" > "$root/$JOURNAL_NAME"
}

journal_entry() {
  # Recorded before the action so an interruption always leaves a recoverable trace.
  printf '%s|%s\n' "$2" "$3" >> "$1/$JOURNAL_NAME"
}

complete_journal() {
  rm -f -- "$1/$JOURNAL_NAME"
}

restore_journal() {
  # Roll the destination back to the pre-update content, newest action first.
  local root=$1 journal_path backup_id restored action path backup target
  journal_path="$root/$JOURNAL_NAME"
  [ -f "$journal_path" ] || { printf '0\n'; return 0; }
  backup_id=$(awk -F'|' '$1 == "BEGIN" {print $2; exit}' "$journal_path")
  [ -n "$backup_id" ] || fail 'interrupted-update journal has no BEGIN row'
  restored=0
  while IFS='|' read -r action path; do
    case "$action" in
      REPLACE|CREATE|DELETE) ;;
      *) continue ;;
    esac
    [ -n "$path" ] || continue
    assert_relative "$path"
    target="$root/$path"
    if [ "$action" = CREATE ]; then
      if [ -f "$target" ]; then
        rm -f -- "$target"
        restored=$((restored + 1))
      fi
      continue
    fi
    backup="$root/.looppilot-backups/$backup_id/$path"
    if [ -f "$backup" ]; then
      mkdir -p -- "$(dirname -- "$target")"
      cp -p -- "$backup" "$target"
      restored=$((restored + 1))
    fi
  done < <(grep -v '^BEGIN|' "$journal_path" |
    awk '{lines[NR]=$0} END {for (i=NR; i>=1; i--) print lines[i]}')
  complete_journal "$root"
  printf '%s\n' "$restored"
}

preflight_destination() {
  local destination_root=$1 entries_file=$2 entry path
  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    assert_safe_destination_path "$destination_root" "$entry"
    path="$destination_root/$entry"
    if [ -e "$path" ] && [ ! -f "$path" ]; then
      fail "managed path is not a regular file: $entry"
    fi
  done < "$entries_file"
}

new_backup_id() {
  printf '%s-%s-%s\n' "$(date -u +%Y%m%d-%H%M%S)" "$$" "${RANDOM:-0}"
}

backup_file() {
  local root=$1 relative=$2 backup_id=$3 source backup
  source="$root/$relative"
  [ -f "$source" ] || return 0
  backup="$root/.looppilot-backups/$backup_id/$relative"
  mkdir -p -- "$(dirname -- "$backup")"
  cp -p -- "$source" "$backup"
}

copy_source_file() {
  local destination_root=$1 entry=$2 expected_hash=$3 destination
  destination="$destination_root/$entry"
  mkdir -p -- "$(dirname -- "$destination")"
  cp -p -- "$SOURCE_ROOT/$entry" "$destination"
  chmod u+w -- "$destination"
  [ "$(file_hash "$destination")" = "$expected_hash" ] ||
    fail "source changed during copy: $entry"
}

build_source_hashes() {
  local entries_file=$1 hashes_file=$2 entry
  : > "$hashes_file"
  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    printf '%s|%s\n' "$entry" "$(file_hash "$SOURCE_ROOT/$entry")" >> "$hashes_file"
  done < "$entries_file"
}

source_hash() {
  awk -F'|' -v path="$1" '$1 == path {print $2; exit}' "$2"
}

write_state() {
  local destination_root=$1 version=$2 commit=$3 manifest_hash=$4 entries_file=$5 customized_file=$6 baseline_file=$7
  local state_path state_tmp entry flag base
  state_path="$destination_root/$STATE_NAME"
  state_tmp=$(mktemp "$destination_root/.looppilot-installation.tmp.XXXXXX")
  TEMP_PATHS+=("$state_tmp")
  {
    printf 'FORMAT|%s\n' "$STATE_FORMAT"
    printf 'VERSION|%s\n' "$version"
    printf 'COMMIT|%s\n' "$commit"
    printf 'MANIFEST|%s\n' "$manifest_hash"
    printf 'PROVENANCE|%s|%s|%s\n' "$PROVENANCE_MODE" "$SNAPSHOT_DIGEST" "$(payload_digest "$destination_root" "$entries_file")"
    while IFS= read -r entry; do
      [ -n "$entry" ] || continue
      [ -f "$destination_root/$entry" ] || fail "managed file is missing while writing state: $entry"
      flag=0
      grep -F -x -q -- "$entry" "$customized_file" && flag=1 || true
      base=$(source_hash "$entry" "$baseline_file")
      [ -n "$base" ] || base=$UNKNOWN_HASH
      printf 'FILE|%s|%s|%s|%s\n' "$entry" "$(file_hash "$destination_root/$entry")" "$flag" "$base"
    done < "$entries_file"
  } > "$state_tmp"
  mv -f -- "$state_tmp" "$state_path"
}

compare_installation() {
  # Emits "CATEGORY|path" lines using the three-way BASE/LOCAL/REMOTE comparison.
  local destination_root=$1 entries_file=$2 hashes_file=$3 state_path=$4
  local all_file old_file entry path local_hash base_hash remote_hash has_state has_base
  all_file=$(mktemp)
  old_file=$(mktemp)
  TEMP_PATHS+=("$all_file" "$old_file")
  has_state=0
  : > "$old_file"
  if [ -n "$state_path" ] && [ -f "$state_path" ]; then
    has_state=1
    awk -F'|' '{sub(/\r$/, "")} $1 == "FILE" {print $2}' "$state_path" | sort -u > "$old_file"
  fi
  sort -u "$entries_file" "$old_file" > "$all_file"

  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    path="$destination_root/$entry"
    remote_hash=$(source_hash "$entry" "$hashes_file")
    has_base=0
    base_hash=''
    if [ "$has_state" -eq 1 ] && [ -n "$(state_file_row "$entry" "$state_path")" ]; then
      has_base=1
      base_hash=$(state_base "$entry" "$state_path")
      [ "$base_hash" != "$UNKNOWN_HASH" ] || base_hash=''
    fi

    if [ -z "$remote_hash" ]; then
      [ -f "$path" ] || continue
      local_hash=$(file_hash "$path")
      if [ -n "$base_hash" ] && [ "$local_hash" = "$base_hash" ]; then
        printf 'REMOVE|%s\n' "$entry"
      else
        printf 'REMOVE-PRESERVE|%s\n' "$entry"
      fi
      continue
    fi

    if [ ! -f "$path" ]; then
      if [ "$has_base" -eq 1 ]; then
        printf 'UPDATE|%s\n' "$entry"
      else
        printf 'ADD|%s\n' "$entry"
      fi
      continue
    fi

    local_hash=$(file_hash "$path")
    if [ "$local_hash" = "$remote_hash" ]; then
      printf 'CURRENT|%s\n' "$entry"
      continue
    fi
    if [ "$has_base" -eq 0 ] || [ -z "$base_hash" ]; then
      # Either a new managed path colliding with user content, or a baseline
      # lost by a legacy format 1 state. Neither can be proven safe.
      printf 'CONFLICT|%s\n' "$entry"
      continue
    fi
    if [ "$local_hash" = "$base_hash" ]; then
      printf 'UPDATE|%s\n' "$entry"
    elif [ "$remote_hash" = "$base_hash" ]; then
      printf 'LOCAL|%s\n' "$entry"
    else
      printf 'CONFLICT|%s\n' "$entry"
    fi
  done < "$all_file"
}

plan_paths() {
  awk -F'|' -v category="$1" '$1 == category {print $2}' "$2"
}

plan_count() {
  plan_paths "$1" "$2" | grep -c . || true
}

synchronization_state() {
  local plan_file=$1 metadata_changed=$2 recovery_required=$3
  if [ "$recovery_required" -eq 1 ]; then printf 'RECOVERY_REQUIRED\n'; return; fi
  if [ "$(plan_count CONFLICT "$plan_file")" -gt 0 ]; then printf 'CONFLICT\n'; return; fi
  if [ "$(plan_count UPDATE "$plan_file")" -gt 0 ] ||
     [ "$(plan_count ADD "$plan_file")" -gt 0 ] ||
     [ "$(plan_count REMOVE "$plan_file")" -gt 0 ] ||
     [ "$metadata_changed" -eq 1 ]; then
    printf 'UPDATE_AVAILABLE\n'; return
  fi
  if [ "$(plan_count LOCAL "$plan_file")" -gt 0 ] ||
     [ "$(plan_count REMOVE-PRESERVE "$plan_file")" -gt 0 ]; then
    printf 'LOCAL_MODIFICATIONS\n'; return
  fi
  printf 'CURRENT\n'
}

show_installed() {
  printf 'LoopPilot %s complete\n' "$4"
  printf 'Destination: %s\n' "$1"
  printf 'Installed version: %s\n' "$2"
  printf 'Installed commit: %s\n' "$3"
  printf 'Installed source mode: %s\n' "$(awk -F'|' '$1 == "PROVENANCE" {print $2}' "$1/$STATE_NAME")"
  printf 'Installed SHA-256: %s\n' "$(awk -F'|' '$1 == "PROVENANCE" {print $4}' "$1/$STATE_NAME")"
  if [ "$5" -gt 0 ]; then
    printf 'Warning: %s local file(s) preserved; review .looppilot-backups before using --force\n' "$5" >&2
  fi
}

install_action() {
  local destination_root version commit manifest_hash entries_file hashes_file state_path
  local same entry path conflicts_file conflict_count first_conflict backup_id customized_file baseline_file
  destination_root=$(resolve_destination)
  preflight_generated_paths "$destination_root"
  version=$(source_version)
  commit=$(source_commit)
  manifest_hash=$(file_hash "$MANIFEST_PATH")
  entries_file=$(mktemp)
  hashes_file=$(mktemp)
  conflicts_file=$(mktemp)
  customized_file=$(mktemp)
  baseline_file=$(mktemp)
  TEMP_PATHS+=("$entries_file" "$hashes_file" "$conflicts_file" "$customized_file" "$baseline_file")
  manifest_entries > "$entries_file"
  build_source_hashes "$entries_file" "$hashes_file"
  preflight_destination "$destination_root" "$entries_file"
  state_path="$destination_root/$STATE_NAME"

  if [ -f "$state_path" ]; then
    validate_state "$state_path" "$destination_root"
    same=1
    [ "$(state_value VERSION "$state_path")" = "$version" ] || same=0
    [ "$(state_value COMMIT "$state_path")" = "$commit" ] || same=0
    [ "$(state_value MANIFEST "$state_path")" = "$manifest_hash" ] || same=0
    [ "$(awk -F'|' '$1 == "FILE" {count++} END {print count+0}' "$state_path")" -eq "$(wc -l < "$entries_file")" ] || same=0
    while IFS= read -r entry; do
      [ -n "$entry" ] || continue
      path="$destination_root/$entry"
      [ -n "$(state_file_row "$entry" "$state_path")" ] || same=0
      [ -f "$path" ] || { same=0; continue; }
      [ "$(file_hash "$path")" = "$(source_hash "$entry" "$hashes_file")" ] || same=0
    done < "$entries_file"
    if [ "$same" -eq 1 ]; then
      show_installed "$destination_root" "$version" "$commit" 'reinstall (no changes)' 0
      return
    fi
    [ "$FORCE" -eq 1 ] || fail 'an installation already exists and differs from this source; use update.sh or pass --force'
    update_action
    return
  fi

  : > "$conflicts_file"
  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    path="$destination_root/$entry"
    if [ -f "$path" ] && [ "$(file_hash "$path")" != "$(source_hash "$entry" "$hashes_file")" ]; then
      printf '%s\n' "$entry" >> "$conflicts_file"
    fi
  done < "$entries_file"
  if [ -s "$conflicts_file" ] && [ "$FORCE" -ne 1 ]; then
    conflict_count=$(wc -l < "$conflicts_file")
    IFS= read -r first_conflict < "$conflicts_file"
    fail "destination contains $conflict_count conflicting file(s), including '$first_conflict'; no files were copied or overwritten"
  fi

  mkdir -p -- "$destination_root"
  backup_id=$(new_backup_id)
  : > "$baseline_file"
  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    path="$destination_root/$entry"
    if [ -f "$path" ]; then
      if [ "$(file_hash "$path")" = "$(source_hash "$entry" "$hashes_file")" ]; then
        printf '%s|%s\n' "$entry" "$(source_hash "$entry" "$hashes_file")" >> "$baseline_file"
        continue
      fi
      backup_file "$destination_root" "$entry" "$backup_id"
    fi
    copy_source_file "$destination_root" "$entry" "$(source_hash "$entry" "$hashes_file")"
    printf '%s|%s\n' "$entry" "$(source_hash "$entry" "$hashes_file")" >> "$baseline_file"
  done < "$entries_file"
  : > "$customized_file"
  write_state "$destination_root" "$version" "$commit" "$manifest_hash" "$entries_file" "$customized_file" "$baseline_file"
  show_installed "$destination_root" "$version" "$commit" install 0
}

update_action() {
  local destination_root version commit manifest_hash entries_file hashes_file state_path all_entries
  local customized_file baseline_file plan_file preserved backup_id entry path recovered conflict_names old_entries
  destination_root=$(resolve_destination)
  preflight_generated_paths "$destination_root"

  # Reject a dirty source before even recovering an interrupted destination.
  commit=$(source_commit)
  # An interrupted update is rolled back first so every update starts from a
  # known-good baseline and retrying is deterministic.
  recovered=$(restore_journal "$destination_root")
  if [ "$recovered" -gt 0 ]; then
    printf 'Warning: recovered %s file(s) from an interrupted update before continuing\n' "$recovered" >&2
  fi

  state_path="$destination_root/$STATE_NAME"
  validate_state "$state_path" "$destination_root"
  version=$(source_version)
  commit=$(source_commit)
  manifest_hash=$(file_hash "$MANIFEST_PATH")
  entries_file=$(mktemp)
  hashes_file=$(mktemp)
  all_entries=$(mktemp)
  old_entries=$(mktemp)
  customized_file=$(mktemp)
  baseline_file=$(mktemp)
  plan_file=$(mktemp)
  TEMP_PATHS+=("$entries_file" "$hashes_file" "$all_entries" "$old_entries" "$customized_file" "$baseline_file" "$plan_file")
  manifest_entries > "$entries_file"
  build_source_hashes "$entries_file" "$hashes_file"
  awk -F'|' '{sub(/\r$/, "")} $1 == "FILE" {print $2}' "$state_path" | sort -u > "$old_entries"
  sort -u "$entries_file" "$old_entries" > "$all_entries"
  preflight_destination "$destination_root" "$all_entries"

  compare_installation "$destination_root" "$entries_file" "$hashes_file" "$state_path" > "$plan_file"
  if [ "$(plan_count CONFLICT "$plan_file")" -gt 0 ] && [ "$FORCE" -ne 1 ]; then
    conflict_names=$(plan_paths CONFLICT "$plan_file" |
      awk 'NR == 1 {printf "%s", $0; next} {printf ", %s", $0} END {print ""}')
    fail "update stopped: $(plan_count CONFLICT "$plan_file") conflicting file(s) changed both locally and upstream ($conflict_names); resolve them or pass --force. No managed file was changed."
  fi

  : > "$customized_file"
  : > "$baseline_file"
  preserved=0
  backup_id=$(new_backup_id)
  start_journal "$destination_root" "$backup_id" "$version" "$commit" "$manifest_hash"

  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    journal_entry "$destination_root" DELETE "$entry"
    backup_file "$destination_root" "$entry" "$backup_id"
    rm -f -- "$destination_root/$entry"
  done < <(plan_paths REMOVE "$plan_file")

  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    backup_file "$destination_root" "$entry" "$backup_id"
    preserved=$((preserved + 1))
    printf 'Warning: preserved retired customized file as user-owned content: %s\n' "$entry" >&2
  done < <(plan_paths REMOVE-PRESERVE "$plan_file")

  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    path="$destination_root/$entry"
    if [ -f "$path" ]; then
      journal_entry "$destination_root" REPLACE "$entry"
      backup_file "$destination_root" "$entry" "$backup_id"
    else
      journal_entry "$destination_root" CREATE "$entry"
    fi
    copy_source_file "$destination_root" "$entry" "$(source_hash "$entry" "$hashes_file")"
    printf '%s|%s\n' "$entry" "$(source_hash "$entry" "$hashes_file")" >> "$baseline_file"
  done < <(plan_paths UPDATE "$plan_file"; plan_paths ADD "$plan_file")

  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    printf '%s|%s\n' "$entry" "$(source_hash "$entry" "$hashes_file")" >> "$baseline_file"
  done < <(plan_paths CURRENT "$plan_file")

  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    backup_file "$destination_root" "$entry" "$backup_id"
    printf '%s\n' "$entry" >> "$customized_file"
    # REMOTE still equals BASE here, so the baseline is retained exactly.
    printf '%s|%s\n' "$entry" "$(source_hash "$entry" "$hashes_file")" >> "$baseline_file"
    preserved=$((preserved + 1))
    printf 'Warning: preserved customized managed file: %s\n' "$entry" >&2
  done < <(plan_paths LOCAL "$plan_file")

  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    path="$destination_root/$entry"
    if [ "$FORCE" -eq 1 ]; then
      if [ -f "$path" ]; then
        journal_entry "$destination_root" REPLACE "$entry"
        backup_file "$destination_root" "$entry" "$backup_id"
      else
        journal_entry "$destination_root" CREATE "$entry"
      fi
      copy_source_file "$destination_root" "$entry" "$(source_hash "$entry" "$hashes_file")"
      printf '%s|%s\n' "$entry" "$(source_hash "$entry" "$hashes_file")" >> "$baseline_file"
      continue
    fi
    backup_file "$destination_root" "$entry" "$backup_id"
    printf '%s\n' "$entry" >> "$customized_file"
    printf '%s|%s\n' "$entry" "$(source_hash "$entry" "$hashes_file")" >> "$baseline_file"
    preserved=$((preserved + 1))
    printf 'Warning: preserved conflicting managed file: %s\n' "$entry" >&2
  done < <(plan_paths CONFLICT "$plan_file")

  # Verify before the transaction is marked complete.
  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    path="$destination_root/$entry"
    [ -f "$path" ] || fail "managed file is missing after update: $entry"
    if ! grep -F -x -q -- "$entry" "$customized_file"; then
      [ "$(file_hash "$path")" = "$(source_hash "$entry" "$hashes_file")" ] ||
        fail "managed file does not match the source after update: $entry"
    fi
  done < "$entries_file"

  write_state "$destination_root" "$version" "$commit" "$manifest_hash" "$entries_file" "$customized_file" "$baseline_file"
  complete_journal "$destination_root"
  show_installed "$destination_root" "$version" "$commit" update "$preserved"
}

status_action() {
  local destination_root version commit manifest_hash entries_file hashes_file state_path plan_file
  local interrupted state_broken metadata_changed present entry sync installed_version installed_commit
  local installed_manifest state_format
  destination_root=$(resolve_destination)
  preflight_generated_paths "$destination_root"
  state_path="$destination_root/$STATE_NAME"
  interrupted=0
  [ -f "$destination_root/$JOURNAL_NAME" ] && interrupted=1

  version=$(source_version)
  commit=$(source_commit)
  manifest_hash=$(file_hash "$MANIFEST_PATH")
  entries_file=$(mktemp)
  hashes_file=$(mktemp)
  plan_file=$(mktemp)
  TEMP_PATHS+=("$entries_file" "$hashes_file" "$plan_file")
  manifest_entries > "$entries_file"
  build_source_hashes "$entries_file" "$hashes_file"

  state_broken=0
  if [ -f "$state_path" ]; then
    validate_state "$state_path" "$destination_root" 2>/dev/null || state_broken=1
  else
    present=0
    while IFS= read -r entry; do
      [ -n "$entry" ] || continue
      [ -f "$destination_root/$entry" ] && present=$((present + 1))
    done < "$entries_file"
    [ "$present" -gt 0 ] || fail "no compatible LoopPilot installation found at '$destination_root'"
    state_broken=1
  fi

  if [ "$state_broken" -eq 1 ]; then
    compare_installation "$destination_root" "$entries_file" "$hashes_file" '' > "$plan_file"
    installed_version=unknown
    installed_commit=unknown
    installed_manifest=''
    state_format=unreadable
  else
    compare_installation "$destination_root" "$entries_file" "$hashes_file" "$state_path" > "$plan_file"
    installed_version=$(state_value VERSION "$state_path")
    installed_commit=$(state_value COMMIT "$state_path")
    installed_manifest=$(state_value MANIFEST "$state_path")
    state_format=$(state_value FORMAT "$state_path")
  fi

  metadata_changed=0
  [ "$installed_version" = "$version" ] || metadata_changed=1
  [ "$installed_commit" = "$commit" ] || metadata_changed=1
  [ "$installed_manifest" = "$manifest_hash" ] || metadata_changed=1
  sync=$(synchronization_state "$plan_file" "$metadata_changed" "$((interrupted | state_broken))")

  printf 'LoopPilot installation status\n'
  printf 'Destination: %s\n' "$destination_root"
  printf 'State: %s\n' "$sync"
  printf 'State format: %s\n' "$state_format"
  printf 'Installed version: %s\n' "$installed_version"
  printf 'Installed commit: %s\n' "$installed_commit"
  if [ -f "$state_path" ]; then
    printf 'Installed source mode: %s\n' "$(awk -F'|' '$1 == "PROVENANCE" {mode=$2} END {print mode ? mode : "legacy-unverified"}' "$state_path")"
  fi
  printf 'Source version: %s\n' "$version"
  printf 'Source commit: %s\n' "$commit"
  if [ "$installed_commit" = "$commit" ]; then
    printf 'Revision: unchanged\n'
  else
    printf 'Revision: changed\n'
  fi
  if [ "$installed_manifest" = "$manifest_hash" ]; then
    printf 'Manifest: unchanged\n'
  else
    printf 'Manifest: changed\n'
  fi
  if [ "$interrupted" -eq 1 ]; then
    printf 'Interrupted update: yes\n'
  else
    printf 'Interrupted update: no\n'
  fi
  printf 'Files current: %s\n' "$(plan_count CURRENT "$plan_file")"
  printf 'Files updatable: %s\n' "$(plan_count UPDATE "$plan_file")"
  printf 'Files locally modified: %s\n' "$(plan_count LOCAL "$plan_file")"
  printf 'Files conflicted: %s\n' "$(plan_count CONFLICT "$plan_file")"
  printf 'Files to add: %s\n' "$(plan_count ADD "$plan_file")"
  printf 'Files to remove: %s\n' "$(plan_count REMOVE "$plan_file")"
  printf 'Files preserved on remove: %s\n' "$(plan_count REMOVE-PRESERVE "$plan_file")"
  awk -F'|' '$1 == "UPDATE" || $1 == "LOCAL" || $1 == "CONFLICT" || $1 == "ADD" ||
             $1 == "REMOVE" || $1 == "REMOVE-PRESERVE" {print $1 "|" $2}' "$plan_file"
}

uninstall_action() {
  local destination_root state_path entries_file preserved entry path version commit recovered
  destination_root=$(resolve_destination)
  preflight_generated_paths "$destination_root"
  # Roll back an interrupted update first, so removal works from recorded state.
  recovered=$(restore_journal "$destination_root")
  if [ "$recovered" -gt 0 ]; then
    printf 'Warning: recovered %s file(s) from an interrupted update before uninstalling\n' "$recovered" >&2
  fi
  state_path="$destination_root/$STATE_NAME"
  validate_state "$state_path" "$destination_root"
  entries_file=$(mktemp)
  TEMP_PATHS+=("$entries_file")
  awk -F'|' '{sub(/\r$/, "")} $1 == "FILE" {print $2}' "$state_path" | sort -u > "$entries_file"
  preflight_destination "$destination_root" "$entries_file"

  preserved=0
  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    path="$destination_root/$entry"
    [ -f "$path" ] || continue
    if [ "$(state_customized "$entry" "$state_path")" = 1 ] ||
       [ "$(file_hash "$path")" != "$(state_file_hash "$entry" "$state_path")" ]; then
      preserved=$((preserved + 1))
      printf 'Warning: preserved modified managed file as user-owned content: %s\n' "$entry" >&2
      continue
    fi
    rm -f -- "$path"
  done < "$entries_file"
  version=$(state_value VERSION "$state_path")
  commit=$(state_value COMMIT "$state_path")
  rm -f -- "$state_path"
  printf 'LoopPilot uninstall complete\nDestination: %s\nRemoved files from version: %s\nInstalled commit: %s\n' "$destination_root" "$version" "$commit"
  if [ "$preserved" -gt 0 ]; then
    printf 'Warning: %s modified managed file(s) were preserved as user-owned content\n' "$preserved" >&2
  fi
}

DESTINATION=''
FORCE=0
operation=${1:-}
[ -n "$operation" ] || usage
shift
while [ "$#" -gt 0 ]; do
  case "$1" in
    --destination) [ "$#" -ge 2 ] || usage; DESTINATION=$2; shift 2 ;;
    --force) FORCE=1; shift ;;
    --source-mode) [ "$#" -ge 2 ] || usage; SOURCE_MODE=$2; shift 2 ;;
    --archive-sha256) [ "$#" -ge 2 ] || usage; ARCHIVE_SHA256=$2; shift 2 ;;
    -h|--help) usage ;;
    *) usage ;;
  esac
done

case "$operation" in install|update|status) prepare_source ;; esac

case "$operation" in
  install) install_action ;;
  update) update_action ;;
  uninstall) uninstall_action ;;
  status) status_action ;;
  *) usage ;;
esac
