#!/usr/bin/env sh
# Install the agentic toolbox into a codebase.
#
# One-liner (run from the root of the target repo):
#   curl -fsSL https://raw.githubusercontent.com/dphillip11/agentic_toolbox/main/install.sh | sh
#
# Or from a local checkout of the toolbox:
#   ./install.sh [/path/to/target/repo]   (defaults to the current directory)
set -eu

# Overridable for forks/testing: AGENTIC_TOOLBOX_TARBALL=<url|file> sh install.sh
REPO_TARBALL="${AGENTIC_TOOLBOX_TARBALL:-https://github.com/dphillip11/agentic_toolbox/archive/refs/heads/main.tar.gz}"

# --- resolve destination -----------------------------------------------------
DEST="$(cd "${1:-.}" && pwd)"

# --- resolve source ----------------------------------------------------------
# If we're running from a checkout of the toolbox, use it. Otherwise (curl-
# piped), download the tarball into a temp dir.
TMPDIR_CREATED=""
SCRIPT_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd || pwd)"
if [ -f "$0" ] && [ -f "$SCRIPT_DIR/.agentic/scripts/kb_build.py" ] \
   && [ -f "$SCRIPT_DIR/skills/initialise/SKILL.md" ]; then
  SRC="$SCRIPT_DIR"
else
  TMPDIR_CREATED="$(mktemp -d)"
  trap 'rm -rf "$TMPDIR_CREATED"' EXIT
  echo "fetching agentic_toolbox ..."
  if [ -f "$REPO_TARBALL" ]; then
    tar -xz -C "$TMPDIR_CREATED" -f "$REPO_TARBALL"
  else
    curl -fsSL "$REPO_TARBALL" | tar -xz -C "$TMPDIR_CREATED"
  fi
  SRC="$(find "$TMPDIR_CREATED" -maxdepth 1 -mindepth 1 -type d | head -n 1)"
  if [ -z "$SRC" ] || [ ! -f "$SRC/.agentic/scripts/kb_build.py" ]; then
    echo "error: downloaded archive does not look like the agentic toolbox" >&2
    exit 1
  fi
fi

if [ "$SRC" = "$DEST" ]; then
  echo "target is the toolbox itself; aborting" >&2
  exit 1
fi

if [ ! -d "$DEST/.git" ]; then
  echo "warning: $DEST is not a git repository root" >&2
fi

# --- copy toolbox files (never overwrites an existing env.json / kb) ---------
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

# --- bootstrap kb tooling ----------------------------------------------------
if command -v python3 >/dev/null 2>&1; then
  echo "setting up .agentic/.venv ..."
  if python3 -m venv "$DEST/.agentic/.venv" 2>/dev/null; then
    "$DEST/.agentic/.venv/bin/pip" install -q -r "$DEST/.agentic/scripts/requirements.txt" \
      && echo "kb tooling ready (.agentic/.venv)" \
      || echo "warning: pip install failed — run it manually later" >&2
  else
    echo "warning: could not create venv — install deps manually:" >&2
    echo "  pip install -r .agentic/scripts/requirements.txt" >&2
  fi
else
  echo "warning: python3 not found — kb scripts need Python 3.10+" >&2
fi

echo ""
echo "toolbox installed into $DEST"
echo "next: open your agent (opencode) here and say: initialise this repo"
