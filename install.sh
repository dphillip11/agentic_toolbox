#!/usr/bin/env sh
# Copy the agentic toolbox into a target repository.
#
# Usage: ./install.sh /path/to/target/repo
set -eu

if [ $# -ne 1 ]; then
  echo "usage: $0 /path/to/target/repo" >&2
  exit 1
fi

SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="$(cd "$1" && pwd)"

if [ "$SRC" = "$DEST" ]; then
  echo "target is the toolbox itself; aborting" >&2
  exit 1
fi

if [ ! -d "$DEST/.git" ]; then
  echo "warning: $DEST is not a git repository root" >&2
fi

# Toolbox scripts and templates (never overwrite an existing env.json / kb)
mkdir -p "$DEST/.agentic/scripts" "$DEST/.agentic/templates"
cp "$SRC/.agentic/scripts/kb_build.py" \
   "$SRC/.agentic/scripts/kb_query.py" \
   "$SRC/.agentic/scripts/requirements.txt" \
   "$DEST/.agentic/scripts/"
cp "$SRC/.agentic/templates/env.json" \
   "$SRC/.agentic/templates/agentic.yml" \
   "$DEST/.agentic/templates/"

# Skills
mkdir -p "$DEST/skills"
cp -R "$SRC/skills/initialise" "$SRC/skills/ingest" "$SRC/skills/dev-task" \
      "$DEST/skills/"

# opencode config: create if absent, otherwise leave for the user to merge
if [ ! -f "$DEST/opencode.jsonc" ] && [ ! -f "$DEST/opencode.json" ]; then
  cp "$SRC/opencode.jsonc" "$DEST/opencode.jsonc"
  echo "created opencode.jsonc"
else
  echo "opencode config already exists — ensure skills.paths includes \"skills\""
fi

# gitignore the kb venv
if [ -f "$DEST/.gitignore" ]; then
  grep -q '^\.agentic/\.venv/$' "$DEST/.gitignore" || \
    printf '\n.agentic/.venv/\n' >> "$DEST/.gitignore"
else
  printf '.agentic/.venv/\n' > "$DEST/.gitignore"
fi

echo "toolbox installed into $DEST"
echo "next: open opencode in $DEST and run the 'initialise' skill"
