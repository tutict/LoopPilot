#!/usr/bin/env bash
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
exec "$BASH" "$SCRIPT_DIR/distribution/loop-pilot.sh" install "$@"
