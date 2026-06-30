#!/usr/bin/env bash
# per-run-certificate.sh — the-finishable-path.md Step 5 (D3 #1), achievable form.
#
# A per-compile coherence CERTIFICATE (translation-validation flavored). For the
# given input it derives the Module-5 IR statement kinds and reports, per kind,
# whether the emitter that lowers it is backed by:
#   • a machine-checked coherence LEMMA   (pycsl-wp-spec.mlw, Z3-discharged), or
#   • a human-audited coherence AXIOM      (sound, Z3 times out on the case-split), or
#   • NO WP arm yet → audited-trusted      (rides on LINK-2 only).
#
# This is the "achievable" half of D3 #1: it certifies, for THIS run, that every
# construct the input emits lies inside the validated/audited set, and names any
# construct that is NOT yet backed by a coherence lemma. It does NOT yet do the
# full byte-level per-run check (run the Rocq-extracted emit_stmt_full_complete on
# this input's serialized stmt_ir and diff) — that needs the OCaml driver to ingest
# an arbitrary stmt_ir on stdin (today it iterates the fixed cases.txt). That driver
# extension is the remaining research-grade step; see the TODO at the end.
#
# Usage:  bin/per-run-certificate.sh <source.py> [--json]
# Exits:  0 = every construct backed by a lemma or audited axiom (no surprises)
#         3 = input emits a construct with no WP arm (audited-trusted) — informational, still 0-able via --lenient
#         2 = setup error (IR dump failed)
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PY="${ROOT}/.venv/bin/python3"; [ -x "$PY" ] || PY=python3
SRC="${1:-}"; JSON=0; [ "${2:-}" = "--json" ] && JSON=1
if [ -z "$SRC" ] || [ ! -f "$SRC" ]; then echo "usage: $0 <source.py> [--json]" >&2; exit 2; fi

IR_FILE="$(mktemp -t per-run-cert.XXXX.json)"
trap 'rm -f "$IR_FILE"' EXIT
$PY "$ROOT/bin/pycsl-ir-dump.py" "$SRC" --resolved >"$IR_FILE" 2>/dev/null \
  || { echo "[error] IR dump failed for $SRC" >&2; exit 2; }

# NB: pass the IR via a file (env IR_FILE), NOT a pipe — a heredoc `<<` overrides
# a pipe for stdin, so `echo "$IR" | py - <<EOF` would feed py its own source.
SRC="$SRC" JSON="$JSON" IR_FILE="$IR_FILE" "$PY" - <<'PYEOF'
import json, os, re, sys
ir = open(os.environ["IR_FILE"]).read()
src = os.environ["SRC"]; as_json = os.environ["JSON"] == "1"

# IR stmt-kind  →  (arm-coverage decision, coherence symbol)
# Mirrors src/self-annotate/arm-coverage.md.  LEMMA = Z3-checked; AXIOM = audited; TRUSTED = no WP arm.
ARM = {
    "Assign":          ("LEMMA",   "assign_code_state_coherent"),
    "AugAssign":       ("LEMMA",   "aug_assign_code_state_coherent"),
    "If":              ("LEMMA",   "if_code_state_coherent"),
    "While":           ("LEMMA",   "while_code_state_coherent"),
    "For":             ("LEMMA",   "for_code_state_coherent"),
    "Continue":        ("LEMMA",   "continue_code_state_coherent"),
    "Return":          ("LEMMA",   "return_plain_code_state_coherent"),
    "ArraySet":        ("AXIOM",   "array_set_code_state_coherent"),
    "Pass":            ("AXIOM",   "skip_code_state_coherent"),
    # Implicit sequencing of a block is the SSeq arm (audited axiom).
    "_seq":            ("AXIOM",   "seq_code_state_coherent"),
    # No base-WP arm yet — explicitly audited-trusted (LINK-2 only).
    "FieldAssign":     ("TRUSTED", "(no WP arm)"),
    "FieldAugAssign":  ("TRUSTED", "(no WP arm)"),
    "ArraySliceSet":   ("TRUSTED", "(no WP arm)"),
    "TupleUnpack":     ("TRUSTED", "(desugars to SSeq∘SAssign)"),
    "CriticalSection": ("TRUSTED", "(concurrency — out of base model)"),
    "GhostAssign":     ("TRUSTED", "(ghost — erased at extraction)"),
    "GhostArraySet":   ("TRUSTED", "(ghost — erased)"),
    "Expr":            ("TRUSTED", "(expression statement / SCall)"),
    "Try":             ("TRUSTED", "(exceptions)"),
    "Raise":           ("TRUSTED", "(exceptions)"),
    "Match":           ("TRUSTED", "(desugars to SIf chain)"),
    "Break":           ("TRUSTED", "(loop break)"),
    "Label":           ("TRUSTED", "(ghost label)"),
    "ProofAssert":     ("TRUSTED", "(proof assertion)"),
}

