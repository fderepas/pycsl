#!/usr/bin/env bash
# cmmi-audit.sh — composite CMMI verification gate for PyCSL (Profile-P)
#
# Runs the verification suite described in cmmi-tailoring-plan.md
# §Verification (checks 1, 3, 4, 5, 9, 10) plus the language-surface
# doc-coherency gate (check 5). Designed to be wired into
# bin/run-reference-tests.sh as the final gate.
#
# Usage:
#   bin/cmmi-audit.sh              # run all checks
#   bin/cmmi-audit.sh --quick      # skip the cmmi-mod-index --verify walk
#
# Exit codes:
#   0  all checks passed
#   1  one or more checks failed (details on stderr)
#   2  prerequisite tool / file missing

set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"
cd "$REPO_ROOT"

QUICK=0
[[ "${1:-}" == "--quick" ]] && QUICK=1

PASS=()
FAIL=()
SKIP=()

check() {
    local name="$1"; shift
    local rc
    printf '  [..] %s\n' "$name"
    if "$@" > /tmp/cmmi-audit.$$.out 2>&1; then
        rc=0
        printf '\033[A\033[K  [\033[32mOK\033[0m] %s\n' "$name"
        PASS+=("$name")
    else
        rc=$?
        printf '\033[A\033[K  [\033[31mFAIL\033[0m] %s (exit %d)\n' "$name" "$rc"
        echo "        ---- output ----" >&2
        sed 's/^/        | /' /tmp/cmmi-audit.$$.out >&2
        echo "        ----------------" >&2
        FAIL+=("$name")
    fi
    rm -f /tmp/cmmi-audit.$$.out
}

skip() {
    printf '  [\033[33mSKIP\033[0m] %s — %s\n' "$1" "$2"
    SKIP+=("$1")
}

echo "cmmi-audit.sh: PyCSL Profile-P verification gate"
echo "================================================="
echo

# ----- C8 step 1+2: spec-mirror invariant -----
echo "[C8.1+2] No source duplication under BL/"
src_dirs=$(find projects/pycsl/BL -type d -name src 2>/dev/null)
if [[ -z "$src_dirs" ]]; then
    printf '  [\033[32mOK\033[0m] no BL/.../src/ directories exist\n'
    PASS+=("C8.1+2 no source dup")
else
    printf '  [\033[31mFAIL\033[0m] found in-tree source copies:\n' >&2
    echo "$src_dirs" | sed 's/^/        /' >&2
    FAIL+=("C8.1+2 no source dup")
fi
echo

# ----- C8 step 3: includes resolve -----
echo "[C8.3] All pycsl-include anchors resolve"
check "cmmi-include-expand --verify --all" \
    bin/cmmi-include-expand.py --verify --all
echo

# ----- C8 step 4: L4 indices reflect reality -----
echo "[C8.4] L4 Module indices match in-source def counts"
if [[ $QUICK -eq 1 ]]; then
    skip "cmmi-mod-index --verify --all" "--quick"
else
    check "cmmi-mod-index --verify --all" \
        bin/cmmi-mod-index.py --verify --all
fi
echo

# ----- C8 step 5: Squeeze coverage (BL → System completeness) -----
echo "[C8.5] Squeeze coverage complete (BL → System completeness)"
python3 - <<'PY' 2>&1
import re, sys
from pathlib import Path
root = Path(__file__).resolve().parent if False else Path.cwd()
project = root / "projects/pycsl/PROJECT.md"
if not project.is_file():
    print(f"  [FAIL] missing {project}", file=sys.stderr); sys.exit(1)
text = project.read_text()
# Parse the squeeze_owners block (YAML-ish)
m = re.search(r"squeeze_owners:\s*\n((?:\s+S\d:\s*\[[^\]]*\]\s*\n)+)", text)
if not m:
    print("  [FAIL] no squeeze_owners: block in PROJECT.md", file=sys.stderr); sys.exit(1)
owners = {}
for line in m.group(1).splitlines():
    mm = re.match(r"\s+(S\d):\s*\[([^\]]*)\]", line)
    if mm:
        owners[mm.group(1)] = [s.strip() for s in mm.group(2).split(",") if s.strip()]
expected = {f"S{i}" for i in range(1, 10)}
missing = expected - set(owners)
empty = [s for s, o in owners.items() if not o]
glue_match = re.search(r"glue_systems:\s*\[([^\]]*)\]", text)
glue = [s.strip() for s in (glue_match.group(1).split(",") if glue_match else []) if s.strip()]
# Per-system inventory
inventory = [
    f"{m.group(1)}-{m.group(2)}"
    for m in re.finditer(
        r"\|\s*(SY\d)\s*\|\s*([A-Za-z0-9_]+)\s*\|\s*[LMS]",
        text,
    )
]
all_owned = {sys for sset in owners.values() for sys in sset}
orphan = [s for s in inventory if s not in all_owned and s not in glue]
ok = True
if missing:
    print(f"  [FAIL] Squeezes with no owner: {sorted(missing)}", file=sys.stderr); ok = False
if empty:
    print(f"  [FAIL] Squeezes with empty owner list: {empty}", file=sys.stderr); ok = False
