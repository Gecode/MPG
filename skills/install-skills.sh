#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DEFAULT="${HOME}/.codex/skills"
DEST="${1:-${CODEX_HOME:-$DEST_DEFAULT}/skills}"

if [[ "$DEST" == "$HOME/.codex/skills/skills" ]]; then
  DEST="$HOME/.codex/skills"
fi

mkdir -p "$DEST"

for skill in \
  gecode-general-knowledge \
  gecode-modeling \
  gecode-propagator-implementation \
  gecode-brancher-implementation \
  gecode-memory-handling; do
  rm -rf "$DEST/$skill"
  cp -R "$SCRIPT_DIR/$skill" "$DEST/$skill"
  echo "installed: $DEST/$skill"
done
