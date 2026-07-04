#!/bin/bash
# Checks that the self-annotation mirror (src/self-annotate/src/) stays faithful to the live
# emitter (src/pycsl/). Exit 1 on any drift.
#
# The mirror is HETEROGENEOUS: un-\trusted methods are verbatim copies of the live emitter
# (+ #@ annotations), while \trusted methods are intentionally-divergent bodyless stubs. So a
# whole-file diff is the wrong tool — the load-bearing invariant is method-level: every
# un-\trusted mirror method == the same-named live emitter method. `check-self-annotate-mirror-
# sync.py` enforces exactly that over the whole mirror tree.
#
# (This supersedes the old whole-file rocq/lean tier, which pointed at empty, never-populated
# directories with module paths that predated the frontend/ refactor — resync-campaign.md.)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 "$SCRIPT_DIR/check-self-annotate-mirror-sync.py"
