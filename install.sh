#!/usr/bin/env bash
set -euo pipefail

# Installs two skills side by side:
#   discovery-guide/    the method. Its folder is the method root: the steps,
#                       the agents, the templates and the scripts live inside it,
#                       at the same relative paths as in this repository.
#   process-interview/  the "after the interview" skill that steps 4a and 7b run.
#                       It finds the scripts in discovery-guide/.

TARGET="${1:-codex}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$TARGET" in
  codex)
    SKILLS="$HOME/.codex/skills"
    ;;
  claude)
    SKILLS="$HOME/.claude/skills"
    ;;
  *)
    echo "Usage: ./install.sh [codex|claude]"
    exit 1
    ;;
esac

DEST="$SKILLS/discovery-guide"
PROCESS="$SKILLS/process-interview"

rm -rf "$DEST" "$PROCESS"
mkdir -p "$DEST" "$PROCESS"

cp -R "$ROOT_DIR/skills/discovery-guide/." "$DEST/"
cp -R "$ROOT_DIR/workflows" "$DEST/workflows"
# The skill keeps its platform file in agents/ (openai.yaml); the method's
# agents go in the same folder, so every step can say agents/council.md.
mkdir -p "$DEST/agents"
cp -R "$ROOT_DIR/agents/." "$DEST/agents/"
cp -R "$ROOT_DIR/templates" "$DEST/templates"
cp -R "$ROOT_DIR/scripts" "$DEST/scripts"

cp -R "$ROOT_DIR/skills/process-interview/." "$PROCESS/"

echo "Installed Design with Empathy and AI into $DEST"
echo "Installed process-interview into $PROCESS"
