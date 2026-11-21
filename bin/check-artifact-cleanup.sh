#!/usr/bin/env bash
# check-artifact-cleanup.sh — L-PLANE ORACLE for the build-exhaust epilogue of
# `bin/check-proof-reverify.sh`.
#
# WHY THIS EXISTS. The axiom-footprint gate recompiles cited Rocq/Lean proofs IN PLACE, so
# a run dirties TRACKED artifacts and creates UNTRACKED ones. 990 build artifacts are
# tracked in this repository (611 `.aux`, 94 each of `.vo`/`.vok`/`.vos`/`.glob`, 3
# `.olean`), and gen #30 came within one command of clearing the exhaust with a glob aimed
# at the same directory — an `rm -f .../rocq/.tmp*.aux` that DELETED SEVERAL HUNDRED
# TRACKED FILES. Gen #31 gave the gate a self-cleaning epilogue. An epilogue that restores
# files is exactly the kind of code that must never be believed from a reading: its
# dangerous direction is SILENT (it discards a change nobody asked it to discard), and the
# only run that shows it is the run where somebody was mid-edit.
#
# THIS PLANE RUNS THE SHIPPED LINES, not a copy: it EXTRACTS the block between `set -u` and
# `trap _art_restore EXIT` out of `bin/check-proof-reverify.sh`, so an edit that renames the
# function or moves the trap makes the extraction fail and this gate REFUSE (rc=2) rather
# than pass over a hole. It then drives that block against a throwaway git repository.
#
# THE CASE THAT CAUGHT A REAL DEFECT (case 7). The first draft keyed the snapshot on the
# whole `git status` LINE. A file that was already ` M` when the run started and that the
# run then DELETED came back as ` D` — a different line, so the epilogue did not recognise
# the path as pre-existing and RESURRECTED it, writing committed content over a tree state
# the user owned. The snapshot is now keyed on the PATH. The epilogue cannot recover an edit
# the GATE destroyed; what it must never do is act on that path at all.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATE="$ROOT/bin/check-proof-reverify.sh"
[ -f "$GATE" ] || { echo "[!] artifact-cleanup: $GATE is missing." >&2; exit 2; }

TMP="$(mktemp -d)"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

python3 - "$GATE" "$TMP/epilogue.sh" <<'PYEOF'
import sys
src = open(sys.argv[1], encoding="utf-8").read()
try:
    start = src.index("set -u\nPROJECT_ROOT=")
    end = src.index("trap _art_restore EXIT\n") + len("trap _art_restore EXIT\n")
except ValueError:
    sys.stderr.write(
        "[!] artifact-cleanup: could not find the epilogue block in check-proof-reverify.sh\n"
        "    (expected `set -u` + `PROJECT_ROOT=` ... `trap _art_restore EXIT`).\n"
        "    The gate was restructured; UPDATE THIS PLANE rather than deleting it — an\n"
        "    unextractable epilogue is an UNTESTED one.\n")
    sys.exit(2)
block = src[start:end].replace(
    'PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"',
    'PROJECT_ROOT="$1"')
if "_art_restore" not in block or "_ART_SCOPE" not in block:
    sys.stderr.write("[!] artifact-cleanup: the extracted block is not the epilogue.\n")
    sys.exit(2)
open(sys.argv[2], "w", encoding="utf-8").write("#!/usr/bin/env bash\n" + block + """
# --- simulate exactly what a recompiling gate does to the tree ---
D=test-suite/corpus/pycsl-reference/0342.proofs/rocq
echo GATE  > $D/c1_clean_modified.aux      # clean before -> the epilogue must RESTORE
rm -f       $D/c2_clean_deleted.aux        # clean before -> the epilogue must RESTORE
rm -f       $D/c7_predirty_deleted.aux     # DIRTY before -> the epilogue must NOT resurrect
echo NEW   > $D/c5_gate_untracked.aux      # created here -> the epilogue must REMOVE
echo TOUCH > unix-filesystem/build.vo      # clean before -> the epilogue must RESTORE
mkdir -p .audit-cache && echo C > .audit-cache/entry.json   # new untracked DIR -> DECLINE
exit 7
""")
PYEOF
rc=$?; [ "$rc" -eq 0 ] || exit 2

