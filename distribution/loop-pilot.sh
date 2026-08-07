#!/usr/bin/env bash
set -euo pipefail

SOURCE_ROOT=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
MANIFEST_PATH="$SOURCE_ROOT/distribution/managed-files.txt"
VERSION_PATH="$SOURCE_ROOT/distribution/version.txt"
STATE_NAME=".looppilot-installation"
STATE_FORMAT="1"
TEMP_PATHS=()

cleanup() {
  local path
  for path in "${TEMP_PATHS[@]}"; do
    rm -f -- "$path"
  done
}
trap cleanup EXIT

fail() {
  printf 'LoopPilot distribution: %s\n' "$1" >&2
  exit 1
}

usage() {
  printf 'Usage: %s {install|update|uninstall} [--destination DIR] [--force]\n' "$0" >&2
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
  local commit=''
  if command -v git >/dev/null 2>&1; then
    commit=$(git -C "$SOURCE_ROOT" rev-parse --verify HEAD 2>/dev/null || true)
  fi
  if [ -z "$commit" ] && [ -f "$SOURCE_ROOT/distribution/commit.txt" ]; then
    commit=$(tr -d '\r\n' < "$SOURCE_ROOT/distribution/commit.txt")
  fi
  [ "${#commit}" -eq 40 ] && ! printf '%s' "$commit" | grep -Eq '[^0-9a-f]' ||
    fail 'cannot determine a 40-character source commit; run from Git or provide distribution/commit.txt'
  printf '%s\n' "$commit"
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
  root=$(git -C "$SOURCE_ROOT" rev-parse --show-toplevel 2>/dev/null || true)
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
        git -C "$SOURCE_ROOT" ls-files -- "$trimmed/" >> "$raw" ||
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

validate_state() {
  local state=$1 destination_root=$2
  [ -f "$state" ] || fail "no compatible LoopPilot installation found at '$destination_root'"
  awk -F'|' -v expected_format="$STATE_FORMAT" '
    BEGIN { ok=1; files=0 }
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
    $1 == "FILE" {
      if (NF != 4 || $2 == "" || $2 ~ /^\// || $2 ~ /\\/ || $2 ~ /:/ || $2 ~ /\/\// || $2 ~ /\/$/ ||
          length($3) != 64 || $3 ~ /[^0-9a-f]/ || $4 !~ /^[01]$/ || seen_file[$2]++) ok=0
      count=split($2, parts, "/")
      for (i=1; i<=count; i++) if (parts[i] == "" || parts[i] == "." || parts[i] == "..") ok=0
      files++
      next
    }
    { ok=0 }
    END {
      if (format_seen != 1 || format != expected_format || version_seen != 1 || commit_seen != 1 ||
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
  local root=$1 state_path backup_root
  state_path="$root/$STATE_NAME"
  backup_root="$root/.looppilot-backups"
  if [ -L "$state_path" ] || { [ -e "$state_path" ] && [ ! -f "$state_path" ]; }; then
    fail "generated installation state path must be a regular file: '$state_path'"
  fi
  if [ -L "$backup_root" ] || { [ -e "$backup_root" ] && [ ! -d "$backup_root" ]; }; then
    fail "generated backup path must be a regular directory: '$backup_root'"
  fi
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
  local destination_root=$1 entry=$2 destination
  destination="$destination_root/$entry"
  mkdir -p -- "$(dirname -- "$destination")"
  cp -p -- "$SOURCE_ROOT/$entry" "$destination"
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
  local destination_root=$1 version=$2 commit=$3 manifest_hash=$4 entries_file=$5 customized_file=$6
  local state_path state_tmp entry flag
  state_path="$destination_root/$STATE_NAME"
  state_tmp=$(mktemp "$destination_root/.looppilot-installation.tmp.XXXXXX")
  TEMP_PATHS+=("$state_tmp")
  {
    printf 'FORMAT|%s\n' "$STATE_FORMAT"
    printf 'VERSION|%s\n' "$version"
    printf 'COMMIT|%s\n' "$commit"
    printf 'MANIFEST|%s\n' "$manifest_hash"
    while IFS= read -r entry; do
      [ -n "$entry" ] || continue
      [ -f "$destination_root/$entry" ] || fail "managed file is missing while writing state: $entry"
      flag=0
      grep -F -x -q -- "$entry" "$customized_file" && flag=1 || true
      printf 'FILE|%s|%s|%s\n' "$entry" "$(file_hash "$destination_root/$entry")" "$flag"
    done < "$entries_file"
  } > "$state_tmp"
  mv -f -- "$state_tmp" "$state_path"
}

show_installed() {
  printf 'LoopPilot %s complete\n' "$4"
  printf 'Destination: %s\n' "$1"
  printf 'Installed version: %s\n' "$2"
  printf 'Installed commit: %s\n' "$3"
  if [ "$5" -gt 0 ]; then
    printf 'Warning: %s local file(s) preserved; review .looppilot-backups before using --force\n' "$5" >&2
  fi
}

install_action() {
  local destination_root version commit manifest_hash entries_file hashes_file state_path
  local same entry path conflicts_file conflict_count first_conflict backup_id customized_file
  destination_root=$(resolve_destination)
  preflight_generated_paths "$destination_root"
  version=$(source_version)
  commit=$(source_commit)
  manifest_hash=$(file_hash "$MANIFEST_PATH")
  entries_file=$(mktemp)
  hashes_file=$(mktemp)
  conflicts_file=$(mktemp)
  customized_file=$(mktemp)
  TEMP_PATHS+=("$entries_file" "$hashes_file" "$conflicts_file" "$customized_file")
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
  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    path="$destination_root/$entry"
    if [ -f "$path" ]; then
      [ "$(file_hash "$path")" = "$(source_hash "$entry" "$hashes_file")" ] && continue
      backup_file "$destination_root" "$entry" "$backup_id"
    fi
    copy_source_file "$destination_root" "$entry"
  done < "$entries_file"
  : > "$customized_file"
  write_state "$destination_root" "$version" "$commit" "$manifest_hash" "$entries_file" "$customized_file"
  show_installed "$destination_root" "$version" "$commit" install 0
}

update_action() {
  local destination_root version commit manifest_hash entries_file hashes_file state_path old_entries all_entries
  local customized_file preserved backup_id entry path current_hash row was_customized baseline_hash was_managed
  destination_root=$(resolve_destination)
  preflight_generated_paths "$destination_root"
  state_path="$destination_root/$STATE_NAME"
  validate_state "$state_path" "$destination_root"
  version=$(source_version)
  commit=$(source_commit)
  manifest_hash=$(file_hash "$MANIFEST_PATH")
  entries_file=$(mktemp)
  hashes_file=$(mktemp)
  old_entries=$(mktemp)
  all_entries=$(mktemp)
  customized_file=$(mktemp)
  TEMP_PATHS+=("$entries_file" "$hashes_file" "$old_entries" "$all_entries" "$customized_file")
  manifest_entries > "$entries_file"
  build_source_hashes "$entries_file" "$hashes_file"
  awk -F'|' '{sub(/\r$/, "")} $1 == "FILE" {print $2}' "$state_path" | sort -u > "$old_entries"
  sort -u "$entries_file" "$old_entries" > "$all_entries"
  preflight_destination "$destination_root" "$all_entries"

  : > "$customized_file"
  preserved=0
  backup_id=$(new_backup_id)
  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    grep -F -x -q -- "$entry" "$entries_file" && continue
    path="$destination_root/$entry"
    [ -f "$path" ] || continue
    backup_file "$destination_root" "$entry" "$backup_id"
    if [ "$(state_customized "$entry" "$state_path")" = 1 ] ||
       [ "$(file_hash "$path")" != "$(state_file_hash "$entry" "$state_path")" ]; then
      preserved=$((preserved + 1))
      printf 'Warning: preserved retired customized file as user-owned content: %s\n' "$entry" >&2
      continue
    fi
    rm -f -- "$path"
  done < "$old_entries"

  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    path="$destination_root/$entry"
    if [ ! -f "$path" ]; then
      copy_source_file "$destination_root" "$entry"
      continue
    fi
    current_hash=$(file_hash "$path")
    [ "$current_hash" = "$(source_hash "$entry" "$hashes_file")" ] && continue
    row=$(state_file_row "$entry" "$state_path")
    was_managed=0
    was_customized=0
    baseline_hash=''
    if [ -n "$row" ]; then
      was_managed=1
      was_customized=$(printf '%s\n' "$row" | awk -F'|' '{print $4}')
      baseline_hash=$(printf '%s\n' "$row" | awk -F'|' '{print $3}')
    fi
    if [ "$FORCE" -eq 1 ] ||
       { [ "$was_managed" -eq 1 ] && [ "$was_customized" -ne 1 ] && [ "$current_hash" = "$baseline_hash" ]; }; then
      backup_file "$destination_root" "$entry" "$backup_id"
      copy_source_file "$destination_root" "$entry"
      continue
    fi
    backup_file "$destination_root" "$entry" "$backup_id"
    printf '%s\n' "$entry" >> "$customized_file"
    preserved=$((preserved + 1))
    printf 'Warning: preserved customized managed file: %s\n' "$entry" >&2
  done < "$entries_file"

  write_state "$destination_root" "$version" "$commit" "$manifest_hash" "$entries_file" "$customized_file"
  show_installed "$destination_root" "$version" "$commit" update "$preserved"
}

uninstall_action() {
  local destination_root state_path entries_file preserved entry path version commit
  destination_root=$(resolve_destination)
  preflight_generated_paths "$destination_root"
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
    -h|--help) usage ;;
    *) usage ;;
  esac
done

case "$operation" in
  install) install_action ;;
  update) update_action ;;
  uninstall) uninstall_action ;;
  *) usage ;;
esac