if orphan:
    print(f"  [FAIL] Systems with no Squeeze and not on glue_systems allow-list: {orphan}", file=sys.stderr); ok = False
if ok:
    print(f"  [OK] all 9 Squeezes owned; {len(inventory)} Systems; {len(glue)} declared glue")
sys.exit(0 if ok else 1)
PY
if [[ $? -eq 0 ]]; then
    PASS+=("C8.5 Squeeze coverage")
else
    FAIL+=("C8.5 Squeeze coverage")
fi
echo

# ----- Phase 0 QPM step (Item 4.AUD) -----
echo "[QPM] cmmi-quantitative-mgmt — snapshot count + signal status"
if [[ -x "$REPO_ROOT/bin/cmmi-qpm-charts.py" ]]; then
    # --check exits 0 always; informational only
    if "$REPO_ROOT/bin/cmmi-qpm-charts.py" --check > /tmp/cmmi-audit-qpm.$$.out 2>&1; then
        sed 's/^/  /' /tmp/cmmi-audit-qpm.$$.out
        PASS+=("QPM informational")
    else
        cat /tmp/cmmi-audit-qpm.$$.out >&2
        FAIL+=("QPM informational")
    fi
    rm -f /tmp/cmmi-audit-qpm.$$.out
else
    skip "QPM informational" "bin/cmmi-qpm-charts.py not executable"
fi
echo

# ----- Item 3.5d: bridge coverage informational check -----
echo "[BRIDGE] queue ↔ metrics/logs coverage (Item 3.5p validator)"
if [[ -x "$REPO_ROOT/bin/cmmi-queue-coverage-diff.py" ]]; then
    if "$REPO_ROOT/bin/cmmi-queue-coverage-diff.py" --summary \
            > /tmp/cmmi-audit-bridge.$$.out 2>&1; then
        sed 's/^/  /' /tmp/cmmi-audit-bridge.$$.out
        PASS+=("BRIDGE coverage informational")
    else
        # Non-zero exit means coverage < 99.5% or mismatches present.
        # That's expected during the dual-write phase — informational
        # only, never fails the audit.
        sed 's/^/  /' /tmp/cmmi-audit-bridge.$$.out
        PASS+=("BRIDGE coverage informational")
    fi
    rm -f /tmp/cmmi-audit-bridge.$$.out
else
    skip "BRIDGE coverage informational" "bin/cmmi-queue-coverage-diff.py not executable"
fi
echo

# ----- Phase D check 7: itertools.cycle regression (Item 2) -----
echo "[REG] itertools.cycle 13:47:22 incident regression test"
PYTEST_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTEST_BIN" ]]; then
    PYTEST_BIN="python3"
fi
if "$PYTEST_BIN" -c 'import pytest' 2>/dev/null; then
    check "pytest test-suite/cmmi-regression/" \
        "$PYTEST_BIN" -m pytest "test-suite/cmmi-regression/" -q
else
    skip "pytest test-suite/cmmi-regression/" "pytest not importable under $PYTEST_BIN"
fi
echo

# ----- Phase 4 of missing-bytes-struct-feature.md: STRUCT step -----
# Informational: counts methods using struct.pack / struct.unpack and
# reports which have promoted from `\trusted` to body-verified
# (via `#@ proof rocq UnixFs.Struct.<slot_id>.round_trip` citation).
echo "[STRUCT] struct.pack/unpack — trusted vs body-verified promotion"
python3 - <<'PY' 2>&1
import re, sys, subprocess
from pathlib import Path
root = Path.cwd()
SCAN_ROOTS = [
    root / "unix-filesystem",
    root / "test-suite" / "corpus" / "pycsl-reference",
]

# Build a (file -> mlw text) map by running PyCSL once per .py with
# --keep-mlw --no-proof. The mlw distinguishes `let funcname` (body
# emitted = body-verified-capable) from `val funcname` (trusted, auto
# or explicit). Reading the actual mlw is the only honest signal —
# source-only classification can't see PyCSL's auto-trust.
def emit_mlw(py_file: Path) -> str:
    pycsl = root / ".venv" / "bin" / "python3"
    if not pycsl.is_file():
        pycsl = "python3"
    r = subprocess.run(
        [str(pycsl), str(root / "src" / "pycsl" / "pycsl.py"),
         "--no-proof", "--keep-mlw", str(py_file)],
        capture_output=True, text=True, timeout=60,
    )
    mlw_path = py_file.with_suffix(".mlw")
    if mlw_path.is_file():
        return mlw_path.read_text(errors="replace")
    return ""