REPO="$TMP/repo"
mkdir -p "$REPO/test-suite/corpus/pycsl-reference/0342.proofs/rocq" \
         "$REPO/test-suite/corpus/python-reference" "$REPO/unix-filesystem"
cd "$REPO"
git init -q .
D=test-suite/corpus/pycsl-reference/0342.proofs/rocq
echo BASE > "$D/c1_clean_modified.aux"
echo BASE > "$D/c2_clean_deleted.aux"
echo BASE > "$D/c3_predirty_untouched.aux"
echo BASE > "$D/c7_predirty_deleted.aux"
echo BASE > unix-filesystem/build.vo
git add -A && git -c user.email=t@t -c user.name=t commit -qm init

echo "USER-EDIT" > "$D/c3_predirty_untouched.aux"   # must survive VERBATIM
echo "USER-EDIT" > "$D/c7_predirty_deleted.aux"     # the gate deletes it; see case 7
echo "USER-NEW"  > "$D/c4_user_untracked.aux"       # pre-existing untracked -> KEEP

bash "$TMP/epilogue.sh" "$REPO" > "$TMP/run.out" 2>&1
grc=$?

fail=0
chk() {
    if [ "$2" != "$3" ]; then
        echo "[-] artifact-cleanup: $1" >&2
        echo "      expected: $2" >&2
        echo "      actual:   $3" >&2
        fail=1
    fi
}
state() { if [ -f "$1" ]; then cat "$1"; else echo "<absent>"; fi; }

if [ "$grc" -ne 7 ]; then
    echo "[-] artifact-cleanup: the epilogue changed the gate's exit code ($grc, expected 7)." >&2
    echo "    A cleanup trap that swallows a FAILING gate's status turns red into green." >&2
    fail=1
fi

chk "case 1 — a tracked file the run MODIFIED was not restored" \
    "BASE" "$(state "$D/c1_clean_modified.aux")"
chk "case 2 — a tracked file the run DELETED was not restored" \
    "BASE" "$(state "$D/c2_clean_deleted.aux")"
chk "case 6 — a tracked artifact outside the corpus tree was not restored" \
    "BASE" "$(state unix-filesystem/build.vo)"
chk "case 3 — a PRE-EXISTING EDIT was discarded (the destructive direction)" \
    "USER-EDIT" "$(state "$D/c3_predirty_untouched.aux")"
chk "case 7 — a path that was ALREADY DIRTY was resurrected by the epilogue" \
    "<absent>" "$(state "$D/c7_predirty_deleted.aux")"
chk "case 4 — a PRE-EXISTING UNTRACKED file was deleted" \
    "USER-NEW" "$(state "$D/c4_user_untracked.aux")"
chk "case 5 — the run's OWN untracked exhaust was left behind" \
    "<absent>" "$(state "$D/c5_gate_untracked.aux")"
chk "case 8 — a NEW untracked directory was removed (a pattern delete wearing a path)" \
    "C" "$(state .audit-cache/entry.json)"
grep -q "left 1 new untracked" "$TMP/run.out" || {
    echo "[-] artifact-cleanup: the declined untracked directory was not REPORTED." >&2
    echo "    Silently leaving exhaust behind is how the next run inherits a dirty tree." >&2
    fail=1; }

if [ "$fail" -ne 0 ]; then
    echo "--- epilogue output ---" >&2; sed 's/^/    /' "$TMP/run.out" >&2
    echo "--- final status ---" >&2; git status --porcelain | sed 's/^/    /' >&2
    exit 1
fi
echo "[*] artifact-cleanup: 8 cases — restore-modified, restore-deleted, restore-other-tree,"
echo "    keep-pre-dirty, keep-pre-untracked, remove-own-exhaust, never-resurrect-pre-dirty,"
echo "    decline-and-report-new-untracked-dir."
echo "[+] artifact-cleanup: OK — the reverify gate cleans exactly its own exhaust."
exit 0