kinds = sorted(set(re.findall(r'"stmt":\s*"([A-Za-z_]+)"', ir)))
rows, has_seq = [], '";\\n"' in ir or len(kinds) > 1   # >1 stmt ⇒ sequencing present
for k in kinds:
    cls, sym = ARM.get(k, ("TRUSTED", "(unmodeled kind — audited-trusted)"))
    rows.append((k, cls, sym))
if has_seq:
    rows.append(("<block-seq>",) + ARM["_seq"])

n_lemma  = sum(1 for _, c, _ in rows if c == "LEMMA")
n_axiom  = sum(1 for _, c, _ in rows if c == "AXIOM")
n_trust  = sum(1 for _, c, _ in rows if c == "TRUSTED")
verdict  = "CLEAN" if n_trust == 0 else "AUDITED-TRUSTED-CONSTRUCTS-PRESENT"

if as_json:
    print(json.dumps({
        "source": src, "verdict": verdict,
        "link2": "bin/extraction-byte-diff.sh (Rocq emit_stmt_full_complete ≡ Python _stmts_to_whyml), 26 cases",
        "constructs": [{"kind": k, "class": c, "coherence": s} for k, c, s in rows],
        "counts": {"lemma": n_lemma, "audited_axiom": n_axiom, "audited_trusted": n_trust},
    }, indent=2))
else:
    print(f"┌─ per-run coherence certificate ─ {src}")
    print(f"│  LINK-2 bridge: bin/extraction-byte-diff.sh (26 cases, emit_stmt_full_complete ≡ Python)")
    print(f"│  constructs emitted, by coherence backing:")
    for k, c, s in rows:
        mark = {"LEMMA": "✓ lemma ", "AXIOM": "~ axiom ", "TRUSTED": "! trusted"}[c]
        print(f"│    {mark}  {k:16s} {s}")
    print(f"│  counts: {n_lemma} lemma-backed, {n_axiom} audited-axiom, {n_trust} audited-trusted(no-arm)")
    print(f"└─ verdict: {verdict}")

sys.exit(0 if n_trust == 0 else 3)
PYEOF
rc=$?
# Lenient mode: treat audited-trusted constructs as informational (still useful as a record).
[ "${PER_RUN_LENIENT:-0}" = "1" ] && [ $rc -eq 3 ] && rc=0
exit $rc

# ── Remaining step (research-grade, the full D3 #1) ──────────────────────────
# To upgrade this from a COVERAGE certificate to a byte-level EQUIVALENCE
# certificate per run, extend the extracted OCaml driver
# (src/formal-semantics/rocq/extracted/driver.ml, built by extraction-byte-diff.sh)
# to read a serialized stmt_ir on stdin and print emit_stmt_full_complete of it;
# then this script would diff that against `pycsl-ir-dump.py | Module6` for THIS
# input — a Necula-style certificate that the codegen for this exact run matched
# the formal emitter. The reusable build is already in bin/extraction-byte-diff.sh.