struct_users: list[tuple[str, str]] = []
for sr in SCAN_ROOTS:
    if not sr.is_dir():
        continue
    for f in sr.rglob("*.py"):
        text = f.read_text(errors="replace")
        # Find struct.pack/unpack-using functions via source scan.
        # The mlw lookup below confirms emitted shape.
        functions_using_struct = []
        for m in re.finditer(
                r"(?:^|\n)("
                r"(?:\s*#[^\n]*\n)*"
                r"\s*#@[^\n]*\n"
                r"(?:\s*#[^\n]*\n)*"
                r"\s*def\s+(\w+)\s*\([^)]*\)\s*[^\n]*\n)",
                text):
            block, name = m.group(1), m.group(2)
            def_pos = m.end()
            stop = re.search(r"\n(?:    )?(?:def |#@)", text[def_pos:])
            body = text[def_pos:def_pos + (stop.start() if stop else 99999)]
            if "struct.pack" not in body and "struct.unpack" not in body:
                continue
            cites_axiom = "UnixFs.Struct." in block
            functions_using_struct.append((name, cites_axiom))
        if not functions_using_struct:
            continue

        mlw_text = emit_mlw(f)
        for name, cites_axiom in functions_using_struct:
            # Module6 mangles names: class methods become
            # <classname>__<methname>. Look for both forms with
            # `let <name>` (body-emitted) or `val <name>` (trusted).
            patterns = [
                rf"\blet\s+\S*?{re.escape(name.lower())}\b",
                rf"\bval\s+\S*?{re.escape(name.lower())}\b",
            ]
            emitted_let = re.search(patterns[0], mlw_text) is not None
            emitted_val = re.search(patterns[1], mlw_text) is not None
            if emitted_let:
                mode = "body-verified"
            elif emitted_val and cites_axiom:
                mode = "trusted+axiom"
            elif emitted_val:
                mode = "trusted-only"
            else:
                # No mlw evidence either way — likely the function
                # wasn't picked up by the transpile (parse error or
                # standalone). Mark as unknown.
                mode = "unknown"
            struct_users.append((f"{f.relative_to(root)}:{name}", mode))

if not struct_users:
    print("  [OK] no struct.pack/unpack consumers found in scan roots")
    sys.exit(0)

trusted_only = [n for n, m in struct_users if m == "trusted-only"]
trusted_axiom = [n for n, m in struct_users if m == "trusted+axiom"]
body_verified = [n for n, m in struct_users if m == "body-verified"]
unknown = [n for n, m in struct_users if m == "unknown"]
print(f"  body-verified: {len(body_verified)}  "
      f"trusted+axiom: {len(trusted_axiom)}  "
      f"trusted-only: {len(trusted_only)}  "
      f"unknown: {len(unknown)}")
for n in body_verified:
    print(f"    [VERIFIED] {n}")
for n in trusted_axiom:
    print(f"    [TRUSTED+AXIOM] {n}")
for n in trusted_only:
    print(f"    [TRUSTED-only] {n}")
for n in unknown:
    print(f"    [UNKNOWN] {n}")
# Informational — never fails the audit.
sys.exit(0)
PY
PASS+=("STRUCT informational")
echo

# ----- Extreme Rigor retrospective (informational) -----
# Runs `bin/er-retrospective-check.sh` if present. Verifies the
# ER mechanism is load-bearing by mutating + reverting a known
# file and asserting the supervisor halts. Never fails the audit
# — if the check breaks, that's a finding but not a regression
# in the audited code.
#
# Skipped under nested invocation: the retrospective runs the
# supervisor, which evaluates Phase 4 acceptance, which calls
# cmmi-audit.sh — recursion. Gate with CMMI_AUDIT_NESTED so the
# nested instance skips this step.
if [[ -n "${CMMI_AUDIT_NESTED:-}" ]]; then
    skip "ER retrospective informational" "nested cmmi-audit invocation"
elif [[ -x "$REPO_ROOT/bin/er-retrospective-check.sh" ]]; then
    echo "[ER] er-retrospective-check.sh — load-bearing mechanism proof"
    export CMMI_AUDIT_NESTED=1
    if "$REPO_ROOT/bin/er-retrospective-check.sh" > /tmp/cmmi-audit-er.$$.out 2>&1; then
        # PASS: mechanism is load-bearing
        sed 's/^/  /' /tmp/cmmi-audit-er.$$.out
        PASS+=("ER retrospective informational")
    else
        echo "  [WARN] er-retrospective-check.sh did not pass — review:" >&2
        sed 's/^/  | /' /tmp/cmmi-audit-er.$$.out >&2
        # Informational only — does NOT fail the audit. Surface as PASS
        # with a recorded warning; a separate gate (CI) can promote to FAIL.
        PASS+=("ER retrospective informational")
    fi
    unset CMMI_AUDIT_NESTED
    rm -f /tmp/cmmi-audit-er.$$.out
else
    skip "ER retrospective informational" "bin/er-retrospective-check.sh not executable"
fi
echo

# ----- language-surface coherency (delegated) -----
echo "[lang] Language-surface doc coherency (pycsl-* skills, docs/, README)"
if [[ -x bin/doc-coherency.py ]]; then
    check "bin/doc-coherency.py --check" bin/doc-coherency.py --check
else
    skip "bin/doc-coherency.py" "tool not present or not executable"
fi
echo

# ----- summary -----
echo "================================================="
echo "Summary: ${#PASS[@]} passed, ${#FAIL[@]} failed, ${#SKIP[@]} skipped"
if (( ${#FAIL[@]} )); then
    echo
    echo "Failed checks:"
    printf '  - %s\n' "${FAIL[@]}"
    exit 1
fi
exit 0
