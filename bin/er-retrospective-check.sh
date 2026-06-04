#!/usr/bin/env bash
# bin/er-retrospective-check.sh — codified ER retrospective.
#
# Proves the Extreme Rigor mechanism is LOAD-BEARING by introducing a
# regression and asserting the supervisor catches it:
#
#   1. Snapshot unix-filesystem/UnixInodeFileSystem.py
#   2. Add `\trusted reviewer:` back to `_read_directory` (the
#      method body-verified during Phase 4 gap-closure)
#   3. Run `bin/agent-feature-supervisor --feature-file
#      missing-bytes-struct-feature.md --skip-gate` — must exit 75
#      (ACCEPTANCE_FAILED, because Phase 4's claim of
#      `grep -c "[VERIFIED]" >= 15` breaks: mutating one struct method
#      to `\trusted` drops the body-verified count 15 -> 14, below the
#      floor. The floor must equal the real verified count, else a
#      single-method regression slips under a loose threshold.)
#   4. Restore the snapshot
#   5. Re-run the supervisor — must exit 0 again
#
# Exit codes:
#   0   the mechanism is load-bearing (supervisor halted on the
#       mutation, passed after revert)
#   1   the mechanism is broken (supervisor accepted the mutation OR
#       failed the original-state check)
#   2   prerequisite missing
#
# Referenced from `feature-supervisor-extreme-rigor.md` Phase 8 +
# whole-plan acceptance (gap 11 of the post-implementation
# retrospective).

set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"
cd "$REPO_ROOT"

TARGET="unix-filesystem/UnixInodeFileSystem.py"
PLAN="missing-bytes-struct-feature.md"
SUPERVISOR="bin/agent-feature-supervisor"

if [[ ! -f "$TARGET" ]]; then
    echo "[er-retrospective-check] missing target: $TARGET" >&2
    exit 2
fi
if [[ ! -f "$PLAN" ]]; then
    echo "[er-retrospective-check] missing plan: $PLAN" >&2
    exit 2
fi
if [[ ! -x "$SUPERVISOR" ]]; then
    echo "[er-retrospective-check] supervisor not executable: $SUPERVISOR" >&2
    exit 2
fi

# Step 1: snapshot. We use cp instead of git stash so this works in
# a non-git context too and doesn't disturb the user's stash list.
SNAPSHOT="$(mktemp --tmpdir er-retrospective.XXXXXX.py)"
trap 'cp "$SNAPSHOT" "$TARGET"; rm -f "$SNAPSHOT"' EXIT
cp "$TARGET" "$SNAPSHOT"

# Step 0: confirm baseline state passes.
if ! "$SUPERVISOR" --feature-file "$PLAN" --skip-gate >/dev/null 2>&1; then
    echo "[er-retrospective-check] baseline FAIL: supervisor does not pass on the unmodified plan" >&2
    exit 1
fi

# Step 2: mutate — add `\trusted reviewer:` to _read_directory.
python3 - <<'PY'
import pathlib
p = pathlib.Path("unix-filesystem/UnixInodeFileSystem.py")
text = p.read_text()
# The post-Phase-2.3b _read_directory carries `#@ proof rocq
# UnixFs.Struct.i1a1.round_trip`. Insert a `\trusted reviewer:` marker
# just before it.
marker_old = "    #@ proof rocq UnixFs.Struct.i1a1.round_trip"
marker_new = ("    #@ \\trusted reviewer: pycsl-self-annotate\n"
              "    #@ proof rocq UnixFs.Struct.i1a1.round_trip")
new_text, n = text.replace(marker_old, marker_new, 1), 1
if marker_new not in new_text:
    raise SystemExit("could not locate the _read_directory proof-rocq marker")
p.write_text(new_text)
PY

# Step 3: supervisor MUST halt now.
"$SUPERVISOR" --feature-file "$PLAN" --skip-gate >/dev/null 2>&1
mutated_exit=$?
if [[ $mutated_exit -ne 75 ]]; then
    echo "[er-retrospective-check] FAIL: supervisor exit=$mutated_exit on mutated tree (expected 75)" >&2
    echo "[er-retrospective-check] the ER mechanism did NOT catch the regression" >&2
    exit 1
fi

# Step 4 (via trap): restore snapshot, ensure post-revert state passes.
cp "$SNAPSHOT" "$TARGET"
if ! "$SUPERVISOR" --feature-file "$PLAN" --skip-gate >/dev/null 2>&1; then
    echo "[er-retrospective-check] FAIL: supervisor does not pass after revert" >&2
    exit 1
fi

echo "[er-retrospective-check] PASS — ER mechanism is load-bearing"
echo "  baseline: exit 0"
echo "  mutated:  exit 75 (ACCEPTANCE_FAILED on the mutation)"
echo "  reverted: exit 0"
exit 0
