#!/usr/bin/env bash
set -euo pipefail

# Local snapshot installer for MPG development.
# Canonical published skills are in Gecode/gecode-skills.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DEFAULT="${HOME}/.codex/skills"
DEST="${1:-${CODEX_HOME:-$DEST_DEFAULT}/skills}"

if [[ "$DEST" == "$HOME/.codex/skills/skills" ]]; then
  DEST="$HOME/.codex/skills"
fi

mkdir -p "$DEST"

echo "Note: canonical published skills are in Gecode/gecode-skills (npx skills add Gecode/gecode-skills)."
echo "Installing MPG snapshot copies into: $DEST"

for skill in \
  gecode-general-knowledge \
  gecode-modeling \
  gecode-propagator-implementation \
  gecode-brancher-implementation \
  gecode-memory-handling \
  gecode-search-engines \
  gecode-search-engine-implementation; do
  rm -rf "$DEST/$skill"
  cp -R "$SCRIPT_DIR/$skill" "$DEST/$skill"
  echo "installed: $DEST/$skill"
done
