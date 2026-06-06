#!/usr/bin/env bash
# bin/pre-commit-er.sh — Extreme Rigor pre-commit gate (gap 13).
#
# Runs the feature-supervisor over every ER-managed plan that is staged
# for this commit and BLOCKS the commit if a plan is *dishonest* or
# *malformed*:
#
#   STATUS_FORGED       a phase marked `**Status:** DONE` whose
#                       acceptance claims fail — the marker is a lie.
#   MISSING_ACCEPTANCE  a non-DONE phase with no Acceptance block and
#                       no explicit opt-out — the plan is malformed.
#   CLAIM_REJECTED      an acceptance claim uses a forbidden (mutating /
#                       networked / multi-statement) command.
#
# It does NOT block a normal work-in-progress plan: an open (non-DONE)
# phase whose acceptance simply isn't met yet halts the supervisor with
# ACCEPTANCE_FAILED (exit 75) — that's expected mid-development and is
# reported as a warning, not a blocker.
#
# Install (opt-in, per clone):
#   git config core.hooksPath .githooks
# .githooks/pre-commit is a symlink to this script.
#
# Bypass a single commit (use sparingly): `git commit --no-verify`.

set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"
cd "$REPO_ROOT"

SUPERVISOR="bin/agent-feature-supervisor"
if [[ ! -x "$SUPERVISOR" ]]; then
    # Nothing to enforce with; don't block the commit.
    exit 0
fi

# Plans staged for this commit: any `missing-*.md` (repo root or
# proposed-features/) plus the ER plan itself.
mapfile -t STAGED < <(
    git diff --cached --name-only --diff-filter=ACM 2>/dev/null \
    | grep -E '(^|/)(missing-.*\.md|feature-supervisor-extreme-rigor\.md)$' \
    || true
)

if [[ ${#STAGED[@]} -eq 0 ]]; then
    exit 0   # no ER-managed plan touched — fast path
fi

# The plans' acceptance claims shell out to `cmmi-audit.sh --quick`,
# whose [ER] step would otherwise re-enter the retrospective and
# recurse. Guard it. (See infinite-rec.md.)
export CMMI_AUDIT_NESTED=1

block=0
echo "[pre-commit-er] checking ${#STAGED[@]} staged ER plan(s) ..."
for plan in "${STAGED[@]}"; do
    [[ -f "$plan" ]] || continue
    out="$(timeout 600 "$SUPERVISOR" --feature-file "$plan" --skip-gate 2>&1)"
    rc=$?
    if [[ $rc -eq 0 ]]; then
        echo "  ✓ $plan — verified"
    elif [[ $rc -eq 75 ]]; then
        if echo "$out" | grep -qE "STATUS_FORGED|MISSING_ACCEPTANCE|CLAIM_REJECTED"; then
            reason="$(echo "$out" | grep -oE "STATUS_FORGED|MISSING_ACCEPTANCE|CLAIM_REJECTED" | head -1)"
            echo "  ✗ $plan — BLOCKED ($reason)"
            block=1
        else
            echo "  • $plan — open phases not yet met (ACCEPTANCE_FAILED); allowed (WIP)"
        fi
    else
        echo "  ✗ $plan — supervisor error (exit $rc)"
        block=1
    fi
done

if [[ $block -ne 0 ]]; then
    echo ""
    echo "[pre-commit-er] commit blocked: a staged plan is dishonest or malformed."
    echo "  Fix the plan (or close the gap it claims), then re-commit."
    echo "  To bypass for one commit: git commit --no-verify"
    exit 1
fi
exit 0
