#!/usr/bin/env python3
"""agent-feature-supervisor — orchestrate the rollout of an approved
missing-*-feature.md plan.

Per better-agent.md Phase 3 and cmmi-tailoring-plan-follow-up.md
Item 1.3. **v1: gate-only.** The supervisor never writes code itself.
It does three things:

  1. Parse the feature plan's "Implementation surface" section into
     a list of phases, each phase with a list of target files.
  2. For each phase, check the targets against the load-bearing
     deny-list (config/skills/agent-stdlib-annotate/references/
     load-bearing-files.md). If any target matches the deny-list,
     halt with exit 75 (human-needed) and write a halt-report.
  3. Otherwise, run the verification gate (pytest, reference tests,
     doc-coherency, cmmi-audit, stdlib-coverage diff). Halt with
     exit 74 on first gate failure.

Exit codes (extend coordinator.py's 72/73 convention):
  0   all phases either passed the gate or finished without action.
  72  inherited from coordinator (max retries) — not used by v1.
  73  inherited from coordinator (loop detection) — not used by v1.
  74  phase gate failure (pytest, doc-coherency, etc.).
  75  human-needed signal raised (load-bearing file modification).
  76  rollback failure (per-phase git-tag restore failed) — v1 stub.

The supervisor's persona and Extreme Rigor discipline are documented in
``config/agents/agent-feature-supervisor.md`` (loaded as ``_AGENT_DESCRIPTION``
and prepended to LLM-delegation prompts so a delegate inherits the same
rules). The acceptance-block syntax authors write against lives in
``config/skills/csl-from-scratch/references/acceptance-syntax.md``.

Usage:
    bin/agent-feature-supervisor --feature-file <path.md>
    bin/agent-feature-supervisor --feature-file <path.md> --skip-gate
        (parse + classify only; useful for dry runs and tests)
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

# Make this script's directory (…/agents) importable so the
# `feature_supervisor` package and the sibling `llm_client` resolve under both
# direct execution AND importlib loading (the ER tests load this file by path).
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Modular internals (extracted) — re-exported so the importlib-loaded
# module (tests) sees the same names, and the orchestrators below resolve
# them in this namespace (so monkeypatching e.g. run_gate works).
from feature_supervisor._common import *  # noqa: E402,F401,F403
from feature_supervisor.denylist import *  # noqa: E402,F401,F403
from feature_supervisor.acceptance import *  # noqa: E402,F401,F403
from feature_supervisor.plan import *  # noqa: E402,F401,F403
from feature_supervisor.gate import *  # noqa: E402,F401,F403
from feature_supervisor.competency import *  # noqa: E402,F401,F403
from feature_supervisor.delegation import *  # noqa: E402,F401,F403
from feature_supervisor.report import *  # noqa: E402,F401,F403

def _delegate_phase(phase: "Phase", plan_text: str,
                    slug: str) -> tuple[bool, str]:
    """Run coding-LLM delegation for one phase. Returns (success, message).

    Behaviour:
        1. Tag HEAD as feature-<slug>-phase-<N>-start.
        2. Build phase-scoped prompt, dispatch via llm_generate.
        3. Extract fenced diff. If absent (LLM refused or malformed),
           return (False, "llm-refused").
        4. git apply --check then git apply.
        5. Run verification gate (subset).
        6. On gate fail: _rollback_phase and return (False, "gate-fail").
        7. On success: KEEP the tag (audit trail) and return (True, "").
    """
    # Best-effort import of llm_generate; defer error until needed
    try:
        from llm_client import llm_generate  # type: ignore
    except ImportError as e:
        return False, f"llm_client unavailable: {e}"

    tag = _phase_tag(slug, phase.number)
    # Create the start tag at HEAD; allow overwrite via -f (the only
    # -f we allow, scoped to tags only; bypass _git's check).
    subprocess.run(["git", "tag", "-f", tag],
                   cwd=str(_PROJECT_ROOT),
                   capture_output=True)

    prompt = _build_phase_prompt(phase, plan_text)
    try:
        llm_output = llm_generate(
            prompt=prompt,
            system="You are a coding assistant. Follow the rules in the "
                   "coding-llm-prompt scaffold above. " + FILE_OUTPUT_INSTRUCTION,
            agent_id=AGENT_NAME,
            model=_delegate_model(),
        )
    except Exception as e:
        return False, f"llm_generate raised: {e}"

    # Prefer full-file blocks (robust); fall back to a unified diff.
    files = _extract_files(llm_output)
    if files:
        ok, err, written = _write_files(files)
        if not ok:
            _rollback_phase(slug, phase.number, phase.target_files)
            return False, err
        rollback_targets = sorted(set(phase.target_files) | set(written))
    else:
        diff = _extract_diff(llm_output)
        if not diff:
            return False, ("llm refused or produced no diff "
                           "(output had neither FILE blocks nor a diff block)")
        ok, err = _apply_diff(diff)
        if not ok:
            return False, err
        rollback_targets = list(phase.target_files)

    # Re-run the gate (subset — just the cheap steps)
    quick_results = run_gate()
    if not all(r.passed for r in quick_results):
        _rollback_phase(slug, phase.number, rollback_targets)
        return False, "gate-fail (rolled back)"

    # ER gap 6: also evaluate the phase's acceptance claims after the
    # LLM diff applies. Without this, delegation succeeds based on
    # gate alone — exactly the proxy-claim pattern ER exists to
    # prevent. Empty acceptance list means the phase opted out or
    # was caught upstream by the completeness guard.
    if phase.acceptance:
        for claim in phase.acceptance:
            res = _check_acceptance(
                claim, _PROJECT_ROOT, _DEFAULT_TIMEOUT_SEC)
            if not res.passed:
                _rollback_phase(slug, phase.number, rollback_targets)
                return False, (
                    f"acceptance-fail (rolled back): {claim.raw_line!r} → "
                    f"{res.reason_if_failed}"
                )

    return True, ""


# ---------------------------------------------------------------------------
# Item 3.4 — agent log-context reader (queue-first, log-fallback)
# ---------------------------------------------------------------------------
#
# Backwards-compatible reader used by future log-citing features
# (e.g., LLM delegation prompts that quote recent agent activity,
# halt-reports that include relevant log lines). NOT YET CALLED by
# any existing code — pure forward-looking infrastructure landed
# today so that Item 3.4r (fallback removal) becomes a 1-line edit
# after the 14-day bridge clock plus a successful 1.4 delegation
# elapses (per cmmi-tailoring-plan-follow-up-3.md).
#
# Order of precedence:
#   1. Queue (projects/pycsl/message-queues/<agent>/inbox-from-logs/) —
#      canonical source once the bridge has run.
#   2. metrics/logs/<agent>.log — fallback when the queue is empty
#      AND the bridge cursor doesn't exist (fresh checkout, or
#      bridge has never run).
#
# Returns line text only (strings); callers that need the structured
# message envelope can call queue_reader.iter_messages() directly.

def _read_agent_log_context(
    agent: str,
    *,
    since: Optional["datetime.datetime"] = None,
    max_messages: int = 100,
) -> List[str]:
    """Return up to `max_messages` log lines for `agent`, queue-first.

    Item 3.4 scaffolding: no callers yet. The signature is the
    target API that future features (1.4-era LLM prompts,
    halt-report enrichment) will call.
    """
    # Try queue first
    queue_lines: List[str] = []
    try:
        import queue_reader  # type: ignore
        for msg in queue_reader.iter_messages(agent, since=since):
            queue_lines.append(msg.get("line_text", ""))
            if len(queue_lines) >= max_messages:
                break
    except ImportError:
        # queue_reader missing means we're in a degraded environment;
        # fall through to log-only mode.
        pass

    if queue_lines:
        return queue_lines

    # Fallback to metrics/logs/<agent>.log — only when the bridge
    # has never run (cursor absent). If the bridge HAS run and the
    # queue is empty, the agent legitimately has no recent activity;
    # do NOT fall back (that would mask bridge breakage).
    if _BRIDGE_CURSOR.is_file():
        return []

    log_file = _METRICS_LOGS / f"{agent}.log"
    if not log_file.is_file():
        return []
    try:
        lines = log_file.read_text(errors="replace").splitlines()
    except OSError:
        return []
    # Take last `max_messages` non-blank lines (most-recent activity)
    non_blank = [ln for ln in lines if ln.strip()]
    return non_blank[-max_messages:]



def supervise(feature_file: Path, skip_gate: bool,
              allow_llm_delegation: bool = False,
              allow_load_bearing: bool = False) -> int:
    if not feature_file.is_file():
        print(f"[{AGENT_NAME}] error: feature file does not exist: "
              f"{feature_file}", file=sys.stderr)
        return 2
    text = feature_file.read_text()
    phases = parse_feature_plan(text)
    if not phases:
        print(f"[{AGENT_NAME}] error: no '### Phase N' headers found under "
              f"'## Implementation surface' in {feature_file}", file=sys.stderr)
        return 2

    deny_list = load_deny_list()
    deny_hits: List[Tuple[int, str, str]] = []
    for p in phases:
        for t in p.target_files:
            matched = is_load_bearing(t, deny_list)
            if matched:
                deny_hits.append((p.number, t, matched))

    print(f"[{AGENT_NAME}] parsed {len(phases)} phases from {feature_file.name}")
    for p in phases:
        tags = []
        if p.status_done:
            tags.append("DONE")
        if p.optout_reason is not None:
            tags.append("OPTOUT")
        if p.acceptance:
            tags.append(f"{len(p.acceptance)} claim(s)")
        tag_str = f" [{', '.join(tags)}]" if tags else ""
        print(f"  Phase {p.number}: {p.title} — "
              f"{len(p.target_files)} target file(s){tag_str}")
    print(f"[{AGENT_NAME}] deny-list entries: {len(deny_list)}; "
          f"load-bearing hits: {len(deny_hits)}")

    # Record the competency-matrix resolution into the harness log (§5.1) so a
    # human can review which skills each phase's delegate receives.
    _append_resolved_competencies(phases)

    # ---- ER: plan-completeness guard (MISSING_ACCEPTANCE) ----
    # An open phase (not DONE) lacking an Acceptance block AND lacking
    # an explicit `none — <reason>` opt-out is incomplete. Halt
    # before running gate/acceptance — the plan itself is malformed.
    missing_acceptance = [
        p for p in phases
        if not p.status_done
        and not p.has_acceptance_header
    ]
    if missing_acceptance:
        reason = (
            f"{REASON_MISSING_ACCEPTANCE}: {len(missing_acceptance)} phase(s) "
            f"lack an **Acceptance:** block. Under Extreme Rigor every open "
            f"phase must declare its acceptance claims, or opt out via "
            f"`**Acceptance:** none — <reason>`."
        )
        miss_nums = ', '.join(str(p.number) for p in missing_acceptance)
        explanation = (
            f"{len(missing_acceptance)} open phase(s) (phase(s) {miss_nums}) "
            f"declare neither `**Status:** DONE` nor an `**Acceptance:**` block, "
            f"so they have no machine-checkable definition of done — the plan "
            f"is malformed and nothing was run yet. Add an `**Acceptance:**` "
            f"block to each (a command + predicate per `acceptance-syntax.md`), "
            f"or opt out explicitly with `**Acceptance:** none — <reason>` for "
            f"research/scoping phases.\n"
            f"See the report's `## Missing Acceptance blocks` section."
        )
        out = write_halt_report(
            feature_file, phases, deny_hits, [], reason,
            missing_acceptance_phases=missing_acceptance,
            explanation=explanation,
        )
        _print_halt(out, reason, EXIT_HUMAN_NEEDED, explanation,
                    review=[("feature file", feature_file)])
        log(str(_PROJECT_ROOT), AGENT_NAME,
            f"HALT exit=75 feature={feature_file.name} "
            f"reason={REASON_MISSING_ACCEPTANCE} "
            f"missing={len(missing_acceptance)}")
        return EXIT_HUMAN_NEEDED

    # ---- ER: acceptance evaluation ----
    # Run acceptance claims for every phase that has them. DONE phases
    # with claims must still pass (STATUS_FORGED if not). DONE phases
    # without claims are LEGACY_ACCEPTED (informational, no halt).
    # Opt-out phases are skipped entirely.
    acceptance_failures: List[Tuple[Phase, AcceptanceResult]] = []
    any_rejection = False
    legacy_count = 0
    optout_count = 0
    claims_evaluated = 0
    if phases:
        print(f"[{AGENT_NAME}] evaluating acceptance claims ...")
    for p in phases:
        if p.optout_reason is not None:
            optout_count += 1
            print(f"  [OPTOUT] Phase {p.number} — "
                  f"reason: {p.optout_reason or '(unspecified)'}")
            continue
        if p.status_done and not p.acceptance:
            legacy_count += 1
            print(f"  [LEGACY_ACCEPTED] Phase {p.number} — "
                  f"DONE without Acceptance block (grandfathered)")
            continue
        if not p.acceptance:
            # Shouldn't reach here: completeness guard caught it.
            continue
        all_pass = True
        for claim in p.acceptance:
            claims_evaluated += 1
            res = _check_acceptance(
                claim, _PROJECT_ROOT, _DEFAULT_TIMEOUT_SEC)
            if not res.passed:
                all_pass = False
                acceptance_failures.append((p, res))
                if res.reason_if_failed.startswith("CLAIM_REJECTED"):
                    any_rejection = True
        tag = "STATUS_VERIFIED" if (p.status_done and all_pass) else (
              "PASS" if all_pass else "FAIL")
        print(f"  [{tag}] Phase {p.number} — {len(p.acceptance)} claim(s)")

    # In delegation mode the failing claims are exactly the work to be done,
    # so don't halt here — fall through to delegation (its per-phase gate +
    # rollback is the arbiter). CLAIM_REJECTED (an unsafe acceptance command)
    # still halts: that is a malformed plan, not work to delegate.
    _will_delegate = allow_llm_delegation and (not deny_hits or allow_load_bearing)
    if acceptance_failures and (not _will_delegate or any_rejection):
        if any_rejection:
            reason_code = REASON_CLAIM_REJECTED
        elif any(p.status_done for (p, _) in acceptance_failures):
            reason_code = REASON_STATUS_FORGED
        else:
            reason_code = REASON_ACCEPTANCE_FAILED
        n_fail = len(acceptance_failures)
        n_pass = claims_evaluated - n_fail
        reason = (
            f"{reason_code}: {n_fail} acceptance "
            f"claim(s) failed. See the Acceptance failures section "
            f"of the halt-report for details."
        )
        if reason_code == REASON_STATUS_FORGED:
            explanation = (
                f"{n_fail} of {claims_evaluated} acceptance claim(s) failed, and "
                f"at least one belongs to a phase marked `**Status:** DONE` — so "
                f"that DONE marker is now untrue (STATUS_FORGED). An acceptance "
                f"claim is a phase's definition of done; it re-runs every "
                f"invocation. A DONE phase whose claim fails means the work it "
                f"claimed has regressed or never shipped.\n"
                f"Open the report's `## Acceptance failures` section: each entry "
                f"shows the exact command, predicate, and actual outcome."
            )
        elif reason_code == REASON_CLAIM_REJECTED:
            explanation = (
                f"An acceptance command was refused by the read-only safety "
                f"classifier (it tried to mutate state or reach the network). "
                f"Acceptance claims must be read-only. Rewrite the command "
                f"read-only, or move the mutation into a `bin/*` script and have "
                f"the claim invoke that script.\n"
                f"The offending command is in the report's `## Acceptance "
                f"failures` section ({n_fail} of {claims_evaluated} claim(s) failed)."
            )
        else:
            explanation = (
                f"{n_pass} of {claims_evaluated} acceptance claim(s) passed; "
                f"{n_fail} failed. A claim is the phase's definition of done; it "
                f"fails when the file, flag, or output it checks does not exist "
                f"yet. The gate passes what is already present and fails what is "
                f"not yet built — so this halt means the feature has not shipped "
                f"those phases yet, NOT that anything is broken (a claim "
                f"referencing an existing, already-verified artifact still "
                f"passes).\n"
                f"Open the report's `## Acceptance failures` section: each entry "
                f"shows the command, the predicate, and the actual outcome (e.g. "
                f"\"File '…' not found\" or \"unrecognized arguments\")."
            )
        out = write_halt_report(
            feature_file, phases, deny_hits, [], reason,
            acceptance_failures=acceptance_failures,
            explanation=explanation,
        )
        _print_halt(out, reason, EXIT_HUMAN_NEEDED, explanation,
                    review=[("feature file", feature_file)])
        log(str(_PROJECT_ROOT), AGENT_NAME,
            f"HALT exit=75 feature={feature_file.name} "
            f"reason={reason_code} "
            f"failures={n_fail}")
        return EXIT_HUMAN_NEEDED

    if legacy_count:
        print(f"[{AGENT_NAME}] {legacy_count} legacy DONE phase(s) "
              f"grandfathered (no Acceptance to verify).")
    if optout_count:
        print(f"[{AGENT_NAME}] {optout_count} phase(s) opted out of acceptance.")

    gate_results: List[GateResult] = []

    # 1.4a — LLM delegation (off by default). Only invoked when the
    # flag is set AND there are no deny-list hits AND there are
    # phases that have target files.
    delegation_results: list[tuple[int, bool, str]] = []
    if allow_llm_delegation and (not deny_hits or allow_load_bearing):
        slug = _slug(feature_file.stem)
        delegate_phases = [p for p in phases if p.target_files and not p.status_done]
        if deny_hits and allow_load_bearing:
            print(f"[{AGENT_NAME}] *** --allow-load-bearing: delegating "
                  f"LOAD-BEARING phases to the coding LLM. Each edit must pass "
                  f"the full gate or it is ROLLED BACK; surviving diffs STILL "
                  f"REQUIRE human review before merge. ***")
        if not delegate_phases:
            print(f"[{AGENT_NAME}] --allow-llm-delegation: no open phases "
                  f"with target files to delegate.")
        else:
            print(f"[{AGENT_NAME}] --allow-llm-delegation: delegating "
                  f"{len(delegate_phases)} phase(s) (LLM-driven; per-phase "
                  f"git-tag rollback on gate failure).")
            for p in delegate_phases:
                ok, msg = _delegate_phase(p, text, slug)
                delegation_results.append((p.number, ok, msg))
                status = "OK" if ok else "FAIL"
                print(f"  Phase {p.number} {status}: {msg or 'delegated diff applied + gate green'}")
                if not ok:
                    break  # halt on first failure
    elif not skip_gate and not deny_hits:
        print(f"[{AGENT_NAME}] running verification gate ...")
        gate_results = run_gate()
        for r in gate_results:
            mark = "SKIP" if r.skipped else ("PASS" if r.passed else "FAIL")
            print(f"  [{mark}] {r.step}")

    # Decide exit
    if deny_hits and not (allow_llm_delegation and allow_load_bearing):
        n = len(deny_hits)
        hit_phases = sorted({ph for ph, _, _ in deny_hits})
        reason = (
            f"Human-needed: {n} load-bearing file(s) named in "
            f"feature-plan phases. Supervisor (v1, gate-only) does not "
            f"edit load-bearing files autonomously."
        )
        explanation = (
            f"{n} phase target(s) (phase(s) {', '.join(map(str, hit_phases))}) "
            f"match the load-bearing deny-list. These files are the "
            f"parser/IR/emitter pipeline and normative docs: a wrong edit "
            f"silently breaks the proof pipeline, so the supervisor is "
            f"gate-only (v1) and never edits them autonomously — even when "
            f"every acceptance claim passes. A human (or an explicitly "
            f"delegated, reviewed coding session) must make and review those "
            f"edits, then re-run the supervisor to confirm the gate is green.\n"
            f"See the report's `## Load-bearing deny-list hits` section for the "
            f"exact phase→file→deny-list-entry matches."
        )
        out = write_halt_report(feature_file, phases, deny_hits, gate_results,
                                reason, explanation=explanation)
        _print_halt(out, reason, EXIT_HUMAN_NEEDED, explanation,
                    review=[("deny-list", _LOAD_BEARING_FILE),
                            ("feature file", feature_file)])
        log(str(_PROJECT_ROOT), AGENT_NAME,
            f"HALT exit=75 feature={feature_file.name} "
            f"deny_hits={n}")
        return EXIT_HUMAN_NEEDED

    if gate_results and not all(r.passed for r in gate_results):
        failed_steps = ', '.join(r.step for r in gate_results
                                 if not r.passed and not r.skipped)
        reason = "Gate failure: one or more verification steps failed."
        explanation = (
            f"The verification gate ran but a step failed: {failed_steps}. "
            f"This is an infrastructure/regression failure (the test suite, "
            f"audit, or doc-coherency itself is red), independent of the "
            f"feature's acceptance claims. Fix the failing step, then re-run.\n"
            f"See the report's `## Verification gate` section for the last "
            f"lines of the failing step's output."
        )
        out = write_halt_report(feature_file, phases, deny_hits, gate_results,
                                reason, explanation=explanation)
        _print_halt(out, reason, EXIT_GATE_FAIL, explanation,
                    review=[("feature file", feature_file)])
        log(str(_PROJECT_ROOT), AGENT_NAME,
            f"HALT exit=74 feature={feature_file.name} gate_fail")
        return EXIT_GATE_FAIL

    # 1.4a delegation result handling
    if delegation_results and not all(ok for (_, ok, _) in delegation_results):
        failed = [(n, m) for (n, ok, m) in delegation_results if not ok]
        reason = (
            f"Delegated phase(s) failed: {failed[0][0]} ({failed[0][1]}). "
            f"Tree restored via per-phase tag."
        )
        explanation = (
            f"Under `--allow-llm-delegation`, the coding-LLM delegate for "
            f"phase {failed[0][0]} did not land a gate-green diff "
            f"({failed[0][1]}). The working tree was restored from the "
            f"per-phase git tag, so no partial edit remains. Inspect the "
            f"phase, refine the plan or implement it manually, then re-run."
        )
        out = write_halt_report(feature_file, phases, deny_hits, [], reason,
                                explanation=explanation)
        _print_halt(out, reason, EXIT_GATE_FAIL, explanation,
                    review=[("feature file", feature_file)])
        log(str(_PROJECT_ROOT), AGENT_NAME,
            f"HALT exit=74 feature={feature_file.name} delegation_fail")
        return EXIT_GATE_FAIL

    # v1 success: no deny-list hits AND (gate skipped OR gate green).
    # The supervisor doesn't claim to have IMPLEMENTED anything — it
    # claims that no load-bearing files would be touched and the gate
    # is currently green. The actual implementation is the human's job
    # under v1.
    print(f"[{AGENT_NAME}] OK — no load-bearing hits; gate green. "
          f"Human implements phases manually; supervisor verifies after.")
    log(str(_PROJECT_ROOT), AGENT_NAME,
        f"OK feature={feature_file.name} phases={len(phases)}")
    return EXIT_OK


def main() -> int:
    parser = argparse.ArgumentParser(description="Feature-rollout supervisor.")
    parser.add_argument("--feature-file", type=Path, required=True,
                        help="Path to an approved missing-*-feature.md plan.")
    parser.add_argument("--skip-gate", action="store_true",
                        help="Skip the verification gate (parse + "
                        "deny-list check only).")
    parser.add_argument("--allow-llm-delegation", action="store_true",
                        help="Item 1.4a: delegate non-load-bearing phases "
                        "to a coding LLM. Per-phase git-tag rollback on "
                        "gate failure. Default OFF (preserves gate-only "
                        "v1 behaviour).")
    parser.add_argument("--allow-load-bearing", action="store_true",
                        help="DANGER: with --allow-llm-delegation, also "
                        "delegate phases that touch load-bearing files (the "
                        "parser/IR/emitter). Each delegated edit must still "
                        "pass the full gate or it is rolled back, and the "
                        "surviving diff REQUIRES human review before merge. "
                        "Relaxes the soundness perimeter — use deliberately.")
    args = parser.parse_args()
    if args.allow_load_bearing and not args.allow_llm_delegation:
        print(f"[{AGENT_NAME}] --allow-load-bearing implies --allow-llm-delegation "
              f"— enabling LLM delegation.")
        args.allow_llm_delegation = True
    return supervise(args.feature_file, args.skip_gate,
                     allow_llm_delegation=args.allow_llm_delegation,
                     allow_load_bearing=args.allow_load_bearing)


if __name__ == "__main__":
    sys.exit(main())
