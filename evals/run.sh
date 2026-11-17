#!/usr/bin/env bash
# Evaluate the toolsmith skill against a baseline. See evals/run.py --help.
exec python3 "$(dirname "${BASH_SOURCE[0]}")/run.py" "$@"
