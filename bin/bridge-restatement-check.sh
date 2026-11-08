#!/usr/bin/env bash
# bridge-restatement-check.sh — P0.1 of richer-contracts-bridge-plan.md.
#
# Thin wrapper over bin/bridge-restatement-check.py.  Mechanically checks that
# the WhyML re-statement EmitAssignExport.emit_F_assign (in
# src/formal-semantics/pycsl-formal-export.mlw) agrees with the certified Rocq
# emitter Phase6L_EmitAssign.v::emit_assign on the assign-relevant cases.
#
# Why not `why3 extract` + byte-diff (plan approach a)?  Why3 string.String.concat
# is a pure LOGIC symbol with no executable content, so the WhyML fragment cannot
# be extracted to OCaml.  This is the plan's fallback approach (b): a shared-oracle
# test, Rocq-pinned (the oracle atoms are validated against the Rocq-extracted
# emit_assign every run) and SMT-checked on the WhyML side (best-of-N Alt-Ergo/Z3).
#
# Usage:
#   bin/bridge-restatement-check.sh                      # run the cross-check
#   bin/bridge-restatement-check.sh --corrupt 'OLD/NEW'  # non-vacuity demo
# Exit: 0 pass, 1 a check failed, 2 setup error.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "${ROOT}/bin/bridge-restatement-check.py" "$@"
