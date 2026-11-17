#!/usr/bin/env bash
# Install the toolsmith skill.
#
#   curl -fsSL https://raw.githubusercontent.com/Scorbutics/agentic-toolsmith/main/install.sh | bash
#   ./install.sh                 # from a clone of this repository
#
# Options:
#   --project        install into this project (./.claude/skills/, or ./.github/skills/ with --copilot)
#   --copilot        install for GitHub Copilot: ~/.copilot/skills/ (or ./.github/skills/ with --project)
#   --all            install for both Claude Code and GitHub Copilot
#   --dir DIR        install into DIR/toolsmith
#   --ref REF        git ref to install from GitHub (default: main); ignored when run from a clone
#   --uninstall      remove the installed skill
#   -h, --help       show this help
set -euo pipefail

REPO="Scorbutics/agentic-toolsmith"
REF="main"
PROJECT=0
TARGETS="claude"
DIR_OVERRIDE=""
UNINSTALL=0

usage() { sed -n '2,/^set -e/{s/^# \{0,1\}//;/^set -e/d;p}' "${BASH_SOURCE[0]:-$0}" 2>/dev/null || true; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)   PROJECT=1; shift ;;
    --copilot)   TARGETS="copilot"; shift ;;
    --all)       TARGETS="claude copilot"; shift ;;
    --dir)       DIR_OVERRIDE="$2"; shift 2 ;;
    --ref)       REF="$2"; shift 2 ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help)   usage; exit 0 ;;
    *) echo "install.sh: unknown option $1" >&2; exit 2 ;;
  esac
done

dest_root() {  # where skills live for a harness: Claude Code or GitHub Copilot, personal or project
  if [[ -n "$DIR_OVERRIDE" ]]; then echo "$DIR_OVERRIDE"; return; fi
  case "$1:$PROJECT" in
    claude:0)  echo "${HOME}/.claude/skills" ;;
    claude:1)  echo "$(pwd)/.claude/skills" ;;
    copilot:0) echo "${HOME}/.copilot/skills" ;;
    copilot:1) echo "$(pwd)/.github/skills" ;;
  esac
}

if [[ $UNINSTALL -eq 1 ]]; then
  for t in $TARGETS; do d="$(dest_root "$t")/toolsmith"; rm -rf "$d" && echo "toolsmith: removed ${d}"; done
  exit 0
fi

# Source: this clone if the script runs from one, otherwise a tarball of REF from GitHub.
SRC=""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
if [[ -n "$SCRIPT_DIR" && -f "$SCRIPT_DIR/skills/toolsmith/SKILL.md" ]]; then
  SRC="$SCRIPT_DIR/skills/toolsmith"
  echo "toolsmith: installing from this clone ($SCRIPT_DIR)"
else
  command -v curl >/dev/null || { echo "toolsmith: curl is required" >&2; exit 1; }
  TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
  echo "toolsmith: downloading ${REPO}@${REF}"
  curl -fsSL "https://codeload.github.com/${REPO}/tar.gz/${REF}" | tar -xz -C "$TMP"
  SRC="$(find "$TMP" -maxdepth 3 -type d -path '*/skills/toolsmith' | head -n1)"
  [[ -f "$SRC/SKILL.md" ]] || { echo "toolsmith: SKILL.md not found in the download" >&2; exit 1; }
fi

for t in $TARGETS; do
  DEST="$(dest_root "$t")/toolsmith"
  mkdir -p "$(dirname "$DEST")"
  rm -rf "$DEST"
  cp -R "$SRC" "$DEST"
  chmod +x "$DEST/scripts/"*.py 2>/dev/null || true
  echo "toolsmith: installed for ${t} to ${DEST}"
done

command -v python3 >/dev/null || echo "toolsmith: note — python3 is needed to render review pages (scripts/review_page.py)"

echo
echo "Try it — in any project, start your agent (claude, or copilot) and ask for:"
echo "  /toolsmith map"
echo "  /toolsmith task \"<a fix or feature>\""
echo "  /toolsmith want \"<a capability, e.g. direct DB access from the CLI>\""
